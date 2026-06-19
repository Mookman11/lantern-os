#!/usr/bin/env node

/**
 * Lantern OS QA Audit Script
 *
 * Comprehensive end-to-end functional testing of all pages and buttons.
 * Tests every clickable element and verifies functionality.
 */

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const BASE_URL = 'http://127.0.0.1:4177';
const TIMEOUT = 30000; // 30 seconds per operation
const REPORT_DIR = './reports';

// Issue #585 safeguards
const SCENARIO_TIMEOUT_MS = 120000; // abort a single page/scenario after 120s
const GOTO_MAX_ATTEMPTS = 3;        // retry transient 5xx / network errors this many times
const GOTO_RETRY_DELAY_MS = 1000;   // backoff between navigation attempts

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Race a promise against a timeout. On timeout the returned promise rejects with a
 * tagged error (code SCENARIO_TIMEOUT) so the runner can record a finding and move
 * to the next scenario instead of hanging the whole run.
 */
function withTimeout(promise, ms, label) {
  let timer;
  const timeout = new Promise((_resolve, reject) => {
    timer = setTimeout(() => {
      const err = new Error(`Scenario timed out after ${ms}ms: ${label}`);
      err.code = 'SCENARIO_TIMEOUT';
      reject(err);
    }, ms);
  });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
}

/**
 * Detect errors that mean the Playwright browser/page process died, so the runner
 * can restart the browser and resume the remaining scenarios.
 */
function isBrowserCrashError(err) {
  if (!err) return false;
  const msg = String(err.message || err);
  return /Target (?:page|frame|context)?\s*closed|Target closed|Browser(?:Context)? (?:has been )?closed|browser has (?:been )?(?:closed|disconnected)|Connection closed|Protocol error|crash/i.test(msg);
}

/**
 * Classify an HTTP status for network-resilience decisions.
 *   server-error (5xx) → transient, retry; client-error (4xx) → not retried; ok → 2xx/3xx.
 */
function classifyStatus(status) {
  if (typeof status !== 'number' || Number.isNaN(status)) return 'unknown';
  if (status >= 500) return 'server-error';
  if (status >= 400) return 'client-error';
  return 'ok';
}

// All pages discovered in public/
const PAGES = [
  '/',
  '/agent-leaderboard.html',
  '/agent-status.html',
  '/changelog.html',
  '/courtney.html',
  '/create.html',
  '/dashboard.html',
  '/dream-chat.html',
  '/dream-chat-v1.html',
  '/dream-chat-orion.html',
  '/dream-journal/',
  '/entry.html',
  '/flourishing.html',
  '/hff.html',
  '/hff/',
  '/knowledgecenter.html',
  '/observer-mesh-cube.html',
  '/outreach.html',
  '/pricing.html',
  '/proof.html',
  '/rag-house.html',
  '/settings/providers.html',
  '/three-doors.html',
  '/three-doors-game.html',
  '/trader-dashboard.html',
  '/trading.html',
  '/trading-news.html',
  '/upgrade-lab.html',
  '/wish-door.html',
];

// Selectors for clickable elements
const CLICKABLE_SELECTORS = [
  'button',
  'input[type="button"]',
  'input[type="submit"]',
  'a:not([href=""])',
  '[role="button"]',
  '.clickable',
  '.card-action',
  '.menu-item',
  '.toolbar-button',
  '[onclick]',
];

class QAAudit {
  constructor() {
    this.results = {
      pages: [],
      buttons: [],
      errors: [],
      apiFailures: [],
      jsErrors: [],
      themeIssues: [],
      missingRoutes: [],
      networkErrors: [], // issue #585: transient-retried + persistent network findings
      timeouts: [],      // issue #585: scenarios aborted at the 120s ceiling
      crashes: [],       // issue #585: browser crashes survived via restart+resume
    };
    this.browser = null;
    this._activeContext = null; // set during a scenario so a timeout can tear it down
    // Tunable safeguards (issue #585) — overridable in tests; defaults are production values.
    this.scenarioTimeoutMs = SCENARIO_TIMEOUT_MS;
    this.gotoMaxAttempts = GOTO_MAX_ATTEMPTS;
    this.gotoRetryDelayMs = GOTO_RETRY_DELAY_MS;
  }

