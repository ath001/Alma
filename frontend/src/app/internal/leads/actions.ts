"use server";

import { revalidatePath } from "next/cache";

import { markLeadReachedOut } from "@/lib/api-client";
import { getSessionToken } from "@/lib/session";

export async function reachOutAction(formData: FormData) {
  const leadId = formData.get("leadId");
  if (typeof leadId !== "string") return;

  const token = await getSessionToken();
  if (!token) return;

  await markLeadReachedOut(leadId, token);
  revalidatePath("/internal/leads");
}
