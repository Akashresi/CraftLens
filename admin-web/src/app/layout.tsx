import type { Metadata } from "next";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "CraftLens Admin | Government & Platform Governance Portal",
  description: "Artisan verification, product moderation, GI authenticity governance, and AI job monitoring for CraftLens 2.0.",
};

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-craft-background text-craft-text antialiased">
        <header className="sticky top-0 z-50 bg-craft-surface border-b border-craft-border px-6 py-3 shadow-subtle flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-craft-primary flex items-center justify-center text-white font-bold text-sm">
              CL
            </div>
            <div>
              <span className="font-extrabold text-sm text-craft-primary tracking-tight">
                CraftLens Admin Portal
              </span>
              <span className="block text-[10px] text-craft-muted font-medium">
                MoSJE Artisan Governance • Production
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-3 text-xs">
            <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-craft-success/10 text-craft-success border border-craft-success/20 font-bold">
              ● All AI Services Operational
            </span>
            <div className="border-l border-craft-border pl-3">
              <span className="font-semibold text-craft-text">admin@craftlens.gov.in</span>
            </div>
          </div>
        </header>

        <main className="p-6 max-w-7xl mx-auto">{children}</main>
      </body>
    </html>
  );
}

