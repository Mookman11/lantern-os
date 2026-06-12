# Store Release Lanes

Generated: 2026-05-26.

## Decision

Lantern OS needs a store lane, but not necessarily Steam first.

## Lanes

| Lane | Status | Cost | Best First Product | Decision |
|---|---|---:|---|---|
| Local Garage Store | promote now | `$0` | whitepaper, ADS PDF, RAG cleanup invoice, school packet | use immediately |
| Direct invoice | promote now | `$0` platform fee | RAG cleanup, report pack, setup session | use for cash sprint |
| Itch.io | promote next | low/frictionless | school art/game/learning packet, HTML demo, ZIP | best first public store lane |
| GitHub Releases | candidate | `$0` | PDFs, ZIP packets, source bundles | use after v1 approval |
| GOG | later candidate | curated/approval-based | DRM-free polished game/app | hold until a real build has traction |
| Steam | future candidate | `$100 USD per app` | game-like Lantern learning/tool demo | hold until playable app target exists |

## Steam Notes

Official Steamworks documentation currently says Steam Direct requires a
`$100 USD` fee, or equivalent, for each new app distributed on Steam. Steam also
has store/release checklists and review steps before launch.

Sources:

- `https://partner.steamgames.com/doc/gettingstarted/appfee`
- `https://partner.steamgames.com/doc/store/releasing`

## Recommendation

Skip Steam for the immediate cash loop. Build the cool stuff in the garage, but
ship the first store as local/direct plus Itch:

```text
Tony Garage -> Store Shelf -> Invoice -> Delivery -> Testimonial
Tony Garage -> Itch prototype page -> playable/downloadable packet -> feedback
```

Steam becomes attractive when the product is a real playable or app-like build:

- GameMaker learning game;
- Lantern RAG cleanup simulator;
- One World Leader science/art/math demo;
- local AI garage companion with clear executable packaging.

## Itch.io Notes

Itch is the best next store lane because it fits weird, early, creative,
education/game/tool hybrids. Official itch docs recommend `butler` as the best
way to upload games/projects, with pushes shaped like:

```text
butler push directory user/game:channel
```

Sources:

- `https://itch.io/docs/itch/integrating/quickstart.html`
- `https://itch.io/docs/butler/pushing.html`
- `https://itch.io/docs/butler/`

Best Lantern first Itch products:

1. Gage/tesseract art and math packet as a downloadable ZIP.
2. One World Leader HTML micro-demo.
3. Lantern Garage static demo.
4. GameMaker room/editor demo after repo intake.
5. COMET LEAP printable pack as a paid-or-donation download.

## GOG Notes

GOG is valuable because the Lantern philosophy is local-first and DRM-free, but
GOG is not the fastest first store. Official GOG developer docs describe a
Developer Portal and say unsigned developers should submit their game for
review.

Sources:

- `https://docs.gog.com/`
- `https://docs.gog.com/quick-start/`

Best Lantern GOG target:

- a polished DRM-free game/app after Itch or direct pilots prove demand.

## Free Online SDK Lane

Prioritize free SDKs/tools that can build locally and package for Itch first:

| SDK / Tool | Use | First Lantern Target |
|---|---|---|
| itch `butler` | upload/update builds | Itch release lane |
| GOG Build Creator / Pipeline Builder | future DRM-free packaging | later GOG lane |
| GameMaker runtime/tooling | existing GameMaker repos | ChildOfLevistus / room editor |
| Godot | free/open-source game/app builds | One World Leader demo |
| Electron or Tauri | desktop app shell | Tony Garage packaged app |
| Python + ReportLab | PDFs and reports | whitepaper/ADS/cash packets |
| PowerShell | Windows/local automation | dual boot prep, wallet, surfaces |
| Internet Archive / Wayback APIs | metadata intake | commons RAG lane |
| OpenAI / local LLM APIs | optional intelligence layer | RAG cleanup and report synthesis |

Do not bind Lantern to one store SDK yet. Build small HTML/ZIP/desktop artifacts
that can move from local store to Itch, then to Steam/GOG if they prove demand.
