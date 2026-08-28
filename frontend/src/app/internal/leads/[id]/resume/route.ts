import { fetchResume } from "@/lib/api-client";
import { getSessionToken } from "@/lib/session";

export async function GET(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  const token = await getSessionToken();
  if (!token) {
    return new Response("Unauthorized", { status: 401 });
  }

  const { id } = await params;
  const backendResponse = await fetchResume(id, token);
  if (!backendResponse.ok) {
    return new Response(backendResponse.statusText, { status: backendResponse.status });
  }

  return new Response(backendResponse.body, {
    status: 200,
    headers: {
      "Content-Type": backendResponse.headers.get("content-type") ?? "application/octet-stream",
      "Content-Disposition": backendResponse.headers.get("content-disposition") ?? "attachment",
    },
  });
}
