const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8010";

function authHeaders(token?: string): HeadersInit {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

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

export async function getLeads(token: string): Promise<Lead[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/leads`, {
    cache: "no-store",
    headers: authHeaders(token),
  });
  if (!res.ok) {
    throw new Error(`Failed to load leads: ${res.status}`);
  }
  return res.json();
}

export async function markLeadReachedOut(id: string, token: string): Promise<Lead> {
  const res = await fetch(`${API_BASE_URL}/api/v1/leads/${id}/reach-out`, {
    method: "POST",
    headers: authHeaders(token),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Failed to mark lead reached out: ${res.status}`);
  }
  return res.json();
}

export async function fetchResume(id: string, token: string): Promise<Response> {
  return fetch(`${API_BASE_URL}/api/v1/leads/${id}/resume`, { headers: authHeaders(token) });
}

export type LoginResult = {
  token: string;
  username: string;
};

export async function login(username: string, password: string): Promise<LoginResult> {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Login failed: ${res.status}`);
  }
  return res.json();
}

export async function logout(token: string): Promise<void> {
  await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
    method: "POST",
    headers: authHeaders(token),
  });
}

export async function getMe(token: string): Promise<{ username: string } | null> {
  const res = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
    cache: "no-store",
    headers: authHeaders(token),
  });
  if (!res.ok) return null;
  return res.json();
}
