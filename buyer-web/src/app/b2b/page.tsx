"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Building2, FileText, CheckCircle2, Send, Clock, ShieldCheck, ArrowRight } from "lucide-react";
import { api } from "@/lib/api";

const DEMO_QUOTATIONS = [
  {
    id: "q-101",
    rfq_title: "100 Units Vilachery Terracotta Ayyanar Sculptures",
    artisan_coop: "Vilachery Rural Pottery Cooperative Society",
    cluster: "Madurai, Tamil Nadu",
    unit_price: 1100,
    total_amount: 110000,
    lead_time_days: 28,
    sample_available: true,
    sample_cost: 1200,
    milestones: "30% Material Advance • 40% Kiln Dispatch • 30% Final Delivery",
    gi_certified: true,
    status: "ACTIVE",
  },
  {
    id: "q-102",
    rfq_title: "50 Bastar Tribal Lost-Wax Dokra Bell Metal Statues",
    artisan_coop: "Kondagaon Bastar Shilp Samiti",
    cluster: "Bastar, Chhattisgarh",
    unit_price: 2400,
    total_amount: 120000,
    lead_time_days: 35,
    sample_available: true,
    sample_cost: 2500,
    milestones: "40% Raw Wax/Brass Advance • 30% Casting • 30% Delivery",
    gi_certified: true,
    status: "ACTIVE",
  },
];

