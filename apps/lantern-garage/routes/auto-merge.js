const ConverganceMergeTrainer = require('../lib/convergance-merge-trainer');

const trainer = new ConverganceMergeTrainer();

module.exports = async function autoMergeRoutes(req, res, url, deps) {
  const { sendJson, collectRequestBody } = deps;

  console.log('[auto-merge] Checking route:', url.pathname);
  if (!url.pathname.startsWith('/api/merge/')) {
    console.log('[auto-merge] Not a merge route, skipping');
    return false;
  }
  console.log('[auto-merge] Found merge route!');

  // GET /api/merge/status
  if (req.method === 'GET' && url.pathname === '/api/merge/status') {
    const status = trainer.getResolverStatus();
    sendJson(res, status, 200);
    return true;
  }

  // GET /api/merge/convergance-query
  if (req.method === 'GET' && url.pathname === '/api/merge/convergance-query') {
    const prompt = trainer.generateTrainingPrompt();
    sendJson(res, prompt, 200);
    return true;
  }

  // POST /api/merge/analyze — Analyze PR readiness
  if (req.method === 'POST' && url.pathname === '/api/merge/analyze') {
    return collectRequestBody(req, async (body) => {
      try {
        const prData = JSON.parse(body);
        const decision = trainer.resolver.analyzeMergeReadiness(prData);
        sendJson(res, decision, 200);
      } catch (e) {
        sendJson(res, { error: e.message }, 400);
      }
    });
  }

  // POST /api/merge/record — Record merge outcome
  if (req.method === 'POST' && url.pathname === '/api/merge/record') {
    return collectRequestBody(req, async (body) => {
      try {
        const { prData, outcome } = JSON.parse(body);
        trainer.resolver.recordMergeDecision(prData, prData.decision || {}, outcome);
        sendJson(
          res,
          { status: 'recorded', outcome, metrics: trainer.resolver.patterns.successMetrics },
          200
        );
      } catch (e) {
        sendJson(res, { error: e.message }, 400);
      }
    });
  }

  // POST /api/merge/apply-improvements — Apply Keystone recommendations
  if (req.method === 'POST' && url.pathname === '/api/merge/apply-improvements') {
    return collectRequestBody(req, async (body) => {
      try {
        const { approved } = JSON.parse(body);
        const result = trainer.applyRecommendations(approved || []);
        sendJson(res, result, 200);
      } catch (e) {
        sendJson(res, { error: e.message }, 400);
      }
    });
  }

  // POST /api/merge/keystone-response — Process Keystone training response
  if (req.method === 'POST' && url.pathname === '/api/merge/keystone-response') {
    return collectRequestBody(req, async (body) => {
      try {
        const keystoneAnalysis = JSON.parse(body);
        const result = trainer.processKeystoneResponse(keystoneAnalysis);
        sendJson(res, result, 200);
      } catch (e) {
        sendJson(res, { error: e.message }, 400);
      }
    });
  }

  // GET /api/merge/analysis — Get full analysis
  if (req.method === 'GET' && url.pathname === '/api/merge/analysis') {
    const analysis = trainer.analyzeAndImprove();
    sendJson(res, analysis, 200);
    return true;
  }

  // GET /api/merge/export — Export training history
  if (req.method === 'GET' && url.pathname === '/api/merge/export') {
    const history = trainer.exportTrainingHistory();
    sendJson(res, history, 200);
    return true;
  }

  return false;
};
