// Σ₀ V10 Integration — Wraps V10 analyzer to return HighlightTimeline format
// Bridges the new Sigma0 scorer with the existing Creator Dashboard pipeline

const path = require("path");
const fs = require("fs");

// Import V10 components from project lib/
let AnalyzerV10, FeatureExtractorV10, SigmaZeroV10Scorer;
try {
  const v10analyzer = require("../../../lib/analyzer-v10");
  AnalyzerV10 = v10analyzer.AnalyzerV10;
  const v10features = require("../../../lib/feature-extractor-v10");
  FeatureExtractorV10 = v10features.FeatureExtractorV10;
  const v10scorer = require("../../../lib/sigma0-v10-scoring");
  SigmaZeroV10Scorer = v10scorer.SigmaZeroV10Scorer;
} catch (e) {
  console.warn("[analyzer-v10-integration] V10 modules not available, falling back to placeholder:", e.message);
  // Fallback stubs if modules unavailable
  AnalyzerV10 = null;
  FeatureExtractorV10 = null;
  SigmaZeroV10Scorer = null;
}

// Import HighlightTimeline for compatibility
const { HighlightTimeline } = require("./highlight-engine");

/**
 * analyzeVideoWithSigmaZeroV10
 *
 * Main entry point for Σ₀ V10 analysis.
 * Replaces the old analyzeVideoForHighlights in the job pipeline.
 *
 * Args:
 *   videoPath: full path to video file
 *   options: { gaming, segmentDuration, ... }
 *   onProgress: (percent, statusKey, message) callback for progress reporting
 *
 * Returns:
 *   HighlightTimeline object (compatible with existing pipeline)
 */
async function analyzeVideoWithSigmaZeroV10(videoPath, options = {}, onProgress = () => {}) {
  if (!fs.existsSync(videoPath)) {
    throw new Error(`Video file not found: ${videoPath}`);
  }

  const isGaming = options.gaming !== false;
  const segmentDuration = options.segmentDuration || 0.5; // 500ms chunks

  // Get video metadata
  const metadata = await getVideoMetadata(videoPath);
  if (!metadata) {
    throw new Error(`Could not read video metadata: ${videoPath}`);
  }

  const videoDuration = metadata.duration || 60;
  const fps = metadata.fps || 30;

  // Create output timeline
  const timeline = new HighlightTimeline(videoPath, videoDuration, fps);

  // Create analyzer with V10 configuration
  const analyzer = new AnalyzerV10({
    isGaming,
    segmentDuration,
  });

  // Context for progress reporting (adapts to job-worker expectations)
  const ctx = {
    stage: (stageId) => {
      const stageMap = {
        analysis: "analyzing_motion",
        frame_scan: "analyzing_motion",
        features: "analyzing_motion",
        scoring: "detecting_highlights",
        thumbnail: "detecting_highlights",
      };
      onProgress(45, stageMap[stageId] || stageId, `[V10] ${stageId}`);
    },
    log: (msg) => {
      onProgress(45, "analyzing_motion", `[V10] ${msg}`);
    },
    liveStats: (stats) => {
      if (stats.processedSegments && stats.totalSegments) {
        const pct = 20 + (stats.processedSegments / stats.totalSegments) * 50; // 20% → 70%
        onProgress(pct, "analyzing_motion", `Analyzed ${stats.processedSegments}/${stats.totalSegments}`);
      }
    },
  };

  try {
    // Check if V10 modules are available
    if (!AnalyzerV10) {
      console.warn("[analyzer-v10-integration] V10 modules not loaded, using fallback");
      // Fallback: use legacy analyzer but mark as V10-compatible
      const legacyAnalyzer = require("./highlight-engine");
      const legacyTimeline = await legacyAnalyzer.analyzeVideoForHighlights(videoPath, {
        ...options,
        motionThreshold: 0.15,
      }, onProgress);
      legacyTimeline.metadata.version = "9.0 (legacy fallback)";
      return legacyTimeline;
    }

    // Run V10 analysis pipeline
    const analysis = await analyzer.analyzeVideo(videoPath, videoDuration, ctx);

    // Convert highlights to HighlightTimeline format
    if (analysis.highlights && Array.isArray(analysis.highlights)) {
      for (const hl of analysis.highlights) {
        timeline.addHighlight(
          hl.start,
          hl.end,
          hl.score,
          hl.reason || "Σ₀ V10 detected",
          ["v10", isGaming ? "gaming" : "general"]
        );
      }
    }

    // Ensure at least one highlight (safety)
    if (timeline.highlights.length === 0) {
      console.warn("[analyzer-v10-integration] No highlights detected, adding fallback");
      timeline.addHighlight(
        Math.max(0, videoDuration * 0.25),
        Math.min(videoDuration, videoDuration * 0.75),
        0.6,
        "Fallback (no strong signals)",
        ["fallback"]
      );
    }

    // Sort chronologically
    timeline.sort();

    // Attach Σ₀ metadata for downstream use
    if (analysis.sigma0State) {
      timeline.metadata.sigma0State = analysis.sigma0State;
    }
    timeline.metadata.version = "10.0 (Σ₀)";
    timeline.metadata.analyzedAt = new Date().toISOString();
    if (analysis.thumbnailFrame) {
      timeline.thumbnailFrame = analysis.thumbnailFrame;
    }

    onProgress(95, "detecting_highlights", `Highlights extracted: ${timeline.highlights.length} segments`);

    return timeline;
  } catch (error) {
    console.error("[analyzer-v10-integration] Analysis failed:", error.message);
    console.error("[analyzer-v10-integration] Falling back to legacy analyzer");

    // Emergency fallback to legacy analyzer
    try {
      const legacyAnalyzer = require("./highlight-engine");
      const legacyTimeline = await legacyAnalyzer.analyzeVideoForHighlights(videoPath, options || {}, onProgress);
      legacyTimeline.metadata.version = "9.0 (error fallback)";
      return legacyTimeline;
    } catch (fallbackError) {
      console.error("[analyzer-v10-integration] Fallback also failed:", fallbackError.message);
      throw fallbackError;
    }
  }
}

/**
 * getVideoMetadata
 * Placeholder — in production, use ffprobe
 */
async function getVideoMetadata(videoPath) {
  return new Promise((resolve) => {
    // TODO: Integrate ffprobe for real metadata
    // For now, return sensible defaults
    resolve({
      duration: 60,
      fps: 30,
      width: 1920,
      height: 1080,
    });
  });
}

module.exports = {
  analyzeVideoWithSigmaZeroV10,
  AnalyzerV10,
  SigmaZeroV10Scorer,
  FeatureExtractorV10,
};
