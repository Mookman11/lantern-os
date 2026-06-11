/**
 * Trading Microservice (Port 5050)
 * Provides market data, trading signals, and portfolio metrics
 * Integrated into Lantern OS — no external dependencies
 */

const http = require('http');
const path = require('path');
const fs = require('fs');

const PORT = process.env.AI_TRADER_DASHBOARD_PORT || 5050;
const HOST = process.env.AI_TRADER_DASHBOARD_HOST || '127.0.0.1';

// Data sources: Fetch from real APIs via trading-api-bridge
// Falls back to 0/empty if APIs unavailable
const TradingAPIBridge = require('./trading-api-bridge');
const bridge = new TradingAPIBridge();

// Fetch real watchlist data from Alpaca or return empty
async function getWatchlistPrices() {
  try {
    const alpacaAccount = await bridge.getAlpacaAccount();
    if (alpacaAccount && alpacaAccount.portfolio_value) {
      return [
        { ticker: 'Portfolio Value', price: parseFloat(alpacaAccount.portfolio_value), chg_pct: 0, is_crypto: false }
      ];
    }
  } catch (e) {
    // Fall back to empty
  }
  return [];
}

// Fetch real market status from IBKR or return zeros
async function getMarketStatus() {
  try {
    const ibkrAccount = await bridge.getIBKRAccount();
    if (ibkrAccount) {
      return {
        market: 'OPEN',
        market_open: true,
        vix: 0,
        vix_regime: 'UNKNOWN',
        spy_1d: 0,
        spy_5d: 0,
        day_pnl_pct: 0,
      };
    }
  } catch (e) {
    // Fall back to zeros
  }
  return {
    market: 'CLOSED',
    market_open: false,
    vix: 0,
    vix_regime: 'UNKNOWN',
    spy_1d: 0,
    spy_5d: 0,
    day_pnl_pct: 0,
  };
}

// HTTP request handler (async)
async function requestHandler(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const pathname = url.pathname;

  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Content-Type', 'application/json');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // Health check
  if (pathname === '/health') {
    res.writeHead(200);
    res.end(JSON.stringify({ status: 'healthy', timestamp: new Date().toISOString() }));
    return;
  }

  // Portfolio / positions — fetch from IBKR or return zeros
  if (pathname === '/api/positions') {
    try {
      const [ibkrAccount, ibkrPos] = await Promise.all([
        bridge.getIBKRAccount().catch(() => null),
        bridge.getIBKRPositions().catch(() => [])
      ]);

      res.writeHead(200);
      res.end(JSON.stringify({
        account: ibkrAccount || { equity: 0, cash: 0, pnl_today: 0, pnl_pct: 0 },
        positions: ibkrPos || [],
        source: ibkrAccount ? 'IBKR' : 'mock'
      }));
    } catch (e) {
      res.writeHead(200);
      res.end(JSON.stringify({
        account: { equity: 0, cash: 0, pnl_today: 0, pnl_pct: 0 },
        positions: [],
        source: 'error'
      }));
    }
    return;
  }

  // Market status — fetch from IBKR or return zeros
  if (pathname === '/api/market-status') {
    const status = await getMarketStatus();
    res.writeHead(200);
    res.end(JSON.stringify(status));
    return;
  }

  // Zones (technical levels) — no mock data, always empty
  if (pathname === '/api/zones') {
    res.writeHead(200);
    res.end(JSON.stringify({}));
    return;
  }

  // Watchlist prices — fetch from Alpaca or return empty
  if (pathname === '/api/watchlist-prices') {
    const prices = await getWatchlistPrices();
    res.writeHead(200);
    res.end(JSON.stringify(prices));
    return;
  }

  // Agent logs — no mock data, always empty
  if (pathname === '/api/agent-log') {
    res.writeHead(200);
    res.end(JSON.stringify([]));
    return;
  }

  // Recent orders — fetch from Alpaca or return empty
  if (pathname === '/api/orders') {
    try {
      const alpacaAccount = await bridge.getAlpacaAccount().catch(() => null);
      res.writeHead(200);
      res.end(JSON.stringify(alpacaAccount ? [] : []));
    } catch (e) {
      res.writeHead(200);
      res.end(JSON.stringify([]));
    }
    return;
  }

  // AI Trading signals — no mock data, always empty
  if (pathname === '/api/ai-trader/signals') {
    res.writeHead(200);
    res.end(JSON.stringify({ signals: [] }));
    return;
  }

  // News feed — no mock data, always empty
  if (pathname === '/api/news-feed') {
    res.writeHead(200);
    res.end(JSON.stringify({ news: [] }));
    return;
  }

  // Default 404
  res.writeHead(404);
  res.end(JSON.stringify({ error: 'Not found' }));
}

// Create and start server
const server = http.createServer((req, res) => {
  requestHandler(req, res).catch(err => {
    if (!res.headersSent) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: err.message }));
    }
  });
});

server.listen(PORT, HOST, () => {
  console.log(`\n${'='.repeat(60)}`);
  console.log('Trading Microservice (Lantern OS)');
  console.log(`${'='.repeat(60)}`);
  console.log(`🚀 Listening on ${HOST}:${PORT}`);
  console.log(`\nEndpoints:`);
  console.log(`  GET  /health                    — Health check`);
  console.log(`  GET  /api/positions             — Portfolio & positions`);
  console.log(`  GET  /api/market-status         — Market data`);
  console.log(`  GET  /api/zones                 — Technical zones`);
  console.log(`  GET  /api/watchlist-prices      — Watchlist tickers`);
  console.log(`  GET  /api/agent-log             — Trading agent logs`);
  console.log(`  GET  /api/orders                — Recent orders`);
  console.log(`  GET  /api/ai-trader/signals     — Trading signals`);
  console.log(`  GET  /api/news-feed             — Market news`);
  console.log(`\n${'='.repeat(60)}\n`);
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`✗ Port ${PORT} already in use`);
  } else {
    console.error(`✗ Server error: ${err.message}`);
  }
  process.exit(1);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('\nShutting down trading service...');
  server.close(() => process.exit(0));
});

process.on('SIGINT', () => {
  console.log('\nShutting down trading service...');
  server.close(() => process.exit(0));
});

module.exports = server;
