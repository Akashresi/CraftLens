"use client";

import React, { useState } from "react";
import {
  Users,
  CheckCircle2,
  XCircle,
  ShieldCheck,
  AlertTriangle,
  Cpu,
  Activity,
  FileCheck,
  Building,
  TrendingUp,
} from "lucide-react";

interface VerificationItem {
  id: string;
  artisan_name: string;
  cluster: string;
  craft_type: string;
  pehchan_id: string;
  state: string;
  date: string;
  status: "PENDING" | "APPROVED" | "REJECTED";
}

interface ModerationItem {
  id: string;
  title: string;
  artisan: string;
  materials: string;
  gi_claim: string;
  image_quality_score: number;
  status: "PENDING" | "APPROVED" | "REJECTED";
}

const INITIAL_ARTISANS: VerificationItem[] = [
  {
    id: "art-1",
    artisan_name: "Kuppusamy Karuppiah",
    cluster: "Vilachery Clay Cluster, Madurai",
    craft_type: "Terracotta Sculpture",
    pehchan_id: "PEH-TN-98102",
    state: "Tamil Nadu",
    date: "2026-11-04",
    status: "PENDING",
  },
  {
    id: "art-2",
    artisan_name: "Mangala Bai Maravi",
    cluster: "Dindori Gond Art Cluster",
    craft_type: "Gond Painting",
    pehchan_id: "PEH-MP-41092",
    state: "Madhya Pradesh",
    date: "2026-11-03",
    status: "PENDING",
  },
  {
    id: "art-3",
    artisan_name: "Shabbir Hussain Mir",
    cluster: "Srinagar Papier Mache Guild",
    craft_type: "Kashmir Papier Mache",
    pehchan_id: "PEH-JK-10842",
    state: "Jammu & Kashmir",
    date: "2026-11-02",
    status: "PENDING",
  },
];

const INITIAL_MODERATION: ModerationItem[] = [
  {
    id: "mod-1",
    title: "Hand-turned Earthen Clay Water Jug with Natural Terracotta Glaze",
    artisan: "Meenakshi Sundaram",
    materials: "River silt, husk, organic natural dyes (Verified: No synthetic chemicals)",
    gi_claim: "GI-TN-412 (Vilachery)",
    image_quality_score: 96,
    status: "PENDING",
  },
  {
    id: "mod-2",
    title: "Pure Zari Korvai Temple Border Silk Stole",
    artisan: "Kanchipuram Society",
    materials: "100% Mulberry Silk, Tested Silver Zari",
    gi_claim: "GI-TN-001 (Kanchipuram Silk)",
    image_quality_score: 98,
    status: "PENDING",
  },
];

