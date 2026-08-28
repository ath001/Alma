import type { ReactNode } from "react";
import { redirect } from "next/navigation";

import { getMe } from "@/lib/api-client";
import { getSessionToken } from "@/lib/session";

import { logoutAction } from "./actions";

export default async function InternalLayout({ children }: { children: ReactNode }) {
  const token = await getSessionToken();
  const me = token ? await getMe(token) : null;

  if (!me) {
    redirect("/login");
  }

  return (
    <>
      <header className="flex items-center justify-between px-8 py-4 border-b border-gray-200">
        <span className="text-sm text-gray-500">Signed in as {me.username}</span>
        <form action={logoutAction}>
          <button type="submit" className="text-sm text-gray-500 hover:underline">
            Log out
          </button>
        </form>
      </header>
      {children}
    </>
  );
}
