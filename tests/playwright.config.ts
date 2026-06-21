import { defineConfig, devices } from '@playwright/test';

/**
 * Lantern OS Playwright Configuration
 *
 * Browser testing for Lantern OS surfaces:
 * - Trade chat app (Kalshi integration)
 * - Garage app (payment bridge)
 * - Desktop surfaces
 * - Static HTML surfaces
 */
export default defineConfig({
  testDir: './e2e',
  timeout: 120_000,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  globalSetup: './global-setup.ts',
  globalTeardown: './global-teardown.ts',
  use: {
    baseURL: 'http://localhost:8080',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'python -m http.server 8080 --directory ../surfaces',
    url: 'http://localhost:8080',
    reuseExistingServer: !!process.env.CI,
  },
});
