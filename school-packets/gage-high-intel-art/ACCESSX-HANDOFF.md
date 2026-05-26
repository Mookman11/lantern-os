# AccessX / Local Handoff

AccessX is running locally as:

`C:\Program Files\WindowsApps\SUPSI.AccessX_1.4.0.0_x64__bzz41p7kqy1nr\AccessX.exe`

The current ngrok tunnel points to:

`https://crinkle-utmost-debit.ngrok-free.dev`

That tunnel currently forwards to `http://localhost:8787`, which is the
orchestrator MCP server (`Start-OrchMcpServer.ps1 -NoAuth`) and returns 404 for
ordinary static files. Do not overwrite that service for school sharing.

Use these local packet files instead:

- `GAGE-HIGH-INTEL-ART-PACKET.zip`
- `GAGE-SCHOOL-COVER-LETTER.pdf`
- `GAGE-HIGH-INTEL-ART-INFO-PAGE.pdf`
- `GAGE-HIGH-INTEL-ART-CONTACT-SHEET.pdf`
- `index.html`

If AccessX has a file/open/share picker, point it at:

`C:\tmp\lantern-os\school-packets\gage-high-intel-art`

If a public link is needed later, start a separate static file server on a new
port and tunnel that port, rather than reusing the orchestrator MCP port.
