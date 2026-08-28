"use server";

import { redirect } from "next/navigation";

import { login } from "@/lib/api-client";
import { setSessionCookie } from "@/lib/session";

export type LoginState = { error: string } | null;

export async function loginAction(_prevState: LoginState, formData: FormData): Promise<LoginState> {
  const username = formData.get("username");
  const password = formData.get("password");
  if (typeof username !== "string" || typeof password !== "string") {
    return { error: "Username and password are required" };
  }

  try {
    const { token } = await login(username, password);
    await setSessionCookie(token);
  } catch {
    return { error: "Invalid username or password" };
  }

  redirect("/internal/leads");
}
