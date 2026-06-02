# Project Rock and Stone — Crypto Mining Feasibility Research

**Status:** research-only, no miner code shipped  
**Evidence class:** `web_secondary` / `source_repo_evidence` — see notes  
**Last updated:** 2026-06-02

---

## Summary Verdict

Solo-mining any proof-of-work coin on consumer-grade CPU or GPU hardware is
**not economically viable** as of 2026 without explicitly framing it as a
lottery ticket. Global hash rates for all major PoW coins have grown by orders
of magnitude since the GPU era. A single consumer GPU earns roughly
$0.01–$0.10 per day before electricity on the most favorable small-cap coins,
and the expected time to solo-find a block on anything like Monero (XMR) or
Ethereum Classic (ETC) exceeds years to decades for a single machine.

**Pool mining on a consumer machine:** marginally cash-positive on a handful of
CPU-friendly coins (e.g. RandomX-family like Monero) only if electricity cost
is near zero (solar, already-on hardware). The margin is thin and shrinks with
any electricity cost above ~$0.05/kWh at realistic hash rates.

**Bottom line for Lantern OS:** mining is a research topic and an optional
user-opt-in capability only. Lantern OS will **not ship miner code** in any
default configuration. Any future integration requires explicit user consent,
visible status, local-first control, and a kill switch.

---

## Hardware / Power Table

The table below uses mid-2026 estimates. Difficulty and coin prices fluctuate;
treat these as order-of-magnitude references, not guarantees.

| Path | Example hardware | Hash rate (algo) | Power draw | Electricity cost/day ($0.10/kWh) | Est. gross revenue/day | Est. net/day | Notes |
|------|-----------------|-----------------|-----------|----------------------------------|----------------------|-------------|-------|
| CPU — budget | i5-12400 (6c) | ~8 kH/s (RandomX) | 65 W | $0.16 | ~$0.05–$0.15 (XMR pool) | **-$0.01–+$0.00** | Near break-even only at low elec. cost |
| CPU — high-end | Ryzen 9 7950X (16c) | ~23 kH/s (RandomX) | 170 W | $0.41 | ~$0.14–$0.40 (XMR pool) | **-$0.27–+$0.00** | Loses money at standard rates |
| GPU — mid-range | RTX 3070 | ~60 MH/s (Ethash/ETC) | 115 W | $0.28 | ~$0.05–$0.20 (ETC pool) | **-$0.23–-$0.08** | ETC difficulty still high post-merge |
| GPU — high-end | RTX 4090 | ~130 MH/s (Ethash) or ~2.5 MH/s (Kawpow) | 350 W | $0.84 | ~$0.10–$0.30 (best case) | **-$0.74–-$0.54** | Power cost dominates |
| ASIC — Antminer S21 (BTC) | Bitmain S21 Pro | 234 TH/s (SHA-256) | 3,510 W | $8.42 | ~$8–$15 at current diff | **-$0.42–+$6.58** | Economical only at low-cost power; requires significant capital outlay |
| ASIC — Monero/CPU class | N/A (ASIC-resistant by design) | — | — | — | — | **N/A** | RandomX intentionally ASIC-hostile |

**Key takeaway:** Only purpose-built ASICs (SHA-256 or similar) can meaningfully
compete for block rewards, and only with low electricity costs. Consumer hardware
mining is at best a break-even lottery on ASIC-resistant coins.

---

## Solo vs Pool Comparison

| Dimension | Solo mining | Pool mining |
|-----------|-------------|-------------|
| Expected payout per day | Near zero (stochastic; blocks are rare) | Proportional share of block reward, minus pool fee (1–3%) |
| Variance | Extremely high — could go months/years without a reward | Low — daily fractional payouts |
| Pool fee | None | 1–3% of earnings |
| Privacy | Higher (no external coordinator) | Lower (pool sees your address and IP) |
| Minimum viable hardware | Anything (but expected value ≈ 0) | Anything with enough hash rate to register shares |
| Recommended for consumer hardware? | Lottery framing only | Yes, if mining at all |
| When solo makes sense | Very small-cap coins with low network difficulty; large mining farms; ideological preference | Default choice for most users |

### Solo-mining lottery framing

Solo mining a large-network coin on consumer hardware is correctly framed as
buying a lottery ticket: your chance per day of finding a block on Monero solo
with a single 8 kH/s CPU is approximately 1 in 10,000+. This can be disclosed
honestly to users who want "set and forget" participation without pool trust.

---

## Coins Still Meaningful to Solo-Mine on Consumer Hardware

Almost none — but with lottery framing, the following are the least hostile:

