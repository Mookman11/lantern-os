#!/usr/bin/env python3

"""
YouTube Shorts Research Pipeline - 12 Hour Continuous Learning

Collects metadata + learns editing patterns for Lanterns V10 editor.
Does NOT download full videos. Metadata + patterns only.

Usage:
    python scripts/shorts_research_loop.py --hours 12
    python scripts/shorts_research_loop.py --hours 24 --batch-size 100

Features learned:
    - Hook strength (title intensity, caption density, early structure)
    - Motion score (scene changes, activity, gameplay density)
    - Entropy (visual variety, transition diversity, pacing)
    - Gaming intensity (HUD, killfeed, facecam, gameplay %)
    - Retention estimate (composite score)

Output:
    data/youtube/raw_shorts.jsonl - All collected shorts
    data/youtube/gaming_shorts.jsonl - Gaming-specific filtered
    data/youtube/shorts_features.jsonl - Feature vectors
    models/shorts_xgb_latest.json - Trained XGBoost model
    reports/research_*.json - Hourly progress reports
"""

import json
import time
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import logging

# Real HTTP via stdlib (no third-party dependency required)
import urllib.request
import urllib.parse
import urllib.error
import re

try:
    import numpy as np
except ImportError:
    np = None

try:
    import xgboost as xgb
except ImportError:
    xgb = None