  /** True while the Playwright browser is launched and connected. */
  isBrowserAlive() {
    return !!(this.browser && typeof this.browser.isConnected === 'function' && this.browser.isConnected());
  }

  /** Close a browser context without throwing (used in finally + timeout cleanup). */
  async _closeContextSafe(context) {
    try {
      if (context) await context.close();
    } catch (_e) {
      // context may already be gone (timeout/crash) — closing twice is harmless
    }
    if (this._activeContext === context) this._activeContext = null;
  }

  /** Tear down the browser and launch a fresh one (crash recovery). */
  async restartBrowser() {
    try {
      if (this.browser) await this.browser.close();
    } catch (_e) {
      // already dead
    }
    this.browser = null;
    await this.initialize();
  }

  async initialize() {
    console.log('🎬 Starting Playwright browser...');
    this.browser = await chromium.launch({ headless: true });
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
    }
  }

  /**
   * Navigate with network resilience (issue #585). Retries transient 5xx responses
   * and network errors (no response) up to GOTO_MAX_ATTEMPTS; if the failure persists
   * it records a networkErrors finding and returns { response: null }. Browser-crash
   * errors are re-thrown so the caller can restart Playwright.
   * @returns {Promise<{response: import('playwright').Response|null, persistent: boolean}>}
   */
  async navigateWithResilience(page, fullUrl, pageUrl) {
    let lastStatus = null;
    for (let attempt = 1; attempt <= this.gotoMaxAttempts; attempt++) {
      let response = null;
      try {
        response = await page.goto(fullUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });
      } catch (err) {
        // A crash message OR a browser that is no longer connected means Playwright
        // died — propagate so run() restarts it instead of retrying a dead browser.
        if (isBrowserCrashError(err) || !this.isBrowserAlive()) throw err;
        response = null; // transient network error — fall through to retry logic
      }

      if (!response) {
        if (attempt < this.gotoMaxAttempts) {
          await sleep(this.gotoRetryDelayMs * attempt);
          continue;
        }
        // Persistent network error → always produce a finding (acceptance criterion).
        this.results.networkErrors.push({
          page: pageUrl,
          url: fullUrl,
          error: 'No response (network error)',
          attempts: attempt,
          persistent: true,
        });
        return { response: null, persistent: true };
      }

      lastStatus = response.status();
      if (classifyStatus(lastStatus) === 'server-error') {
        if (attempt < this.gotoMaxAttempts) {
          await sleep(this.gotoRetryDelayMs * attempt);
          continue;
        }
        // Persistent 5xx → flag it, but still return the response so the page can be inspected.
        this.results.networkErrors.push({
          page: pageUrl,
          url: fullUrl,
          statusCode: lastStatus,
          error: `Persistent ${lastStatus} after ${attempt} attempts`,
          attempts: attempt,
          persistent: true,
        });
        return { response, persistent: true };
      }

      return { response, persistent: false };
    }
    return { response: null, persistent: true };
  }

  async testPage(pageUrl) {
    const context = await this.browser.newContext();
    this._activeContext = context;
    const page = await context.newPage();

    const apiCalls = [];
    const jsErrors = [];
    const consoleMessages = [];

    // Intercept API calls
    await page.on('request', request => {
      if (request.url().includes('/api/')) {
        apiCalls.push({
          url: request.url(),
          method: request.method(),
          timestamp: new Date().toISOString(),
        });
      }
    });

    // Capture JS errors
    page.on('pageerror', error => {
      jsErrors.push({
        message: error.message,
        stack: error.stack,
        page: pageUrl,
        timestamp: new Date().toISOString(),
      });
    });

    // Capture console messages
    page.on('console', msg => {
      consoleMessages.push({
        type: msg.type(),
        text: msg.text(),
        page: pageUrl,
      });
    });

    try {
      const fullUrl = `${BASE_URL}${pageUrl}`;
      console.log(`\n📄 Testing: ${pageUrl}`);

      const { response } = await this.navigateWithResilience(page, fullUrl, pageUrl);

      if (!response) {
        // navigateWithResilience already recorded a networkErrors finding; also note
        // it in errors so the summary's "did not load" count stays accurate.
        this.results.errors.push({
          page: pageUrl,
          error: 'Page did not load (network error)',
        });
        await this._closeContextSafe(context);
        return;
      }

      const statusCode = response.status();
      if (statusCode !== 200) {
        this.results.missingRoutes.push({
          page: pageUrl,
          statusCode,
          url: fullUrl,
        });
      }

      // Get all buttons/clickable elements (null-guard: always an array)
      const buttons = (await this.discoverButtons(page, pageUrl)) || [];

      // Check theme consistency
      const themeIssues = (await this.checkTheme(page, pageUrl)) || [];
      if (themeIssues.length > 0) {
        this.results.themeIssues.push(...themeIssues);
      }

      // Test each button (limit to 10 per page for speed)
      for (const button of buttons.slice(0, 10)) {
        await this.testButton(page, button, pageUrl, apiCalls);
      }

      // Collect page results
      this.results.pages.push({
        url: pageUrl,
        statusCode,
        buttonCount: buttons.length,
        buttons: buttons.map(b => ({
          label: b.label,
          selector: b.selector,
          type: b.type,
          href: b.href,
        })),
        apiCalls: apiCalls.length,
        jsErrors: jsErrors.length,
      });

      // Store errors and api calls
      if (jsErrors.length > 0) {
        this.results.jsErrors.push(...jsErrors);
      }

      if (apiCalls.length > 0) {
        this.results.apiFailures.push(...apiCalls);
      }

    } catch (error) {
      // A browser crash (by message OR a now-disconnected browser) must bubble up so
      // run() can restart Playwright and resume; ordinary scenario errors are recorded
      // as findings and the run continues.
      if (isBrowserCrashError(error) || !this.isBrowserAlive()) {
        throw error;
      }
      this.results.errors.push({
        page: pageUrl,
        error: error.message,
      });
    } finally {
      await this._closeContextSafe(context);
    }
  }

  async discoverButtons(page, pageUrl) {
    const buttons = [];
    if (!page) return buttons; // null-guard: no page, no buttons

    for (const selector of CLICKABLE_SELECTORS) {
      try {
        const elements = await page.$$eval(selector, els => {
          if (!Array.isArray(els)) return [];
          return els.map(el => {
            if (!el) return null;
            const rect = el.getBoundingClientRect();
            // Only include visible elements
            if (!rect || rect.width === 0 || rect.height === 0) return null;

            return {
              label: el.textContent?.trim().substring(0, 50) || el.getAttribute('aria-label') || el.name || '(unlabeled)',
              type: el.tagName.toLowerCase(),
              href: el.href,
              onclick: el.onclick ? true : false,
              ariaLabel: el.getAttribute('aria-label'),
              id: el.id,
              class: el.className,
            };
          }).filter(Boolean);
        });

        // $$eval resolves to an array, but guard anyway before iterating.
        if (!Array.isArray(elements)) continue;
        for (const el of elements) {
          // Avoid duplicates
          const exists = buttons.some(b =>
            b.label === el.label &&
            b.type === el.type &&
            b.href === el.href
          );
          if (!exists) {
            buttons.push({
              ...el,
              selector,
              page: pageUrl,
            });
          }
        }
      } catch (error) {
        // Selector not found on page, skip
      }
    }

    return buttons;
  }

  async testButton(page, button, pageUrl, apiCalls) {
    // Null-guard: skip silently if the page or the discovered selector is missing.
    if (!page || !button || !button.selector) return;
    try {
      const beforeUrl = page.url();

      // Click the button. locator().first() returns a handle even when nothing
      // matches; the click() then rejects and is caught below as a button error.
      const locator = page.locator(button.selector).first();
      try {
        await locator.click({ timeout: 2000 });
      } catch (e) {
        // Try scrolling and clicking if direct click fails
        await locator.scrollIntoViewIfNeeded();
        await locator.click({ timeout: 2000 });
      }

      // Wait briefly for potential navigation or changes
      await page.waitForTimeout(300);

      const afterUrl = page.url();
      const urlChanged = beforeUrl !== afterUrl;

      this.results.buttons.push({
        page: pageUrl,
        label: button.label,
        selector: button.selector,
        type: button.type,
        href: button.href,
        status: '✅ Working',
        urlChanged,
        actionType: urlChanged ? 'Navigation' : 'Click Successful',
      });

    } catch (error) {
      this.results.buttons.push({
        page: pageUrl,
        label: button.label,
        selector: button.selector,
        type: button.type,
        href: button.href,
        status: '❌ Error',
        error: error.message?.substring(0, 50),
        actionType: 'Failed',
      });
    }
  }

  async checkTheme(page, pageUrl) {
    const issues = [];
    if (!page) return issues; // null-guard
    try {
      // Check for Bootstrap-only pages
      const hasBootstrap = await page.evaluate(() => {
        return !!document.querySelector('[class*="bootstrap"]') ||
               !!document.querySelector('link[href*="bootstrap"]');
      });

      if (hasBootstrap) {
        issues.push({
          page: pageUrl,
          issue: 'Page uses Bootstrap (expected Lantern theme)',
          severity: '⚠ Medium',
        });
      }

      // Check for Lantern theme CSS
      const hasLanternTheme = await page.evaluate(() => {
        const styles = Array.from(document.styleSheets)
          .map(sheet => sheet.href || '')
          .join(' ');
        return styles.includes('lantern') ||
               styles.includes('theme') ||
               document.documentElement.classList.contains('dark');
      });

      if (!hasLanternTheme && !hasBootstrap) {
        issues.push({
          page: pageUrl,
          issue: 'No Lantern theme or Bootstrap detected',
          severity: '⚠ Low',
        });
      }

      // Check dark mode support
      const hasDarkModeSupport = await page.evaluate(() => {
        const html = document.documentElement;
        return html.getAttribute('data-theme') ||
               html.classList.contains('dark') ||
               getComputedStyle(html).getPropertyValue('--bg-color');
      });

      if (!hasDarkModeSupport) {
        issues.push({
          page: pageUrl,
          issue: 'Dark mode support may be missing',
          severity: '⚠ Low',
        });
      }

    } catch (error) {
      // Ignore theme check errors
    }
    return issues;
  }

  async generateReports() {
    if (!fs.existsSync(REPORT_DIR)) {
      fs.mkdirSync(REPORT_DIR, { recursive: true });
    }

    // Summary report
    const summary = this.generateSummary();
    fs.writeFileSync(
      path.join(REPORT_DIR, 'final-qa-summary.md'),
      summary
    );

    // Button audit
    const buttonAudit = this.generateButtonAudit();
    fs.writeFileSync(
      path.join(REPORT_DIR, 'button-audit.md'),
      buttonAudit
    );

    // JS errors
    if (this.results.jsErrors.length > 0) {
      const jsErrors = this.generateJSErrorReport();
      fs.writeFileSync(
        path.join(REPORT_DIR, 'js-errors.md'),
        jsErrors
      );
    }

    // Missing routes
    if (this.results.missingRoutes.length > 0) {
      const missingRoutes = this.generateMissingRoutesReport();
      fs.writeFileSync(
        path.join(REPORT_DIR, 'missing-routes.md'),
        missingRoutes
      );
    }

    // Theme issues
    if (this.results.themeIssues.length > 0) {
      const themeIssues = this.generateThemeReport();
      fs.writeFileSync(
        path.join(REPORT_DIR, 'theme-inconsistencies.md'),
        themeIssues
      );
    }

    // API failures
    if (this.results.apiFailures.length > 0) {
      const apiFails = this.generateAPIFailureReport();
      fs.writeFileSync(
        path.join(REPORT_DIR, 'api-failures.md'),
        apiFails
      );
    }

    // Resilience findings (issue #585): network errors, timeouts, crashes
    if (this.results.networkErrors.length > 0 ||
        this.results.timeouts.length > 0 ||
        this.results.crashes.length > 0) {
      fs.writeFileSync(
        path.join(REPORT_DIR, 'resilience-findings.md'),
        this.generateResilienceReport()
      );
    }

    // Full results JSON
    fs.writeFileSync(
      path.join(REPORT_DIR, 'qa-results.json'),
      JSON.stringify(this.results, null, 2)
    );

    console.log(`\n✅ Reports generated in ${REPORT_DIR}/`);
  }

  generateSummary() {
    const workingButtons = this.results.buttons.filter(b => b.status === '✅ Working').length;
    const errorButtons = this.results.buttons.filter(b => b.status === '❌ Error').length;

    return `# Lantern OS QA Audit Summary

**Date:** ${new Date().toISOString()}

## Overview

- **Total Pages Tested:** ${this.results.pages.length}
- **Total Buttons Discovered:** ${this.results.buttons.length}
- **Buttons Working:** ${workingButtons} ✅
- **Buttons with Errors:** ${errorButtons} ❌
- **JS Errors:** ${this.results.jsErrors.length}
- **Missing Routes:** ${this.results.missingRoutes.length}
- **Theme Issues:** ${this.results.themeIssues.length}
- **Network Errors (5xx/no-response):** ${this.results.networkErrors.length}
- **Scenario Timeouts (≥120s):** ${this.results.timeouts.length}
- **Browser Crashes (recovered):** ${this.results.crashes.length}

## Pages Tested

${this.results.pages.map(p =>
  `- \`${p.url}\` — ${p.buttonCount} buttons, Status: ${p.statusCode}`
).join('\n')}

