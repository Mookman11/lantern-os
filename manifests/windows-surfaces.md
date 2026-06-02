# Windows Surface Manifest

Status: installed on current Windows user profile.

## Installed Paths

- Desktop bundle: `C:\Users\alexp\OneDrive\Desktop\Lantern Surfaces`
- Start Menu folder: `C:\Users\alexp\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Lantern`
- Feather Lantern icon: `C:\Users\alexp\OneDrive\Desktop\Lantern Surfaces\assets\feather-lantern.ico`

## Verified Surface Count

Last observed shortcut count: 23.

## Included Surface Classes

- Lantern desktop auth
- Lantern chat UI
- Lantern Kids UI
- Lantern integrated runtime
- Lantern tutorial pages
- Local dashboard URL
- Discord radio bot launcher
- HFF local app launcher
- COMET LEAP PDFs
- Buffett / COMET LEAP docs
- NixOS config links
- Dual boot prep document

## Reproducible Setup Script

**Status: Complete**

Created `scripts/Invoke-WindowsSurfaceSetup.ps1` for reproducible Windows surface setup.

### Script Features

- Creates desktop and Start Menu folder structure
- Generates shortcuts to all Lantern surfaces
- References COMET LEAP artifacts
- Links to NixOS configurations
- Sets Feather Lantern icon
- Idempotent (safe to run multiple times)

### Usage

```powershell
# Create/recreate Windows Lantern surfaces
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Invoke-WindowsSurfaceSetup.ps1

# With custom paths (optional)
. scripts/Invoke-WindowsSurfaceSetup.ps1 -DesktopPath "C:\Custom\Desktop"
```

### Verified Shortcuts Created

- 23+ shortcuts across surface classes
- COMET LEAP artifacts (PDFs, DOCX, reports)
- NixOS configs and dual boot prep
- Lantern OS project links
- Start Menu dashboard entry
- All with proper descriptions and icons

## Promotion Status

**Current: Validated - Ready for integration**

The Windows surface is now fully reproducible via script. Can be promoted after operator approval.

### Ready for v1.0.0 When:
- [x] Reproducible script created
- [x] Script tested and validated
- [x] All shortcuts properly linked
- [x] Icon asset managed correctly
- [ ] Operator runs script successfully
- [ ] Operator approves for promotion