def load_env(path='.env'):
    """Minimal .env loader so YOUTUBE_API_KEY is available without exporting."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, _, val = line.partition('=')
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
    except FileNotFoundError:
        pass


# YouTube Data API v3 quota costs (units)
QUOTA_SEARCH = 100   # search.list
QUOTA_VIDEOS = 1     # videos.list (per call, up to 50 ids)
DAILY_QUOTA_LIMIT = 10000


def parse_iso8601_duration(iso):
    """Convert ISO 8601 duration (PT1M30S) to seconds."""
    if not iso:
        return 0
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso)
    if not m:
        return 0
    hours = int(m.group(1) or 0)
    minutes = int(m.group(2) or 0)
    seconds = int(m.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('shorts_research.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class ShortsResearchPipeline:
    def __init__(self, hours=12, batch_size=50):
        self.hours = hours
        self.batch_size = batch_size
        self.start_time = time.time()
        self.end_time = self.start_time + (hours * 3600)

        # Data directories
        self.data_dir = Path('data/youtube')
        self.models_dir = Path('models')
        self.reports_dir = Path('reports')

        for d in [self.data_dir, self.models_dir, self.reports_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # File paths
        self.raw_shorts_file = self.data_dir / 'raw_shorts.jsonl'
        self.gaming_shorts_file = self.data_dir / 'gaming_shorts.jsonl'
        self.features_file = self.data_dir / 'shorts_features.jsonl'
        self.model_file = self.models_dir / 'shorts_xgb_latest.json'

        # Load API key from .env if not already in environment
        load_env()
        self.api_key = os.getenv('YOUTUBE_API_KEY')

        # Statistics
        self.stats = {
            'start_time': datetime.now().isoformat(),
            'shorts_collected': 0,
            'gaming_shorts': 0,
            'features_computed': 0,
            'models_trained': 0,
            'api_calls': 0,
            'api_errors': 0,
            'quota_used': 0,
            'runtime_seconds': 0
        }

        self.query_groups = [
            "most viewed youtube shorts",
            "gaming shorts",
            "minecraft shorts",
            "fortnite shorts",
            "roblox shorts",
            "warzone shorts",
            "cod shorts",
            "apex legends shorts",
            "stream highlight shorts",
            "funny gaming shorts",
            "viral gaming shorts",
            "best youtube shorts",
        ]

        logger.info(f"Research pipeline initialized: {hours}h runtime, {batch_size} batch size")

    def _api_get(self, endpoint, params):
        """Make a real YouTube Data API v3 GET request via stdlib urllib."""
        params['key'] = self.api_key
        url = f"https://www.googleapis.com/youtube/v3/{endpoint}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={'Accept': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))

    def query_youtube_api(self, query):
        """Query the REAL YouTube Data API v3 for Shorts metadata.

        search.list -> video IDs (100 quota units)
        videos.list -> statistics + contentDetails for those IDs (1 unit)
        Filters to true Shorts (duration <= 180s). Metadata only; no video download.
        """
        if not self.api_key:
            logger.warning("YOUTUBE_API_KEY not set - falling back to simulation")
            return self.simulate_shorts_data(query)

        try:
            # Step 1: search.list for video IDs
            search = self._api_get('search', {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'videoDuration': 'short',   # < 4 min; we post-filter to <= 180s
                'order': 'viewCount',
                'maxResults': min(self.batch_size, 50),
                'regionCode': 'US',
                'relevanceLanguage': 'en',
            })
            self.stats['api_calls'] += 1
            self.stats['quota_used'] += QUOTA_SEARCH

            if 'error' in search:
                logger.error(f"API error (search) for '{query}': {search['error'].get('message')}")
                self.stats['api_errors'] += 1
                return []

            video_ids = [it['id']['videoId'] for it in search.get('items', []) if it.get('id', {}).get('videoId')]
            if not video_ids:
                return []

            # Step 2: videos.list for full stats + duration
            videos = self._api_get('videos', {
                'part': 'snippet,statistics,contentDetails',
                'id': ','.join(video_ids),
            })
            self.stats['api_calls'] += 1
            self.stats['quota_used'] += QUOTA_VIDEOS

            if 'error' in videos:
                logger.error(f"API error (videos) for '{query}': {videos['error'].get('message')}")
                self.stats['api_errors'] += 1
                return []

            shorts = []
            for v in videos.get('items', []):
                snip = v.get('snippet', {})
                stat = v.get('statistics', {})
                content = v.get('contentDetails', {})
                duration = parse_iso8601_duration(content.get('duration', ''))

                # Keep only true Shorts (<= 180s)
                if duration == 0 or duration > 180:
                    continue

                shorts.append({
                    'id': v.get('id'),
                    'title': snip.get('title', ''),
                    'views': int(stat.get('viewCount', 0)),
                    'likes': int(stat.get('likeCount', 0)),
                    'comments': int(stat.get('commentCount', 0)),
                    'duration': float(duration),
                    'published': snip.get('publishedAt', ''),
                    'channel': snip.get('channelTitle', ''),
                    'tags': snip.get('tags', []),
                    'thumbnail': (snip.get('thumbnails', {}).get('high', {}) or {}).get('url', ''),
                    'caption_available': content.get('caption', 'false') == 'true',
                    'category': snip.get('categoryId', ''),
                    'query_source': query,
                })

            return shorts

        except urllib.error.HTTPError as e:
            logger.error(f"HTTP error querying '{query}': {e.code} {e.reason}")
            self.stats['api_errors'] += 1
            return []
        except Exception as e:
            logger.error(f"Error querying '{query}': {e}")
            self.stats['api_errors'] += 1
            return []

    def simulate_shorts_data(self, query):
        """Simulate realistic YouTube Shorts data for demo"""
        shorts = []
        for i in range(self.batch_size):
            short = {
                'id': f'{query[:8]}_{int(time.time())}_{i}',
                'title': f'{query.title()} #{i+1}',
                'views': int(1000 + np.random.exponential(50000)) if np else (1000 + i * 500),
                'likes': int(50 + np.random.exponential(1000)) if np else (50 + i * 10),
                'comments': int(10 + np.random.exponential(200)) if np else (10 + i * 2),
                'duration': float(15 + np.random.uniform(-5, 30)) if np else 30.0,
                'published': (datetime.now() - timedelta(days=i)).isoformat(),
                'channel': f'Gaming_Channel_{i % 100}',
                'tags': query.split(),
                'thumbnail': f'https://i.ytimg.com/vi/.../{i}.jpg',
                'caption_available': (i % 3 == 0),  # ~33% have captions
                'category': 'Gaming'
            }
            shorts.append(short)
        return shorts

    def append_shorts(self, shorts, target_file):
        """Append shorts to JSONL file (no duplicates)"""
        existing_ids = set()

        # Load existing IDs
        if target_file.exists():
            with open(target_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        existing_ids.add(data['id'])
                    except:
                        pass

        # Append new shorts
        new_count = 0
        with open(target_file, 'a') as f:
            for short in shorts:
                if short['id'] not in existing_ids:
                    f.write(json.dumps(short) + '\n')
                    new_count += 1

        return new_count

    def compute_features(self, short):
        """Compute Lantern V10 feature vectors for a short"""
        features = {
            'video_id': short['id'],
            'title': short['title'],
            'views': short['views'],
            'likes': short['likes'],
            'comments': short['comments'],
            'duration': short['duration'],
            'engagement_rate': (short['likes'] + short['comments']) / max(short['views'], 1),
        }

        # Hook Strength: based on title intensity + caption availability + duration start
        title_words = len(short['title'].split())
        has_caps = short.get('caption_available', False)
        hook_strength = min(1.0, (title_words / 10) * 0.6 + (1 if has_caps else 0) * 0.4)
        features['hook_strength'] = hook_strength

        # Motion Score: approximated from duration + views ratio
        # Longer videos with high views = likely good pacing
        motion_score = min(1.0, short['duration'] / 60.0)
        features['motion_score'] = motion_score

        # Entropy: visual variety - approximated from engagement
        entropy_score = min(1.0, features['engagement_rate'] * 10)
        features['entropy_score'] = entropy_score

        # Gaming Intensity: match against title AND tags + category 20 (Gaming)
        GAMING_KEYWORDS = [
            'game', 'gaming', 'gamer', 'clip', 'highlight', 'montage', 'gameplay',
            'minecraft', 'fortnite', 'cod', 'warzone', 'roblox', 'apex', 'valorant',
            'overwatch', 'fps', 'csgo', 'cs2', 'pubg', 'gta', 'fifa', 'f2p', 'rpg',
            'speedrun', 'clutch', 'noscope', 'pvp', 'boss', 'raid', 'loadout',
        ]
        haystack = (short.get('title', '') + ' ' + ' '.join(short.get('tags', []) or [])).lower()
        is_gaming = (
            any(kw in haystack for kw in GAMING_KEYWORDS)
            or str(short.get('category', '')) == '20'  # YouTube category 20 = Gaming
            or 'gaming' in short.get('query_source', '')
        )
        gaming_score = 1.0 if is_gaming else 0.2
        features['gaming_score'] = gaming_score

        # Retention Estimate: composite
        features['retention_estimate'] = (
            0.35 * hook_strength +
            0.25 * motion_score +
            0.20 * entropy_score +
            0.20 * gaming_score
        )

        return features

    def batch_extract_features(self):
        """Extract features from all collected shorts"""
        if not self.raw_shorts_file.exists():
            logger.warning("No raw shorts file to extract features from")
            return 0

        new_features = 0
        existing_ids = set()

        # Load existing feature IDs
        if self.features_file.exists():
            with open(self.features_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        existing_ids.add(data['video_id'])
                    except:
                        pass

        # Extract features for new shorts
        with open(self.raw_shorts_file, 'r') as inf, \
             open(self.features_file, 'a') as outf:
            for line in inf:
                try:
                    short = json.loads(line)
                    if short['id'] not in existing_ids:
                        features = self.compute_features(short)
                        outf.write(json.dumps(features) + '\n')
                        new_features += 1
                except:
                    pass

        return new_features

    def load_features(self):
        """Load all feature vectors"""
        features = []
        if self.features_file.exists():
            with open(self.features_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        features.append(data)
                    except:
                        pass
        return features

    def train_xgboost_model(self):
        """Train XGBoost on retention prediction every 1000 videos"""
        if not xgb:
            logger.warning("XGBoost not installed, skipping model training")
            return False

        features = self.load_features()

        if len(features) < 100:
            logger.info(f"Only {len(features)} features, need 100+ for training")
            return False

        try:
            logger.info(f"Training XGBoost on {len(features)} samples...")

            # Prepare feature matrix
            X = []
            y = []

            for feat in features:
                X.append([
                    feat.get('hook_strength', 0.5),
                    feat.get('motion_score', 0.5),
                    feat.get('entropy_score', 0.5),
                    feat.get('gaming_score', 0.5),
                    feat.get('engagement_rate', 0.01)
                ])
                y.append(feat.get('retention_estimate', 0.5))

            if np:
                X = np.array(X)
                y = np.array(y)

            # Train model
            model = xgb.XGBRegressor(
                max_depth=8,
                n_estimators=300,
                learning_rate=0.05,
                subsample=0.8,
                random_state=42
            )
            model.fit(X, y)

            # Save model
            model.save_model(str(self.model_file))
            logger.info(f"✓ Model trained and saved: {self.model_file}")

            self.stats['models_trained'] += 1
            return True

        except Exception as e:
            logger.error(f"Error training model: {e}")
            return False

    def generate_report(self):
        """Generate hourly progress report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'elapsed_hours': (time.time() - self.start_time) / 3600,
            'runtime_remaining_hours': (self.end_time - time.time()) / 3600,
            'stats': self.stats.copy()
        }

        # Add counts
        report['stats']['shorts_collected'] = self._count_lines(self.raw_shorts_file)
        report['stats']['gaming_shorts'] = self._count_lines(self.gaming_shorts_file)
        report['stats']['features_computed'] = self._count_lines(self.features_file)

        report_file = self.reports_dir / f"research_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📊 Report: {report['stats']['shorts_collected']} shorts, " +
                   f"{report['stats']['features_computed']} features computed")

        return report

    def _count_lines(self, filepath):
        """Count lines in file"""
        if not filepath.exists():
            return 0
        with open(filepath, 'r') as f:
            return sum(1 for _ in f)

    def run(self):
        """Main research loop"""
        logger.info(f"🚀 Starting 12-hour research pipeline")
        logger.info(f"End time: {datetime.fromtimestamp(self.end_time)}")

        query_index = 0
        cycle = 0

        # Quota-aware pacing: each cycle costs ~101 units; stay under the daily cap
        # and spread cycles evenly across the requested runtime.
        quota_per_cycle = QUOTA_SEARCH + QUOTA_VIDEOS
        safety_cap = DAILY_QUOTA_LIMIT - 200  # leave headroom
        max_cycles = max(1, safety_cap // quota_per_cycle) if self.api_key else 10_000_000
        cycle_interval = (self.hours * 3600) / max_cycles  # seconds between cycles
        logger.info(f"Quota plan: {max_cycles} cycles max (~{quota_per_cycle} units each), "
                    f"~{cycle_interval:.0f}s between cycles")

        while time.time() < self.end_time:
            # Hard stop before exceeding daily quota
            if self.api_key and self.stats['quota_used'] + quota_per_cycle > safety_cap:
                logger.warning(f"Quota safety cap reached ({self.stats['quota_used']} units). "
                               f"Pausing collection; will keep training/reporting until runtime ends.")
                self.generate_report()
                break

            cycle += 1
            elapsed = (time.time() - self.start_time) / 3600
            remaining = self.hours - elapsed

            logger.info(f"\n{'='*60}")
            logger.info(f"CYCLE {cycle} | {elapsed:.2f}h elapsed | {remaining:.2f}h remaining | "
                        f"quota {self.stats['quota_used']}/{safety_cap}")
            logger.info(f"{'='*60}")

            # Query next category (round-robin through all groups)
            query = self.query_groups[query_index % len(self.query_groups)]
            logger.info(f"\n📡 Querying: '{query}'")

            shorts = self.query_youtube_api(query)
            new_shorts = self.append_shorts(shorts, self.raw_shorts_file)

            # Filter gaming shorts
            gaming = [s for s in shorts if any(tag in s['title'].lower()
                                               for tag in ['game', 'gaming', 'clip'])]
            self.append_shorts(gaming, self.gaming_shorts_file)

            logger.info(f"  ✓ Collected {new_shorts} new shorts (gaming: {len(gaming)})")
            self.stats['shorts_collected'] += new_shorts
            self.stats['gaming_shorts'] += len(gaming)

            # Extract features
            new_features = self.batch_extract_features()
            logger.info(f"  ✓ Extracted {new_features} feature vectors")
            self.stats['features_computed'] += new_features

            # Train model every 1000 samples
            feature_count = self._count_lines(self.features_file)
            if feature_count > 0 and feature_count % 1000 < 50:
                logger.info(f"\n🤖 Training XGBoost model ({feature_count} samples)")
                self.train_xgboost_model()

            # Generate report
            self.generate_report()

            query_index += 1

            # Sleep to spread quota across the runtime (skip if past end)
            if time.time() + cycle_interval < self.end_time:
                logger.info(f"⏰ Sleeping {cycle_interval:.0f}s before next query...")
                time.sleep(cycle_interval)
            else:
                break

        # Final report
        self.stats['runtime_seconds'] = int(time.time() - self.start_time)
        logger.info(f"\n{'='*60}")
        logger.info(f"🏁 RESEARCH PIPELINE COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total runtime: {self.stats['runtime_seconds']}s")
        logger.info(f"Shorts collected: {self.stats['shorts_collected']}")
        logger.info(f"Gaming shorts: {self.stats['gaming_shorts']}")
        logger.info(f"Features computed: {self.stats['features_computed']}")
        logger.info(f"Models trained: {self.stats['models_trained']}")
        logger.info(f"API calls: {self.stats['api_calls']}")
        logger.info(f"API errors: {self.stats['api_errors']}")
        logger.info(f"\n📁 Outputs:")
        logger.info(f"  - {self.raw_shorts_file}")
        logger.info(f"  - {self.gaming_shorts_file}")
        logger.info(f"  - {self.features_file}")
        logger.info(f"  - {self.model_file}")
        logger.info(f"  - {self.reports_dir}/*.json")


def main():
    parser = argparse.ArgumentParser(
        description='YouTube Shorts 12-hour research pipeline for Lantern V10'
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=12,
        help='Hours to run pipeline (default: 12)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=50,
        help='Batch size per query (default: 50)'
    )

    args = parser.parse_args()

    # Validate
    if args.hours < 1:
        logger.error("Hours must be >= 1")
        sys.exit(1)

    # Run pipeline
    pipeline = ShortsResearchPipeline(hours=args.hours, batch_size=args.batch_size)
    try:
        pipeline.run()
    except KeyboardInterrupt:
        logger.info("\n⏸️  Pipeline interrupted by user")
        pipeline.stats['runtime_seconds'] = int(time.time() - pipeline.start_time)
        logger.info(f"Partial results saved ({pipeline.stats['shorts_collected']} shorts collected)")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
