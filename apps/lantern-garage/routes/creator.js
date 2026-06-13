// Creator Suite Routes
// Handles highlight analysis, variant generation, exports, and analytics

const { analyzeVideoForHighlights } = require("../lib/highlight-engine");
const { generateVariants } = require("../lib/retention-engine");
const { detectSafeZones } = require("../lib/safe-zone-detector");
const { generateCaptions, generateVTT, generateSRT, generateJSON } = require("../lib/caption-engine");

module.exports = async function creatorRoutes(req, res, url, deps) {
  const { sendJson, path: pathModule, repoRoot } = deps;

  // =========================================================================
  // POST /api/creator/analyze
  // =========================================================================
  // Start highlight analysis on an uploaded video
  //
  // Request:
  // {
  //   "videoPath": "data/dreamer/videos/1234567890-video.mp4",
  //   "options": {
  //     "fps": 5,
  //     "motionThreshold": 0.15,
  //     "audioThreshold": 0.7,
  //     "minHighlightDuration": 1.0,
  //     "maxHighlightDuration": 30.0
  //   }
  // }
  //
  // Response:
  // {
  //   "success": true,
  //   "jobId": "highlight-12345",
  //   "videoPath": "data/dreamer/videos/1234567890-video.mp4",
  //   "timeline": { ... }
  // }

  if (url.pathname === "/api/creator/analyze" && req.method === "POST") {
    try {
      const raw = await deps.collectRequestBody(req);
      const body = JSON.parse(raw);

      const videoPath = body.videoPath;
      if (!videoPath) {
        sendJson(res, { error: "videoPath required" }, 400);
        return true;
      }

      const fullVideoPath = pathModule.join(repoRoot, videoPath);

      // Check if file exists
      const fs = require("fs");
      if (!fs.existsSync(fullVideoPath)) {
        sendJson(res, { error: "video file not found" }, 404);
        return true;
      }

      // Analyze video
      const timeline = await analyzeVideoForHighlights(fullVideoPath, body.options || {});

      // Store analysis result
      const analysisDir = pathModule.join(repoRoot, "data", "creator", "analyses");
      if (!fs.existsSync(analysisDir)) {
        fs.mkdirSync(analysisDir, { recursive: true });
      }

      const analysisPath = pathModule.join(analysisDir, `${Date.now()}-analysis.json`);
      fs.writeFileSync(analysisPath, JSON.stringify(timeline.toJSON(), null, 2));

      sendJson(res, {
        success: true,
        videoPath,
        timeline: timeline.toJSON(),
        analysisPath: analysisPath.replace(repoRoot, ""),
      });
    } catch (error) {
      console.error("[creator] analyze error:", error.message);
      sendJson(res, { error: error.message }, 500);
    }
    return true;
  }

  // =========================================================================
  // POST /api/creator/variants
  // =========================================================================
  // Generate A/B/C retention variants from highlight timeline
  //
  // Request:
  // {
  //   "highlightTimeline": { ... from /api/creator/analyze }
  // }
  //
  // Response:
  // {
  //   "variants": [
  //     {
  //       "variantId": "variant-a-hook-focused",
  //       "hook": { "text": "WAIT FOR IT", "duration": 0.8 },
  //       "pacing": "Fast Cut",
  //       "endingCaption": "WORTH IT",
  //       "captions": [...],
  //       "estimatedCompletionRate": 0.85,
  //       "estimatedReWatchRate": 0.72,
  //       "estimatedViralScore": 0.78
  //     },
  //     { ... variant B ... },
  //     { ... variant C ... }
  //   ]
  // }

  if (url.pathname === "/api/creator/variants" && req.method === "POST") {
    try {
      const raw = await deps.collectRequestBody(req);
      const body = JSON.parse(raw);

      if (!body.highlightTimeline) {
        sendJson(res, { error: "highlightTimeline required" }, 400);
        return true;
      }

      const variants = generateVariants(body.highlightTimeline);

      sendJson(res, {
        success: true,
        variantCount: variants.length,
        variants: variants.map((v) => v.toJSON()),
      });
    } catch (error) {
      console.error("[creator] variants error:", error.message);
      sendJson(res, { error: error.message }, 500);
    }
    return true;
  }

  // =========================================================================
  // POST /api/creator/captions
  // =========================================================================
  // Generate captions from highlight timeline with multiple export formats
  //
  // Request:
  // {
  //   "highlightTimeline": { ... },
  //   "strategy": "auto|gaming|emotional|narrative",
  //   "format": "vtt|srt|json"
  // }
  //
  // Response:
  // {
  //   "success": true,
  //   "captions": [...],
  //   "vtt": "...",
  //   "srt": "...",
  //   "json": {...}
  // }

  if (url.pathname === "/api/creator/captions" && req.method === "POST") {
    try {
      const raw = await deps.collectRequestBody(req);
      const body = JSON.parse(raw);

      if (!body.highlightTimeline) {
        sendJson(res, { error: "highlightTimeline required" }, 400);
        return true;
      }

      const strategy = body.strategy || "auto";
      const format = body.format || "all";

      const captions = generateCaptions(body.highlightTimeline, null, strategy);

      const result = {
        success: true,
        captionCount: captions.length,
        captions: captions.map((c) => c.toJSON()),
      };

      if (format === "vtt" || format === "all") {
        result.vtt = generateVTT(captions);
      }
      if (format === "srt" || format === "all") {
        result.srt = generateSRT(captions);
      }
      if (format === "json" || format === "all") {
        result.json = JSON.parse(generateJSON(captions));
      }

      sendJson(res, result);
    } catch (error) {
      console.error("[creator] captions error:", error.message);
      sendJson(res, { error: error.message }, 500);
    }
    return true;
  }

  // =========================================================================
  // POST /api/creator/safe-zones
  // =========================================================================
  // Detect safe zones in video (facecam, HUD, minimap, killfeed)
  //
  // Request:
  // {
  //   "videoPath": "data/dreamer/videos/...",
  //   "frameData": { width, height, pixels: [...] }
  // }

  if (url.pathname === "/api/creator/safe-zones" && req.method === "POST") {
    try {
      const raw = await deps.collectRequestBody(req);
      const body = JSON.parse(raw);

      if (!body.frameData) {
        sendJson(res, { error: "frameData required" }, 400);
        return true;
      }

      const safeZoneMap = await detectSafeZones(body.videoPath, body.frameData);

      sendJson(res, {
        success: true,
        zoneCount: safeZoneMap.safeZones.length,
        ...safeZoneMap.toJSON(),
      });
    } catch (error) {
      console.error("[creator] safe-zones error:", error.message);
      sendJson(res, { error: error.message }, 500);
    }
    return true;
  }

  // =========================================================================
  // GET /api/creator/health
  // =========================================================================
  // Check if creator service is ready

  if (url.pathname === "/api/creator/health" && req.method === "GET") {
    sendJson(res, {
      status: "ready",
      service: "creator-suite-v9",
      features: [
        "highlight-analysis",
        "motion-detection",
        "audio-spike-detection",
        "scene-detection",
        "variant-generation",
        "completion-prediction",
        "viral-scoring",
      ],
    });
    return true;
  }

  return false;
};