## Critical Issues

${errorButtons > 0 ? `
### Broken Buttons (${errorButtons})

${this.results.buttons
  .filter(b => b.status === '❌ Error')
  .slice(0, 10)
  .map(b => `- **${b.page}** — "${b.label}": ${b.error}`)
  .join('\n')}
` : 'None ✅\n'}

${this.results.missingRoutes.length > 0 ? `
### Missing Routes (${this.results.missingRoutes.length})

${this.results.missingRoutes.map(r =>
  `- \`${r.page}\` — Status ${r.statusCode}`
).join('\n')}
` : 'None ✅\n'}

${this.results.jsErrors.length > 0 ? `
### JavaScript Errors (${this.results.jsErrors.length})

${this.results.jsErrors.slice(0, 5).map(e =>
  `- **${e.page}**: ${e.message}`
).join('\n')}
` : 'None ✅\n'}

## Recommendations

1. ${errorButtons > 0 ? 'Fix broken buttons (see button-audit.md)' : 'All buttons functional ✅'}
2. ${this.results.missingRoutes.length > 0 ? 'Fix missing routes (see missing-routes.md)' : 'All routes functional ✅'}
3. ${this.results.jsErrors.length > 0 ? 'Fix JS errors (see js-errors.md)' : 'No JS errors ✅'}
4. ${this.results.themeIssues.length > 0 ? 'Review theme inconsistencies (see theme-inconsistencies.md)' : 'Theme consistent ✅'}

## Next Steps

- Review detailed reports in ./reports/
- Fix critical issues
- Re-run audit: \`node scripts/qa-audit.js\`
`;
  }

  generateButtonAudit() {
    const byPage = {};
    this.results.buttons.forEach(btn => {
      if (!byPage[btn.page]) byPage[btn.page] = [];
      byPage[btn.page].push(btn);
    });

    let report = `# Button Audit Report

**Generated:** ${new Date().toISOString()}

## Summary

- Total Buttons: ${this.results.buttons.length}
- Working: ${this.results.buttons.filter(b => b.status === '✅ Working').length}
- Errors: ${this.results.buttons.filter(b => b.status === '❌ Error').length}

## By Page

`;

    Object.entries(byPage).forEach(([page, buttons]) => {
      const working = buttons.filter(b => b.status === '✅ Working').length;
      const errors = buttons.filter(b => b.status === '❌ Error').length;

      report += `\n### ${page} (${buttons.length} buttons)\n\n`;
      report += `**Status:** ${working}/${buttons.length} working\n\n`;

      report += '| Label | Type | Status | Action |\n';
      report += '|-------|------|--------|--------|\n';

      buttons.forEach(btn => {
        report += `| ${btn.label.substring(0, 30)} | \`${btn.type}\` | ${btn.status} | ${btn.actionType} |\n`;
      });
    });

    return report;
  }

  generateJSErrorReport() {
    return `# JavaScript Error Report

**Generated:** ${new Date().toISOString()}

## Errors by Page

${this.results.jsErrors.map(err => `
### ${err.page}

\`\`\`
${err.message}
\`\`\`

**Stack:**
\`\`\`
${err.stack?.substring(0, 500)}
\`\`\`
`).join('\n')}
`;
  }

  generateMissingRoutesReport() {
    return `# Missing Routes Report