export default function AdminDashboardPage() {
  const [activeTab, setActiveTab] = useState<"verifications" | "moderation" | "ai_health" | "compliance">("verifications");
  const [artisans, setArtisans] = useState<VerificationItem[]>(INITIAL_ARTISANS);
  const [products, setProducts] = useState<ModerationItem[]>(INITIAL_MODERATION);

  const handleVerifyArtisan = (id: string, newStatus: "APPROVED" | "REJECTED") => {
    setArtisans((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: newStatus } : a))
    );
  };

  const handleModerateProduct = (id: string, newStatus: "APPROVED" | "REJECTED") => {
    setProducts((prev) =>
      prev.map((p) => (p.id === id ? { ...p, status: newStatus } : p))
    );
  };

  return (
    <div className="space-y-8">
      {/* Top Banner & Quick Metrics */}
      <div>
        <h1 className="text-2xl font-extrabold text-craft-text tracking-tight">
          CraftLens Governance & Verification Portal
        </h1>
        <p className="text-xs text-craft-muted mt-1">
          Monitor artisan authenticity, ensure non-exploitation, moderate AI descriptions, and track platform metrics.
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-craft-surface border border-craft-border rounded-xl p-4 shadow-subtle">
          <div className="flex justify-between items-center text-craft-muted mb-1">
            <span className="text-xs">Registered Artisans</span>
            <Users className="w-4 h-4 text-craft-primary" />
          </div>
          <p className="text-2xl font-bold text-craft-text">4,820</p>
          <span className="text-[10px] text-craft-success font-semibold">Across 18 States</span>
        </div>

        <div className="bg-craft-surface border border-craft-border rounded-xl p-4 shadow-subtle">
          <div className="flex justify-between items-center text-craft-muted mb-1">
            <span className="text-xs">Pending Approvals</span>
            <AlertTriangle className="w-4 h-4 text-craft-warning" />
          </div>
          <p className="text-2xl font-bold text-craft-warning">
            {artisans.filter((a) => a.status === "PENDING").length}
          </p>
          <span className="text-[10px] text-craft-muted">Requires GI audit</span>
        </div>

        <div className="bg-craft-surface border border-craft-border rounded-xl p-4 shadow-subtle">
          <div className="flex justify-between items-center text-craft-muted mb-1">
            <span className="text-xs">Direct Artisan Payouts</span>
            <TrendingUp className="w-4 h-4 text-craft-secondary" />
          </div>
          <p className="text-2xl font-bold text-craft-secondary">₹1.84 Cr</p>
          <span className="text-[10px] text-craft-success font-semibold">100% Living Wage Verified</span>
        </div>

        <div className="bg-craft-surface border border-craft-border rounded-xl p-4 shadow-subtle">
          <div className="flex justify-between items-center text-craft-muted mb-1">
            <span className="text-xs">AI Jobs Completed</span>
            <Cpu className="w-4 h-4 text-craft-primary" />
          </div>
          <p className="text-2xl font-bold text-craft-text">48,920</p>
          <span className="text-[10px] text-craft-muted">Studio + Multilingual Voice</span>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-craft-border text-xs font-semibold space-x-6">
        <button
          onClick={() => setActiveTab("verifications")}
          className={`pb-3 transition-colors ${
            activeTab === "verifications"
              ? "border-b-2 border-craft-primary text-craft-primary font-bold"
              : "text-craft-muted hover:text-craft-text"
          }`}
        >
          Artisan Verifications ({artisans.filter((a) => a.status === "PENDING").length})
        </button>
        <button
          onClick={() => setActiveTab("moderation")}
          className={`pb-3 transition-colors ${
            activeTab === "moderation"
              ? "border-b-2 border-craft-primary text-craft-primary font-bold"
              : "text-craft-muted hover:text-craft-text"
          }`}
        >
          Catalog Moderation ({products.filter((p) => p.status === "PENDING").length})
        </button>
        <button
          onClick={() => setActiveTab("ai_health")}
          className={`pb-3 transition-colors ${
            activeTab === "ai_health"
              ? "border-b-2 border-craft-primary text-craft-primary font-bold"
              : "text-craft-muted hover:text-craft-text"
          }`}
        >
          AI Pipeline & Services Health
        </button>
        <button
          onClick={() => setActiveTab("compliance")}
          className={`pb-3 transition-colors ${
            activeTab === "compliance"
              ? "border-b-2 border-craft-primary text-craft-primary font-bold"
              : "text-craft-muted hover:text-craft-text"
          }`}
        >
          DPDP Act 2023 Consent Logs
        </button>
      </div>

      {/* Tab 1: Artisan Verifications */}
      {activeTab === "verifications" && (
        <div className="bg-craft-surface border border-craft-border rounded-xl overflow-hidden shadow-subtle">
          <div className="p-4 bg-craft-background/50 border-b border-craft-border flex justify-between items-center">
            <h3 className="font-bold text-sm text-craft-text">Pending Artisan Cluster Onboarding</h3>
            <span className="text-xs text-craft-muted">Validating Ministry Pehchan IDs & GI Registrations</span>
          </div>

          <div className="divide-y divide-craft-border">
            {artisans.map((artisan) => (
              <div key={artisan.id} className="p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-sm text-craft-text">{artisan.artisan_name}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-craft-background text-craft-primary border border-craft-border">
                      {artisan.state}
                    </span>
                    <span className="text-xs text-craft-muted font-mono">{artisan.pehchan_id}</span>
                  </div>
                  <p className="text-xs text-craft-muted">
                    {artisan.craft_type} • <span className="text-craft-text font-medium">{artisan.cluster}</span>
                  </p>
                  <span className="text-[10px] text-craft-muted block">Applied on: {artisan.date}</span>
                </div>

                <div className="flex items-center space-x-2">
                  {artisan.status === "PENDING" ? (
                    <>
                      <button
                        onClick={() => handleVerifyArtisan(artisan.id, "APPROVED")}
                        className="px-3 py-1.5 rounded-lg bg-craft-success text-white text-xs font-semibold hover:brightness-110 flex items-center space-x-1"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Approve & Issue Key</span>
                      </button>
                      <button
                        onClick={() => handleVerifyArtisan(artisan.id, "REJECTED")}
                        className="px-3 py-1.5 rounded-lg bg-craft-surface border border-craft-border text-craft-error text-xs font-semibold hover:bg-craft-surface-hover flex items-center space-x-1"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                        <span>Reject</span>
                      </button>
                    </>
                  ) : (
                    <span
                      className={`px-3 py-1 rounded text-xs font-bold ${
                        artisan.status === "APPROVED"
                          ? "bg-craft-success/10 text-craft-success"
                          : "bg-craft-error/10 text-craft-error"
                      }`}
                    >
                      {artisan.status}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Catalog Moderation */}
      {activeTab === "moderation" && (
        <div className="bg-craft-surface border border-craft-border rounded-xl overflow-hidden shadow-subtle">
          <div className="p-4 bg-craft-background/50 border-b border-craft-border flex justify-between items-center">
            <h3 className="font-bold text-sm text-craft-text">AI Catalog Integrity Check</h3>
            <span className="text-xs text-craft-muted">Enforcing Truthful AI (No synthetic claims or fake GI tags)</span>
          </div>

          <div className="divide-y divide-craft-border">
            {products.map((p) => (
              <div key={p.id} className="p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-bold text-sm text-craft-text">{p.title}</h4>
                    <p className="text-xs text-craft-muted mt-0.5">By {p.artisan}</p>
                  </div>
                  <span className="px-2 py-1 rounded bg-craft-background border border-craft-border text-xs font-semibold text-craft-primary">
                    Quality: {p.image_quality_score}/100
                  </span>
                </div>

                <div className="bg-craft-background p-3 rounded-lg border border-craft-border text-xs space-y-1">
                  <div>
                    <span className="font-semibold text-craft-muted">Extracted Materials: </span>
                    <span className="text-craft-text">{p.materials}</span>
                  </div>
                  <div>
                    <span className="font-semibold text-craft-muted">Claimed GI Provenance: </span>
                    <span className="text-craft-success font-bold">{p.gi_claim}</span>
                  </div>
                </div>

                <div className="flex justify-end space-x-2 pt-1">
                  {p.status === "PENDING" ? (
                    <>
                      <button
                        onClick={() => handleModerateProduct(p.id, "APPROVED")}
                        className="px-3 py-1.5 rounded-lg bg-craft-primary text-white text-xs font-semibold hover:bg-craft-primary-dark"
                      >
                        Publish to Marketplace
                      </button>
                      <button
                        onClick={() => handleModerateProduct(p.id, "REJECTED")}
                        className="px-3 py-1.5 rounded-lg border border-craft-border text-craft-error text-xs font-semibold"
                      >
                        Reject & Request Edit
                      </button>
                    </>
                  ) : (
                    <span className="text-xs font-bold text-craft-primary">{p.status}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: AI Health */}
      {activeTab === "ai_health" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-craft-surface border border-craft-border rounded-xl p-5 shadow-subtle space-y-4">
            <h3 className="font-bold text-sm text-craft-text border-b border-craft-border pb-2 flex items-center space-x-2">
              <Cpu className="w-4 h-4 text-craft-primary" />
              <span>Vision & Image Services</span>
            </h3>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-craft-muted">rembg / GrabCut Engine</span>
                <span className="text-craft-success font-bold">Operational (0.8s avg)</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-craft-muted">OpenCV Laplacian Blur Detection</span>
                <span className="text-craft-success font-bold">Active (&lt;15ms)</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-craft-muted">CLAHE Lighting Correction</span>
                <span className="text-craft-success font-bold">Active (&lt;40ms)</span>
              </div>
            </div>
          </div>

          <div className="bg-craft-surface border border-craft-border rounded-xl p-5 shadow-subtle space-y-4">
            <h3 className="font-bold text-sm text-craft-text border-b border-craft-border pb-2 flex items-center space-x-2">
              <Activity className="w-4 h-4 text-craft-secondary" />
              <span>Voice AI & Translation</span>
            </h3>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-craft-muted">Bhashini / Whisper Indic ASR</span>
                <span className="text-craft-success font-bold">Connected (Tamil, Hindi, Telugu, Kannada, Malayalam)</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-craft-muted">Gemini Catalog Extraction</span>
                <span className="text-craft-success font-bold">99.8% Availability</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-craft-muted">IndicTrans2 Neural Engine</span>
                <span className="text-craft-success font-bold">Active</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Compliance */}
      {activeTab === "compliance" && (
        <div className="bg-craft-surface border border-craft-border rounded-xl p-6 shadow-subtle space-y-4">
          <div className="flex items-center space-x-2 border-b border-craft-border pb-3">
            <FileCheck className="w-4 h-4 text-craft-primary" />
            <h3 className="font-bold text-sm text-craft-text">Digital Personal Data Protection (DPDP) Act 2023 Audit Log</h3>
          </div>
          <p className="text-xs text-craft-muted">
            All voice recordings, Aadhaar hashes, and artisan personal data are stored under informed consent and end-to-end encryption.
          </p>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border border-craft-border">
              <thead className="bg-craft-background text-craft-muted uppercase text-[10px]">
                <tr>
                  <th className="p-2.5 border-b border-craft-border">Timestamp</th>
                  <th className="p-2.5 border-b border-craft-border">User / Artisan</th>
                  <th className="p-2.5 border-b border-craft-border">Consent Purpose</th>
                  <th className="p-2.5 border-b border-craft-border">Status</th>
                  <th className="p-2.5 border-b border-craft-border">Signature SHA-256</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-craft-border font-mono text-[11px]">
                <tr>
                  <td className="p-2.5">2026-11-04 18:22:10</td>
                  <td>Meenakshi Sundaram</td>
                  <td className="font-sans">Voice Cataloging & Audio Training Consent</td>
                  <td className="text-craft-success font-sans font-bold">GRANTED</td>
                  <td className="text-craft-muted truncate max-w-[120px]">9f83ac27...</td>
                </tr>
                <tr>
                  <td className="p-2.5">2026-11-04 17:15:02</td>
                  <td>Ramanathan Weavers</td>
                  <td className="font-sans">Direct Payout Bank Account Verification</td>
                  <td className="text-craft-success font-sans font-bold">GRANTED</td>
                  <td className="text-craft-muted truncate max-w-[120px]">3b72c9a1...</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
