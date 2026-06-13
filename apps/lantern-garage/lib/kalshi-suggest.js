/**
 * Kalshi suggestion engine — NOW-SLICE favorability for the swipe deck.
 *
 * Each card carries ONE favorable position the AI picks for *this instant*:
 * buy YES or buy NO, chosen from the current data slice only —
 *   - tick      : current yes_ask vs the previous tick (live momentum)
 *   - spread    : bid/ask tightness (how cleanly you can enter)
 *   - liquidity : resting size / liquidity on the book
 *   - urgency   : time to close (shorter game times rank first)
 * No historical trajectory is used — the decision is "only relevant to now's
 * data slice", so it stays valid under a tight (~6s) refresh.
 *
 * The deck is a binary: GREEN/right takes the favorable position, RED/left
 * passes. Nothing is sent here — the take routes through the existing dry-run /
 * kill-switch-gated /order endpoint.
 */

"use strict";

const kalshi = require("./kalshi-api");

function prevYesCents(m) {
  const f = parseFloat(m.previous_yes_ask_dollars);
  return Number.isFinite(f) ? Math.round(f * 100) : null;
}

function favorability(m, nowMs) {
  const yesA = m.yes_ask, yesB = m.yes_bid, noA = m.no_ask, noB = m.no_bid;
  const prevYes = prevYesCents(m);
  const tick = (yesA != null && prevYes != null) ? yesA - prevYes : 0;
  const spreadYes = (yesA != null && yesB != null) ? yesA - yesB : 99;
  const spreadNo = (noA != null && noB != null) ? noA - noB : 99;

  // favorable side from the now-slice: follow the live tick; tie → tighter book
  let side;
  if (tick > 0) side = "yes";
  else if (tick < 0) side = "no";
  else side = spreadYes <= spreadNo ? "yes" : "no";
  const sideAsk = side === "yes" ? yesA : noA;
  const spread = side === "yes" ? spreadYes : spreadNo;

  const close = m.close_time ? Date.parse(m.close_time) : NaN;
  const minsToClose = Number.isFinite(close) ? Math.max(0, (close - nowMs) / 60000) : Infinity;

  // conviction (all current-slice): momentum + book tightness + liquidity + urgency
  const mom = Math.min(20, Math.abs(tick) * 6);
  const tight = spread <= 1 ? 16 : spread <= 2 ? 9 : spread <= 4 ? 3 : 0;
  const liq = Math.min(14, Math.log10((parseFloat(m.liquidity_dollars) || 0) + 1) * 5);
  const urgency = minsToClose < 60 ? 12 : minsToClose < 240 ? 7 : minsToClose < 1440 ? 3 : 0;
  const conviction = Math.round(Math.min(82, 28 + mom + tight + liq + urgency));

  const dir = tick > 0 ? `YES ticked +${tick}¢`
            : tick < 0 ? `YES ticked ${tick}¢`
            : "flat tick";
  const tt = minsToClose === Infinity ? ""
           : minsToClose < 60 ? `closes ${Math.round(minsToClose)}m`
           : minsToClose < 1440 ? `closes ${Math.round(minsToClose / 60)}h`
           : `closes ${Math.round(minsToClose / 1440)}d`;
  const reason = [dir, `${spread}¢ spread`, tt].filter(Boolean).join(" · ");

  return { side, sideAsk, spread, tick, conviction, reason, minsToClose };
}

async function getSuggestions({ limit = 60, series_ticker = "KXMLBGAME" } = {}) {
  const mk = await kalshi.getMarkets({ series_ticker, status: "open", limit: 200 });
  const markets = (mk.data && mk.data.markets) || [];
  const nowMs = Date.now();

  const cards = [];
  for (const m of markets) {
    if (m.yes_ask == null && m.no_ask == null) continue;
    const f = favorability(m, nowMs);
    const denom = (m.yes_ask || 0) + (m.no_ask || 0);
    const yesPct = denom > 0 ? Math.round((m.yes_ask / denom) * 100) : (m.yes_ask || 0);
    cards.push({
      ticker: m.ticker,
      title: m.title || m.ticker,
      yesLabel: m.yes_sub_title || "YES",
      noLabel: m.no_sub_title || "NO",
      yesCents: m.yes_ask, noCents: m.no_ask, yesPct,
      favSide: f.side,                                   // 'yes' | 'no'
      favLabel: f.side === "yes" ? (m.yes_sub_title || "YES") : (m.no_sub_title || "NO"),
      favAsk: f.sideAsk,
      conviction: f.conviction,
      reason: f.reason,
      minsToClose: Number.isFinite(f.minsToClose) ? Math.round(f.minsToClose) : null,
      close: m.close_time || "",
    });
  }

  // time-sensitive: soonest-closing first (shorter game times), then conviction
  cards.sort((a, b) => {
    const ma = a.minsToClose == null ? 1e9 : a.minsToClose;
    const mb = b.minsToClose == null ? 1e9 : b.minsToClose;
    if (ma !== mb) return ma - mb;
    return b.conviction - a.conviction;
  });

  return {
    count: cards.length,
    generatedAt: new Date().toISOString(),
    note: "Now-slice favorability (live tick + spread + liquidity + time-to-close). Practice mode — green takes the favorable side, gated dry-run.",
    cards: cards.slice(0, limit),
  };
}

module.exports = { getSuggestions };