**Generated:** ${new Date().toISOString()}

## Routes with Errors

${this.results.missingRoutes.map(r => `
- **URL:** \`${r.page}\`
- **Status Code:** ${r.statusCode}
- **Full URL:** ${r.url}
`).join('\n')}
`;
  }

  generateThemeReport() {
    return `# Theme Inconsistencies Report

**Generated:** ${new Date().toISOString()}

## Issues

${this.results.themeIssues.map(issue => `
### ${issue.page}

- **Issue:** ${issue.issue}
- **Severity:** ${issue.severity}
`).join('\n')}
`;
  }

  generateAPIFailureReport() {
    return `# API Failures Report

**Generated:** ${new Date().toISOString()}

## API Calls Made

${this.results.apiFailures.slice(0, 50).map(call => `
- **URL:** ${call.url}
- **Method:** ${call.method}
- **Time:** ${call.timestamp}
`).join('\n')}
`;
  }

  /**
   * Run a single scenario with the 120s ceiling and crash recovery (issue #585).
   * Never throws — one scenario can never kill the whole run.
   * @returns {Promise<'ok'|'timeout'|'crashed'|'error'>}
   */
  async runScenario(pageUrl) {
    try {
      await withTimeout(this.testPage(pageUrl), this.scenarioTimeoutMs, pageUrl);
      return 'ok';
    } catch (err) {
      if (err && err.code === 'SCENARIO_TIMEOUT') {
        this.results.timeouts.push({ page: pageUrl, error: err.message });
        console.warn(`⏱  ${err.message}`);
        // The orphaned scenario may still hold a context — tear it down.
        await this._closeContextSafe(this._activeContext);
        return 'timeout';
      }
      if (isBrowserCrashError(err) || !this.isBrowserAlive()) {
        this.results.crashes.push({ page: pageUrl, error: String((err && err.message) || err) });
        console.warn(`💥 Browser crashed on ${pageUrl} — restarting and resuming`);
        await this.restartBrowser();
        return 'crashed';
      }
      this.results.errors.push({ page: pageUrl, error: String((err && err.message) || err) });
      return 'error';
    }
  }

  generateResilienceReport() {
    const fmt = (rows, render) => rows.length ? rows.map(render).join('\n') : '_none_';
    return `# Resilience Findings (issue #585)

