// Lantern V8 AI Highlight Engine
// Analyzes video content for highlights, motion, reactions, and key moments
// Output: HighlightTimeline with scored segments

const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

// ============================================================================
// DATA STRUCTURES
// ============================================================================

class HighlightTimeline {
  constructor(videoPath, duration, fps = 30) {
    this.videoPath = videoPath;
    this.duration = duration;
    this.fps = fps;
    this.highlights = [];
    this.metadata = {
      analyzedAt: new Date().toISOString(),
      version: "8.0",
    };
  }

  addHighlight(start, end, score, reason, tags = []) {
    this.highlights.push({
      start: Number(start.toFixed(1)),
      end: Number(end.toFixed(1)),
      duration: Number((end - start).toFixed(1)),
      score: Number(score.toFixed(2)),
      reason,
      tags,
    });
  }

  sort() {
    this.highlights.sort((a, b) => a.start - b.start);
    return this;
  }

  getTopHighlights(count = 5) {
    return [...this.highlights].sort((a, b) => b.score - a.score).slice(0, count);
  }

  toJSON() {
    return {
      videoPath: this.videoPath,
      duration: this.duration,
      fps: this.fps,
      highlights: this.highlights,
      topHighlights: this.getTopHighlights(5),
      metadata: this.metadata,
    };
  }
}

// ============================================================================
// MAIN ANALYSIS FUNCTION
// ============================================================================

async function analyzeVideoForHighlights(videoPath, options = {}) {
  const {
    fps = 5, // sample every 1/5th second
    motionThreshold = 0.15,
    audioThreshold = 0.7,
    sceneThreshold = 0.3,
    minHighlightDuration = 2.0,
    maxHighlightDuration = 30.0,
  } = options;

  // Get video metadata
  const metadata = await getVideoMetadata(videoPath);
  if (!metadata) {
    throw new Error(`Could not read video: ${videoPath}`);
  }

  const timeline = new HighlightTimeline(videoPath, metadata.duration, fps);

  // Analyze video streams
  const [motionFrames, audioSpikes, sceneChanges] = await Promise.all([
    detectMotion(videoPath, fps, motionThreshold),
    detectAudioSpikes(videoPath, fps, audioThreshold),
    detectSceneChanges(videoPath, fps, sceneThreshold),
  ]);

  // Merge and score highlights
  const highlights = mergeDetections(
    motionFrames,
    audioSpikes,
    sceneChanges,
    fps,
    minHighlightDuration,
    maxHighlightDuration
  );

  highlights.forEach((hl) => {
    timeline.addHighlight(hl.start, hl.end, hl.score, hl.reason, hl.tags);
  });

  timeline.sort();
  return timeline;
}

// ============================================================================
// MOTION DETECTION
// ============================================================================

async function detectMotion(videoPath, fps = 5, threshold = 0.15) {
  const frames = [];

  return new Promise((resolve, reject) => {
    const args = [
      "-i",
      videoPath,
      "-vf",
      `fps=${fps},scale=160:90`, // Downsample for speed
      "-f",
      "rawvideo",
      "-pix_fmt",
      "rgb24",
      "-",
    ];

    const ffmpeg = spawn("ffmpeg", args);
    let frameData = Buffer.alloc(0);
    let lastFrame = null;
    let frameIndex = 0;

    ffmpeg.stdout.on("data", (chunk) => {
      frameData = Buffer.concat([frameData, chunk]);
      const frameSize = 160 * 90 * 3; // RGB24

      while (frameData.length >= frameSize) {
        const frame = frameData.slice(0, frameSize);
        frameData = frameData.slice(frameSize);

        if (lastFrame) {
          const motion = calculateMotion(lastFrame, frame);
          // Record EVERY frame's motion at its REAL timestamp (frameIndex/fps).
          // Adaptive thresholding happens later in mergeDetections — a fixed
          // absolute threshold is scale-dependent and unreliable (real footage
          // here ranges ~0.7–50). The previous code also keyed timestamp off
          // frames.length, collapsing all detections into one 0.2s-spaced run
          // that always exceeded maxDuration → zero highlights.
          frames.push({ timestamp: frameIndex / fps, motion });
        }

        lastFrame = frame;
        frameIndex++;
      }
    });

    ffmpeg.stderr.on("data", () => {}); // Suppress ffmpeg output
    ffmpeg.on("close", (code) => {
      if (code === 0) {
        resolve(frames);
      } else {
        reject(new Error(`FFmpeg failed with code ${code}`));
      }
    });

    ffmpeg.on("error", reject);
  });
}

function calculateMotion(frame1, frame2) {
  let diff = 0;
  for (let i = 0; i < frame1.length; i += 3) {
    const dr = Math.abs(frame1[i] - frame2[i]);
    const dg = Math.abs(frame1[i + 1] - frame2[i + 1]);
    const db = Math.abs(frame1[i + 2] - frame2[i + 2]);
    diff += (dr + dg + db) / 3;
  }
  return diff / frame1.length;
}

