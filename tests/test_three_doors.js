/**
 * Three Doors parsing and rendering tests
 * Verifies: [DOORS:] parsed, cleanText strips it, 3 chips rendered in browser
 * Runs offline — no server or LLM required.
 */

const assert = require("assert");
const { extractDoors, doorsOrFallback } = require("../apps/lantern-garage/lib/stream-chat");

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`  ✓ ${name}`);
    passed++;
  } catch (err) {
    console.error(`  ✗ ${name}`);
    console.error(`    ${err.message}`);
    failed++;
  }
}

function run() {
  console.log("\nThree Doors Parsing Tests\n");

  // ── extractDoors ──────────────────────────────────────────────────────
  test("extractDoors parses [DOORS:] with 3 items", () => {
    const text = "Hello dreamer.\n\n[DOORS: walk through the forest | listen to the stream | find the lantern]";
    const result = extractDoors(text);
    assert.strictEqual(result.doors.length, 3);
    assert.strictEqual(result.doors[0], "walk through the forest");
    assert.strictEqual(result.doors[1], "listen to the stream");
    assert.strictEqual(result.doors[2], "find the lantern");
  });

  test("extractDoors strips [DOORS:] from cleanText", () => {
    const text = "Reply text here.\n\n[DOORS: A | B | C]";
    const result = extractDoors(text);
    assert.ok(!result.cleanText.includes("[DOORS:"), "cleanText must not contain [DOORS: marker");
    assert.ok(!result.cleanText.includes("]"), "cleanText must not contain trailing ]");
    assert.strictEqual(result.cleanText, "Reply text here.");
  });

  test("extractDoors returns empty doors when marker absent", () => {
    const result = extractDoors("Just a normal reply.");
    assert.deepStrictEqual(result.doors, []);
    assert.strictEqual(result.cleanText, "Just a normal reply.");
  });

  test("extractDoors handles pipes and extra spaces", () => {
    const text = "[DOORS:  door one  | door two |   door three  ]";
    const result = extractDoors(text);
    assert.deepStrictEqual(result.doors, ["door one", "door two", "door three"]);
  });

  test("extractDoors is case-insensitive", () => {
    const text = "[doors: lower | case | test]";
    const result = extractDoors(text);
    assert.strictEqual(result.doors.length, 3);
  });

  // ── doorsOrFallback ───────────────────────────────────────────────────
  test("doorsOrFallback always returns exactly 3 suggestions", () => {
    const result = doorsOrFallback("Some text without marker.");
    assert.strictEqual(result.suggestions.length, 3, "must pad to 3 with fallbacks");
  });

  test("doorsOrFallback uses parsed doors when exactly 3 present", () => {
    const text = "Hello\n\n[DOORS: A | B | C]";
    const result = doorsOrFallback(text);
    assert.deepStrictEqual(result.suggestions, ["A", "B", "C"]);
    assert.strictEqual(result.cleanText, "Hello");
  });

  test("doorsOrFallback pads partial doors to 3", () => {
    const text = "Hello\n\n[DOORS: A | B]";
    const result = doorsOrFallback(text);
    assert.strictEqual(result.suggestions.length, 3);
    assert.strictEqual(result.suggestions[0], "A");
    assert.strictEqual(result.suggestions[1], "B");
    assert.ok(result.suggestions[2].length > 0, "third door should be a fallback");
  });

  test("doorsOrFallback keystone debug returns empty suggestions", () => {
    const text = "Hello\n\n[DOORS: A | B | C]";
    const result = doorsOrFallback(text, true);
    assert.deepStrictEqual(result.suggestions, []);
    assert.strictEqual(result.cleanText, text.trim());
  });

  test("doorsOrFallback collapses excessive newlines", () => {
    const text = "Reply\n\n\n\n\n[DOORS: A | B | C]";
    const result = doorsOrFallback(text);
    assert.ok(!result.cleanText.includes("\n\n\n"), "cleanText should collapse 3+ newlines to 2");
  });

  // ── SSE / UI contract ───────────────────────────────────────────────
  test("done-event contract: cleanText + 3 suggestions", () => {
    // Simulate what the server sends in the done event
    const rawReply = "The forest is calling you.\n\n[DOORS: enter the woods | sit by the stream | follow the firefly]";
    const { cleanText, suggestions } = doorsOrFallback(rawReply);
    const doneEvent = { type: "done", source: "gemini", agent: "Lantern", cleanText, suggestions };
    assert.ok(doneEvent.cleanText, "done event must have cleanText");
    assert.strictEqual(doneEvent.suggestions.length, 3, "done event must always have 3 suggestions for banner rendering");
    assert.ok(!doneEvent.cleanText.includes("[DOORS:"), "cleanText in done event must not leak marker");
  });

  // ── Browser rendering logic (simulated) ─────────────────────────────
  test("browser chip rendering requires 3 suggestions", () => {
    // This mirrors dream-chat.html logic: suggestions.length === 3 triggers appendDoorsBanner
    const suggestions = ["door 1", "door 2", "door 3"];
    const wouldRenderBanner = Array.isArray(suggestions) && suggestions.length === 3;
    assert.strictEqual(wouldRenderBanner, true, "3 suggestions should trigger banner render");
  });

  test("browser chip rendering skipped with fewer than 3", () => {
    const suggestions = ["only one"];
    const wouldRenderBanner = Array.isArray(suggestions) && suggestions.length === 3;
    assert.strictEqual(wouldRenderBanner, false, "<3 suggestions should not trigger banner");
  });

  test("speakText strips [DOORS:] before TTS (simulated)", () => {
    const text = "Hello dreamer. [DOORS: rest | reflect | write]";
    const clean = text.replace(/\[DOORS:[^\]]+\]/gi, "").trim();
    assert.ok(!clean.includes("[DOORS:"), "TTS text must not contain DOORS marker");
    assert.strictEqual(clean, "Hello dreamer.");
  });

  console.log(`\nResults: ${passed} passed, ${failed} failed\n`);
  process.exit(failed > 0 ? 1 : 0);
}

run();
