# Security Checklist

This is the section to be most thorough on. A missing feature is annoying; a security gap is invisible until someone finds it, and by then the cost is much higher than fixing it now would have been.

## Secrets management

- [ ] No API keys, tokens, DB credentials, or webhook secrets are hardcoded anywhere in source — including "temporary" debug code, comments, or config files that look internal.
- [ ] Run `scripts/secret_scan.py` against the repo — don't rely on manual review alone for this one.
- [ ] If a secret has ever been committed to git history (even if later removed), it must be rotated. Removing it from the latest commit does not remove it from history — treat any historically-committed secret as compromised.
- [ ] Different secrets for development/staging/production, especially payment gateway keys (test vs. live mode) and DB credentials.

## CORS

- [ ] CORS is configured with an explicit allowlist of origins (the actual frontend domain(s)), not `*` for any endpoint that handles authenticated requests or sensitive data.
- [ ] Wildcard CORS (`*`) is acceptable only for genuinely public, unauthenticated read endpoints.

## Auth

- [ ] Passwords (if not using a third-party auth provider like Supabase Auth/Firebase Auth) are hashed with bcrypt/argon2, never stored plain or with weak hashing (MD5/SHA1).
- [ ] Session tokens/JWTs have reasonable expiry; refresh token rotation if using JWTs long-term.
- [ ] Authorization is checked on every protected endpoint server-side — never rely on the frontend hiding a button as the only protection for a privileged action. Check: can a logged-in user directly hit another user's data by guessing/changing an ID in the request?

## Injection & XSS

- [ ] All database queries use parameterized queries/ORM methods — no raw string concatenation building SQL from user input.
- [ ] User-generated content rendered in the frontend is escaped by default (React/Next.js does this automatically — the risk is specifically `dangerouslySetInnerHTML` or equivalent raw-HTML-injection points; audit any use of those).

## Webhook security (payments, third-party integrations)

- [ ] Every webhook verifies the provider's signature (Razorpay `x-razorpay-signature`, Stripe signature header, Cashfree signature, Meta's `X-Hub-Signature-256`, etc.) against the raw request body before processing. Skipping this means anyone who discovers the webhook URL can send fake events — e.g. a fake "payment succeeded" call that grants access without payment.
- [ ] Signature verification uses the raw request body bytes, not a re-serialized/parsed version — many frameworks parse the body before your handler runs, which breaks signature verification unless done correctly. Confirm the raw body is what's actually being hashed.

## Dependency hygiene

- [ ] Run the ecosystem's audit tool (`npm audit`, `pip-audit`) and address high/critical findings before launch — doesn't need to be zero-warning, but nothing severe left unaddressed.
- [ ] No abandoned/unmaintained packages handling anything security-sensitive (auth, payments, crypto).

## Security headers (web apps)

- [ ] Basic security headers set (via middleware or platform config): `Content-Security-Policy` (at least a starting policy), `X-Content-Type-Options: nosniff`, `X-Frame-Options` or frame-ancestors CSP directive to prevent clickjacking.
- [ ] HTTPS enforced (usually automatic on Vercel/Railway, but confirm no mixed-content or HTTP-fallback paths).

## Rate limiting & abuse prevention

- [ ] Auth endpoints (login, signup, password reset, OTP send) are rate-limited per IP/account to prevent brute force and abuse — this is a security item as much as a backend-performance one.
- [ ] Any endpoint that triggers a paid third-party action (sending SMS/WhatsApp/email) is rate-limited or otherwise protected against being used to run up costs by an attacker hammering it.

## GDPR/privacy basics (if handling user data, especially EU/India cross-border)

- [ ] Privacy policy and ToS exist and are accurate to what's actually collected/done with data (not boilerplate that overclaims or underclaims).
- [ ] A path exists for a user to request account/data deletion, even if manual for now at small scale.
