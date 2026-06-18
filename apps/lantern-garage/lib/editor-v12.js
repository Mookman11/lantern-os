// Editor V12 — creator style archetypes (editing-parameter presets).
//
// HONESTY BOUNDARY: these are NOT fingerprints of real named creators and this
// module does not surveil or copy any individual's channel. They are named
// bundles of EDITING PARAMETERS — recognizable *categories* of short-form
// editing style (fast/aggressive, cinematic, reaction-led, etc.) — that map to
// real knobs the Lantern pipeline already exposes (target duration, cut
// behavior, zoom usage, caption density, story-arc on/off). Picking a profile
// changes how Lantern edits; it does not reproduce anyone's footage or brand.
//
// Each profile's fields:
//   targetSec        desired finished length (s)
//   maxCutSpacingSec soft cap on how long one segment runs before preferring a cut
//   zoom             "none" | "subtle" | "punch-in"  (renderer hint; honest: zoom
//                    application itself is a renderer feature, this only requests it)
//   captionDensity   "sparse" | "medium" | "heavy"   (caption-engine hint)
//   storyArc         true -> use the V12 story-engine ordering; false -> intensity order
//   pacing           "calm" | "balanced" | "fast"    (affects min segment length)
//   strategyHint     which variant-engine strategy this profile maps to

"use strict";

const CREATOR_PROFILES = {
  // Fast, punchy, caption-heavy — the high-energy gaming-clip look.
  aggressive: {
    label: "Aggressive",
    targetSec: 20,
    maxCutSpacingSec: 2.5,
    zoom: "punch-in",
    captionDensity: "heavy",
    storyArc: false,
    pacing: "fast",
    strategyHint: "maximum_excitement",
    description: "Rapid cuts, punch-in zooms, captions on every beat. High energy.",
  },
  // Longer holds, fewer cuts, breathing room — the cinematic montage look.
  cinematic: {
    label: "Cinematic",
    targetSec: 40,
    maxCutSpacingSec: 6,
    zoom: "subtle",
    captionDensity: "sparse",
    storyArc: true,
    pacing: "calm",
    strategyHint: "story_arc",
    description: "Longer shots, subtle moves, sparse captions, deliberate arc.",
  },
  // Builds to and lingers on the reaction moment — the reaction-channel look.
  reaction: {
    label: "Reaction",
    targetSec: 30,
    maxCutSpacingSec: 4,
    zoom: "subtle",
    captionDensity: "medium",
    storyArc: true,
    pacing: "balanced",
    strategyHint: "story_arc",
    description: "Story arc that emphasizes the post-peak reaction beat.",
  },
  // Gameplay-forward, minimal decoration — the competitive-highlight look.
  competitive: {
    label: "Competitive",
    targetSec: 25,
    maxCutSpacingSec: 3.5,
    zoom: "none",
    captionDensity: "sparse",
    storyArc: false,
    pacing: "balanced",
    strategyHint: "maximum_retention",
    description: "Gameplay-first, minimal captions, no gimmick zooms. Skill on display.",
  },
  // Strong instant hook + tight payoff — the broad viral-gaming look.
  viralGaming: {
    label: "Viral Gaming",
    targetSec: 22,
    maxCutSpacingSec: 3,
    zoom: "punch-in",
    captionDensity: "medium",
    storyArc: true,
    pacing: "fast",
    strategyHint: "story_arc",
    description: "Instant hook, tight build, big payoff. Broad-appeal gaming Short.",
  },
};

const DEFAULT_PROFILE = "viralGaming";

/** Map pacing -> minimum segment length (s) the variant engine should respect. */
const PACING_MIN_SEG = { calm: 3.0, balanced: 2.0, fast: 1.2 };

/**
 * Resolve a profile name to a profile object (falls back to default).
 */
function getProfile(name) {
  return CREATOR_PROFILES[name] || CREATOR_PROFILES[DEFAULT_PROFILE];
}

/**
 * Translate a creator profile into the options object the variant engine and
 * downstream renderer actually consume. Pure mapping — no side effects.
 * @param {string} name  profile key
 * @returns {Object} options usable as generateVariantsV10(analysis, opts)
 */
function profileToVariantOpts(name) {
  const p = getProfile(name);
  return {
    profile: name in CREATOR_PROFILES ? name : DEFAULT_PROFILE,
    targetSec: p.targetSec,
    minHighlightDuration: PACING_MIN_SEG[p.pacing] || 2.0,
    preferStrategy: p.strategyHint,
    // Renderer hints — honest: these REQUEST behavior the renderer may apply;
    // this module does not itself zoom or draw captions.
    rendererHints: {
      zoom: p.zoom,
      captionDensity: p.captionDensity,
      storyArc: p.storyArc,
      maxCutSpacingSec: p.maxCutSpacingSec,
    },
  };
}

/** List available profiles (for UI/API exposure). */
function listProfiles() {
  return Object.entries(CREATOR_PROFILES).map(([key, p]) => ({
    key, label: p.label, description: p.description,
  }));
}

module.exports = {
  CREATOR_PROFILES,
  DEFAULT_PROFILE,
  getProfile,
  profileToVariantOpts,
  listProfiles,
};
