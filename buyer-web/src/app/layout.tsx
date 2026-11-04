import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";
import { AuthProvider } from "@/context/AuthContext";

export const metadata: Metadata = {
  title: "CraftLens 2.0 | Empowering Artisans with AI & Direct Global Trade",
  description:
    "AI-powered digital business manager and global marketplace platform for marginalized artisans, traditional craftspeople, and craft cooperatives.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-craft-background text-craft-text font-sans antialiased">
        <AuthProvider>
          <Navbar />
          <main className="flex-1">{children}</main>
          <footer className="bg-craft-surface border-t border-craft-border py-12 mt-16 text-sm text-craft-muted">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-4 gap-8">
              <div>
                <h4 className="text-base font-bold text-craft-primary mb-2">CraftLens</h4>
                <p className="text-xs leading-relaxed">
                  Bridging traditional Indian artisans with global conscious buyers through AI cataloging, transparent pricing, and verifiable GI heritage.
                </p>
                <div className="mt-4 flex space-x-2 text-xs">
                  <span className="px-2 py-1 bg-craft-background rounded border border-craft-border text-craft-primary font-medium">
                    MoSJE / SIH26090
                  </span>
                  <span className="px-2 py-1 bg-craft-background rounded border border-craft-border text-craft-secondary font-medium">
                    DPDP Act 2023
                  </span>
                </div>
              </div>
              <div>
                <h5 className="font-semibold text-craft-text mb-3">Marketplace</h5>
                <ul className="space-y-2 text-xs">
                  <li><a href="/catalog" className="hover:text-craft-primary">Discover Crafts</a></li>
                  <li><a href="/origins" className="hover:text-craft-primary">Geographical Indications</a></li>
                  <li><a href="/b2b" className="hover:text-craft-primary">Wholesale & Bulk Orders</a></li>
                  <li><a href="/cart" className="hover:text-craft-primary">Shopping Bag</a></li>
                </ul>
              </div>
              <div>
                <h5 className="font-semibold text-craft-text mb-3">For Artisans</h5>
                <ul className="space-y-2 text-xs">
                  <li><a href="/artisan/studio" className="hover:text-craft-primary">AI Photography Studio</a></li>
                  <li><a href="/artisan/dashboard" className="hover:text-craft-primary">Artisan Business Hub</a></li>
                  <li><a href="/artisan/pricing" className="hover:text-craft-primary">Fair Living Wage Calculator</a></li>
                  <li><a href="/register" className="hover:text-craft-primary">Onboard as Artisan</a></li>
                </ul>
              </div>
              <div>
                <h5 className="font-semibold text-craft-text mb-3">Integrity & Heritage</h5>
                <p className="text-xs leading-relaxed mb-3">
                  Every product carries a tamper-evident cryptographic QR provenance seal linking directly to the verified maker and cluster.
                </p>
                <p className="text-[11px] text-craft-muted">
                  © 2026 CraftLens Platform. All rights reserved.
                </p>
              </div>
            </div>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
