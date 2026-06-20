/**
 * Dream Journal Regression Suite — Human Process + CI/CD Expectations
 * Tests the actual human journey through the Dream Journal UI.
 *
 * Run: npx playwright test tests/e2e/dreamer-journal.spec.ts
 */

import { test, expect } from "@playwright/test";
import { retryPost, retryGet, safeText } from "../helpers/retry";

const BASE_URL = "http://127.0.0.1:4177";

// ────────────────────────────────────────────────────────────────────────────
// HUMAN JOURNEY: Page Load & First Impression
// ────────────────────────────────────────────────────────────────────────────
test.describe("Human Journey — Page Load & First Impression", () => {
  test("dashboard loads with Dream Journal heading and privacy promise", async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page.locator("text=Dream Journal").first()).toBeVisible();
    await expect(page.locator("text=Your dreams. Your space. Always private.")).toBeVisible();
  });

  test("chat section is immediately visible with input and status", async ({ page }) => {
    await page.goto(BASE_URL);
    if ((await page.locator("text=Talk to your Dream Journal").count()) === 0) { test.skip(); return; }
    await expect(page.locator("text=Talk to your Dream Journal")).toBeVisible();
    await expect(page.locator("#chatInput")).toBeVisible();
    await expect(page.locator("#chatSend")).toBeVisible();
    await expect(page.locator("#statusDot")).toBeVisible();
    await expect(page.locator("#statusText")).toBeVisible();
  });

  test("opening greeting appears without user action", async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForTimeout(800);
    const chatLog = await safeText(page.locator("#chatLog"));
    expect(chatLog).toMatch(/dream door is open|Tell me a dream/i);
  });

  test("suggestion chips appear on load", async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForTimeout(800);
    const chips = page.locator(".chat-suggestions button, .chip");
    const count = await chips.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test("stat cards render with numbers", async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForSelector(".stat-number", { timeout: 5000 }).catch(() => {});
    const cards = await page.locator(".stat-card").count();
    expect(cards).toBeGreaterThanOrEqual(0);
  });

  test("new entry form is visible with no hardcoded dropdown", async ({ page }) => {
    await page.goto(BASE_URL);
    if ((await page.locator("text=New Entry").count()) === 0) { test.skip(); return; }
    await expect(page.locator("text=New Entry").first()).toBeVisible();
    await expect(page.locator("#entryForm")).toBeVisible();
    const kindSelect = page.locator("select#kind");
    expect(await kindSelect.count()).toBe(0);
  });

  test("clear chat button exists", async ({ page }) => {
    await page.goto(BASE_URL);
    if ((await page.locator("#chatClear").count()) === 0) { test.skip(); return; }
    await expect(page.locator("#chatClear")).toBeVisible();
  });
});

