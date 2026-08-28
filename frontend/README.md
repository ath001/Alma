# Alma frontend

Next.js (App Router, TypeScript, Tailwind) web app: a public lead-submission form and an internal, auth-guarded leads list.

## Quickstart

```bash
npm install
cp .env.local.example .env.local
npm run dev
```

Expects the backend running locally at `http://localhost:8010` (see `../backend/README.md`) — the home page's "Backend status" line proves the connection is working. Sign in to `/internal` with the seeded dummy account, **`admin` / `admin`** (see `../backend/README.md#auth` for adding real ones).

## Structure

- `src/app/page.tsx` — public lead-submission form (`src/components/lead-form.tsx`), submits to the backend's `POST /api/v1/leads` and shows loading/success/error state.
- `src/app/login/` — sign-in form (`page.tsx`) posting to a Server Action (`actions.ts`) that calls the backend's `POST /api/v1/auth/login` and sets an httpOnly session cookie (`src/lib/session.ts`).
- `src/app/internal/` — real auth guard in `layout.tsx`: reads the session cookie, validates it against `GET /api/v1/auth/me`, redirects to `/login` if missing/invalid. Renders a "Signed in as {username}" header with a logout button (`internal/actions.ts`). Wraps the leads list at `internal/leads/`, which renders `GET /api/v1/leads` as a table (name, email, resume download link, state, submitted date, and a "Reach out" button on `PENDING` rows via `internal/leads/actions.ts`).
- `src/app/internal/leads/[id]/resume/route.ts` — a Route Handler that proxies resume downloads: reads the session cookie server-side and forwards it as `Authorization: Bearer` to the backend, streaming the file back. Needed because the session token lives in an httpOnly cookie the browser can't read — a plain `<a href>` straight to the backend wouldn't be able to authenticate.
- `src/lib/api-client.ts` — the only place that knows the backend base URL / fetch conventions (`getHealth`, `createLead`, `getLeads`, `markLeadReachedOut`, `login`, `logout`, `getMe`, `fetchResume`).
- `src/lib/session.ts` — the only place that knows the session cookie's name/options.

**How auth flows**: the session token never reaches the browser as JS-readable state — it's set as an httpOnly cookie by a Server Action right after login, and every subsequent authenticated call (`getLeads`, `markLeadReachedOut`, the resume proxy, the layout's `/auth/me` check) happens **server-side** in Next.js (Server Components, Server Actions, or the Route Handler), which reads the cookie and forwards it as `Authorization: Bearer <token>` to the backend. The browser only ever talks to the backend directly for the two public endpoints (`GET /api/v1/health`, `POST /api/v1/leads`).

Not implemented yet: nothing — the assignment's three pieces (Lead CRUD, email, auth) are all done. Possible follow-ups: a real "add attorney" admin UI (currently a CLI script), password reset/change flow.
