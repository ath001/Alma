import { LeadForm } from "@/components/lead-form";
import { getHealth } from "@/lib/api-client";

export default async function Home() {
  const backendStatus = await getHealth()
    .then((h) => h.status)
    .catch(() => "unreachable");

  return (
    <main className="flex flex-col gap-8 p-8 max-w-xl mx-auto">
      <div>
        <h1 className="text-2xl font-semibold">Submit a lead</h1>
        <p className="text-sm text-gray-500">Backend status: {backendStatus}</p>
      </div>
      <LeadForm />
    </main>
  );
}