| Coin | Algorithm | Network difficulty | Consumer hardware chance | Notes |
|------|-----------|--------------------|-------------------------|-------|
| Monero (XMR) | RandomX | High (but ASIC-resistant) | Very low (lottery) | Most CPU-friendly major coin; pool preferred |
| Verus (VRSC) | VerusHash 2.2 | Low-moderate | Low but non-trivial | CPU/GPU parity; true solo still uncommon |
| Raptoreum (RTM) | GhostRider | Low | Low | CPUs competitive; small market cap |
| ZEPH / Zephyr | RandomX variant | Low | Low | Small-cap; lottery framing |
| Small-cap PoW coins | Various | Very low | Moderate (lottery) | High volatility and exit-scam risk |

**Coins to avoid on consumer hardware:**
- Bitcoin (SHA-256): ASIC-only, consumer hardware earns effectively $0
- Ethereum Classic (ETC): GPU farms dominate; single card is lottery-only
- Litecoin, Bitcoin Cash, Dogecoin (Scrypt ASICs): ASIC-dominated

---

## Safety Constraints for Any Future Lantern OS Mining Feature

These constraints are non-negotiable if mining support is ever added:

1. **Opt-in only.** Mining must never start without explicit, informed user action.
   No background processes, no auto-start on install, no default-on flags.

2. **Local-first.** The miner process runs on the user's machine. No cloud
   relay, no silent telemetry about hash rate or earnings to Lantern servers.

3. **Visible.** A visible indicator (tray icon, dashboard widget, terminal
   output) must show mining state: running / paused / stopped.

4. **Stoppable.** A single user action must be able to immediately stop all
   mining processes. No orphan processes after the UI is closed.

5. **Logged.** Start time, stop time, coin, algorithm, and estimated hash rate
   must be written to a local log file. No silent operation.

6. **Power-aware.** The user must be shown an estimated power cost per day
   before starting. Default CPU/GPU usage caps should be conservative (e.g. 50%
   max thread usage) to avoid thermal issues.

7. **No wallet management.** Lantern OS does not store private keys or manage
   mining wallets. The user provides their own address.

8. **No revenue claims.** No projected earnings displayed as expected income.
   Frame all estimates as "estimated gross before electricity."

---

## No-Miner Implementation Boundary

**Lantern OS will NOT ship miner code in any default build.**

This is a hard boundary per the SKILL.md device boundary (section 9) and
wallet/cash rules (section 7):

- No mining binary, script, or library in `main` / `master` / `dev` by default.
- Any mining integration lives behind a feature flag that is `false` by default
  and must be explicitly enabled by the user.
- No miner code is bundled in Docker images, installers, or CI artifacts unless
  there is a separate, clearly labeled "mining edition" build.
- Projected mining revenue is `projection` class evidence — held, never
  promoted to "cleared cash."

---

## Next-Action Checklist (Research-Only Steps)

All items below are research or documentation tasks. None involve shipping miner code.

- [ ] **R1.** Identify 3–5 ASIC-resistant coins with community-maintained open-source
      miners (e.g. XMRig, SRBMiner). Document license and last commit date.
- [ ] **R2.** Benchmark RandomX hash rate on the primary dev machine and record
      in `data/hardware-inventory/` — evidence class `local_verified`.
- [ ] **R3.** Run a 24-hour pool-mining test on XMR (testnet or low-power mode)
      and record actual vs. estimated payout. Evidence class: `local_verified`.
- [ ] **R4.** Research legal and tax treatment of mining income in the operator's
      jurisdiction. Evidence class: `official_source` (IRS Notice 2014-21 + state guidance).
- [ ] **R5.** Evaluate XMRig's opt-in "donation" mode and understand its license
      (GPL-3.0) implications for any Lantern OS bundling.
- [ ] **R6.** Survey existing "mining dashboard" OSS projects (e.g. Awesome Miner
      alternatives) to evaluate reuse vs. build decision.
- [ ] **R7.** Draft a user-facing consent flow mockup (wireframe only) for the
      hypothetical opt-in mining toggle in the Lantern Chat dashboard.
- [ ] **R8.** Estimate thermal impact of sustained 50% CPU load on target
      hardware (record temperatures, throttle behavior). Evidence class: `local_verified`.
- [ ] **R9.** Write a go/no-go brief for product mining integration, gated behind
      at least: (a) legal review complete, (b) user research showing demand,
      (c) at least one successful 24h local test run logged.

---

## Evidence Notes

| Claim | Evidence class | Confidence | Source |
|-------|---------------|-----------|--------|
| Hash rate / revenue estimates | `web_secondary` | 0.60 | whattomine.com, minerstat.com (mid-2026 order-of-magnitude) |
| RandomX ASIC resistance | `official_source` | 0.90 | Monero project docs |
| Consumer GPU profitability negative | `web_secondary` | 0.80 | Mining profitability trackers, multiple sources |
| Legal / tax framing | `web_secondary` | 0.50 | General knowledge; jurisdiction-specific review required |
| Safety constraints | `operator_asserted` | 0.95 | Lantern OS SKILL.md sections 7, 9 + this document |

All revenue figures are `projection` class and must not be promoted to cleared cash.

---

*Project Rock and Stone — research document. No miner code is included or implied.*
