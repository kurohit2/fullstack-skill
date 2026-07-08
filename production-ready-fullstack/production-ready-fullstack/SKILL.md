---
name: production-ready-fullstack
description: Turns a vibe-coded prototype (built with Claude Code, Kiro, Antigravity, Codex, Cursor, or similar AI coding tools) into a genuinely production-ready full-stack app, and guides building new full-stack SaaS projects the right way from the start. Use when the user is starting a new full-stack app/SaaS project, asking to "make this production ready," "prep for launch," "harden this before deploy," "audit my codebase," or deploying a frontend+backend project to Vercel/Railway/AWS/Render. Also trigger for auth hardening, env/secrets management, database migrations, error handling, rate limiting, CI/CD, security headers, webhook verification, health checks, or a "pre-launch checklist." Covers greenfield scaffolding and auditing/hardening an existing repo. Default stack is Next.js + Flask/FastAPI + Supabase/Postgres + Vercel/Railway, but adapts to any stack the user specifies.
---

# Production-Ready Full-Stack

Vibe-coding tools are optimized to get something *running* fast. They almost never push for the things that make an app safe to put in front of real users and real payments: secrets handling, error boundaries, migrations, rate limiting, security headers, webhook verification, deployment configs, monitoring. This skill closes that gap — it turns "it works on my machine" into "it's safe to ship."

This skill works in two modes. Figure out which one applies before doing anything else.

## Mode detection

**Mode A — Greenfield scaffold.** The user is starting a new full-stack project (SaaS, internal tool, side project) and wants it built production-ready from day one.

**Mode B — Audit & harden.** The user already has a working (or partially working) app and wants it reviewed/hardened before launch, or wants a "production readiness audit."

If it's ambiguous, ask directly rather than guessing — the workflows diverge quickly.

---

## Step 1: Discovery

Before writing or reviewing any code, get the essentials. Don't ask everything as one giant form — infer what you can from context (existing repo, prior conversation) and only ask what's actually missing. Good candidates for a quick multiple-choice check-in (via clarifying questions or an input-elicitation tool if available):

1. **Stack** — frontend framework, backend framework, database. Default assumption if unstated: Next.js + Flask/FastAPI + Supabase/Postgres. Confirm rather than silently forcing the default onto an existing repo.
2. **Deployment target** — Vercel/Railway/Render/AWS/other. This changes the deployment checklist used in Step 5.
3. **What the app does** — auth needed? payments/webhooks (Razorpay/Stripe/Cashfree)? third-party integrations (email, WhatsApp/Telegram, etc.)? Each of these has specific hardening needs covered in `references/security-checklist.md`.
4. **Expected scale** — solo side project with a few hundred users vs. something expecting real concurrent load. This changes how much rate-limiting/caching/queueing infrastructure is actually worth building now vs. later. Don't over-engineer a pre-launch MVP with infrastructure it doesn't need yet — call this out explicitly if the user's ask is out of proportion to their stated scale.
5. **Mode A only** — is this a fresh repo or do they already have some scaffolding started?
6. **Mode B only** — do they have a repo path/directory Claude can actually read, or are they describing it?

If the stack is the default (Next.js + Flask/FastAPI + Supabase + Vercel/Railway), read `references/stack-defaults.md` for the opinionated folder structure, env conventions, and starter config. If it's a different stack, apply the same *principles* from the checklists below but adapt file/tool specifics — don't force default-stack file paths onto a different stack.

---

## Step 2: Architecture pass (Mode A) or structure review (Mode B)

Read `references/backend-checklist.md` and `references/frontend-checklist.md` — specifically their "Architecture" sections first. Before generating a full app or auditing one, confirm:

- Clear separation of concerns (routes/controllers vs. services/business logic vs. data access)
- Env var strategy: `.env.example` committed, `.env` gitignored, config validated at startup (fail loudly if a required var is missing, don't silently default secrets)
- API versioning if it's a public-facing API
- Consistent error response shape across the backend

For Mode B, don't rewrite the whole architecture unless it's genuinely broken — flag issues, propose the smallest fix that gets it to production-safe, and let the user decide if a bigger refactor is worth it.

## Step 3: Backend hardening

Read `references/backend-checklist.md` in full and work through it against the codebase (Mode B) or as build targets (Mode A). Covers input validation, error handling middleware, structured logging, rate limiting, DB connection pooling and migrations, health check endpoints, and webhook signature verification.

## Step 4: Frontend hardening

Read `references/frontend-checklist.md`. Covers env-based API URLs (never hardcoded localhost or prod URLs), loading/error/empty states, SEO meta tags, basic accessibility, and avoiding `any`-typed escape hatches if using TypeScript.

## Step 5: Security pass

Read `references/security-checklist.md`. Covers CORS config, secrets rotation, auth token handling (httpOnly cookies vs. localStorage tradeoffs), SQL injection/XSS surface, and dependency auditing. This is the section to be most thorough and least willing to skip steps on — security gaps are the ones that don't show up until they're expensive.

## Step 6: Deployment & ops

Read `references/deployment-checklist.md`, and within it jump to the subsection matching the user's deployment target (Vercel/Railway/Render/AWS/Docker-generic). Covers Dockerfile conventions, CI/CD, monitoring/alerting hooks, and rollback strategy.

## Step 7: Run the automated checks

Two scripts are available for objective, repeatable checks — use them rather than eyeballing the repo for these specific issues:

- `scripts/secret_scan.py <path>` — scans for hardcoded API keys, tokens, and credentials that shouldn't be committed.
- `scripts/env_check.py <path>` — checks `.env.example` exists, is gitignored correctly (`.env*` patterns present, `.env.example` NOT ignored), and that every key in `.env` has a corresponding entry in `.env.example` (and vice versa, flagging orphans).

Run both. If either script isn't applicable (e.g. no `.env` convention in this stack) say so rather than forcing it.

## Step 8: Final audit report

Produce a single structured report using `references/audit-report-template.md` as the format. Group findings by severity (Blocker / Should-fix / Nice-to-have), not by checklist category — the user needs to know what stops them from launching vs. what can wait. Be direct about blockers; don't soften a missing webhook signature check or an exposed secret into a "consideration."

---

## Principles throughout

- **Proportionality.** A solo side project doesn't need Kubernetes. Recommend infrastructure that matches actual stated scale, and say so when a request is over-engineered for the use case.
- **Don't silently rewrite working code.** In Mode B, propose changes and explain the risk being addressed before making sweeping edits, especially to auth, payments, or data-handling code.
- **Never invent secrets or credentials.** If a script or checklist needs an API key, webhook secret, etc., tell the user to provide it via env var — never hardcode a placeholder that looks real.
- **Cite the specific risk, not just the rule.** "Add rate limiting" is weak. "This webhook endpoint has no signature verification, so anyone who finds the URL can trigger fake payment confirmations" is actionable.