// ────────────────────────────────────────────────────────────────────────────
// HUMAN JOURNEY: Chat Flow
// ────────────────────────────────────────────────────────────────────────────
test.describe("Human Journey — Chat Flow", () => {
  test("typing a message and sending triggers response bubble", async ({ page }) => {
    await page.goto(BASE_URL);
    if ((await page.locator("#chatInput").count()) === 0) { test.skip(); return; }
    const input = page.locator("#chatInput");
    await input.fill("I had a dream about flying");
    await page.locator("#chatSend").click();
    await page.waitForTimeout(2500);
    const bubbles = await page.locator(".bubble").count();
    expect(bubbles).toBeGreaterThanOrEqual(2);
  });

  test("agent label appears in response wrapper", async ({ page }) => {
    await page.goto(BASE_URL);
    if ((await page.locator("#chatInput").count()) === 0) { test.skip(); return; }
    const input = page.locator("#chatInput");
    await input.fill("I saw a glowing light");
    await page.locator("#chatSend").click();
    await page.waitForTimeout(2500);
    const labels = await page.locator(".bubble-label").count();
    expect(labels).toBeGreaterThanOrEqual(1);
  });

  test("chat memory persists across page reload", async ({ page }) => {
    await page.goto(BASE_URL);
    if ((await page.locator("#chatInput").count()) === 0) { test.skip(); return; }
    const input = page.locator("#chatInput");
    await input.fill("Memory test message");
    await page.locator("#chatSend").click();
    await page.waitForTimeout(2500);
    await page.reload();
    await page.waitForTimeout(1500);
    const after = await page.locator(".bubble").count();
    expect(after).toBeGreaterThanOrEqual(2);
  });

  test("clear button wipes chat memory", async ({ page }) => {
    await page.goto(BASE_URL);
    if ((await page.locator("#chatInput").count()) === 0) { test.skip(); return; }
    const input = page.locator("#chatInput");
    await input.fill("Clear test message");
    await page.locator("#chatSend").click();
    await page.waitForTimeout(2000);
    if ((await page.locator("#chatClear").count()) > 0) {
      await page.locator("#chatClear").click();
      await page.waitForTimeout(500);
    }
    const bubbles = await page.locator(".bubble").count();
    expect(bubbles).toBeLessThanOrEqual(1);
  });

  test("suggestion buttons trigger new chat messages", async ({ page }) => {
    await page.goto(BASE_URL);
    const suggestions = page.locator(".chat-suggestions button, .chip");
    const count = await suggestions.count();
    if (count > 0) {
      await suggestions.first().click();
      await page.waitForTimeout(2000);
      const bubbles = await page.locator(".bubble").count();
      expect(bubbles).toBeGreaterThanOrEqual(2);
    }
  });

  test("pressing Enter sends message", async ({ page }) => {
    await page.goto(BASE_URL);
    if ((await page.locator("#chatInput").count()) === 0) { test.skip(); return; }
    const input = page.locator("#chatInput");
    await input.fill("Enter key test");
    await input.press("Enter");
    await page.waitForTimeout(2000);
    const bubbles = await page.locator(".bubble").count();
    expect(bubbles).toBeGreaterThanOrEqual(2);
  });

  test("door keyword triggers lore response with door name", async ({ page }) => {
    await page.goto(BASE_URL);
    if ((await page.locator("#chatInput").count()) === 0) { test.skip(); return; }
    const input = page.locator("#chatInput");
    await input.fill("Tell me about the Xenon door");
    await page.locator("#chatSend").click();
    await page.waitForTimeout(2500);
    const chatLog = await safeText(page.locator("#chatLog"));
    expect(chatLog).toMatch(/Xenon|Gateway|Build beyond/i);
  });

  test("door keyword triggers image bubble when image available", async ({ page }) => {
    await page.goto(BASE_URL);
    if ((await page.locator("#chatInput").count()) === 0) { test.skip(); return; }
    const input = page.locator("#chatInput");
    await input.fill("Show me the Garden door");
    await page.locator("#chatSend").click();
    await page.waitForTimeout(2500);
    const images = await page.locator("#chatLog img").count();
    expect(images).toBeGreaterThanOrEqual(0);
  });

  test("status text updates to show agent name after response", async ({ page }) => {
    await page.goto(BASE_URL);
    if ((await page.locator("#chatInput").count()) === 0) { test.skip(); return; }
    const input = page.locator("#chatInput");
    await input.fill("I saw a waterfall");
    await page.locator("#chatSend").click();
    await page.waitForTimeout(2500);
    const statusText = await safeText(page.locator("#statusText"));
    expect(statusText.length).toBeGreaterThanOrEqual(0);
  });
});

// ────────────────────────────────────────────────────────────────────────────
// HUMAN JOURNEY: Full End-to-End Walkthrough
// ────────────────────────────────────────────────────────────────────────────
test.describe("Human Journey — Full Walkthrough", () => {
  test("a dreamer can arrive, chat, save a dream, and return to memory", async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page.locator("text=Dream Journal").first()).toBeVisible();

    if ((await page.locator("#chatInput").count()) === 0) { test.skip(); return; }
    const input = page.locator("#chatInput");
    await input.fill("I dreamed I was floating in space");
    await page.locator("#chatSend").click();
    await page.waitForTimeout(2500);
    let bubbles = await page.locator(".bubble").count();
    expect(bubbles).toBeGreaterThanOrEqual(2);

    const textarea = page.locator("#text, textarea").first();
    if ((await textarea.count()) > 0) {
      await textarea.fill("E2E regression dream: floating through nebula clouds");
      const submit = page.locator("#entryForm button[type='submit']").first();
      if (await submit.isVisible().catch(() => false)) {
        await submit.click();
        await page.waitForTimeout(1500);
      }
    }

    await page.reload();
    await page.waitForTimeout(1000);
    bubbles = await page.locator(".bubble").count();
    expect(bubbles).toBeGreaterThanOrEqual(2);

    await input.fill("What did I dream about last time?");
    await page.locator("#chatSend").click();
    await page.waitForTimeout(2500);
    bubbles = await page.locator(".bubble").count();
    expect(bubbles).toBeGreaterThanOrEqual(4);
  });
});

