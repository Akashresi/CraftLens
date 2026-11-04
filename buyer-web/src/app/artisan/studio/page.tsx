"use client";

import React, { useState } from "react";
import Navbar from "../../../components/Navbar";
import { UploadCloud, Sparkles, CheckCircle2, AlertTriangle, Layers, Eye, ArrowRight, RefreshCw } from "lucide-react";

export default function AIProductStudioPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [qualityData, setQualityData] = useState<any>(null);
  const [processedResult, setProcessedResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<"white" | "lifestyle" | "original">("white");
  const [lifestyleTheme, setLifestyleTheme] = useState("wood");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setQualityData(null);
      setProcessedResult(null);
      runQualityCheck(file);
    }
  };

  const runQualityCheck = async (file: File) => {
    setAnalyzing(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/studio/analyze", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("craftlens_token") || ""}`,
        },
        body: formData,
      });
      const data = await res.json();
      if (data.success) {
        setQualityData(data.data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  const runStudioPipeline = async () => {
    if (!selectedFile) return;
    setProcessing(true);
    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("lifestyle_theme", lifestyleTheme);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/studio/process", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("craftlens_token") || ""}`,
        },
        body: formData,
      });
      const data = await res.json();
      if (data.success) {
        setProcessedResult(data.data);
        setActiveTab("white");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-craft-background text-craft-text">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Title */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between pb-6 border-b border-craft-border mb-8">
          <div>
            <div className="inline-flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-craft-secondary mb-1">
              <Sparkles className="w-4 h-4" />
              <span>Module 1 • Intelligent Studio</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-craft-text tracking-tight">
              AI Product Photography Studio
            </h1>
            <p className="text-sm text-craft-muted mt-1">
              Capture handcrafted products, remove messy backgrounds, correct lighting, and generate e-commerce ready studio photos.
            </p>
          </div>
        </div>

        {/* Studio Workspace Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Image Canvas & Preview (7 cols) */}
          <div className="lg:col-span-7 space-y-4">
            <div className="bg-craft-surface border border-craft-border rounded-xl p-4 shadow-card">
              {/* Canvas Header & Tabs */}
              <div className="flex items-center justify-between pb-3 border-b border-craft-border">
                <span className="text-xs font-semibold uppercase tracking-wider text-craft-muted">
                  Interactive Canvas Preview
                </span>
                {processedResult && (
                  <div className="flex items-center space-x-1 p-1 bg-craft-background rounded-lg border border-craft-border">
                    <button
                      onClick={() => setActiveTab("white")}
                      className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                        activeTab === "white"
                          ? "bg-craft-surface text-craft-primary shadow-subtle font-semibold"
                          : "text-craft-muted hover:text-craft-text"
                      }`}
                    >
                      Studio White
                    </button>
                    <button
                      onClick={() => setActiveTab("lifestyle")}
                      className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                        activeTab === "lifestyle"
                          ? "bg-craft-surface text-craft-primary shadow-subtle font-semibold"
                          : "text-craft-muted hover:text-craft-text"
                      }`}
                    >
                      Lifestyle Staging
                    </button>
                    <button
                      onClick={() => setActiveTab("original")}
                      className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                        activeTab === "original"
                          ? "bg-craft-surface text-craft-primary shadow-subtle font-semibold"
                          : "text-craft-muted hover:text-craft-text"
                      }`}
                    >
                      Original
                    </button>
                  </div>
                )}
              </div>

              {/* Main Image Display Box */}
              <div className="relative aspect-square mt-3 rounded-lg overflow-hidden bg-craft-background flex items-center justify-center border border-craft-border">
                {previewUrl ? (
                  /* eslint-disable-next-line @next/next/no-img-element */
                  <img
                    src={
                      activeTab === "white" && processedResult
                        ? `http://127.0.0.1:8000${processedResult.white_bg_url}`
                        : activeTab === "lifestyle" && processedResult
                        ? `http://127.0.0.1:8000${processedResult.lifestyle_url}`
                        : previewUrl
                    }
                    alt="Product preview"
                    className="max-h-full max-w-full object-contain"
                  />
                ) : (
                  <label className="flex flex-col items-center justify-center p-8 text-center cursor-pointer hover:bg-craft-surface-hover/50 transition-colors w-full h-full">
                    <UploadCloud className="w-12 h-12 text-craft-muted mb-3" />
                    <span className="text-sm font-semibold text-craft-text">
                      Upload Raw Craft Photograph
                    </span>
                    <span className="text-xs text-craft-muted mt-1 max-w-xs">
                      Supports high-resolution JPG or PNG. Works best with direct overhead or side lighting.
                    </span>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </label>
                )}
              </div>
            </div>
          </div>

          {/* Right Column: Controls, Quality Metrics & AI Actions (5 cols) */}
          <div className="lg:col-span-5 space-y-5">
            {/* 1. Quality Analysis Card */}
            <div className="bg-craft-surface border border-craft-border rounded-xl p-5 shadow-card">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-craft-text mb-3">
                Pre-Flight Quality Inspector
              </h2>

              {analyzing ? (
                <div className="flex items-center space-x-2 py-4 text-xs text-craft-muted">
                  <RefreshCw className="w-4 h-4 animate-spin text-craft-primary" />
                  <span>Computing Laplacian variance & exposure metrics...</span>
                </div>
              ) : qualityData ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 rounded-lg bg-craft-background border border-craft-border">
                    <span className="text-xs font-medium text-craft-muted">Studio Quality Score</span>
                    <span className="text-lg font-bold text-craft-primary">
                      {qualityData.quality_score} <span className="text-xs text-craft-muted">/ 10.0</span>
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="p-2.5 rounded-lg border border-craft-border bg-craft-surface">
                      <div className="text-craft-muted">Sharpness Variance</div>
                      <div className="font-semibold text-craft-text mt-0.5">
                        {qualityData.sharpness_variance}
                      </div>
                    </div>
                    <div className="p-2.5 rounded-lg border border-craft-border bg-craft-surface">
                      <div className="text-craft-muted">Mean Brightness</div>
                      <div className="font-semibold text-craft-text mt-0.5">
                        {qualityData.mean_brightness}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 text-xs text-craft-text pt-1">
                    {qualityData.is_blurry ? (
                      <AlertTriangle className="w-4 h-4 text-craft-warning flex-shrink-0" />
                    ) : (
                      <CheckCircle2 className="w-4 h-4 text-craft-success flex-shrink-0" />
                    )}
                    <span>{qualityData.recommendations}</span>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-craft-muted py-2">
                  Upload an image to inspect blur, contrast, and color balance.
                </p>
              )}
            </div>

            {/* 2. Studio Configuration & Processing Card */}
            <div className="bg-craft-surface border border-craft-border rounded-xl p-5 shadow-card space-y-4">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-craft-text">
                Studio Settings & AI Pipeline
              </h2>

              <div>
                <label className="block text-xs font-semibold text-craft-muted uppercase tracking-wider mb-2">
                  Lifestyle Texture Background
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { id: "wood", label: "Rustic Wood" },
                    { id: "terracotta", label: "Terracotta" },
                    { id: "linen", label: "Warm Linen" },
                  ].map((theme) => (
                    <button
                      key={theme.id}
                      type="button"
                      onClick={() => setLifestyleTheme(theme.id)}
                      className={`py-2 px-2 text-xs font-medium rounded-lg border transition-all ${
                        lifestyleTheme === theme.id
                          ? "border-craft-primary bg-craft-background text-craft-primary font-bold shadow-subtle"
                          : "border-craft-border text-craft-muted hover:bg-craft-surface-hover"
                      }`}
                    >
                      {theme.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="pt-2">
                <button
                  type="button"
                  onClick={runStudioPipeline}
                  disabled={!selectedFile || processing}
                  className="w-full flex items-center justify-center py-3 px-4 rounded-lg bg-craft-primary hover:bg-craft-primary-dark text-white text-sm font-semibold shadow-subtle transition-colors disabled:opacity-50"
                >
                  {processing ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                      <span>Enhancing, Segmenting & Rendering...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 text-craft-secondary mr-2" />
                      <span>Run AI Studio Pipeline</span>
                    </>
                  )}
                </button>
              </div>

              {processedResult && (
                <div className="pt-2 border-t border-craft-border">
                  <a
                    href="/artisan/catalog/new"
                    className="w-full flex items-center justify-center py-2.5 px-4 rounded-lg bg-craft-secondary hover:bg-craft-secondary/90 text-white text-sm font-semibold shadow-subtle transition-colors"
                  >
                    <span>Proceed to Voice Cataloging</span>
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
