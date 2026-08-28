"use server";

import { redirect } from "next/navigation";

import { logout } from "@/lib/api-client";
import { clearSessionCookie, getSessionToken } from "@/lib/session";

export async function logoutAction(): Promise<void> {
  const token = await getSessionToken();
  if (token) {
    await logout(token);
  }
  await clearSessionCookie();
  redirect("/login");
}
