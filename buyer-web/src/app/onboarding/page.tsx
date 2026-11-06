"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../context/AuthContext";
import { apiRequest } from "../../lib/api";
import { Sparkles, CheckCircle2, UploadCloud, MapPin, Award } from "lucide-react";

export default function ArtisanOnboardingPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [step, setStep] = useState(1);
  const [specialization, setSpecialization] = useState("Handloom & Mulberry Silk Weaving");
  const [experience, setExperience] = useState(10);
  const [city, setCity] = useState("Kanchipuram");
  const [state, setState] = useState("Tamil Nadu");
  const [pincode, setPincode] = useState("631501");
  const [bio, setBio] = useState("Traditional handloom weaver creating pure silk sarees using time-honored korvai techniques.");
  const [docType, setDocType] = useState("PEHCHAN_CARD");
  const [docNumber, setDocNumber] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFinish = async () => {
    setLoading(true);
    // 1. Update artisan profile
    await apiRequest("/artisans/me", {
      method: "PUT",
      body: JSON.stringify({
        craft_specialization: specialization,
        experience_years: Number(experience),
        city,
        state,
        pincode,
        bio,
        bank_account_configured: true,
      }),
    });

    // 2. Submit verification if provided
    if (docNumber) {
      await apiRequest("/artisans/me/verify", {
        method: "POST",
        body: JSON.stringify({
          document_type: docType,
          document_number: docNumber,
          document_url: "https://craftlens-storage.org/docs/artisan_id_sample.pdf",
        }),
      });
    }

    setLoading(false);
    router.push("/artisan/dashboard");
  };

  return (
    <div className="min-h-screen bg-craft-background py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-craft-primary text-white shadow-card mb-3">
            <Sparkles className="w-6 h-6 text-craft-secondary" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-craft-text">
            Welcome to CraftLens Artisan Studio
          </h1>
          <p className="mt-1 text-sm text-craft-muted">
            Let&apos;s set up your digital craft profile in 2 quick steps
          </p>
        </div>

        {/* Stepper Indicator */}
        <div className="flex items-center justify-center space-x-4 mb-8">
          <div
            className={`flex items-center space-x-2 text-xs font-semibold px-3 py-1.5 rounded-full ${
              step === 1 ? "bg-craft-primary text-white" : "bg-craft-surface text-craft-muted border border-craft-border"
            }`}
          >
            <span>1. Craft & Studio</span>
          </div>
          <div className="w-8 h-px bg-craft-border" />
          <div
            className={`flex items-center space-x-2 text-xs font-semibold px-3 py-1.5 rounded-full ${
              step === 2 ? "bg-craft-primary text-white" : "bg-craft-surface text-craft-muted border border-craft-border"
            }`}
          >
            <span>2. Verification & Pehchan</span>
          </div>
        </div>

        {/* Step 1: Craft & Studio */}
        {step === 1 && (
          <div className="bg-craft-surface p-6 sm:p-8 rounded-xl border border-craft-border shadow-card space-y-5">
            <div>
              <label className="block text-xs font-semibold text-craft-text uppercase tracking-wider">
                Craft Specialization
              </label>
              <input
                type="text"
                value={specialization}
                onChange={(e) => setSpecialization(e.target.value)}
                placeholder="e.g. Terracotta Pottery, Madhubani Painting, Banarasi Brocade"
                className="mt-1 block w-full px-3 py-2 border border-craft-border rounded-md text-sm focus:ring-craft-primary focus:border-craft-primary"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-craft-text uppercase tracking-wider">
                  Years of Experience
                </label>
                <input
                  type="number"
                  value={experience}
                  onChange={(e) => setExperience(Number(e.target.value))}
                  min={1}
                  max={70}
                  className="mt-1 block w-full px-3 py-2 border border-craft-border rounded-md text-sm focus:ring-craft-primary focus:border-craft-primary"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-craft-text uppercase tracking-wider">
                  City / Town / Village
                </label>
                <input
                  type="text"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-craft-border rounded-md text-sm focus:ring-craft-primary focus:border-craft-primary"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-craft-text uppercase tracking-wider">
                  State
                </label>
                <input
                  type="text"
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-craft-border rounded-md text-sm focus:ring-craft-primary focus:border-craft-primary"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-craft-text uppercase tracking-wider">
                  PIN Code
                </label>
                <input
                  type="text"
                  value={pincode}
                  onChange={(e) => setPincode(e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-craft-border rounded-md text-sm focus:ring-craft-primary focus:border-craft-primary"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-craft-text uppercase tracking-wider">
                Artisan Story & Craft Background
              </label>
              <textarea
                rows={3}
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-craft-border rounded-md text-sm focus:ring-craft-primary focus:border-craft-primary"
              />
            </div>

            <button
              type="button"
              onClick={() => setStep(2)}
              className="w-full py-2.5 px-4 rounded-md text-sm font-semibold text-white bg-craft-primary hover:bg-craft-primary-dark transition-colors shadow-subtle"
            >
              Continue to Verification
            </button>
          </div>
        )}

        {/* Step 2: Verification */}
        {step === 2 && (
          <div className="bg-craft-surface p-6 sm:p-8 rounded-xl border border-craft-border shadow-card space-y-5">
            <div className="flex items-center space-x-3 p-3 bg-craft-background rounded-lg border border-craft-border text-xs text-craft-text">
              <Award className="w-5 h-5 text-craft-secondary flex-shrink-0" />
              <span>
                Verification unlocks the <strong>Verified Master Artisan</strong> badge on your products, increasing buyer trust by 4.2x.
              </span>
            </div>

            <div>
              <label className="block text-xs font-semibold text-craft-text uppercase tracking-wider">
                Government / Craft ID Type
              </label>
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-craft-border rounded-md text-sm focus:ring-craft-primary focus:border-craft-primary bg-white"
              >
                <option value="PEHCHAN_CARD">Ministry of Textiles Pehchan Card</option>
                <option value="WEAVER_ID">Weavers Service Centre (WSC) ID</option>
                <option value="AADHAAR">Aadhaar Card</option>
                <option value="COOP_CERTIFICATE">Cooperative Society Certificate</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-craft-text uppercase tracking-wider">
                Card / Registration Number
              </label>
              <input
                type="text"
                value={docNumber}
                onChange={(e) => setDocNumber(e.target.value)}
                placeholder="e.g. PEH-TN-987654"
                className="mt-1 block w-full px-3 py-2 border border-craft-border rounded-md text-sm focus:ring-craft-primary focus:border-craft-primary"
              />
            </div>

            <div className="p-4 border-2 border-dashed border-craft-border rounded-lg text-center bg-craft-background/50 hover:bg-craft-background transition-colors cursor-pointer">
              <UploadCloud className="w-8 h-8 text-craft-muted mx-auto mb-2" />
              <p className="text-xs font-medium text-craft-text">
                Tap to upload card scan or photo
              </p>
              <p className="text-[11px] text-craft-muted mt-0.5">
                PNG, JPG or PDF up to 10MB
              </p>
            </div>

            <div className="flex space-x-3 pt-2">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="w-1/3 py-2.5 px-4 rounded-md text-sm font-semibold text-craft-text border border-craft-border hover:bg-craft-surface-hover transition-colors"
              >
                Back
              </button>
              <button
                type="button"
                onClick={handleFinish}
                disabled={loading}
                className="w-2/3 py-2.5 px-4 rounded-md text-sm font-semibold text-white bg-craft-primary hover:bg-craft-primary-dark transition-colors shadow-subtle disabled:opacity-50"
              >
                {loading ? "Saving Profile..." : "Complete & Enter Studio"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

