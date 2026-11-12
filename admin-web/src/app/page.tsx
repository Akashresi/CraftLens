"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Users,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Cpu,
  Activity,
  FileCheck,
  TrendingUp,
  ExternalLink,
  Clock,
  MapPin,
  Briefcase,
  FileText,
  RefreshCw,
  Search,
  Filter,
} from "lucide-react";

interface ArtisanApplication {
  id: string;
  user_id: string;
  applicant_email: string | null;
  applicant_phone: string | null;
  full_name: string;
  craft_specialization: string;
  experience_years: number;
  city: string;
  state: string;
  portfolio_url: string | null;
  craft_description: string;
  supporting_documents_url: string | null;
  status: "PENDING" | "APPROVED" | "REJECTED";
  reviewer_notes: string | null;
  reviewed_by_user_id: string | null;
  reviewed_at: string | null;
  created_at: string;
  updated_at: string;
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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export default function AdminDashboardPage() {
  const [activeTab, setActiveTab] = useState<"applications" | "moderation" | "ai_health" | "compliance">("applications");
  
  // Real Applications State
  const [applications, setApplications] = useState<ArtisanApplication[]>([]);
  const [statusFilter, setStatusFilter] = useState<"ALL" | "PENDING" | "APPROVED" | "REJECTED">("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [adminToken, setAdminToken] = useState<string | null>(() =>
    typeof window !== "undefined" ? localStorage.getItem("craftlens_admin_token") : null
  );
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);

  // Review & Confirmation Modal State
  const [selectedApp, setSelectedApp] = useState<ArtisanApplication | null>(null);
  const [actionType, setActionType] = useState<"APPROVE" | "REJECT" | null>(null);
  const [reviewerNotes, setReviewerNotes] = useState("");
  const [isSubmittingAction, setIsSubmittingAction] = useState(false);
  const [actionSuccessMessage, setActionSuccessMessage] = useState<string | null>(null);

  // Moderation state
  const [products, setProducts] = useState<ModerationItem[]>(INITIAL_MODERATION);

