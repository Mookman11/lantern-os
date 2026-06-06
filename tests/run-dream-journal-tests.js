const { spawn, spawnSync } = require("child_process");
const http = require("http");
const net = require("net");
const path = require("path");

const repoRoot = path.resolve(__dirname, "..");
const explicitPort = process.env.LANTERN_GARAGE_TEST_PORT || process.env.LANTERN_GARAGE_PORT;
const explicitBaseUrl = process.env.LANTERN_GARAGE_TEST_BASE_URL;
let port = Number(explicitPort || 4177);
let baseUrl = explicitBaseUrl || `http://127.0.0.1:${port}`;
const node = process.execPath;
const playwrightCli = path.join(repoRoot, "node_modules", "@playwright", "test", "cli.js");

const allCommands = {
  api: [node, ["tests/test_dream_journal_api.js"]],
  chat: [node, ["tests/test_dream_journal_chat.js"]],
  multiturn: [node, ["tests/test_dream_chat_multiturns.js"]],
  keystone: [node, ["tests/test_dream_journal_keystone.js"]],
  cache: [node, ["tests/test_provider_cache.js"]],
  validate: [node, ["apps/lantern-garage/validate.js"]],
  ui: [node, [playwrightCli, "test", "tests/test_dream_journal_ui.spec.js"]],
  "ui:headed": [node, [playwrightCli, "test", "tests/test_dream_journal_ui.spec.js", "--headed"]],
};

function selectedCommands() {
  const requested = process.argv.slice(2);
  const names = requested.length ? requested : ["api", "chat", "multiturn", "keystone", "cache", "ui"];
  for (const name of names) {
    if (!allCommands[name]) {
      throw new Error(`Unknown test target "${name}". Use api, chat, multiturn, keystone, cache, validate, ui, or ui:headed.`);
    }
  }
  return names;
}
