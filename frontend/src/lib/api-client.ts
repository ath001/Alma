const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8010";

export type HealthStatus = {
  status: string;
};

export async function getHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE_URL}/api/v1/health`);
  if (!res.ok) {
    throw new Error(`Backend health check failed: ${res.status}`);
  }
  return res.json();
}

export type Lead = {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  resume_filename: string;
  resume_url: string;
  state: "PENDING" | "REACHED_OUT";
  created_at: string;
  updated_at: string;
  reached_out_at: string | null;
};

export type CreateLeadInput = {
  firstName: string;
  lastName: string;
  email: string;
  resume: File;
};

export async function createLead(input: CreateLeadInput): Promise<Lead> {
  const formData = new FormData();
  formData.set("first_name", input.firstName);
  formData.set("last_name", input.lastName);
  formData.set("email", input.email);
  formData.set("resume", input.resume);

  const res = await fetch(`${API_BASE_URL}/api/v1/leads`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Lead submission failed: ${res.status}`);
  }
  return res.json();
}

export async function getLeads(): Promise<Lead[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/leads`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to load leads: ${res.status}`);
  }
  return res.json();
}