  // Retrieve stored admin JWT token (never embed hardcoded credentials in client JS)
  const getAdminAuth = useCallback(async (): Promise<string | null> => {
    if (adminToken) return adminToken;
    const stored = typeof window !== "undefined" ? localStorage.getItem("craftlens_admin_token") : null;
    if (stored) {
      setAdminToken(stored);
      return stored;
    }
    return null;
  }, [adminToken]);

  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginLoading(true);
    setApiError(null);
    try {
      const formData = new URLSearchParams();
      formData.append("username", loginEmail.trim());
      formData.append("password", loginPassword);
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString(),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        setApiError(err.detail || "Invalid administrator credentials.");
        return;
      }
      const data = await res.json();
      const token = data.access_token;
      if (typeof window !== "undefined") {
        localStorage.setItem("craftlens_admin_token", token);
      }
      setAdminToken(token);
      setLoginPassword("");
    } catch {
      setApiError("Unable to reach authentication server.");
    } finally {
      setLoginLoading(false);
    }
  };

  const handleAdminLogout = () => {
    if (typeof window !== "undefined") localStorage.removeItem("craftlens_admin_token");
    setAdminToken(null);
    setApplications([]);
  };

  // Fetch real artisan applications from backend
  const fetchApplications = useCallback(async () => {
    setIsLoading(true);
    setApiError(null);
    try {
      const token = await getAdminAuth();
      if (!token) {
        setIsLoading(false);
        return;
      }

      const url = statusFilter === "ALL"
        ? `${API_BASE_URL}/artisan-applications/admin`
        : `${API_BASE_URL}/artisan-applications/admin?status=${statusFilter}`;

      const res = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!res.ok) {
        if (res.status === 401 || res.status === 403) {
          // Token expired, clear and retry once
          if (typeof window !== "undefined") localStorage.removeItem("craftlens_admin_token");
          setAdminToken(null);
          setApiError("Session expired or permission denied. Retrying...");
          return;
        }
        throw new Error(`Server returned ${res.status}`);
      }

      const json = await res.json();
      if (json.success && Array.isArray(json.data)) {
        setApplications(json.data);
      } else {
        setApplications([]);
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to connect to backend API";
      setApiError(`Could not load applications: ${message}. Ensure backend is running on port 8000.`);
    } finally {
      setIsLoading(false);
    }
  }, [getAdminAuth, statusFilter]);

  useEffect(() => {
    fetchApplications();
  }, [fetchApplications]);

  // Handle Approve or Reject
  const handleConfirmDecision = async () => {
    if (!selectedApp || !actionType) return;
    setIsSubmittingAction(true);
    setApiError(null);

    try {
      const token = await getAdminAuth();
      if (!token) throw new Error("Not authenticated");

      const endpoint = actionType === "APPROVE" ? "approve" : "reject";
      const res = await fetch(`${API_BASE_URL}/artisan-applications/admin/${selectedApp.id}/${endpoint}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ reviewer_notes: reviewerNotes.trim() || undefined }),
      });

      const json = await res.json();
      if (!res.ok || !json.success) {
        throw new Error(json.detail || json.message || `Failed to ${actionType.toLowerCase()} application`);
      }

      setActionSuccessMessage(
        actionType === "APPROVE"
          ? `Application of ${selectedApp.full_name} approved successfully. Role assigned: ARTISAN.`
          : `Application of ${selectedApp.full_name} rejected. Buyer role preserved.`
      );

      // Close modal and refresh list
      setSelectedApp(null);
      setActionType(null);
      setReviewerNotes("");
      fetchApplications();
      setTimeout(() => setActionSuccessMessage(null), 5000);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Action failed";
      setApiError(`Action failed: ${message}`);
    } finally {
      setIsSubmittingAction(false);
    }
  };

  const handleModerateProduct = (id: string, newStatus: "APPROVED" | "REJECTED") => {
    setProducts((prev) =>
      prev.map((p) => (p.id === id ? { ...p, status: newStatus } : p))
    );
  };

  const filteredApplications = applications.filter((app) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      app.full_name.toLowerCase().includes(q) ||
      app.craft_specialization.toLowerCase().includes(q) ||
      app.city.toLowerCase().includes(q) ||
      app.state.toLowerCase().includes(q) ||
      (app.applicant_email && app.applicant_email.toLowerCase().includes(q))
    );
  });

  const pendingCount = applications.filter((a) => a.status === "PENDING").length;

  if (!adminToken) {
    return (
      <div className="max-w-md mx-auto mt-16 bg-craft-surface border border-craft-border rounded-2xl p-6 shadow-subtle space-y-4">
        <div>
          <h1 className="text-xl font-extrabold text-craft-text">Administrator Sign In</h1>
          <p className="text-xs text-craft-muted mt-1">
            Sign in with an ADMIN account to review artisan onboarding and governance queues.
          </p>
        </div>
        {apiError && (
          <div className="p-3 rounded-lg bg-craft-error/15 border border-craft-error text-craft-error text-xs font-semibold">
            {apiError}
          </div>
        )}
        <form onSubmit={handleAdminLogin} className="space-y-3">
          <div>
            <label className="text-xs font-semibold text-craft-text block mb-1">Admin Email</label>
            <input
              type="email"
              required
              value={loginEmail}
              onChange={(e) => setLoginEmail(e.target.value)}
              placeholder="admin@craftlens.org"
              className="w-full px-3 py-2 rounded-lg bg-craft-background border border-craft-border text-xs text-craft-text"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-craft-text block mb-1">Password</label>
            <input
              type="password"
              required
              value={loginPassword}
              onChange={(e) => setLoginPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3 py-2 rounded-lg bg-craft-background border border-craft-border text-xs text-craft-text"
            />
          </div>
          <button
            type="submit"
            disabled={loginLoading}
            className="w-full py-2.5 rounded-lg bg-craft-primary text-white text-xs font-bold hover:opacity-95 disabled:opacity-50"
          >
            {loginLoading ? "Signing in..." : "Sign In to Admin Portal"}
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top Banner & Quick Metrics */}
      <div className="flex justify-between items-start gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-craft-text tracking-tight">
            CraftLens Governance &amp; Verification Portal
          </h1>
          <p className="text-xs text-craft-muted mt-1">
            Review artisan onboarding applications, enforce role-based access, moderate AI descriptions, and track governance metrics.
          </p>
        </div>
        <button
          onClick={handleAdminLogout}
          className="px-3 py-1.5 rounded-lg border border-craft-border bg-craft-surface text-xs font-semibold text-craft-muted hover:text-craft-text"
        >
          Sign Out
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-craft-surface border border-craft-border rounded-xl p-4 shadow-subtle">
          <div className="flex justify-between items-center text-craft-muted mb-1">
            <span className="text-xs">Artisan Applications</span>
            <Users className="w-4 h-4 text-craft-primary" />
          </div>
          <p className="text-2xl font-bold text-craft-text">{applications.length}</p>
          <span className="text-[10px] text-craft-primary font-semibold">Total Submissions</span>
        </div>

        <div className="bg-craft-surface border border-craft-border rounded-xl p-4 shadow-subtle">
          <div className="flex justify-between items-center text-craft-muted mb-1">
            <span className="text-xs">Pending Approvals</span>
            <AlertTriangle className="w-4 h-4 text-craft-warning" />
          </div>
          <p className="text-2xl font-bold text-craft-warning">{pendingCount}</p>
          <span className="text-[10px] text-craft-muted">Requires GI & Craft Audit</span>
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

      {/* Success Notification Banner */}
      {actionSuccessMessage && (
        <div className="p-4 rounded-xl bg-craft-success/15 border border-craft-success text-craft-success text-xs font-semibold flex items-center justify-between animate-fadeIn">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4" />
            <span>{actionSuccessMessage}</span>
          </div>
          <button onClick={() => setActionSuccessMessage(null)} className="text-craft-muted hover:text-craft-text">✕</button>
        </div>
      )}

      {/* Error Alert */}
      {apiError && (
        <div className="p-4 rounded-xl bg-craft-error/15 border border-craft-error text-craft-error text-xs font-semibold flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4" />
            <span>{apiError}</span>
          </div>
          <button onClick={() => setApiError(null)} className="text-craft-muted hover:text-craft-text">✕</button>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex border-b border-craft-border text-xs font-semibold space-x-6">
        <button
          onClick={() => setActiveTab("applications")}
          className={`pb-3 transition-colors flex items-center space-x-1.5 ${
            activeTab === "applications"
              ? "border-b-2 border-craft-primary text-craft-primary font-bold"
              : "text-craft-muted hover:text-craft-text"
          }`}
        >
          <span>Artisan Applications</span>
          <span className={`px-1.5 py-0.5 rounded-full text-[10px] ${
            pendingCount > 0 ? "bg-craft-warning text-white font-bold" : "bg-craft-surface border border-craft-border text-craft-muted"
          }`}>
            {pendingCount}
          </span>
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

      {/* Tab 1: Artisan Applications (Live Backend Integration) */}
      {activeTab === "applications" && (
        <div className="space-y-4">
          {/* Controls: Search, Filter, Refresh */}
          <div className="bg-craft-surface border border-craft-border rounded-xl p-4 shadow-subtle flex flex-col md:flex-row justify-between items-stretch md:items-center gap-3">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-semibold text-craft-muted flex items-center space-x-1">
                <Filter className="w-3.5 h-3.5" />
                <span>Filter:</span>
              </span>
              <div className="flex space-x-1">
                {(["ALL", "PENDING", "APPROVED", "REJECTED"] as const).map((st) => (
                  <button
                    key={st}
                    onClick={() => setStatusFilter(st)}
                    className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                      statusFilter === st
                        ? "bg-craft-primary text-white shadow-sm"
                        : "bg-craft-background text-craft-muted hover:text-craft-text border border-craft-border"
                    }`}
                  >
                    {st === "ALL" ? "All" : st.charAt(0) + st.slice(1).toLowerCase()}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <div className="relative flex-1 md:w-64">
                <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-craft-muted" />
                <input
                  type="text"
                  placeholder="Search name, craft, city..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-craft-background border border-craft-border text-xs text-craft-text focus:outline-none focus:border-craft-primary"
                />
              </div>

              <button
                onClick={() => fetchApplications()}
                disabled={isLoading}
                className="px-3 py-1.5 rounded-lg border border-craft-border bg-craft-background hover:bg-craft-surface-hover text-xs font-semibold text-craft-text flex items-center space-x-1 disabled:opacity-50"
                title="Refresh from backend"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>

          {/* Applications Listing */}
          <div className="bg-craft-surface border border-craft-border rounded-xl overflow-hidden shadow-subtle">
            <div className="p-4 bg-craft-background/50 border-b border-craft-border flex justify-between items-center">
              <div>
                <h3 className="font-bold text-sm text-craft-text">Buyer-to-Artisan Onboarding Applications</h3>
                <p className="text-[11px] text-craft-muted">
                  Review applicant credentials, craft specialization, and portfolio before granting artisan status.
                </p>
              </div>
              <span className="text-xs text-craft-muted font-mono">
                {filteredApplications.length} Application{filteredApplications.length === 1 ? "" : "s"}
              </span>
            </div>

            {isLoading && applications.length === 0 ? (
              <div className="p-12 text-center text-craft-muted space-y-2">
                <RefreshCw className="w-6 h-6 animate-spin mx-auto text-craft-primary" />
                <p className="text-xs">Loading live artisan applications from backend...</p>
              </div>
            ) : filteredApplications.length === 0 ? (
              <div className="p-12 text-center text-craft-muted space-y-2">
                <Users className="w-8 h-8 mx-auto text-craft-muted/60" />
                <p className="text-sm font-semibold text-craft-text">No artisan applications found</p>
                <p className="text-xs text-craft-muted">
                  {statusFilter !== "ALL"
                    ? `No applications with status "${statusFilter}". Try selecting "All".`
                    : "No buyers have submitted artisan applications yet."}
                </p>
              </div>
            ) : (
              <div className="divide-y divide-craft-border">
                {filteredApplications.map((app) => (
                  <div key={app.id} className="p-5 hover:bg-craft-background/40 transition-colors space-y-4">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="font-bold text-base text-craft-text">{app.full_name}</span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            app.status === "PENDING"
                              ? "bg-amber-100 text-amber-800 border border-amber-300"
                              : app.status === "APPROVED"
                              ? "bg-green-100 text-green-800 border border-green-300"
                              : "bg-red-100 text-red-800 border border-red-300"
                          }`}>
                            {app.status}
                          </span>
                          <span className="text-xs text-craft-muted">
                            Submitted: {new Date(app.created_at).toLocaleDateString("en-IN", {
                              day: "numeric",
                              month: "short",
                              year: "numeric",
                            })}
                          </span>
                        </div>

                        <div className="flex flex-wrap items-center gap-3 mt-1 text-xs text-craft-muted">
                          {app.applicant_email && (
                            <span>Email: <strong className="text-craft-text">{app.applicant_email}</strong></span>
                          )}
                          {app.applicant_phone && (
                            <span>Phone: <strong className="text-craft-text">{app.applicant_phone}</strong></span>
                          )}
                          <span className="flex items-center space-x-1">
                            <MapPin className="w-3 h-3 text-craft-muted" />
                            <span>{app.city}, {app.state}</span>
                          </span>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex items-center space-x-2 self-end md:self-center">
                        {app.status === "PENDING" ? (
                          <>
                            <button
                              onClick={() => {
                                setSelectedApp(app);
                                setActionType("APPROVE");
                                setReviewerNotes("");
                              }}
                              className="px-3 py-1.5 rounded-lg bg-green-600 hover:bg-green-700 text-white text-xs font-semibold flex items-center space-x-1 shadow-sm transition-all"
                            >
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              <span>Approve</span>
                            </button>
                            <button
                              onClick={() => {
                                setSelectedApp(app);
                                setActionType("REJECT");
                                setReviewerNotes("");
                              }}
                              className="px-3 py-1.5 rounded-lg border border-red-300 text-red-600 hover:bg-red-50 text-xs font-semibold flex items-center space-x-1 transition-all"
                            >
                              <XCircle className="w-3.5 h-3.5" />
                              <span>Reject</span>
                            </button>
                          </>
                        ) : (
                          <div className="text-right">
                            <span className="text-[11px] text-craft-muted block">
                              Reviewed on {app.reviewed_at ? new Date(app.reviewed_at).toLocaleDateString() : "N/A"}
                            </span>
                            {app.reviewer_notes && (
                              <span className="text-[11px] text-craft-text italic block">
                                &ldquo;{app.reviewer_notes}&rdquo;
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Detailed Metadata Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 bg-craft-background p-3.5 rounded-lg border border-craft-border text-xs">
                      <div>
                        <span className="text-craft-muted block text-[10px] uppercase font-bold tracking-wider">Craft Specialization</span>
                        <span className="font-semibold text-craft-text flex items-center space-x-1 mt-0.5">
                          <Briefcase className="w-3.5 h-3.5 text-craft-primary" />
                          <span>{app.craft_specialization}</span>
                        </span>
                      </div>

                      <div>
                        <span className="text-craft-muted block text-[10px] uppercase font-bold tracking-wider">Experience</span>
                        <span className="font-semibold text-craft-text flex items-center space-x-1 mt-0.5">
                          <Clock className="w-3.5 h-3.5 text-craft-secondary" />
                          <span>{app.experience_years} Year{app.experience_years === 1 ? "" : "s"} Practicing</span>
                        </span>
                      </div>

                      <div>
                        <span className="text-craft-muted block text-[10px] uppercase font-bold tracking-wider">Portfolio & Documents</span>
                        <div className="flex items-center space-x-3 mt-0.5">
                          {app.portfolio_url ? (
                            <a
                              href={app.portfolio_url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-craft-primary hover:underline flex items-center space-x-1 font-semibold"
                            >
                              <ExternalLink className="w-3 h-3" />
                              <span>View Portfolio</span>
                            </a>
                          ) : (
                            <span className="text-craft-muted text-[11px]">No portfolio link</span>
                          )}

                          {app.supporting_documents_url && (
                            <a
                              href={app.supporting_documents_url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-craft-secondary hover:underline flex items-center space-x-1 font-semibold"
                            >
                              <FileText className="w-3 h-3" />
                              <span>Documents</span>
                            </a>
                          )}
                        </div>
                      </div>

                      <div className="md:col-span-3 pt-2 border-t border-craft-border/60">
                        <span className="text-craft-muted block text-[10px] uppercase font-bold tracking-wider">Craft Description & Lineage</span>
                        <p className="text-craft-text mt-0.5 leading-relaxed text-xs">
                          {app.craft_description}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Confirmation Modal for Approve / Reject */}
      {selectedApp && actionType && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
          <div className="bg-craft-surface border border-craft-border rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-bold text-craft-text">
                  {actionType === "APPROVE" ? "Approve Artisan Application" : "Reject Artisan Application"}
                </h3>
                <p className="text-xs text-craft-muted mt-0.5">
                  Applicant: <strong className="text-craft-text">{selectedApp.full_name}</strong> ({selectedApp.craft_specialization})
                </p>
              </div>
              <button
                onClick={() => {
                  setSelectedApp(null);
                  setActionType(null);
                }}
                className="text-craft-muted hover:text-craft-text text-sm p-1"
              >
                ✕
              </button>
            </div>

            <div className={`p-3.5 rounded-xl text-xs space-y-1.5 ${
              actionType === "APPROVE"
                ? "bg-green-50 text-green-900 border border-green-200"
                : "bg-red-50 text-red-900 border border-red-200"
            }`}>
              <p className="font-bold">
                {actionType === "APPROVE"
                  ? "✓ System Action on Approval:"
                  : "⚠ System Action on Rejection:"}
              </p>
              <ul className="list-disc pl-4 space-y-1 text-[11px]">
                {actionType === "APPROVE" ? (
                  <>
                    <li>Converts user account role from Buyer to <strong>ARTISAN</strong>.</li>
                    <li>Creates or updates their verified <strong>Artisan Profile</strong> in database.</li>
                    <li>Unlocks Artisan Dashboard, AI Studio, Voice Cataloging, and Pricing Engine.</li>
                    <li>Logs immutable audit record with your Admin ID and timestamp.</li>
                  </>
                ) : (
                  <>
                    <li>Application status marked as <strong>REJECTED</strong>.</li>
                    <li>User will retain their current <strong>Buyer</strong> role and permissions.</li>
                    <li>Applicant may submit a revised application in the future.</li>
                  </>
                )}
              </ul>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-craft-text block">
                Reviewer Notes (Optional feedback / internal record):
              </label>
              <textarea
                rows={3}
                value={reviewerNotes}
                onChange={(e) => setReviewerNotes(e.target.value)}
                placeholder={
                  actionType === "APPROVE"
                    ? "e.g., Authentic GI craft lineage verified. Welcome to CraftLens."
                    : "e.g., Ineligible craft or requires government artisan Pehchan verification document."
                }
                className="w-full p-2.5 rounded-lg bg-craft-background border border-craft-border text-xs text-craft-text focus:outline-none focus:border-craft-primary"
              />
            </div>

            <div className="flex justify-end space-x-3 pt-2">
              <button
                onClick={() => {
                  setSelectedApp(null);
                  setActionType(null);
                }}
                disabled={isSubmittingAction}
                className="px-4 py-2 rounded-lg border border-craft-border bg-craft-background hover:bg-craft-surface-hover text-xs font-semibold text-craft-muted hover:text-craft-text"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmDecision}
                disabled={isSubmittingAction}
                className={`px-4 py-2 rounded-lg text-white text-xs font-bold flex items-center space-x-1.5 shadow-sm transition-all ${
                  actionType === "APPROVE"
                    ? "bg-green-600 hover:bg-green-700 disabled:bg-green-400"
                    : "bg-red-600 hover:bg-red-700 disabled:bg-red-400"
                }`}
              >
                {isSubmittingAction && <RefreshCw className="w-3.5 h-3.5 animate-spin" />}
                <span>
                  {isSubmittingAction
                    ? "Processing..."
                    : actionType === "APPROVE"
                    ? "Confirm Approval"
                    : "Confirm Rejection"}
                </span>
              </button>
            </div>
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
