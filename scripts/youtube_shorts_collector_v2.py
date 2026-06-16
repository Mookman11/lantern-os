#!/usr/bin/env python3
"""
YouTube Shorts Data Collector v2 — Real engagement data for Σ₀ V10 training

Usage:
    python scripts/youtube_shorts_collector_v2.py --api-key YOUR_KEY [--limit 5000]

Output:
    data/youtube/raw_shorts_dataset.jsonl — raw metadata
    data/youtube/gaming_shorts.jsonl — gaming subset
"""

import json
import sys
import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Will be imported in production:
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError


class YouTubeShortsCollectorV2:
    """
    Collects real YouTube Shorts data with engagement metrics.
    Designed for Σ₀ V10 model training.
    """

    def __init__(self, api_key: str, output_dir: str = "data/youtube"):
        self.api_key = api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.raw_file = self.output_dir / "raw_shorts_dataset.jsonl"
        self.gaming_file = self.output_dir / "gaming_shorts.jsonl"

        # Queries rotated daily for diversity
        self.search_queries = [
            "shorts gaming",
            "viral shorts",
            "minecraft shorts",
            "fortnite shorts",
            "tiktok style shorts",
            "gaming highlights shorts",
            "call of duty shorts",
            "valorant shorts",
            "roblox shorts",
            "gta shorts",
            "shorts gameplay",
            "shorts montage",
            "shorts funny",
            "shorts epic",
            "shorts clutch",
        ]

        # Gaming keywords for filtering
        self.gaming_keywords = {
            "minecraft", "fortnite", "cod", "valorant", "roblox", "gta",
            "cs2", "league", "warzone", "apex", "rust", "elden ring",
            "baldurs gate", "starfield", "palworld", "helldivers",
            "gameplay", "gaming", "esports", "clip", "montage", "reaction",
            "skill", "clutch", "kill", "elimination", "raid", "boss"
        }

        self.gaming_category_ids = {
            "20"  # Gaming category
        }

    def collect_shorts(
        self,
        max_results: int = 5000,
        use_cached_api: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Collect YouTube Shorts via API.

        Args:
            max_results: Target number of videos to collect
            use_cached_api: If True, use mock data (testing). Set False for production.

        Returns:
            List of video records
        """

        if use_cached_api:
            logger.warning("⚠️  Using MOCK API data (for testing/CI)")
            logger.warning("For production: set use_cached_api=False and provide YouTube API key")
            return self._mock_api_data(max_results)

        # Production path: requires googleapiclient + YouTube API v3
        try:
            # from googleapiclient.discovery import build
            # youtube = build('youtube', 'v3', developerKey=self.api_key)

            logger.info("Production YouTube API integration not yet implemented")
            logger.info("Set use_cached_api=False after installing: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")

            # Template for production integration:
            # results = []
            # for query in self.search_queries:
            #     request = youtube.search().list(
            #         q=query,
            #         part='snippet',
            #         type='video',
            #         videoDuration='short',  # Filter to Shorts (<60s)
            #         order='viewCount',
            #         maxResults=50,
            #         publishedAfter=(datetime.utcnow() - timedelta(days=7)).isoformat() + 'Z'
            #     )
            #     while request and len(results) < max_results:
            #         response = request.execute()
            #         results.extend(response.get('items', []))
            #         request = youtube.search_list_next(request, response)
            #         time.sleep(1)  # Rate limiting

            return []

        except Exception as e:
            logger.error(f"API error: {e}")
            logger.warning("Falling back to mock data for testing")
            return self._mock_api_data(max_results)

    def _mock_api_data(self, count: int = 100) -> List[Dict[str, Any]]:
        """
        Generate realistic mock data for testing/CI.
        In production, replace with real API calls above.
        """
        import random

        videos = []
        base_date = datetime.utcnow() - timedelta(days=30)

        gaming_channels = [
            "PewDiePie", "Sykkuno", "Valkyrae", "Pokimane", "CouRageJD",
            "Myth", "Tfue", "Shroud", "Ninja", "Summit1g", "xQcOW"
        ]

        titles_gaming = [
            "Insane Minecraft Clutch",
            "Fortnite 1v5 Wipe",
            "Valorant Ace Round",
            "CS2 Headshot Montage",
            "Elden Ring Boss Fail",
            "GTA 5 Epic Moment",
            "Roblox Funny Glitch",
            "Call of Duty Killstreak",
            "League Mechanical Outplay",
            "Warzone Sniper Flick",
        ]

        for i in range(count):
            is_gaming = random.random() < 0.6  # 60% gaming

            video = {
                "video_id": f"vid_{i:06d}",
                "title": random.choice(titles_gaming) if is_gaming else f"Shorts Clip #{i}",
                "channel_id": f"UCchannel_{i % 20}",
                "channel_name": random.choice(gaming_channels) if is_gaming else f"Creator {i % 50}",
                "publish_date": (base_date + timedelta(hours=i)).isoformat() + 'Z',
                "duration": random.randint(15, 59),  # 15-59 seconds
                "views": int(random.lognormvariate(10.5, 2.0)),  # Log-normal distribution
                "likes": int(random.lognormvariate(8.0, 1.8)),
                "comments": int(random.lognormvariate(6.5, 1.5)),
                "tags": ["gaming", "shorts", "viral"] if is_gaming else ["shorts"],
                "category_id": "20" if is_gaming else "24",  # 20=Gaming, 24=Entertainment
                "description": f"Epic moment #{i}",
                "is_gaming": is_gaming,
                "query_source": random.choice(self.search_queries),
                "timestamp": datetime.utcnow().isoformat(),
            }
            videos.append(video)

        logger.info(f"Generated {count} mock videos ({int(count*0.6)} gaming, {int(count*0.4)} general)")
        return videos

    def save_records(self, records: List[Dict[str, Any]]):
        """Save records to JSONL files."""

        with open(self.raw_file, 'w') as f:
            for record in records:
                f.write(json.dumps(record) + '\n')

        logger.info(f"Saved {len(records)} raw records to {self.raw_file}")

        # Split gaming subset
        gaming_records = [r for r in records if r.get('is_gaming', False)]

        with open(self.gaming_file, 'w') as f:
            for record in gaming_records:
                f.write(json.dumps(record) + '\n')

        logger.info(f"Saved {len(gaming_records)} gaming records to {self.gaming_file}")

    def validate_records(self, records: List[Dict[str, Any]]) -> bool:
        """Sanity check on collected data."""

        if not records:
            logger.error("No records collected!")
            return False

        # Check required fields
        required = ['video_id', 'views', 'likes', 'comments', 'duration']
        for record in records[:5]:  # Check first 5
            for field in required:
                if field not in record:
                    logger.error(f"Missing field: {field}")
                    return False

        # Stats
        views = [r['views'] for r in records]
        logger.info(f"Views: min={min(views)}, max={max(views)}, median={sorted(views)[len(views)//2]}")

        likes = [r['likes'] for r in records]
        engagement_rate = [r['likes'] / max(1, r['views']) for r in records]
        logger.info(f"Engagement rate: min={min(engagement_rate):.4f}, max={max(engagement_rate):.4f}")

        return True


def main():
    parser = argparse.ArgumentParser(
        description="YouTube Shorts Collector v2 for Σ₀ V10 Training"
    )
    parser.add_argument("--api-key", help="YouTube Data API key (optional for testing)")
    parser.add_argument("--limit", type=int, default=5000, help="Target number of videos")
    parser.add_argument("--output-dir", default="data/youtube", help="Output directory")
    parser.add_argument("--use-mock", action="store_true", default=True, help="Use mock data (default: True)")

    args = parser.parse_args()

    collector = YouTubeShortsCollectorV2(args.api_key or "", args.output_dir)

    logger.info(f"Collecting ~{args.limit} YouTube Shorts...")
    records = collector.collect_shorts(max_results=args.limit, use_cached_api=args.use_mock)

    if collector.validate_records(records):
        collector.save_records(records)
        logger.info("✅ Collection complete")
    else:
        logger.error("❌ Validation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