export default function B2BWholesalePage() {
  const [activeTab, setActiveTab] = useState<"submit" | "quotes">("submit");
  const [rfqSubmitted, setRfqSubmitted] = useState(false);

  const [rfqForm, setRfqForm] = useState({
    title: "Bulk Festive Terracotta Diya & Sculptures",
    category: "Pottery & Clay Art",
    quantity: 100,
    target_unit_price: 1000,
    required_by_date: "2026-11-20",
    specifications: "Export quality kiln-fired terracotta with eco-friendly straw packaging and individual artisan bio cards.",
    sample_required: true,
  });

  const [acceptedQuote, setAcceptedQuote] = useState<string | null>(null);

  const handleRfqSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/b2b/rfq", rfqForm);
    } catch (e) {
      // Demo fallback
    }
    setRfqSubmitted(true);
    setTimeout(() => {
      setActiveTab("quotes");
      setRfqSubmitted(false);
    }, 2000);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-craft-background border border-craft-border text-xs font-bold text-craft-secondary mb-2">
            <Building2 className="w-3.5 h-3.5" />
            <span>B2B Wholesale & Institutional Sourcing</span>
          </div>
          <h1 className="text-3xl font-extrabold text-craft-text tracking-tight">
            Direct Cluster Sourcing for Retailers & Exporters
          </h1>
          <p className="text-xs sm:text-sm text-craft-muted mt-1">
            Source bulk handmade goods directly from verified artisan cooperatives with transparent milestone schedules and GI authenticity.
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex rounded-lg border border-craft-border bg-craft-surface p-1 shadow-subtle text-xs font-semibold">
          <button
            onClick={() => setActiveTab("submit")}
            className={`px-4 py-2 rounded-md transition-colors ${
              activeTab === "submit"
                ? "bg-craft-primary text-white"
                : "text-craft-muted hover:text-craft-text"
            }`}
          >
            Submit New RFQ
          </button>
          <button
            onClick={() => setActiveTab("quotes")}
            className={`px-4 py-2 rounded-md transition-colors ${
              activeTab === "quotes"
                ? "bg-craft-primary text-white"
                : "text-craft-muted hover:text-craft-text"
            }`}
          >
            Artisan Quotes ({DEMO_QUOTATIONS.length})
          </button>
        </div>
      </div>

      {activeTab === "submit" ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* RFQ Form */}
          <div className="lg:col-span-7 bg-craft-surface border border-craft-border rounded-xl p-6 shadow-subtle space-y-5">
            <h2 className="font-bold text-base text-craft-text border-b border-craft-border pb-3 flex items-center space-x-2">
              <FileText className="w-4 h-4 text-craft-primary" />
              <span>Create Request for Quotation (RFQ)</span>
            </h2>

            {rfqSubmitted ? (
              <div className="p-6 bg-craft-success/10 border border-craft-success/30 rounded-lg text-center space-y-2">
                <CheckCircle2 className="w-8 h-8 text-craft-success mx-auto" />
                <h3 className="font-bold text-sm text-craft-success">RFQ Dispatched to Clusters!</h3>
                <p className="text-xs text-craft-muted">
                  Artisan cooperatives in Madurai, Kanchipuram, and Bastar have been notified. Switching to quotes view...
                </p>
              </div>
            ) : (
              <form onSubmit={handleRfqSubmit} className="space-y-4">
                <div>
                  <label className="text-xs font-semibold text-craft-text block mb-1">
                    Project / Order Title
                  </label>
                  <input
                    type="text"
                    required
                    value={rfqForm.title}
                    onChange={(e) => setRfqForm({ ...rfqForm, title: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-craft-background border border-craft-border text-xs focus:outline-none focus:border-craft-primary"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-semibold text-craft-text block mb-1">Craft Category</label>
                    <select
                      value={rfqForm.category}
                      onChange={(e) => setRfqForm({ ...rfqForm, category: e.target.value })}
                      className="w-full px-3 py-2 rounded-lg bg-craft-background border border-craft-border text-xs focus:outline-none focus:border-craft-primary"
                    >
                      <option value="Pottery & Clay Art">Pottery & Clay Art</option>
                      <option value="Handloom & Silk Weaves">Handloom & Silk Weaves</option>
                      <option value="Metal & Lost-Wax Brass">Metal & Lost-Wax Brass</option>
                      <option value="Tanjore Gold Art">Tanjore Gold Art</option>
                      <option value="Jaipur Blue Pottery">Jaipur Blue Pottery</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-craft-text block mb-1">
                      Required Quantity (Min 25 units)
                    </label>
                    <input
                      type="number"
                      min="25"
                      required
                      value={rfqForm.quantity}
                      onChange={(e) => setRfqForm({ ...rfqForm, quantity: Number(e.target.value) })}
                      className="w-full px-3 py-2 rounded-lg bg-craft-background border border-craft-border text-xs focus:outline-none focus:border-craft-primary"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-semibold text-craft-text block mb-1">
                      Target Unit Price (₹)
                    </label>
                    <input
                      type="number"
                      required
                      value={rfqForm.target_unit_price}
                      onChange={(e) => setRfqForm({ ...rfqForm, target_unit_price: Number(e.target.value) })}
                      className="w-full px-3 py-2 rounded-lg bg-craft-background border border-craft-border text-xs focus:outline-none focus:border-craft-primary"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-craft-text block mb-1">
                      Required Delivery Date
                    </label>
                    <input
                      type="date"
                      required
                      value={rfqForm.required_by_date}
                      onChange={(e) => setRfqForm({ ...rfqForm, required_by_date: e.target.value })}
                      className="w-full px-3 py-2 rounded-lg bg-craft-background border border-craft-border text-xs focus:outline-none focus:border-craft-primary"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-xs font-semibold text-craft-text block mb-1">
                    Custom Specifications & Packaging Requirements
                  </label>
                  <textarea
                    rows={3}
                    value={rfqForm.specifications}
                    onChange={(e) => setRfqForm({ ...rfqForm, specifications: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg bg-craft-background border border-craft-border text-xs focus:outline-none focus:border-craft-primary"
                  />
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="sample"
                    checked={rfqForm.sample_required}
                    onChange={(e) => setRfqForm({ ...rfqForm, sample_required: e.target.checked })}
                    className="rounded text-craft-primary"
                  />
                  <label htmlFor="sample" className="text-xs text-craft-text font-medium">
                    Request a physical pre-production sample before full batch production
                  </label>
                </div>

                <button
                  type="submit"
                  className="w-full py-3 rounded-lg bg-craft-primary text-white text-xs font-bold hover:bg-craft-primary-dark transition-colors shadow-subtle flex items-center justify-center space-x-2"
                >
                  <Send className="w-4 h-4" />
                  <span>Broadcast RFQ to Artisan Cooperatives</span>
                </button>
              </form>
            )}
          </div>

          {/* Sourcing Benefits */}
          <div className="lg:col-span-5 bg-craft-surface border border-craft-border rounded-xl p-6 shadow-subtle space-y-5">
            <h3 className="font-bold text-sm text-craft-text pb-2 border-b border-craft-border">
              Why Source on CraftLens B2B?
            </h3>

            <div className="space-y-4 text-xs">
              <div className="flex space-x-3">
                <div className="w-8 h-8 rounded-lg bg-craft-background flex items-center justify-center text-craft-primary flex-shrink-0 border border-craft-border">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="font-bold text-craft-text">Verified Cooperative Origins</h4>
                  <p className="text-craft-muted mt-0.5">
                    Connect directly with registered Weaver Societies and Craft SHGs without commercial markups.
                  </p>
                </div>
              </div>

              <div className="flex space-x-3">
                <div className="w-8 h-8 rounded-lg bg-craft-background flex items-center justify-center text-craft-secondary flex-shrink-0 border border-craft-border">
                  <Clock className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="font-bold text-craft-text">Protected Escrow Milestones</h4>
                  <p className="text-craft-muted mt-0.5">
                    Payments are held safely and released in tranches: Advance for raw materials, Inspection upon dispatch, and Final delivery.
                  </p>
                </div>
              </div>

              <div className="flex space-x-3">
                <div className="w-8 h-8 rounded-lg bg-craft-background flex items-center justify-center text-craft-success flex-shrink-0 border border-craft-border">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="font-bold text-craft-text">Authenticity Provenance Guarantee</h4>
                  <p className="text-craft-muted mt-0.5">
                    Each bulk carton and unit comes with a verifiable cryptographic QR seal for export clearance and consumer trust.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Quotes View */
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {DEMO_QUOTATIONS.map((q) => (
              <div
                key={q.id}
                className="bg-craft-surface border border-craft-border rounded-xl p-6 shadow-subtle space-y-4 flex flex-col justify-between"
              >
                <div>
                  <div className="flex justify-between items-start">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-craft-secondary">
                      Quote #{q.id}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-craft-success/10 text-craft-success border border-craft-success/20">
                      Co-op Verified
                    </span>
                  </div>

                  <h3 className="font-bold text-base text-craft-text mt-1">{q.rfq_title}</h3>
                  <p className="text-xs font-semibold text-craft-primary mt-0.5">{q.artisan_coop}</p>
                  <p className="text-[11px] text-craft-muted">{q.cluster}</p>

                  <div className="grid grid-cols-2 gap-3 mt-4 p-3 bg-craft-background rounded-lg border border-craft-border text-xs">
                    <div>
                      <span className="text-craft-muted block text-[10px]">Unit Price</span>
                      <span className="font-bold text-craft-text">₹{q.unit_price}</span>
                    </div>
                    <div>
                      <span className="text-craft-muted block text-[10px]">Total Order</span>
                      <span className="font-extrabold text-craft-primary">₹{q.total_amount}</span>
                    </div>
                    <div>
                      <span className="text-craft-muted block text-[10px]">Production Lead Time</span>
                      <span className="font-semibold text-craft-text">{q.lead_time_days} Days</span>
                    </div>
                    <div>
                      <span className="text-craft-muted block text-[10px]">Sample Cost</span>
                      <span className="font-semibold text-craft-text">₹{q.sample_cost}</span>
                    </div>
                  </div>

                  <div className="mt-3 text-[11px] text-craft-muted">
                    <span className="font-semibold text-craft-text block">Milestone Schedule:</span>
                    <p>{q.milestones}</p>
                  </div>
                </div>

                <div className="pt-4 border-t border-craft-border">
                  {acceptedQuote === q.id ? (
                    <div className="p-3 bg-craft-success/10 border border-craft-success/30 rounded-lg text-center text-xs font-bold text-craft-success">
                      ✓ Purchase Order Generated! Escrow Active.
                    </div>
                  ) : (
                    <button
                      onClick={() => setAcceptedQuote(q.id)}
                      className="w-full py-2.5 rounded-lg bg-craft-primary text-white text-xs font-semibold hover:bg-craft-primary-dark transition-colors flex items-center justify-center space-x-1.5"
                    >
                      <span>Accept & Generate Purchase Order</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