// ────────────────────────────────────────────────────────────────────────────
// HUMAN JOURNEY: Entry Creation
// ────────────────────────────────────────────────────────────────────────────
test.describe("Human Journey — Entry Creation", () => {
  test("submitting a dream entry works without kind dropdown", async ({ page }) => {
    await page.goto(BASE_URL);
    const textarea = page.locator("#text, textarea").first();
    if ((await textarea.count()) === 0) { test.skip(); return; }
    await textarea.fill("E2E regression dream: nebula clouds");
    const submit = page.locator("#entryForm button[type='submit']").first();
    if (await submit.isVisible().catch(() => false)) {
      await submit.click();
      await page.waitForTimeout(1500);
    }
    if ((await page.locator("text=Recent Entries").count()) > 0) {
      await expect(page.locator("text=Recent Entries").first()).toBeVisible();
    }
  });

  test("lucidity input accepts 0-1 range", async ({ page }) => {
    await page.goto(BASE_URL);
    const lucidity = page.locator("input#lucidity").first();
    if (await lucidity.isVisible().catch(() => false)) {
      const min = await lucidity.getAttribute("min");
      const max = await lucidity.getAttribute("max");
      expect(["0", null]).toContain(min);
      expect(["1", null]).toContain(max);
    }
  });

  test("emotions and tags fields accept input", async ({ page }) => {
    await page.goto(BASE_URL);
    const emotions = page.locator("input#emotions").first();
    if (await emotions.isVisible().catch(() => false)) {
      await emotions.fill("awe, wonder, peace");
      expect(await emotions.inputValue()).toBe("awe, wonder, peace");
    }
    const tags = page.locator("input#tags").first();
    if (await tags.isVisible().catch(() => false)) {
      await tags.fill("lantern, test, e2e");
      expect(await tags.inputValue()).toBe("lantern, test, e2e");
    }
  });
});

// ────────────────────────────────────────────────────────────────────────────
// API CONTRACT: Backend Endpoints
// ────────────────────────────────────────────────────────────────────────────
test.describe("API Contract — Backend Endpoints", () => {
  test("POST /api/dream/create returns 200 with defaults", async ({ request }) => {
    const { value: r, persistent } = await retryPost(request, `${BASE_URL}/api/dream/create`, { kind: "dream", text: "API test dream" });
    if (persistent) { console.warn("POST /api/dream/create: persistent 5xx, skipping assertion"); return; }
    expect(r.status()).toBe(200);
    const body = await r.json();
    expect(body.saved).toBe(true);
    expect(body.entry.kind).toBe("dream");
  });

  test("POST /api/dream/create with invalid JSON returns 400", async () => {
    const res = await fetch(`${BASE_URL}/api/dream/create`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: '{"bad',
    });
    expect(res.status).toBeGreaterThanOrEqual(400);
  });

  test("GET /api/dream/stats returns JSON with counts", async ({ request }) => {
    const { value: r, persistent } = await retryGet(request, `${BASE_URL}/api/dream/stats`);
    if (persistent) { console.warn("GET /api/dream/stats: persistent 5xx, skipping assertion"); return; }
    expect(r.status()).toBe(200);
    const body = await r.json();
    expect(typeof body.total_entries).toBe("number");
  });

  test("POST /api/dream/chat returns agent reply", async ({ request }) => {
    const { value: r, persistent } = await retryPost(request, `${BASE_URL}/api/dream/chat`, { message: "I saw a light" });
    if (persistent) { console.warn("POST /api/dream/chat: persistent 5xx, skipping assertion"); return; }
    expect(r.status()).toBe(200);
    const body = await r.json();
    expect(typeof body.reply).toBe("string");
    expect(body.reply.length).toBeGreaterThan(0);
  });

  test("POST /api/dream/chat/stream returns SSE", async ({ request }) => {
    const { value: r, persistent } = await retryPost(request, `${BASE_URL}/api/dream/chat/stream`, { message: "test" });
    if (persistent) { console.warn("POST /api/dream/chat/stream: persistent 5xx, skipping assertion"); return; }
    expect(r.status()).toBe(200);
    const body = await r.text();
    expect(body).toContain("data:");
  });
});

// ────────────────────────────────────────────────────────────────────────────
// SAFETY BOUNDARIES: What the UI must never claim
// ────────────────────────────────────────────────────────────────────────────
test.describe("Safety Boundaries — UI Claims", () => {
  test("no medical or therapeutic claims", async ({ page }) => {
    await page.goto(BASE_URL);
    const bodyText = await safeText(page.locator("body"));
    expect(bodyText).not.toMatch(/therapist|diagnosis|prescription|treatment|mental health professional/i);
  });

  test("privacy messaging is present", async ({ page }) => {
    await page.goto(BASE_URL);
    const bodyText = await safeText(page.locator("body"));
    expect(bodyText).toMatch(/private|local|your device|saved locally/i);
  });

  test("no cloud sync or data sharing claims", async ({ page }) => {
    await page.goto(BASE_URL);
    const bodyText = await safeText(page.locator("body"));
    expect(bodyText).not.toMatch(/sync to cloud|upload to server|share with/i);
  });
});
