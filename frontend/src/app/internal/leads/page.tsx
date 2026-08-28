// TODO: fetch real leads from GET /api/v1/leads once that endpoint exists.
export default function LeadsPage() {
  return (
    <main className="flex flex-col gap-4 p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-semibold">Leads</h1>
      <p className="text-sm text-gray-500">No leads yet.</p>
    </main>
  );
}
