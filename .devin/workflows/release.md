---
description: !release invokes the release-prep assistant. Use it when a Lantern OS change is ready to be packaged, summarized, versioned, or shipped. Give it the branch/PR/commit range, what changed, and the intended audience; it should produce a release summary, version bump if needed, and a checklist of what remains before the change is truly done.
---

## Steps

1. **Identify the commit range.** Use `git log <base>..<head>` to see what changed.
2. **Summarize changes.** Group commits by type (feat, fix, docs, chore). Note breaking changes explicitly.
3. **Determine version impact.** Patch, minor, or major? Follow semver based on user-facing vs internal changes.
4. **Check dependencies.** Are there new env vars, API changes, or migrations the user needs to know about?
5. **Write release notes.** One-line summary + bullet points. Include migration notes if needed.
6. **Update version markers.** If this is a versioned release, bump version strings in `package.json`, manifest files, or UI badges.
7. **Produce a checklist.** What tests were run? What remains? Is the server restarted? Are docs updated?
8. **Commit and tag.** `git tag -a vX.Y.Z -m "Release notes..."` if this is a versioned release.
9. **Report back.** Share the release summary, any blockers, and the next priority.

## Safety Rules

- Never force-push to master.
- Never delete tags that have been pushed.
- If a merge conflict exists, stop and ask the user before resolving.
- Prefer `git merge --no-ff` to preserve branch history.
