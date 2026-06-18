// Tiny CLI wrapper so research_loop_calibration.py can call the real
// detectOpeningHookStrength() from highlight-engine.js without duplicating
// its ffmpeg logic in Python. Usage: node _hook_strength_helper.js <videoPath>
// Prints one JSON line to stdout.
"use strict";

const path = require("path");
const { detectOpeningHookStrength } = require(
  path.join(__dirname, "..", "apps", "lantern-garage", "lib", "highlight-engine.js")
);

const videoPath = process.argv[2];
if (!videoPath) {
  console.log(JSON.stringify({ status: "unavailable", reason: "no videoPath arg" }));
  process.exit(0);
}

detectOpeningHookStrength(videoPath)
  .then((r) => console.log(JSON.stringify(r)))
  .catch((err) => console.log(JSON.stringify({ status: "unavailable", reason: err.message })));