// ============================================================================
// AUDIO SPIKE DETECTION
// ============================================================================

async function detectAudioSpikes(videoPath, fps = 5, threshold = 0.7) {
  return new Promise((resolve) => {
    // Extract audio and analyze loudness
    const audioArgs = [
      "-i",
      videoPath,
      "-vn",
      "-acodec",
      "pcm_s16le",
      "-ar",
      "16000",
      "-ac",
      "1",
      "-f",
      "s16le",
      "-",
    ];

    const ffmpeg = spawn("ffmpeg", audioArgs);
    const audioFrames = [];
    let audioBuffer = Buffer.alloc(0);
    let frameIndex = 0;

    ffmpeg.stdout.on("data", (chunk) => {
      audioBuffer = Buffer.concat([audioBuffer, chunk]);

      const samplesPerFrame = 16000 / fps;
      const bytesPerSample = 2;
      const bytesPerFrame = samplesPerFrame * bytesPerSample;

      while (audioBuffer.length >= bytesPerFrame) {
        const frameData = audioBuffer.slice(0, bytesPerFrame);
        audioBuffer = audioBuffer.slice(bytesPerFrame);

        // Record EVERY frame's loudness at its REAL timestamp (same timestamp
        // bug as motion previously: audioFrames.length keyed the time). Adaptive
        // thresholding happens in mergeDetections.
        const loudness = calculateLoudness(frameData);
        audioFrames.push({ timestamp: frameIndex / fps, loudness });
        frameIndex++;
      }
    });

    ffmpeg.stderr.on("data", () => {});
    ffmpeg.on("close", () => {
      resolve(audioFrames);
    });
    ffmpeg.on("error", () => {
      resolve([]); // Fail gracefully
    });
  });
}

function calculateLoudness(pcmData) {
  let sum = 0;
  for (let i = 0; i < pcmData.length; i += 2) {
    const sample = pcmData.readInt16LE(i);
    sum += Math.abs(sample);
  }
  const rms = Math.sqrt(sum / (pcmData.length / 2));
  return Math.min(1, rms / 32768); // Normalize to 0-1
}

// ============================================================================
// SCENE DETECTION
// ============================================================================

async function detectSceneChanges(videoPath, fps = 5, threshold = 0.3) {
  const frames = [];

  return new Promise((resolve) => {
    const args = [
      "-i",
      videoPath,
      "-vf",
      `fps=${fps},scale=160:90`,
      "-f",
      "rawvideo",
      "-pix_fmt",
      "rgb24",
      "-",
    ];

    const ffmpeg = spawn("ffmpeg", args);
    let frameData = Buffer.alloc(0);
    let lastFrame = null;
    let frameCount = 0;

    ffmpeg.stdout.on("data", (chunk) => {
      frameData = Buffer.concat([frameData, chunk]);
      const frameSize = 160 * 90 * 3;

      while (frameData.length >= frameSize) {
        const frame = frameData.slice(0, frameSize);
        frameData = frameData.slice(frameSize);

        if (lastFrame) {
          const diff = calculateHistogramDifference(lastFrame, frame);
          if (diff > threshold) {
            frames.push({
              timestamp: frameCount / fps,
              difference: diff,
            });
          }
        }

        lastFrame = frame;
        frameCount++;
      }
    });

    ffmpeg.stderr.on("data", () => {});
    ffmpeg.on("close", () => {
      resolve(frames);
    });
    ffmpeg.on("error", () => {
      resolve([]);
    });
  });
}

function calculateHistogramDifference(frame1, frame2) {
  const hist1 = buildHistogram(frame1);
  const hist2 = buildHistogram(frame2);

  let chi2 = 0;
  for (let i = 0; i < 256; i++) {
    const diff = hist1[i] - hist2[i];
    if (hist1[i] + hist2[i] > 0) {
      chi2 += (diff * diff) / (hist1[i] + hist2[i]);
    }
  }
  return Math.min(1, chi2 / 256);
}

function buildHistogram(frame) {
  const hist = new Array(256).fill(0);
  for (let i = 0; i < frame.length; i += 3) {
    const gray = (frame[i] + frame[i + 1] + frame[i + 2]) / 3;
    hist[Math.floor(gray)]++;
  }
  return hist;
}

// ============================================================================
// SCORING & MERGING
// ============================================================================

/** p-th percentile (0..1) of a numeric array. Returns 0 for an empty array. */
function percentile(values, p) {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const idx = Math.min(sorted.length - 1, Math.max(0, Math.floor(sorted.length * p)));
  return sorted[idx];
}

