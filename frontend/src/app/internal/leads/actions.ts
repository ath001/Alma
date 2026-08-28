"use server";

import { revalidatePath } from "next/cache";

import { markLeadReachedOut } from "@/lib/api-client";

export async function reachOutAction(formData: FormData) {
  const leadId = formData.get("leadId");
  if (typeof leadId !== "string") return;

  await markLeadReachedOut(leadId);
  revalidatePath("/internal/leads");
}
