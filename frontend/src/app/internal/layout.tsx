import type { ReactNode } from "react";

// TODO: guard everything under /internal with real auth once a mechanism is
// chosen (e.g. NextAuth, or a session cookie issued by the backend). This
// layout currently renders its children unprotected.
export default function InternalLayout({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
