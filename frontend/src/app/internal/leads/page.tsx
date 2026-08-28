import { getLeads, type Lead } from "@/lib/api-client";

function StateBadge({ state }: { state: Lead["state"] }) {
  const styles =
    state === "REACHED_OUT"
      ? "bg-green-100 text-green-800"
      : "bg-amber-100 text-amber-800";
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${styles}`}>
      {state === "REACHED_OUT" ? "Reached out" : "Pending"}
    </span>
  );
}

// TODO: guard this page with auth (see internal/layout.tsx) and add a
// "mark reached out" action wired to POST /api/v1/leads/{id}/reach-out.
export default async function LeadsPage() {
  const leads = await getLeads().catch(() => null);
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8010";

  return (
    <main className="flex flex-col gap-6 p-8 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-semibold">Leads</h1>
        {leads !== null && (
          <p className="text-sm text-gray-500 mt-1">
            {leads.length} {leads.length === 1 ? "lead" : "leads"}
          </p>
        )}
      </div>

      {leads === null && (
        <p className="text-sm text-red-600">Failed to load leads.</p>
      )}

      {leads !== null && leads.length === 0 && (
        <p className="text-sm text-gray-500">No leads yet.</p>
      )}

      {leads !== null && leads.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-gray-200">
          <table className="w-full text-sm text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="px-4 py-3 font-medium text-xs uppercase tracking-wide text-gray-500">
                  Name
                </th>
                <th className="px-4 py-3 font-medium text-xs uppercase tracking-wide text-gray-500">
                  Email
                </th>
                <th className="px-4 py-3 font-medium text-xs uppercase tracking-wide text-gray-500">
                  Resume
                </th>
                <th className="px-4 py-3 font-medium text-xs uppercase tracking-wide text-gray-500">
                  State
                </th>
                <th className="px-4 py-3 font-medium text-xs uppercase tracking-wide text-gray-500">
                  Submitted
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {leads.map((lead) => (
                <tr key={lead.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">
                    {lead.first_name} {lead.last_name}
                  </td>
                  <td className="px-4 py-3 text-gray-600">{lead.email}</td>
                  <td className="px-4 py-3">
                    <a
                      className="text-blue-600 hover:underline"
                      href={`${apiBaseUrl}${lead.resume_url}`}
                    >
                      {lead.resume_filename}
                    </a>
                  </td>
                  <td className="px-4 py-3">
                    <StateBadge state={lead.state} />
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {new Date(lead.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
