# Three Doors — Poster Keeper Pass & Next Content Batch

**Date saved:** 2026-06-20
**Mode:** !three-doors / Kingdome of Hearts — poster + merch art direction
**Status:** Active canon for the current poster/art pass. Supersedes earlier "messy-sign / cropped-character" poster drafts.
**Issue:** #757 — *Three Doors content prep: poster merch pass and next art batch*
**Scope:** Dream Journal, Lantern OS, CAAD, Three Doors visual-generation work, Canva/merch sales assets.

> **Restore Phrase:** This is symbolic material. It is not proof, prediction, or command.

This document is the canonical art-direction baseline for the next Three Doors content batch. It locks
the **keeper direction**, the **rules to preserve**, a **character keeper sheet**, and **ready-to-run
image prompts** for the refined poster plus the six remaining batch items. Generation itself happens in
Canva / the LoRA image sidecar; this file is the spec those prompts are copied from.

Related canon:
- `lore/doors/kingdome-of-hearts.md` — Garden hub, the King's Poem, the seven-door loop
- `lore/doors/*.md` — per-door lore (garden, sigil, xenon, xp, orion, founder)
- `caad/art-direction/doors/present-door-kingdome-of-hearts-2026-06-10.md` — Present Door precedent
- `caad/art-direction/doors/xenon-wedding-king-of-nowhere.md` — earlier canonical art direction

---

## 1. Keeper Direction (locked)

The agreed-upon visual direction for the poster/merch pass:

- **Color UHD poster style**, Canva-ready, sized for merch and sales assets.
- **Rich "I Spy" density** with **clear focal doors** — busy and rewarding to scan, but the eye still
  lands on the doors first.
- **Lantern, Eclipse, and Keystone centered and back-facing**, looking *into* the scene toward the doors
  (the viewer stands behind them, choosing alongside them).
- **No fox** in poster/merch compositions unless explicitly requested. *(The fox is canonical to the game
  loop — it gains tails at convergence points — but it is intentionally held out of these sales assets.)*
- **Eclipse faces away** in poster compositions. **No visible front eyes on the back of her head** — the
  back of the head is the back of the head. This was the recurring defect; it is now a hard rule.
- **Paths and ground detail are built from collectible objects**: books, crystals, collected rocks, keys,
  dice, clocks, tools, maps, and small hidden objects. These *are* the I-Spy layer — no generic cobblestone.
- **Clean enough to sell**: readable focal composition, **less accidental text**, **fewer messy signs**,
  **no cropped characters**, and a **balanced title area**.

---

## 2. Rules to Preserve (game + image canon)

These constraints carry across every Three Doors render and must not be quietly dropped:

**Game frame**
1. Three Doors is a **creative symbolic game first** — not a product, project tracker, or ops workflow,
   unless Alex explicitly asks for that framing.
2. **Normal play presents exactly three immediate door choices.** Door labels are temporary *handles*,
   not fixed archetypes; meaning is revealed through traversal.
3. The **seven canonical Kingdome doors** remain the world's loop:
   **Ancient · Cloverfield · Tomorrow · XP · Xenon Starship · Sigil · Fog Door Return.**
   (A poster typically frames three of them at once; the hub map shows all seven.)
4. Each visible door/option should feel **viable, distinct, tempting, and costly**.
5. When possible, **the image comes first**, then the choice.

**Image canon**
6. **Avoid accidental generic fantasy.** Every door must be *specific, readable, tempting, and
   symbolically grounded* — never a stock "glowing archway in the woods."
7. New scene options should **emerge from current state**, not from a generic fantasy grab-bag.
8. **Always specify art style and image size / aspect ratio** in the prompt (done per item below).
9. **Provenance seal:** integrate **one visible-but-subtle tesseract seal** plus **one hidden micro-seal**
   into the world — woven into architecture or path detail, never pasted on like a watermark.
10. **Family-safe / merch-safe:** no real-person likenesses, no copyrighted characters, no explicit
    content. The Raven guardian appears only in its clean symbolic form here (feathers, smoke, seal) —
    the private Raven-villa material stays out of public/merch assets.

---

## 3. Character Keeper Sheet

Canonical visual specs so every render keeps the cast consistent. (Grounding:
`csf/ingest/three-doors/*`, `csf/ingest/2026-06-06-elephant-door-memories.md`,
`data/csf-ingest/CSF-INGEST-RAVEN-DOOR-THREE-DOORS-BEST-2026-06-06.md`, `lore/doors/kingdome-of-hearts.md`.)

