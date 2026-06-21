import { chromium, FullConfig } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

const RESUME_FILE = path.join(__dirname, ".crash-resume.json");

export interface ResumeState {
  lastPassedTest?: string;
  crashCount: number;
  startedAt: string;
}

/** Read resume state left by a previous crashed run. */
export function loadResumeState(): ResumeState | null {
  if (!fs.existsSync(RESUME_FILE)) return null;
  try {
    return JSON.parse(fs.readFileSync(RESUME_FILE, "utf8")) as ResumeState;
  } catch {
    return null;
  }
}

/** Persist current progress so a restart can skip already-passed tests. */
export function saveResumeState(state: ResumeState): void {
  fs.writeFileSync(RESUME_FILE, JSON.stringify(state, null, 2));
}

/** Clear resume state after a clean run. */
export function clearResumeState(): void {
  if (fs.existsSync(RESUME_FILE)) fs.unlinkSync(RESUME_FILE);
}

export default async function globalSetup(_config: FullConfig): Promise<void> {
  const prior = loadResumeState();
  if (prior) {
    console.log(
      `[crash-recovery] Resuming after crash #${prior.crashCount}. ` +
        `Last passed: ${prior.lastPassedTest ?? "none"}. ` +
        `Run started: ${prior.startedAt}`
    );
  }

  // Warm up a browser context to verify Playwright itself is healthy.
  // If this throws, it surfaces immediately rather than mid-suite.
  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  await ctx.close();
  await browser.close();

  saveResumeState({
    lastPassedTest: prior?.lastPassedTest,
    crashCount: (prior?.crashCount ?? 0) + (prior ? 1 : 0),
    startedAt: prior?.startedAt ?? new Date().toISOString(),
  });
}
