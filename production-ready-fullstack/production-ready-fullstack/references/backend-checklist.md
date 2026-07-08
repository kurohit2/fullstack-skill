# Backend Production Checklist

Work through each section. For Mode B (audit), check the existing code against each item and report gaps. For Mode A (greenfield), treat these as build requirements.

## Architecture

- [ ] Routes/controllers are thin — they parse input, call a service function, return a response. Business logic lives in `services/`, not inline in route handlers.
- [ ] Data access is isolated (models/repositories), not raw queries scattered through service code.
- [ ] Config loaded and validated once at startup; app refuses to start if a required env var is missing, rather than running with `None`/empty secrets.
- [ ] Consistent error response shape across all endpoints, e.g. `{"error": {"code": "...", "message": "..."}}` — not a mix of plain strings, stack traces, and JSON depending on the route.

## Input validation

- [ ] Every endpoint validates request bodies/query params (Pydantic for FastAPI, marshmallow/pydantic for Flask, zod for a Node backend) — don't trust client input, including type, presence, and length.
- [ ] File uploads (if any) validate file type and size server-side, not just via frontend `accept` attributes.

## Error handling

- [ ] A global error handler catches unhandled exceptions and returns a clean error response — the user should never see a raw stack trace or Python traceback in production.
- [ ] Distinguish expected errors (validation failure, not found, unauthorized → 4xx with a clear message) from unexpected ones (500, logged with full detail server-side, generic message client-side).
- [ ] Errors are logged with enough context to debug (request ID, user ID if available, endpoint) but never log full request bodies containing secrets/passwords/tokens.

## Logging

- [ ] Structured logging (JSON logs or at minimum consistent format) rather than scattered `print()`/`console.log()`.
- [ ] Log levels used correctly — DEBUG for dev detail, INFO for normal operations, WARNING/ERROR for actual problems. Don't ship with DEBUG-level noise in production.
- [ ] No secrets, tokens, passwords, or full payment details ever appear in logs.

## Rate limiting

- [ ] Public-facing endpoints (especially auth: login, signup, password reset) have rate limiting to prevent brute force / abuse. Match the limit to actual expected usage — don't over-engineer for a solo MVP, but auth endpoints need it regardless of scale.
- [ ] Webhook endpoints are rate-limited or otherwise protected against replay/flood even though they're also signature-verified (see security-checklist.md).

## Database

- [ ] Migrations are version-controlled (Alembic for Flask/FastAPI+SQLAlchemy, Prisma migrate, or Supabase migrations) — schema changes aren't applied by hand against production.
- [ ] Connection pooling configured appropriately for the deployment target (see stack-defaults.md's Supabase pooling note if applicable).
- [ ] Indexes exist on columns used in WHERE/JOIN/ORDER BY for any table expected to grow (users, subscriptions, notifications, etc.) — check this explicitly, it's the single most common "why is this suddenly slow at 1000 rows" cause.
- [ ] No N+1 query patterns in hot paths (e.g. looping over users and querying subscriptions one at a time instead of a single joined/batched query).

## Health checks & observability

- [ ] A `/health` or `/healthz` endpoint exists that checks the app is up and (ideally) that it can reach its database — deployment platforms (Railway, etc.) use this for restart/rollback decisions.
- [ ] Some form of error tracking is wired up (Sentry or equivalent) if the project is past pure-prototype stage — silent production errors are worse than noisy ones.

## Webhooks (if applicable — payments, third-party integrations)

- [ ] Every webhook endpoint verifies the signature from the provider (Razorpay, Stripe, Cashfree, Meta, etc.) before trusting the payload. This is a hard requirement, not a nice-to-have — an unverified webhook endpoint means anyone who finds the URL can fake events (e.g. fake payment confirmations).
- [ ] Webhook handlers are idempotent (safe to receive the same event twice) since providers commonly retry.
- [ ] Webhook secrets are stored as env vars, never hardcoded, and are different between test/live modes.

## API design

- [ ] Versioned if it's a public API (`/api/v1/...`) so breaking changes don't silently break existing clients.
- [ ] Pagination on any list endpoint that could return unbounded results (users, notifications, logs).
