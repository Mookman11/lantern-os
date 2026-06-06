/**
 * Dream Chat refactor tests — verify split files & convergence loop route
 * Run against a live lantern-garage server on port 4177.
 */

const http = require("http");
const assert = require("assert");
const { baseUrl: BASE, hostname: HOST, port: PORT } = require("./lantern-test-base");

let passed = 0;
let failed = 0;

async function request(method, path, body) {
  return new Promise((resolve, reject) => {
    const opts = {
      hostname: HOST,
      port: PORT,
      path,
      method,
      headers: body ? { "Content-Type": "application/json" } : {},
    };
    const req = http.request(opts, (res) => {
      let data = "";
      res.on("data", (c) => (data += c));
      res.on("end", () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(data), raw: data }); }
        catch { resolve({ status: res.statusCode, body: data, raw: data }); }
      });
    });
    req.on("error", reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

async function test(name, fn) {
  try {
    await fn();
    console.log(`  ✓ ${name}`);
    passed++;
  } catch (err) {
    console.error(`  ✗ ${name}`);
    console.error(`    ${err.message}`);
    failed++;
  }
}

async function main() {
  console.log("\nDream Chat refactor tests");
  console.log("=========================\n");

  await test("CSS file is served", async () => {
    const r = await request("GET", "/css/dream-chat.css");
    assert.strictEqual(r.status, 200, `expected 200, got ${r.status}`);
    assert(r.raw.includes("--bg:"), "CSS should contain --bg variable");
  });

  await test("JS file is served", async () => {
    const r = await request("GET", "/js/dream-chat.js");
    assert.strictEqual(r.status, 200, `expected 200, got ${r.status}`);
    assert(r.raw.includes("sendMessage"), "JS should contain sendMessage function");
  });

  await test("HTML shell loads external files", async () => {
    const r = await request("GET", "/dream-chat.html");
    assert.strictEqual(r.status, 200, `expected 200, got ${r.status}`);
    assert(r.raw.includes('href="css/dream-chat.css"'), "HTML should link CSS");
    assert(r.raw.includes('src="js/dream-chat.js"'), "HTML should load JS");
    assert(!r.raw.includes("<style>"), "HTML should not contain inline <style>");
  });

  await test("Convergence loop route responds", async () => {
    const r = await request("POST", "/api/actions/run-loop");
    assert([200, 500].includes(r.status), `expected 200 or 500, got ${r.status}`);
    assert(r.body && typeof r.body === "object", "body should be JSON object");
    assert("ok" in r.body, "body should have ok field");
  });

  await test("Provider settings still works", async () => {
    const r = await request("GET", "/api/settings/providers");
    assert.strictEqual(r.status, 200, `expected 200, got ${r.status}`);
    assert(r.body && typeof r.body === "object", "body should be JSON object");
    assert("_any" in r.body, "body should have _any field");
  });

  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
}

main().catch((e) => { console.error(e); process.exit(1); });
