<p align="center">
  <img src="./assets/banner.svg" alt="production-ready-fullstack audit output example" width="800">
</p>

<h1 align="center">production-ready-fullstack</h1>

<p align="center"><em>He doesn't care that it runs. He wants to know what happens when someone finds the webhook URL.</em></p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-111111?style=flat-square" alt="MIT license">
  <img src="https://img.shields.io/badge/type-Claude%20Skill-111111?style=flat-square" alt="Claude Skill">
  <img src="https://img.shields.io/badge/works%20with-Claude.ai%20%7C%20Claude%20Code%20%7C%20Cowork-111111?style=flat-square" alt="Works with Claude.ai, Claude Code, Cowork">
  <img src="https://img.shields.io/badge/stack-Next.js%20%C2%B7%20Flask%2FFastAPI%20%C2%B7%20Supabase-111111?style=flat-square" alt="Stack">
</p>

---

Every team has one. The senior dev who's been on call during the outage you only heard about secondhand. Doesn't say much in code review. Just leaves one comment: *"where's the signature check on this webhook?"* — and now you're rewriting it.

This is a Claude Skill that puts him in the room before you ship.

Your AI coding tool (Claude Code, Kiro, Cursor, Antigravity, whatever) is very good at "it works." It has no opinion on "it survives contact with the internet." That gap — the one between demo and production — is what this skill closes.

## Before / after

You ask your agent to wire up a Razorpay webhook. It gives you this:

```python
@app.route("/webhook/razorpay", methods=["POST"])
def razorpay_webhook():
    data = request.get_json()
    if data["event"] == "payment.captured":
        activate_subscription(data["payload"]["payment"]["entity"]["email"])
    return "", 200
```

It runs. It also means anyone who finds that URL can activate a subscription for free by just POSTing the right JSON — no payment required, no signature checked, nothing.

Run this skill's audit and it flags it as a **🔴 Blocker**, not a suggestion:

```python
@app.route("/webhook/razorpay", methods=["POST"])
def razorpay_webhook():
    signature = request.headers.get("X-Razorpay-Signature", "")
    if not verify_webhook_signature(request.get_data(), signature, WEBHOOK_SECRET):
        abort(400)
    data = request.get_json()
    if data["event"] == "payment.captured":
        activate_subscription(data["payload"]["payment"]["entity"]["email"])
    return "", 200
```

Same feature. One version can be robbed by anyone with `curl`.

## What it actually checks

<p align="center">
  <img src="./assets/workflow.svg" alt="Discovery to Architecture to Backend to Frontend to Security to Deployment to Scan to Report" width="850">
</p>

Not a linter. Not "add more tests." It walks your repo (or your plan for a new one) through the questions that actually decide whether launch day goes fine or goes badly:

- **Secrets** — hardcoded, committed, or one `git log -p` away from being found
- **Webhooks & auth** — verified signatures, checked authorization, no security-by-obscurity
- **Database** — indexes before you need them, pooling before Supabase throttles you, migrations that are actually tracked
- **Deployment** — the Railway `$PORT` bug you will hit at 11pm the night before launch if nobody catches it now
- **The stuff that's boring until it isn't** — rate limiting, error handling, `.env.example` hygiene

Findings come back ranked — 🔴 Blocker, 🟡 Should-fix, 🟢 Nice-to-have — because "audit my app" is useless if you can't tell what stops you from launching tonight versus what can wait a sprint.

## How it works

Two modes, picked automatically from what you ask for:

- **Audit an existing repo** — points at your codebase, checks it against real production risks, hands back a severity-ranked report.
- **Scaffold something new** — sets up the folder structure, env conventions, and deployment config correctly *before* you've written 500 lines you'll have to retrofit later.

Default stack opinion is **Next.js + Flask/FastAPI + Supabase/Postgres + Vercel/Railway** — because that's what most solo builders in this ecosystem actually reach for — but it adapts to whatever you're running instead.

## Install

### Claude.ai / Claude Cowork
1. Download [`production-ready-fullstack.skill`](./production-ready-fullstack.skill) from this repo.
2. Upload it in Claude — you'll get a **Save skill** button if your org allows custom skills.

### Claude Code
```bash
git clone https://github.com/<your-username>/production-ready-fullstack.git
cp -r production-ready-fullstack ~/.claude/skills/
```
(Check `claude skills --help` if your skills directory lives somewhere else.)

That's it. No config file, no setup wizard. Just talk to Claude:

> "Audit my repo before I launch"
> "Help me scaffold a new SaaS, production-ready from day one"
> "Is my webhook actually secure?"
> "Prep this for a Railway deploy"

## What's inside

```
production-ready-fullstack/
├── SKILL.md                          # Entry point — mode detection + 8-step workflow
├── references/
│   ├── stack-defaults.md             # Opinionated default stack conventions
│   ├── backend-checklist.md          # Validation, errors, logging, rate limits, DB, webhooks
│   ├── frontend-checklist.md         # UX states, type safety, SEO, a11y, perf
│   ├── security-checklist.md         # Secrets, CORS, auth, injection/XSS, webhook signing
│   ├── deployment-checklist.md       # Vercel / Railway / Render / AWS / Docker specifics
│   └── audit-report-template.md      # Output format for the final report
└── scripts/
    ├── secret_scan.py                # Pattern-scans for hardcoded keys/tokens/credentials
    └── env_check.py                  # .env / .env.example hygiene + key-parity checks
```

## What it won't do

- It won't rewrite your working auth or payment code without telling you the risk first.
- It won't hand a solo side project a Kubernetes lecture it didn't ask for.
- It won't invent a placeholder secret that looks real. Ever.
- It won't soften a security finding into a "consideration" because the rest of the app looks fine.

## FAQ

**Does it need a config file?**
No. Ask a question, it triggers, it works.

**Will it flag things that don't actually matter for my scale?**
It's supposed to check proportionality — a 50-user MVP doesn't need the same infrastructure as a 50,000-user SaaS, and the skill is instructed to say so rather than pad the audit. If it doesn't, that's a bug, open an issue.

**What if I just want the checklist and not the AI?**
The `references/*.md` files are plain markdown. Read them yourself, no Claude required.

**Why not just use a linter?**
A linter catches syntax. It doesn't know your webhook has no signature check, or that your `.env.example` is missing a key someone will need in production. Different job.

## Contributing

Found a gap in a checklist? A false positive in `secret_scan.py`? A deployment target that isn't covered (Fly.io, DigitalOcean, Cloudflare Workers)? PRs welcome — built by someone actually shipping a SaaS with this, not a committee, so keep additions concrete and risk-based, not generic best-practice filler.

## License

[MIT](./LICENSE). The shortest license that works.

---

<p align="center"><em>Built while shipping <a href="https://purecheck.store">GovNotification</a> and getting tired of manually remembering every pre-launch checklist item.</em></p>
