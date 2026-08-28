"use client";

import { useActionState } from "react";

import { loginAction } from "./actions";

export default function LoginPage() {
  const [state, formAction, pending] = useActionState(loginAction, null);

  return (
    <main className="flex flex-col gap-6 p-8 max-w-sm mx-auto">
      <h1 className="text-2xl font-semibold">Attorney sign in</h1>
      <form action={formAction} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1">
          Username
          <input name="username" className="border rounded px-3 py-2" required />
        </label>
        <label className="flex flex-col gap-1">
          Password
          <input
            name="password"
            type="password"
            className="border rounded px-3 py-2"
            required
          />
        </label>
        {state?.error && <p className="text-sm text-red-600">{state.error}</p>}
        <button
          type="submit"
          disabled={pending}
          className="bg-black text-white rounded px-4 py-2 disabled:opacity-50"
        >
          {pending ? "Signing in…" : "Sign in"}
        </button>
      </form>
    </main>
  );
}
