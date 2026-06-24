// ── Creator Dashboard Performance Optimizer ─────────────────────────────
// Reduces resource usage through visibility-based polling, lazy loading, and caching

class CreatorPerfOptimizer {
  constructor() {
    this.pollingIntervals = new Map(); // Track active intervals
    this.visibilityState = 'visible';
    this.pausedIntervals = new Map(); // Store paused intervals
    this.stats = {
      apiCallsSkipped: 0,
      apiCallsRegistered: 0, // total estimatedApiCalls across all registerPollingInterval calls
      energySaved: 0, // Estimated in mJ
      bandwidthSaved: 0, // In bytes
      startTime: Date.now(),
    };

    // #1113: keep a reference to the handler so cleanup() can removeEventListener
    this._visibilityHandler = null;
    this.setupVisibilityHandler();
  }

  // Setup page visibility listener to pause/resume polling
  setupVisibilityHandler() {
    if (typeof document !== 'undefined') {
      this._visibilityHandler = () => {
        this.visibilityState = document.visibilityState;
        if (document.hidden) {
          this.pauseAllPolling();
        } else {
          this.resumeAllPolling();
        }
      };
      document.addEventListener('visibilitychange', this._visibilityHandler);
    }
  }

  // Register a polling interval for management
  registerPollingInterval(id, interval, estimatedApiCalls = 1) {
    this.pollingIntervals.set(id, {
      interval,
      estimatedApiCalls,
      isPaused: false,
      bytesPerCall: 2048, // Average API response size
    });
    // #1111: track total so apiCallsAvoidedPercent has a real denominator
    this.stats.apiCallsRegistered += estimatedApiCalls;
  }

  // Pause all registered polling intervals
  pauseAllPolling() {
    for (const [id, config] of this.pollingIntervals.entries()) {
      if (!config.isPaused) {
        clearInterval(config.interval);
        // #1110: move entry out of pollingIntervals so cleanup() doesn't double-clear
        this.pausedIntervals.set(id, config);
        this.pollingIntervals.delete(id);
        config.isPaused = true;
        this.stats.apiCallsSkipped += config.estimatedApiCalls;
        this.stats.bandwidthSaved += config.bytesPerCall;
        this.stats.energySaved += 50; // Rough estimate per paused interval
      }
    }
  }

  // Resume all paused polling intervals
  resumeAllPolling() {
    for (const [id, config] of this.pausedIntervals.entries()) {
      config.isPaused = false;
      this.pausedIntervals.delete(id);
      // Restore the config to pollingIntervals (the interval ID is stale after clearInterval,
      // but the caller is responsible for providing a live replacement via registerPollingInterval)
      this.pollingIntervals.set(id, config);
    }
  }

  // Lazy-load module with intersection observer
  lazyLoadModule(elementId, loadCallback) {
    if (typeof IntersectionObserver === 'undefined') {
      loadCallback();
      return;
    }

    const element = document.getElementById(elementId);
    if (!element) return;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          loadCallback();
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    observer.observe(element);
  }

  // Debounce function for resize/scroll events
  debounce(fn, delayMs) {
    let timeoutId;
    return (...args) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => fn(...args), delayMs);
    };
  }

  // Request animation frame batching for UI updates
  batchUIUpdates(updateFn) {
    if (typeof requestAnimationFrame === 'undefined') {
      updateFn();
      return;
    }
    requestAnimationFrame(updateFn);
  }

  // Cache expensive computations with TTL
  memoize(fn, ttlMs = 60000) {
    let cachedResult = null;
    let cacheExpiry = 0;

    return (...args) => {
      const now = Date.now();
      if (cachedResult !== null && now < cacheExpiry) {
        return cachedResult;
      }
      cachedResult = fn(...args);
      cacheExpiry = now + ttlMs;
      return cachedResult;
    };
  }

  // Virtual scrolling for large lists (client-side hint)
  getVirtualScrollConfig(totalItems, itemHeight, containerHeight) {
    const visibleItems = Math.ceil(containerHeight / itemHeight);
    const overscan = 5; // Items to render outside viewport

    return {
      totalItems,
      itemHeight,
      containerHeight,
      visibleItems,
      overscan,
      getVisibleRange: (scrollTop) => {
        const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
        const endIndex = Math.min(totalItems, startIndex + visibleItems + overscan * 2);
        return { startIndex, endIndex };
      },
    };
  }

  // Get performance statistics
  getStats() {
    const uptime = Date.now() - this.stats.startTime;
    // #1111 + #1121: compute real percent from tracked data; format consistently with toFixed(1)
    const avoidedPct = this.stats.apiCallsRegistered > 0
      ? parseFloat((this.stats.apiCallsSkipped / this.stats.apiCallsRegistered * 100).toFixed(1))
      : 0;

    return {
      ...this.stats,
      uptime,
      energySavedJoules: parseFloat((this.stats.energySaved / 1000).toFixed(2)),
      bandwidthMB: parseFloat((this.stats.bandwidthSaved / 1024 / 1024).toFixed(2)),
      apiCallsAvoidedPercent: avoidedPct,
    };
  }

  // Reset all intervals (for cleanup)
  cleanup() {
    for (const config of this.pollingIntervals.values()) {
      clearInterval(config.interval);
    }
    this.pollingIntervals.clear();
    this.pausedIntervals.clear();
    // #1113: remove the visibilitychange listener so the instance can be GC'd
    if (this._visibilityHandler && typeof document !== 'undefined') {
      document.removeEventListener('visibilitychange', this._visibilityHandler);
      this._visibilityHandler = null;
    }
  }
}

module.exports = { CreatorPerfOptimizer };
