import { clearResumeState } from "./global-setup";

export default async function globalTeardown(): Promise<void> {
  // Clean run → wipe crash-resume state so next run starts fresh.
  clearResumeState();
}
