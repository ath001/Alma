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

- `src/app/page.tsx` — public lead-submission form (`src/components/lead-form.tsx`), submits to the backend's `POST /api/v1/leads` and shows loading/success/error state.
- `src/app/internal/` — internal section, **not auth-guarded yet** (`internal/layout.tsx` has a TODO where real auth plugs in), with the leads list at `internal/leads/` rendering `GET /api/v1/leads` as a table (name, email, resume download link, state, submitted date).
- `src/lib/api-client.ts` — the only place that knows the backend base URL / fetch conventions (`getHealth`, `createLead`, `getLeads`).

Not implemented yet: real auth, and a "mark reached out" action in the internal UI (the backend endpoint exists — `POST /api/v1/leads/{id}/reach-out` — just not wired to a button).
