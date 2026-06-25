/**
 * routes/api-tools-log.js
 *
 * REST API for tool execution logs.
 *
 * Endpoints:
 *   GET /api/tools/log/query?tool=Read&status=executed&limit=100
 *   GET /api/tools/log/stats
 *   GET /api/tools/log/failures?limit=50
 */

const express = require("express");
const logger = require("../lib/tool-logger");

const router = express.Router();

/**
 * GET /api/tools/log/query
 * Query tool execution logs.
 *
 * Query params:
 *   - tool: Filter by tool name (e.g., 'Read')
 *   - status: Filter by status ('executed', 'denied', 'error', etc.)
 *   - limit: Max results (default 1000, max 10000)
 *   - date: Specific date (YYYY-MM-DD, default today)
 */
router.get("/query", async (req, res) => {
  try {
    const { tool, status, limit = 100, date } = req.query;
    const maxLimit = Math.min(parseInt(limit, 10) || 100, 10000);

    const entries = await logger.query({
      tool,
      status,
      limit: maxLimit,
      date,
    });

    res.json({
      count: entries.length,
      entries,
    });
  } catch (err) {
    res.status(500).json({
      error: "failed_to_query_logs",
      message: err.message,
    });
  }
});

/**
 * GET /api/tools/log/stats
 * Get usage statistics.
 *
 * Query params: same as /query (to filter stats)
 */
router.get("/stats", async (req, res) => {
  try {
    const { tool, status, date } = req.query;

    const stats_data = await logger.stats({
      tool,
      status,
      date,
    });

    res.json(stats_data);
  } catch (err) {
    res.status(500).json({
      error: "failed_to_compute_stats",
      message: err.message,
    });
  }
});

/**
 * GET /api/tools/log/failures
 * Get recent tool execution failures.
 *
 * Query params:
 *   - limit: Max failures to return (default 50, max 500)
 */
router.get("/failures", async (req, res) => {
  try {
    const limit = Math.min(parseInt(req.query.limit, 10) || 50, 500);
    const failures = await logger.getRecentFailures(limit);

    res.json({
      count: failures.length,
      failures,
    });
  } catch (err) {
    res.status(500).json({
      error: "failed_to_query_failures",
      message: err.message,
    });
  }
});

/**
 * GET /api/tools/log/health
 * Quick health check for tool logger.
 */
router.get("/health", async (req, res) => {
  try {
    // Try a simple query to verify logging is working
    const entries = await logger.query({ limit: 1 });
    res.json({
      status: "ok",
      logger_available: true,
      latest_log_exists: entries.length > 0,
    });
  } catch (err) {
    res.status(500).json({
      status: "error",
      logger_available: false,
      error: err.message,
    });
  }
});

module.exports = router;
