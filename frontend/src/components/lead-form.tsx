"use client";

import { useState } from "react";

import { createLead } from "@/lib/api-client";

type Status = "idle" | "submitting" | "success" | "error";

export function LeadForm() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [resume, setResume] = useState<File | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!resume) return;

    setStatus("submitting");
    setError(null);
    try {
      await createLead({ firstName, lastName, email, resume });
      setStatus("success");
      setFirstName("");
      setLastName("");
      setEmail("");
      setResume(null);
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Something went wrong");
    }
  }

  if (status === "success") {
    return (
      <div className="flex flex-col gap-4 max-w-sm">
        <p className="text-sm text-gray-700">Thanks — your submission was received.</p>
        <button
          type="button"
          className="text-sm underline text-gray-500 self-start"
          onClick={() => setStatus("idle")}
        >
          Submit another
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 max-w-sm">
      <label className="flex flex-col gap-1">
        First name
        <input
          className="border rounded px-3 py-2"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          required
        />
      </label>
      <label className="flex flex-col gap-1">
        Last name
        <input
          className="border rounded px-3 py-2"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          required
        />
      </label>
      <label className="flex flex-col gap-1">
        Email
        <input
          type="email"
          className="border rounded px-3 py-2"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </label>
      <label className="flex flex-col gap-1">
        Resume / CV
        <input
          type="file"
          accept=".pdf,.doc,.docx,.txt"
          className="border rounded px-3 py-2"
          onChange={(e) => setResume(e.target.files?.[0] ?? null)}
          required
        />
        {resume && <span className="text-sm text-gray-500">{resume.name}</span>}
      </label>
      {status === "error" && <p className="text-sm text-red-600">{error}</p>}
      <button
        type="submit"
        disabled={status === "submitting"}
        className="bg-black text-white rounded px-4 py-2 disabled:opacity-50"
      >
        {status === "submitting" ? "Submitting…" : "Submit"}
      </button>
    </form>
  );
}
