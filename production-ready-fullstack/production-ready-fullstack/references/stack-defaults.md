# Default Stack Conventions

This is the opinionated default when the user hasn't specified a stack: **Next.js frontend + Flask or FastAPI backend + Supabase/Postgres + Vercel (frontend) / Railway (backend)**. Use this as a starting point, not a mandate — confirm with the user if they haven't stated their stack, and drop this entirely if they're using something else.

## Folder structure (greenfield)

```
project-root/
├── frontend/                  # Next.js app
│   ├── app/                   # App router
│   ├── components/
│   ├── lib/                   # API client, utils
│   ├── .env.example
│   └── .env.local             # gitignored
├── backend/                   # Flask or FastAPI
│   ├── app/
│   │   ├── routes/            # or api/ - thin, just request/response
│   │   ├── services/          # business logic
│   │   ├── models/            # DB models/schemas
│   │   ├── middleware/        # auth, error handling, rate limiting
│   │   └── config.py          # env validation, fails loudly if missing vars
│   ├── migrations/
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   └── .env                   # gitignored
├── .gitignore                 # covers .env, .env.local, __pycache__, node_modules, .next
└── README.md
```

## Env var conventions

- `.env.example` is committed and lists every required var with a placeholder or description — never a real value.
- `.env` / `.env.local` are gitignored. Verify this explicitly; a surprising number of "accidental secret exposure" incidents are just a missing `.gitignore` entry.
- Config is loaded and validated once at startup (e.g. a `config.py` or `env.ts` that throws immediately if a required var is missing), not read ad-hoc with `os.environ.get()` scattered through the codebase with silent `None` fallbacks for things like API keys.
- Separate env files per environment when it matters (`.env.development`, `.env.production`) rather than branching logic on `NODE_ENV`/`FLASK_ENV` inside business logic.

## Backend framework note

FastAPI is preferable for new projects needing built-in request validation (Pydantic) and auto-generated OpenAPI docs. Flask is fine and often the right call if the user is already invested in it (e.g. an existing Flask backend on Railway) — don't push a rewrite just to switch frameworks. Match the checklist recommendations to whichever is in use.

## Deployment target defaults

- **Frontend → Vercel.** Framework preset auto-detected for Next.js. Set env vars in the Vercel dashboard per-environment (Production/Preview/Development), not just one flat set.
- **Backend → Railway.** Needs a `Dockerfile` (or Railway's Nixpacks if no custom build steps) and explicit `PORT` env var handling — Railway injects `PORT` dynamically, the app must bind to `0.0.0.0:$PORT`, not a hardcoded port. Shell-form `CMD` in a Dockerfile can silently swallow signal handling and env var expansion issues; prefer exec-form `CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]`-style only if the shell is actually needed for var expansion — otherwise use array form with explicit `sh -c` only when required.
- **Database → Supabase (Postgres).** Use connection pooling (Supabase's pooler / pgbouncer) for serverless/edge functions to avoid exhausting connections; use the direct connection for long-running backend processes.

## Payments note (India-specific)

If payments are involved (Razorpay/Cashfree), see `security-checklist.md`'s webhook section — signature verification is non-negotiable, and KYC/category classification issues (e.g. Razorpay flagging a "government job platform" framing) are a business/compliance concern separate from but related to technical hardening.
