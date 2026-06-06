#!/usr/bin/env node
/**
 * Build the CSF Rust crate as part of npm setup.
 * Non-blocking: failures are warnings, not hard errors.
 */

const { execSync } = require("child_process");
const { existsSync } = require("fs");
const { join, resolve } = require("path");

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

  const isWin = process.platform === "win32";
  const env = { ...process.env };

  // On Windows, ensure MinGW-w64 is on PATH (auto-downloaded by ensure-rust.js)
  if (isWin) {
    const mingwPaths = [
      join(process.env.USERPROFILE || "", ".mingw", "mingw64", "bin"),
      join(process.env.USERPROFILE || "", ".mingw-llvm", "llvm-mingw-20240619-ucrt-x86_64", "bin"),
    ];
    const existingPath = env.PATH || "";
    const extraPaths = mingwPaths.filter(p => existsSync(p)).join(";");
    if (extraPaths) {
      env.PATH = extraPaths + ";" + existingPath;
      console.log("[build-csf-rust] Added MinGW to PATH:", extraPaths);
    }
    // Single-job mode avoids file-locking bugs with some MinGW builds on Windows
    env.CARGO_BUILD_JOBS = "1";
  }

  console.log("[build-csf-rust] Building csf_rust crate...");
  try {
    execSync("cargo build --release", { cwd: crateDir, env, stdio: "inherit", timeout: 300000 });
    console.log("[build-csf-rust] Build succeeded.");
  } catch (err) {
    console.warn("[build-csf-rust] Build failed (non-fatal):", err.message);
  }
}

main();
