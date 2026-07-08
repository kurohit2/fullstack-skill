# Frontend Production Checklist

## Architecture

- [ ] API base URL comes from an env var (`NEXT_PUBLIC_API_URL` or equivalent), never hardcoded `localhost:5000` or a hardcoded production URL baked into source.
- [ ] A single API client module wraps fetch calls (auth headers, base URL, error handling) rather than raw `fetch()` calls scattered across components.
- [ ] Client-exposed env vars (`NEXT_PUBLIC_*` in Next.js) contain nothing sensitive — anything with `NEXT_PUBLIC_` is shipped to the browser and publicly readable. Secrets stay server-only.

## UX states

- [ ] Every data-fetching component handles loading, error, and empty states explicitly — not just the happy path. A blank white screen while data loads, or a silent failure with no feedback, reads as broken to a real user.
- [ ] Form submissions show pending/disabled state on the submit button to prevent double-submits (especially important for anything hitting a payment endpoint).
- [ ] User-facing error messages are actionable ("Couldn't save — check your connection and try again") not raw error objects or stack traces surfaced to the UI.

## Type safety (if TypeScript)

- [ ] `any` is avoided as an escape hatch for API response types — define actual interfaces/types for API responses, even loosely, so a backend shape change surfaces as a type error rather than a silent runtime bug.
- [ ] Strict mode enabled in `tsconfig.json` for new projects.

## SEO & metadata

- [ ] Title, meta description, and Open Graph tags set per-page (or at minimum at the app level) — matters even for SaaS landing pages, since this is often the first thing a potential user's link preview shows.
- [ ] `robots.txt` and a sitemap exist if the app has public marketing pages meant to be indexed.
- [ ] Favicon and app icons set (easy to forget, looks unfinished without it).

## Accessibility basics

- [ ] Interactive elements are actual `<button>`/`<a>` tags, not `<div onClick>`, so keyboard navigation and screen readers work.
- [ ] Images have `alt` text; form inputs have associated `<label>`s.
- [ ] Color contrast is reasonable for body text (don't rely on a11y-checking tools alone for a small project, but avoid obviously low-contrast palettes like light-gray-on-white body text).

## Performance

- [ ] Images use Next.js `<Image>` (or equivalent optimization) rather than raw `<img>` for anything above thumbnail size.
- [ ] No obviously unnecessary client-side JS for content that could be server-rendered/static (landing pages, marketing content) — use static generation or server components where the framework supports it.

## Security (frontend-specific — see security-checklist.md for the rest)

- [ ] Auth tokens are not stored in `localStorage` if avoidable (XSS-exposed); prefer httpOnly cookies set by the backend. If localStorage is used anyway (common for simplicity in small projects), flag it as a known tradeoff rather than an oversight.
- [ ] No API keys or secrets embedded in frontend source, including ones that "look internal" — anything shipped to the browser is public.
