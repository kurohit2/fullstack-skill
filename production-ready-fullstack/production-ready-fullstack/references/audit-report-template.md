# Audit Report Format

Use this structure for the final output in Mode B (and as a build-completion summary in Mode A). Group by severity, not by checklist category — the user needs to know what blocks launch vs. what can wait.

```markdown
# Production Readiness Audit — [project name]

## Summary
[2-3 sentences: overall state, how close to launch-ready, biggest risk]

## 🔴 Blockers (fix before launch)
Issues that would cause a security incident, data loss, or broken core functionality in production.

- **[Issue]** — [specific risk, not just the rule broken] — [file/location if known] — [concrete fix]

## 🟡 Should-fix (fix soon, not necessarily before first launch)
Issues that are real problems but wouldn't cause an immediate incident — degraded UX, tech debt that will bite at scale, missing observability.

- **[Issue]** — [risk/impact] — [concrete fix]

## 🟢 Nice-to-have (backlog)
Genuine improvements that aren't urgent given current scale/stage.

- **[Issue]** — [why it matters eventually]

## Automated scan results
[Output/summary from secret_scan.py and env_check.py]

## What's already solid
[Brief acknowledgment of what's correctly done — an audit that's 100% criticism reads as unreliable and buries the signal]
```

Keep each bullet to the "risk, not just rule" standard from the main SKILL.md — e.g. not "add input validation" but "the `/api/subscribe` endpoint doesn't validate the email field, so a malformed value likely fails at the DB layer with an unhandled exception the user sees as a raw 500."
