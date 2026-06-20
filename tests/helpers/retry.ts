import type { APIRequestContext } from "@playwright/test";

const RETRYABLE_CODES = new Set([500, 502, 503, 504]);
const BASE_DELAY_MS = 200;

export interface RetryResult<T> {
  value: T;
  attempts: number;
  persistent: boolean;
}

/**
 * Retry a fetch against a transient 5xx. Flags the error as persistent after
 * exhausting retries so callers can emit a finding without crashing the run.
 */
export async function retryFetch(
  url: string,
  init: RequestInit = {},
  maxRetries = 3
): Promise<RetryResult<Response>> {
  let lastError: Error | null = null;
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(url, init);
      if (!RETRYABLE_CODES.has(res.status) || attempt === maxRetries) {
        return { value: res, attempts: attempt, persistent: !res.ok };
      }
    } catch (err) {
      lastError = err as Error;
    }
    await delay(BASE_DELAY_MS * 2 ** (attempt - 1));
  }
  throw lastError ?? new Error(`retryFetch exhausted after ${maxRetries} attempts: ${url}`);
}

/** Retry a Playwright APIRequestContext POST, flag persistent 5xx. */
export async function retryPost(
  request: APIRequestContext,
  url: string,
  data: Record<string, unknown>,
  maxRetries = 3
): Promise<RetryResult<import("@playwright/test").APIResponse>> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    const res = await request.post(url, { data });
    if (!RETRYABLE_CODES.has(res.status()) || attempt === maxRetries) {
      return { value: res, attempts: attempt, persistent: RETRYABLE_CODES.has(res.status()) };
    }
    await delay(BASE_DELAY_MS * 2 ** (attempt - 1));
  }
  throw new Error(`retryPost exhausted: ${url}`);
}

/** Retry a Playwright APIRequestContext GET. */
export async function retryGet(
  request: APIRequestContext,
  url: string,
  maxRetries = 3
): Promise<RetryResult<import("@playwright/test").APIResponse>> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    const res = await request.get(url);
    if (!RETRYABLE_CODES.has(res.status()) || attempt === maxRetries) {
      return { value: res, attempts: attempt, persistent: RETRYABLE_CODES.has(res.status()) };
    }
    await delay(BASE_DELAY_MS * 2 ** (attempt - 1));
  }
  throw new Error(`retryGet exhausted: ${url}`);
}

/** Null-safe textContent — returns empty string if locator resolves to nothing. */
export async function safeText(
  locator: import("@playwright/test").Locator
): Promise<string> {
  const el = await locator.first().elementHandle().catch(() => null);
  if (!el) return "";
  return (await el.textContent()) ?? "";
}

function delay(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}
