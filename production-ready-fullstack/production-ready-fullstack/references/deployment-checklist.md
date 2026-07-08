# Deployment & Ops Checklist

Read the general section, then jump to the subsection matching the user's actual deployment target.

## General (applies everywhere)

- [ ] Environment variables are set per-environment in the platform dashboard/config, not committed anywhere.
- [ ] A CI pipeline (even a minimal one — GitHub Actions is the common default) runs lint/type-check/tests on every push before merge, so broken code doesn't reach main.
- [ ] Rollback plan exists: know how to revert to the last working deploy quickly (most platforms keep deploy history — confirm this is actually usable, not just theoretical).
- [ ] Monitoring/alerting: at minimum, know within minutes (not from a user complaint) if the app goes down. Uptime monitoring (UptimeRobot, Better Stack, or the platform's built-in health checks) is a five-minute setup with outsized value.
- [ ] Database backups are enabled and the restore process has actually been tested at least once — an untested backup is not a backup.

## Vercel (frontend)

- [ ] Framework preset correctly detected (Next.js auto-detected in most cases).
- [ ] Env vars set separately for Production / Preview / Development in the Vercel dashboard — a common mistake is only setting Production vars, then Preview deploys break.
- [ ] Custom domain configured with SSL (automatic via Vercel, but confirm DNS is correctly pointed).
- [ ] Build command and output directory correct if using a non-default setup.

## Railway (backend)

- [ ] App binds to `0.0.0.0:$PORT` using Railway's dynamically-injected `PORT` env var — a hardcoded port is the most common Railway deploy failure.
- [ ] Dockerfile uses exec-form `CMD` where possible; if shell-form is needed for env var expansion (e.g. `$PORT` substitution), confirm it's intentional and working, since shell-form can swallow signals and complicate graceful shutdown.
- [ ] Health check path configured in Railway settings so it can detect a broken deploy and avoid routing traffic to it.
- [ ] Resource limits (memory/CPU) sized appropriately — not left at whatever the default was if the app has known memory characteristics.

## Render

- [ ] Same `PORT` binding principle as Railway — bind to the platform-provided port, don't hardcode.
- [ ] Health check endpoint configured.
- [ ] Auto-deploy branch set correctly (often defaults to `main`; confirm this is intentional).

## AWS (EC2/ECS/Lambda — more involved, only if the user is actually operating at this level)

- [ ] Secrets in AWS Secrets Manager or Parameter Store, not env vars baked into an AMI/container image.
- [ ] Security groups scoped to actual required access (don't leave a DB port open to `0.0.0.0/0`).
- [ ] If Lambda: cold start behavior considered for user-facing latency-sensitive paths; connection pooling handled carefully since Lambda's execution model doesn't play well with naive long-lived DB connections (use RDS Proxy or a pooler).

## Docker (generic, any platform)

- [ ] Multi-stage builds used to keep image size down (build stage vs. slim runtime stage).
- [ ] Non-root user runs the container process where the base image supports it.
- [ ] `.dockerignore` excludes `node_modules`, `.git`, `.env`, and other files that shouldn't be baked into the image.

## Database (Supabase/Postgres specifically)

- [ ] Connection pooling (Supabase's pooler/pgbouncer) used for serverless or high-connection-count deployments; direct connection reserved for long-running processes that can hold a persistent connection.
- [ ] Row-level security (RLS) policies reviewed if using Supabase's client-side SDK directly from the frontend — without RLS, a client-side Supabase key can expose the whole table to any authenticated (or even anonymous) user.
- [ ] Migrations applied through a tracked migration tool, not manually via the Supabase SQL editor with no record of what ran.

## Pre-launch smoke test

Before calling it done, walk the actual critical user paths end-to-end against the deployed (not local) environment: signup → core action → (payment if applicable) → confirmation. This catches env-var mismatches and deployment-specific bugs that never show up in local dev.
