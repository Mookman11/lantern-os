# Lantern Chat — Bookmark & Shortcut Guide

## Quick start

### 1. Create the desktop and Start Menu shortcuts (run once)

Open PowerShell and run:

```powershell
.\scripts\New-LanternChatShortcut.ps1
```

This creates two shortcuts pointing to `http://127.0.0.1:4177`:

| Shortcut | Location |
|----------|----------|
| Desktop  | `%USERPROFILE%\Desktop\Lantern Chat.url` |
| Start Menu | `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Lantern\Lantern Chat.url` |

No admin rights, no Windsurf, and no IDE required.

To use a custom URL (e.g. a different port), pass it as a parameter:

```powershell
.\scripts\New-LanternChatShortcut.ps1 -TargetUrl 'http://127.0.0.1:4177'
```

### 2. Verify the server is running

```powershell
.\scripts\Test-LanternChatEndpoint.ps1
```

Sample output when the server is up:

```
Lantern Chat Endpoint Test
--------------------------
URL tested : http://127.0.0.1:4177
HTTP status : 200
Result     : PASS
```

Sample output when the server is down:

```
Lantern Chat Endpoint Test
--------------------------
URL tested : http://127.0.0.1:4177
HTTP status : N/A
Reason     : Connection refused (server may not be running)
Result     : FAIL
```

The script exits `0` on success and `1` on failure, making it CI-friendly.

## Default local URL

```
http://127.0.0.1:4177
```

## Starting the server

```bash
node apps/lantern-garage/server.js
```

The server must be running before the shortcuts or the browser will work.
If the port is occupied, check for another process on `4177` and stop it first:

```powershell
# Windows — find and kill the process on port 4177
netstat -ano | findstr :4177
# note the PID from the last column, then:
Stop-Process -Id <PID> -Force
```

## Files

| File | Purpose |
|------|---------|
| `scripts/New-LanternChatShortcut.ps1` | Creates desktop + Start Menu `.url` shortcuts |
| `scripts/Test-LanternChatEndpoint.ps1` | HTTP probe — reports status code, PASS/FAIL, exits 0/1 |
