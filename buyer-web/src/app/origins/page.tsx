import type { Metadata } from "next";
import Link from "next/link";
import { ShieldCheck, MapPin, Award } from "lucide-react";

export const metadata: Metadata = {
  title: "Geographical Indication (GI) Heritage Origins | CraftLens 2.0",
  description:
    "Explore verified Indian craft clusters backed by Ed25519 cryptographic QR provenance and GI Registry authentication.",
};

const CLUSTERS = [
  { name: "Kanchipuram Handloom Silk", state: "Tamil Nadu", gi: "GI-TN-001", craft: "Korvai Mulberry Silk & Zari" },
  { name: "Vilachery Terracotta Crafts", state: "Tamil Nadu", gi: "GI-TN-412", craft: "Vaigai Alluvial Clay Sculpting" },
  { name: "Channapatna Lacquerware Toys", state: "Karnataka", gi: "GI-KA-002", craft: "Ivory Wood & Vegetable Lac" },
  { name: "Bastar Dhokra Metal Craft", state: "Chhattisgarh", gi: "GI-CG-083", craft: "Lost-Wax Brass Casting" },
  { name: "Madhubani Mithila Paintings", state: "Bihar", gi: "GI-BR-014", craft: "Kachni & Bharni Mineral Pigments" },
  { name: "Banarasi Brocades & Sarees", state: "Uttar Pradesh", gi: "GI-UP-009", craft: "Handloom Silk & Real Zari" },
];

export default function HeritageOriginsPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <div className="space-y-2">
        <span className="inline-flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-craft-primary">
          <ShieldCheck className="w-4 h-4" />
          <span>Ed25519 Signed Provenance</span>
        </span>
        <h1 className="text-3xl font-extrabold text-craft-text">
          Verified Craft Clusters &amp; GI Origins
        </h1>
        <p className="text-sm text-craft-muted max-w-2xl">
          Every authentic CraftLens listing carries a digitally signed QR provenance certificate anchored to the artisan&apos;s verified studio and regional GI registry.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {CLUSTERS.map((c) => (
          <div
            key={c.gi}
            className="bg-craft-surface border border-craft-border rounded-xl p-5 shadow-subtle space-y-3"
          >
            <div className="flex items-center justify-between">
              <span className="px-2.5 py-1 rounded-full bg-craft-background border border-craft-border text-xs font-bold text-craft-primary flex items-center space-x-1">
                <Award className="w-3.5 h-3.5" />
                <span>{c.gi}</span>
              </span>
              <span className="text-xs text-craft-muted flex items-center space-x-1">
                <MapPin className="w-3.5 h-3.5" />
                <span>{c.state}</span>
              </span>
            </div>
            <h2 className="text-lg font-bold text-craft-text">{c.name}</h2>
            <p className="text-xs text-craft-muted">{c.craft}</p>
            <Link
              href="/catalog"
              className="inline-block text-xs font-semibold text-craft-primary hover:underline pt-1"
            >
              Browse verified crafts &rarr;
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}