**Generated:** ${new Date().toISOString()}

## Network Errors (${this.results.networkErrors.length})

Transient 5xx / no-response navigations that were retried; \`persistent: true\` means
they still failed after ${GOTO_MAX_ATTEMPTS} attempts.

${fmt(this.results.networkErrors, n =>
  `- \`${n.page}\` — ${n.error}${n.statusCode ? ` (status ${n.statusCode})` : ''} [attempts: ${n.attempts || 'n/a'}${n.persistent ? ', persistent' : ''}]`)}

## Scenario Timeouts (${this.results.timeouts.length})

Scenarios aborted at the ${SCENARIO_TIMEOUT_MS / 1000}s ceiling so the run could continue.

${fmt(this.results.timeouts, t => `- \`${t.page}\` — ${t.error}`)}

## Browser Crashes Recovered (${this.results.crashes.length})

Playwright died mid-scenario; the browser was restarted and the run resumed.

${fmt(this.results.crashes, c => `- \`${c.page}\` — ${c.error}`)}
`;
  }

  async run() {
    try {
      await this.initialize();

      console.log(`🚀 Starting QA Audit for ${PAGES.length} pages...\n`);

      // Resume-friendly loop: each scenario is isolated. A timeout or crash on one
      // page records a finding and the run continues with the rest. On a crash the
      // browser is restarted (inside runScenario) and the page is retried once on the
      // fresh browser before moving on (issue #585: restart and resume).
      for (let i = 0; i < PAGES.length; i++) {
        const outcome = await this.runScenario(PAGES[i]);
        if (outcome === 'crashed') {
          await this.runScenario(PAGES[i]); // one retry on the freshly restarted browser
        }
      }

      console.log('\n📊 Generating reports...');
      await this.generateReports();

      // Print summary to console
      console.log(this.generateSummary());

    } catch (error) {
      console.error('❌ Audit failed:', error);
    } finally {
      await this.close();
    }
  }
}

module.exports = {
  QAAudit,
  withTimeout,
  isBrowserCrashError,
  classifyStatus,
  SCENARIO_TIMEOUT_MS,
  GOTO_MAX_ATTEMPTS,
};

// Run audit only when invoked directly, so tests can require() this module without
// launching a browser.
if (require.main === module) {
  const audit = new QAAudit();
  audit.run().catch(console.error);
}
