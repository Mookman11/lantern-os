/**
 * Auto Merge Resolver Routes
 *
 * Endpoints for auto merge resolver management and !convergance integration:
 * - GET /api/merge/status — Current resolver health and metrics
 * - POST /api/merge/analyze — Analyze readiness of a PR
 * - POST /api/merge/record — Record merge outcome for training
 * - GET /api/merge/convergance-query — Get training prompt for Keystone
 * - POST /api/merge/apply-improvements — Apply Keystone recommendations
 */

const ConverganceMergeTrainer = require('../lib/convergance-merge-trainer');

const trainer = new ConverganceMergeTrainer();

module.exports = {
  pattern: /^\/api\/merge\//,
  handler(req, res, { sendJson, collectRequestBody }) {
    // GET /api/merge/status
    if (req.method === 'GET' && req.url === '/api/merge/status') {
      const status = trainer.getResolverStatus();
      return sendJson(res, status, 200);
    }

    // GET /api/merge/convergance-query
    if (req.method === 'GET' && req.url === '/api/merge/convergance-query') {
      const prompt = trainer.generateTrainingPrompt();
      return sendJson(res, prompt, 200);
    }

    // POST /api/merge/analyze — Analyze PR readiness
    if (req.method === 'POST' && req.url === '/api/merge/analyze') {
      return collectRequestBody(req, async (body) => {
        try {
          const prData = JSON.parse(body);
          const decision = trainer.resolver.analyzeMergeReadiness(prData);
          return sendJson(res, decision, 200);
        } catch (e) {
          return sendJson(res, { error: e.message }, 400);
        }
      });
    }

    // POST /api/merge/record — Record merge outcome
    if (req.method === 'POST' && req.url === '/api/merge/record') {
      return collectRequestBody(req, async (body) => {
        try {
          const { prData, outcome } = JSON.parse(body);
          trainer.resolver.recordMergeDecision(prData, prData.decision || {}, outcome);
          return sendJson(
            res,
            { status: 'recorded', outcome, metrics: trainer.resolver.patterns.successMetrics },
            200
          );
        } catch (e) {
          return sendJson(res, { error: e.message }, 400);
        }
      });
    }

    // POST /api/merge/apply-improvements — Apply Keystone recommendations
    if (req.method === 'POST' && req.url === '/api/merge/apply-improvements') {
      return collectRequestBody(req, async (body) => {
        try {
          const { approved } = JSON.parse(body);
          const result = trainer.applyRecommendations(approved || []);
          return sendJson(res, result, 200);
        } catch (e) {
          return sendJson(res, { error: e.message }, 400);
        }
      });
    }

    // POST /api/merge/keystone-response — Process Keystone training response
    if (req.method === 'POST' && req.url === '/api/merge/keystone-response') {
      return collectRequestBody(req, async (body) => {
        try {
          const keystoneAnalysis = JSON.parse(body);
          const result = trainer.processKeystoneResponse(keystoneAnalysis);
          return sendJson(res, result, 200);
        } catch (e) {
          return sendJson(res, { error: e.message }, 400);
        }
      });
    }

    // GET /api/merge/analysis — Get full analysis
    if (req.method === 'GET' && req.url === '/api/merge/analysis') {
      const analysis = trainer.analyzeAndImprove();
      return sendJson(res, analysis, 200);
    }

    // GET /api/merge/export — Export training history
    if (req.method === 'GET' && req.url === '/api/merge/export') {
      const history = trainer.exportTrainingHistory();
      return sendJson(res, history, 200);
    }

    sendJson(res, { error: 'Not found' }, 404);
  },
};