function mergeDetections(
  motionFrames,
  audioFrames,
  sceneFrames,
  fps,
  minDuration,
  maxDuration
) {
  if (!motionFrames.length) return [];

  // ── Adaptive thresholds ──────────────────────────────────────────────────
  // detectMotion/detectAudioSpikes now return EVERY frame's value, so we pick
  // the genuinely active moments relative to this clip's own distribution
  // rather than against a fixed absolute cutoff (which is scale-dependent and,
  // for real footage, either matched every frame or none).
  const motionVals = motionFrames.map((f) => f.motion);
  const maxMotion = Math.max(...motionVals) || 1;
  // Keep the top ~15% most-active frames, but never fewer than a sane floor so
  // a low-variance clip still yields candidates.
  const motionThresh = Math.max(percentile(motionVals, 0.85), percentile(motionVals, 0.5) * 1.2);

  const audioVals = audioFrames.map((f) => f.loudness);
  const audioThresh = audioVals.length ? percentile(audioVals, 0.85) : Infinity;

  // Peak frames above the adaptive motion threshold.
  const peaks = motionFrames.filter((f) => f.motion >= motionThresh);
  if (!peaks.length) return [];

  // ── Group adjacent peaks into runs ───────────────────────────────────────
  // Use a grouping gap >= minDuration so that distinct runs are always at least
  // minDuration apart. This guarantees that when a short run is later expanded
  // up to minDuration it can never overlap the next run (which would duplicate
  // footage in the rendered Short).
  const gap = Math.max(0.6, minDuration);
  const runs = [];
  let cur = null;
  for (const f of peaks) {
    if (!cur) {
      cur = { start: f.timestamp, end: f.timestamp, peak: f.motion };
    } else if (f.timestamp - cur.end < gap) {
      cur.end = f.timestamp;
      cur.peak = Math.max(cur.peak, f.motion);
    } else {
      runs.push(cur);
      cur = { start: f.timestamp, end: f.timestamp, peak: f.motion };
    }
  }
  if (cur) runs.push(cur);

  // ── Convert runs to highlights: expand short, SPLIT long (don't discard) ──
  const audioHit = (s, e) => audioFrames.some((a) => a.timestamp >= s && a.timestamp <= e && a.loudness >= audioThresh);
  const sceneHit = (s, e) => sceneFrames.some((sc) => sc.timestamp >= s && sc.timestamp <= e);

  const highlights = [];
  for (const run of runs) {
    let start = run.start;
    let end = Math.max(run.end, run.start + 0.4); // avoid zero-length single-frame peaks
    let dur = end - start;
    if (dur < minDuration) { end = start + minDuration; dur = minDuration; }

    // A long continuous run is real action — split it into <=maxDuration pieces
    // instead of throwing the whole thing away (the old bug).
    const nParts = Math.max(1, Math.ceil(dur / maxDuration));
    const partLen = dur / nParts;
    for (let i = 0; i < nParts; i++) {
      const ps = start + i * partLen;
      const pe = Math.min(end, ps + partLen);
      if (pe - ps < minDuration && nParts > 1) continue;

      const tags = ["motion"];
      let reason = "motion";
      let score = Math.min(1, run.peak / maxMotion); // normalized 0..1
      if (audioHit(ps, pe)) { tags.push("audio"); reason += " + audio"; score = Math.min(1, score + 0.15); }
      if (sceneHit(ps, pe)) { tags.push("scene"); reason += " + scene"; score = Math.min(1, score + 0.10); }

      highlights.push({ start: ps, end: pe, score, reason, tags });
    }
  }

  return highlights;
}

function scoreHighlight(motion, audio, scene, weights = {}) {
  const w = { motion: 0.4, audio: 0.4, scene: 0.2, ...weights };
  return (
    motion * w.motion + audio * w.audio + scene * w.scene
  );
}

// ============================================================================
// UTILITIES
// ============================================================================

async function getVideoMetadata(videoPath) {
  return new Promise((resolve) => {
    const ffprobe = spawn("ffprobe", [
      "-v",
      "error",
      "-show_entries",
      "format=duration",
      "-of",
      "default=noprint_wrappers=1:nokey=1:nokey=1",
      videoPath,
    ]);

    let output = "";
    ffprobe.stdout.on("data", (data) => {
      output += data.toString();
    });

    ffprobe.on("close", (code) => {
      if (code === 0) {
        const duration = parseFloat(output.trim());
        resolve({
          duration: isNaN(duration) ? 0 : duration,
          fps: 30, // Default assumption
        });
      } else {
        resolve(null);
      }
    });

    ffprobe.on("error", () => {
      resolve(null);
    });
  });
}

module.exports = {
  analyzeVideoForHighlights,
  HighlightTimeline,
  detectMotion,
  detectAudioSpikes,
  detectSceneChanges,
  scoreHighlight,
};
