"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ShieldCheck,
  ShieldAlert,
  Award,
  MapPin,
  CheckCircle2,
  UserCheck,
  Sparkles,
  ArrowLeft,
  RefreshCw,
} from "lucide-react";
import { api } from "@/lib/api";

interface HeritageStory {
  product_title: string;
  category_name: string;
  primary_material?: string;
  technique?: string;
  craft_origin_name?: string;
  geographical_indication_code?: string;
  artisan_name: string;
  artisan_city?: string;
  artisan_state?: string;
  artisan_experience_years: number;
  artisan_bio?: string;
  verification_level: string;
  batch_code?: string;
  maker_signature_hash?: string;
  signature_ed25519?: string;
  public_key_fingerprint?: string;
  signature_valid: boolean;
  revoked: boolean;
  revoked_reason?: string;
  verified_genuine: boolean;
  scan_count: number;
}

export default function HeritageVerificationPage() {
  const params = useParams();
  const hash = params?.hash as string;

  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [provenance, setProvenance] = useState<HeritageStory | null>(null);

  useEffect(() => {
    if (!hash) {
      setErrorMsg("Missing QR provenance identifier.");
      setLoading(false);
      return;
    }

    api
      .get<HeritageStory>(`/heritage/verify/${encodeURIComponent(hash)}`)
      .then((data) => {
        if (!data || !data.product_title) {
          setErrorMsg("Provenance record could not be verified.");
        } else {
          setProvenance(data);
        }
      })
      .catch((err: unknown) => {
        setErrorMsg(
          err instanceof Error
            ? err.message
            : "This CraftLens QR code is invalid, unregistered, or unreachable."
        );
      })
      .finally(() => setLoading(false));
  }, [hash]);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <Link
        href="/catalog"
        className="inline-flex items-center space-x-1.5 text-xs font-semibold text-craft-muted hover:text-craft-primary"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Return to Marketplace</span>
      </Link>

      {loading ? (
        <div className="bg-craft-surface border border-craft-border rounded-2xl p-12 text-center space-y-3">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-craft-primary" />
          <p className="text-sm font-semibold text-craft-text">
            Verifying Ed25519 Cryptographic Provenance...
          </p>
        </div>
      ) : errorMsg || !provenance ? (
        <div className="bg-craft-surface border-2 border-craft-error rounded-2xl p-8 space-y-3 text-center">
          <ShieldAlert className="w-12 h-12 mx-auto text-craft-error" />
          <h1 className="text-xl font-extrabold text-craft-error">
            Provenance Verification Failed
          </h1>
          <p className="text-xs text-craft-muted max-w-md mx-auto">
            {errorMsg || "No verified heritage signature exists for this code."}
          </p>
        </div>
      ) : (
        <>
          <div
            className={`bg-craft-surface border-2 rounded-2xl p-6 sm:p-8 shadow-card ${
              provenance.verified_genuine ? "border-craft-success" : "border-craft-error"
            }`}
          >
            <div className="flex flex-col sm:flex-row items-center sm:items-start space-y-4 sm:space-y-0 sm:space-x-6 text-center sm:text-left">
              <div
                className={`w-20 h-20 rounded-2xl flex items-center justify-center flex-shrink-0 border ${
                  provenance.verified_genuine
                    ? "bg-craft-success/10 border-craft-success/30 text-craft-success"
                    : "bg-craft-error/10 border-craft-error/30 text-craft-error"
                }`}
              >
                {provenance.verified_genuine ? (
                  <ShieldCheck className="w-12 h-12" />
                ) : (
                  <ShieldAlert className="w-12 h-12" />
                )}
              </div>

              <div className="space-y-1 flex-1">
                <div
                  className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold mb-1 ${
                    provenance.verified_genuine
                      ? "bg-craft-success/10 text-craft-success"
                      : "bg-craft-error/10 text-craft-error"
                  }`}
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>
                    {provenance.revoked
                      ? `REVOKED: ${provenance.revoked_reason || "Tag invalidated"}`
                      : provenance.signature_valid
                        ? "ED25519 CRYPTOGRAPHICALLY VERIFIED ARTISAN HERITAGE"
                        : "SIGNATURE INVALID OR MISSING"}
                  </span>
                </div>
                <h1 className="text-2xl sm:text-3xl font-extrabold text-craft-text">
                  {provenance.product_title}
                </h1>
                <p className="text-xs text-craft-muted">
                  QR Code: <code className="font-mono text-craft-primary">{hash}</code> • Scans:{" "}
                  <strong>{provenance.scan_count}</strong>
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-craft-surface border border-craft-border rounded-xl p-6 space-y-4 shadow-subtle">
              <div className="flex items-center space-x-2 text-craft-primary font-bold text-sm border-b border-craft-border pb-3">
                <UserCheck className="w-4 h-4 text-craft-secondary" />
                <span>Master Artisan &amp; Community</span>
              </div>
              <div className="space-y-3 text-xs">
                <div>
                  <span className="text-craft-muted block">Master Maker</span>
                  <span className="font-bold text-craft-text text-sm">
                    {provenance.artisan_name}
                  </span>
                </div>
                <div>
                  <span className="text-craft-muted block">Verification Level</span>
                  <span className="font-semibold text-craft-text">
                    {provenance.verification_level} ({provenance.artisan_experience_years} yrs exp)
                  </span>
                </div>
                {(provenance.artisan_city || provenance.artisan_state) && (
                  <div className="flex items-center space-x-1 text-craft-text">
                    <MapPin className="w-3.5 h-3.5 text-craft-secondary flex-shrink-0" />
                    <span>
                      {[provenance.artisan_city, provenance.artisan_state, "India"]
                        .filter(Boolean)
                        .join(", ")}
                    </span>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-craft-surface border border-craft-border rounded-xl p-6 space-y-4 shadow-subtle">
              <div className="flex items-center space-x-2 text-craft-primary font-bold text-sm border-b border-craft-border pb-3">
                <Award className="w-4 h-4 text-craft-primary" />
                <span>Craft &amp; Geographical Indication</span>
              </div>
              <div className="space-y-3 text-xs">
                <div>
                  <span className="text-craft-muted block">Category</span>
                  <span className="font-semibold text-craft-text">{provenance.category_name}</span>
                </div>
                {provenance.geographical_indication_code && (
                  <div>
                    <span className="text-craft-muted block">GI Registry Code</span>
                    <span className="font-bold text-craft-primary">
                      {provenance.geographical_indication_code} ({provenance.craft_origin_name})
                    </span>
                  </div>
                )}
                {provenance.technique && (
                  <div>
                    <span className="text-craft-muted block">Technique</span>
                    <span className="font-medium text-craft-text">{provenance.technique}</span>
                  </div>
                )}
                {provenance.primary_material && (
                  <div>
                    <span className="text-craft-muted block">Primary Material</span>
                    <span className="font-medium text-craft-text">
                      {provenance.primary_material}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="bg-craft-surface border border-craft-border rounded-xl p-6 space-y-3 shadow-subtle text-xs">
            <div className="flex items-center space-x-2 text-craft-primary font-bold text-sm border-b border-craft-border pb-2">
              <Sparkles className="w-4 h-4 text-craft-secondary" />
              <span>Ed25519 Digital Signature Proof</span>
            </div>
            {provenance.batch_code && (
              <p className="text-craft-text">
                Batch Code: <strong>{provenance.batch_code}</strong>
              </p>
            )}
            <p className="text-craft-muted">
              Public Key Fingerprint:{" "}
              <code className="font-mono text-craft-primary">
                {provenance.public_key_fingerprint || "N/A"}
              </code>
            </p>
            <p className="font-mono bg-craft-background p-2 rounded border border-craft-border break-all text-craft-primary text-[11px]">
              {provenance.signature_ed25519 || provenance.maker_signature_hash || "N/A"}
            </p>
          </div>
        </>
      )}
    </div>
  );
}
