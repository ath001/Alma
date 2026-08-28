"use client";

import { useState } from "react";

export function LeadForm() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [resume, setResume] = useState<File | null>(null);

  // TODO: wire up submission to POST /api/v1/leads once that endpoint exists.
  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
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
          className="border rounded px-3 py-2"
          onChange={(e) => setResume(e.target.files?.[0] ?? null)}
          required
        />
        {resume && <span className="text-sm text-gray-500">{resume.name}</span>}
      </label>
      <button type="submit" className="bg-black text-white rounded px-4 py-2">
        Submit
      </button>
    </form>
  );
}
