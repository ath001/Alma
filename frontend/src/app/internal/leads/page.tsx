import { getLeads, type Lead } from "@/lib/api-client";
import { getSessionToken } from "@/lib/session";

import { reachOutAction } from "./actions";

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

export default async function LeadsPage() {
  const token = (await getSessionToken())!; // internal/layout.tsx already guards this route
  const leads = await getLeads(token).catch(() => null);

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
                <th className="px-4 py-3 font-medium text-xs uppercase tracking-wide text-gray-500">
                  <span className="sr-only">Actions</span>
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
                      href={`/internal/leads/${lead.id}/resume`}
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
                  <td className="px-4 py-3 text-right whitespace-nowrap">
                    {lead.state === "PENDING" ? (
                      <form action={reachOutAction}>
                        <input type="hidden" name="leadId" value={lead.id} />
                        <button
                          type="submit"
                          className="text-xs font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 rounded px-2.5 py-1"
                        >
                          Reach out
                        </button>
                      </form>
                    ) : (
                      <span className="text-sm text-gray-300">—</span>
                    )}
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
