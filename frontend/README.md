# Alma frontend

Next.js (App Router, TypeScript, Tailwind) web app: a public lead-submission form and an internal, auth-guarded leads list.

## Quickstart

```bash
npm install
cp .env.local.example .env.local
npm run dev
```

Expects the backend running locally at `http://localhost:8010` (see `../backend/README.md`) — the home page's "Backend status" line proves the connection is working.

## Structure

- `src/app/page.tsx` — public lead-submission form (`src/components/lead-form.tsx`).
- `src/app/internal/` — auth-guarded internal section (`internal/layout.tsx` has a TODO where real auth plugs in) with the leads list at `internal/leads/`.
- `src/lib/api-client.ts` — the only place that knows the backend base URL / fetch conventions.

Lead CRUD, real form submission, and auth are not implemented yet — see the TODO comments in the code.
