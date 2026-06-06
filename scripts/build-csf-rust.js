#!/usr/bin/env node
/**
 * Build the CSF Rust crate as part of npm setup.
 * Non-blocking: failures are warnings, not hard errors.
 */

const { execSync } = require("child_process");
const { existsSync } = require("fs");
const { join } = require("path");

function hasCargo() {
  try {
    execSync("cargo --version", { stdio: "pipe" });
    return true;
  } catch {
    return false;
  }
}

function main() {
  if (!hasCargo()) {
    console.warn("[build-csf-rust] cargo not found. Skipping Rust build.");
    return;
  }

  const root = join(__dirname, "..");
  const crateDir = join(root, "src", "csf_rust");

  if (!existsSync(crateDir)) {
    console.warn("[build-csf-rust] Crate directory not found:", crateDir);
    return;
  }

  console.log("[build-csf-rust] Building csf_rust crate...");
  try {
    execSync("cargo build --release", { cwd: crateDir, stdio: "inherit", timeout: 300000 });
    console.log("[build-csf-rust] Build succeeded.");
  } catch (err) {
    console.warn("[build-csf-rust] Build failed (non-fatal):", err.message);
  }
}

main();