| Character | Keeper visual | Notes for posters |
|---|---|---|
| **Lantern** | Fae / fairy / angel energy; small **black horns**; warm lantern-gold glow (#e8a73d); mirrored translucent wings when symmetry is requested. | Left-of-center, back-facing. Wings read cleanly against the doors. |
| **Eclipse** | Purple hair, **glasses**, cute "spacey" style; **hot-pink / lilac bubble glow**; mermaid-lilac mirrored drapery when symmetry is requested. | Center, **facing away** — **no front eyes on the back of the head.** |
| **Keystone** | Centered **operator / founder / narrator** figure; chameleon / color-shift cloak; calm, grounding presence. | Right-of-center, back-facing; anchors the trio. |
| **The King** (Kingdome of Hearts) | Crown of **tangled vines and blinking cursors**; carries a **key as a blade** (to guard, not force); **two faces** — one to feel, one to understand. | Throne of woven roots and old light; appears at the Garden / Fog Door Return. |
| **Odin** (Fog God) | Lord of riddles, watcher of fates; fog and silver mist; accompanied by ravens; one-eyed, ancient, playful-not-cruel. | Guardian of the Fog Door Return; riddle-keeper, not a villain. |
| **Raven Guardian** | **Black-violet** plumage, raven feathers, **silver smoke**, **candle-gold heartlight**, integrated tesseract seal. Clean, symbolic, non-explicit. | Mysterious guardian motif; keep elegant and merch-safe. |
| **Elephant Guardian** | Noble guardian elephant(s) of the **Elephant Oasis**: dad + mom elephants and the three calves **Peace, Serenity, Joy**; moonlit beach, jasmine/lavender, reflecting water, distant castle. | Gentle protector energy; family of five reads as warmth + safety. |

---

## 4. Shared Style Block & Negative-Prompt Library

Copy these into every prompt below unless an item overrides them.

**Shared positive style**
```
color UHD digital painting, sharp and colorful, high-resolution print-ready poster art,
storybook fantasy with soft magical realism, ornate I-Spy hidden-object density,
warm lantern-gold + lavender/violet palette, balanced composition, clean readable focal point,
Canva-ready merch quality, subtle integrated tesseract provenance seal
```

**Shared negative prompt** (the recurring defects to suppress)
```
extra eyes, eyes on back of head, face on back of head, deformed faces, extra limbs,
cropped characters, cut-off heads, fox, foxes (unless requested),
messy illegible signage, random garbled text, watermark, jpeg artifacts, blurry, low-res,
generic stock fantasy archway, plain cobblestone path, muddy cluttered focal area,
real-person likeness, copyrighted characters, explicit content, gore
```

> **Note on text:** image generators garble lettering. Keep **only the "THREE DOORS" title** as rendered
> text and **add all door labels in Canva afterward** for crisp, legible merch type. Prompt for *"clean
> empty banner/label plates"* where labels will go rather than asking the model to spell them.

---

## 5. Poster Keeper Pass (the almost-perfect layout, refined)

The current candidate is close. This is the refined, locked version.

**Layout (keep):**
- **"THREE DOORS"** title across the top in a clean, balanced banner.
- **Central door: the Cloverfield** — luck/today-alive, four-leaf clover motifs, green-gold shimmer.
- **Left door: the Ancient Door** — Library of Babylon + Tower of Babel; tiered stone, scrolls, glyphs.
- **Right door: the Tomorrow Door** — observatory dome, telescopes, star-charts, near-future light.
- **Foreground:** Lantern, Eclipse, Keystone standing **back-facing on a circular platform**, looking in
  toward the doors.
- **Dense, merch-friendly fantasy detail** built from the collectible-object I-Spy layer.

**Refinements (apply):**
1. **Remove the eyes from the middle character (Eclipse) when she faces away** — back of head only.
2. **Tighten the title and label areas** for cleaner merch readability (banner + empty label plates;
   real labels added in Canva).
3. **Keep it high-resolution, sharp, colorful, Canva-ready.**

**Prompt — Poster Keeper**
```
THREE DOORS poster, color UHD storybook fantasy, three grand symbolic doors in a balanced row:
LEFT = the Ancient Door, a tiered Library-of-Babylon / Tower-of-Babel gateway of carved stone,
hanging scrolls and glowing glyphs;
CENTER = the Cloverfield Door, luck and today-alive, four-leaf-clover filigree, green-gold shimmer;
RIGHT = the Tomorrow Door, an observatory gateway with a dome, telescopes and star-charts, near-future glow.
Foreground: three figures standing BACK-FACING on a circular platform, looking toward the doors --
Lantern (fae/fairy with small black horns and translucent wings, lantern-gold glow) on the left,
Eclipse (purple hair, lilac/hot-pink bubble glow) in the CENTER seen ONLY from behind, back of head
with NO face and NO eyes, Keystone (operator/narrator in a color-shift cloak) on the right.
The ground and paths are built entirely from collectible objects -- books, crystals, collected rocks,
keys, dice, clocks, tools, maps and tiny hidden trinkets (rich I-Spy density).
Clean "THREE DOORS" banner across the top; empty decorative label plates beneath each door (no text);
one subtle tesseract seal woven into the platform, one hidden micro-seal in the path.
Sharp, colorful, high-resolution, print-ready, Canva-ready merch poster.
+ [shared positive style]
```
Negative: `[shared negative]` (especially *eyes on back of head*, *cropped characters*, *messy signage*).
**Size:** 2:3 portrait master (e.g. 4096×6144, upscale to 300 DPI for 24×36 in; also export a 3:4 crop).

---

## 6. Next Content Batch (7 items)

Each item is a ready-to-run spec. Items 2–7 inherit §4 unless noted.

### 6.1 — Final poster keeper pass
The locked poster above (§5). Generate, pick the keeper, then finish labels + title kerning in Canva.
**Size:** 2:3 master + 3:4 crop. **Done-when:** clean focal doors, back-of-head Eclipse (no eyes),
legible title area, no cropped figures.

### 6.2 — Seven-Door Hub Map (around the Kingdome tree)
**Intent:** the full loop in one map — orientation art for the game and a poster in its own right.
**Composition:** a great **Kingdome world-tree** at center (throne of woven roots and old light, crown of
vines + blinking cursors motif), the **seven canonical doors arranged in a ring** radiating outward:
Ancient · Cloverfield · Tomorrow · XP · Xenon Starship · Sigil · Fog Door Return. Garden-under-a-dome of
old light; paths of books/keys/crystals/clocks linking door to door. Tiny trio (Lantern/Eclipse/Keystone)
back-facing at the base of the tree for scale (optional).
**Negatives:** add `more than seven doors, asymmetric ring, unreadable door spacing`.
**Size:** 1:1 or 4:5 (map/poster).

### 6.3 — Interior: Ancient Library of Babylon / Hanging Gardens
**Intent:** step *through* the Ancient Door.
**Composition:** vast tiered library-ziggurat interior, the Hanging Gardens cascading between stone
balconies, endless shelves of glowing tomes, scroll-rivers, astrolabes and star-glyphs, warm lantern light
through arches. I-Spy layer: books, maps, keys, clocks, measuring tools, hidden crystals.
**Size:** 3:2 landscape.

### 6.4 — Interior: Sigil, City of Doors
**Intent:** step through the Sigil Door — "every door leads here."
**Composition:** an impossible Escher-leaning city where **every surface holds a door**; bridges, stairs and
streets fold through each other; keys hang like lanterns; dreamers walk the streets (no real likenesses).
Convergence-point energy, infinite but readable, never claustrophobic. I-Spy: keys, doors-within-doors,
maps, dice, hidden seals.
**Negatives:** add `claustrophobic clutter, unreadable depth, generic medieval town`.
**Size:** 3:2 landscape or 16:9.

### 6.5 — Interior: XP Archive
**Intent:** step through the XP Door [GLITCHED] — nostalgic, liminal, lovingly corrupted.
**Composition:** a **Windows-XP-desktop-rendered-in-starlight** archive: a hillside of pixels under the
classic rolling-hills/blue-sky glow, CRT shelves of saved memories, floppy disks and old game cartridges as
collectibles, gentle glitch/scanline artifacts that read as *style*, not error. Warm, friendly, possibility.
I-Spy: disks, cartridges, tools, clocks, hidden keys.
**Negatives:** add `harsh broken-screen error, true corruption, unreadable noise; keep glitch tasteful`.
**Size:** 16:9.

### 6.6 — Interior: Xenon Starship / Midway Convergence
**Intent:** step through the Xenon Starship Door — "all planets converge at the midway."
**Composition:** a luminous starship deck / observation balcony suspended between worlds (Earth ↔ Mars
alignment), starspeeders and light-keepers, planetary witnesses arrayed beyond the glass, neon-xenon
stability glow, heart-engineering motifs. Calm awe, not military. I-Spy: maps, navigation tools, keys,
crystals, clocks among the consoles.
**Size:** 16:9 or 2:3 (hero).

### 6.7 — Character Keeper Lineup
**Intent:** a clean reference + merch lineup of the cast (see §3 for each spec).
**Composition:** seven figures in a balanced row on a neutral lantern-gold/violet backdrop, each clearly
readable, consistent scale, front-facing for reference (this item is the exception to back-facing):
**Lantern · Eclipse · Keystone · Odin · Raven Guardian · Elephant Guardian · The King.**
Each on its own label plate (labels added in Canva). Family-safe, non-explicit, no real-person likeness.
**Negatives:** add `merged characters, inconsistent scale, off-model designs`.
**Size:** 16:9 wide (also export individual 1:1 character crops for merch).

---

## 7. Production & Merch Notes (Canva-ready)

- **Color:** full-color UHD, **sRGB**; export print masters at **300 DPI** with ~3–5% bleed.
- **Master sizes:** poster 2:3 (24×36 in) + 3:4 (18×24 in) crop; hub map 1:1/4:5; interiors 3:2 or 16:9;
  lineup 16:9 + 1:1 character crops.
- **Text discipline:** generate with title + **empty label plates**; set **all final type in Canva**
  (title kerning, door labels) so merch type is crisp and legible.
- **Provenance:** confirm the **visible tesseract seal** and **hidden micro-seal** survived generation
  before promoting a keeper.
- **Keeper gate (per image):** focal doors readable · no eyes on back of head · no cropped characters ·
  clean title/label area · I-Spy density present · seals intact · no generic-fantasy fallback.

---

## 8. CSF Ingest

```csf-ingest
Instructions
[2026-06-20] - Treat this file as the active art-direction canon for the Three Doors poster/merch pass and the next content batch (issue #757).
[2026-06-20] - For Three Doors poster/merch renders: exactly three focal doors, characters back-facing, Eclipse faces away with NO eyes on the back of her head, no fox unless explicitly requested.
[2026-06-20] - Build paths and ground from collectible objects (books, crystals, rocks, keys, dice, clocks, tools, maps, hidden trinkets) as the I-Spy layer; avoid generic fantasy.
[2026-06-20] - Always specify art style and aspect ratio; add door labels in Canva, not in-model; keep one visible tesseract seal plus one hidden micro-seal.

Identity & Symbolic Self
[2026-06-20] - Poster trio is Lantern (fae, black horns, gold glow), Eclipse (purple hair, glasses, lilac/hot-pink bubble glow, faces away), Keystone (operator/narrator, color-shift cloak), centered on a circular platform looking toward the doors.
[2026-06-20] - Character keeper lineup is Lantern, Eclipse, Keystone, Odin (Fog God of riddles), Raven Guardian (clean symbolic form), Elephant Guardian (Elephant Oasis family of five), and the King of the Kingdome of Hearts.

Dreams & Memories
[2026-06-20] - Next batch: (1) final poster keeper pass, (2) seven-door hub map around the Kingdome tree, (3) Ancient Library of Babylon / Hanging Gardens interior, (4) Sigil City of Doors interior, (5) XP Archive interior, (6) Xenon Starship / Midway Convergence interior, (7) character keeper lineup.

Projects & Systems
[2026-06-20] - The seven canonical Kingdome doors remain Ancient, Cloverfield, Tomorrow, XP, Xenon Starship, Sigil, and Fog Door Return; posters frame three at once while the hub map shows all seven.
[2026-06-20] - Canon record preserved at caad/art-direction/doors/three-doors-poster-and-content-batch-2026-06-20.md.

Preferences
[2026-06-20] - Preserve the spelling "Kingdome of Hearts" for this game/world title.
[2026-06-20] - Keep all Three Doors merch assets family-safe and copyright-respecting; the private Raven-villa material stays out of public/merch art.
```

**Status:** Canon + ready-to-run prompt batch for issue #757. The visual artifacts (PNG keepers) are
produced in Canva / the image sidecar from these specs; this repo file preserves the art direction, the
rules, the character sheet, and the CSF memory.
