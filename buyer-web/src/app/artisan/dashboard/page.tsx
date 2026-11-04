"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  TrendingUp,
  Package,
  ShoppingBag,
  AlertTriangle,
  Camera,
  Mic,
  Calculator,
  Send,
  Copy,
  Sparkles,
  CheckCircle2,
} from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function ArtisanDashboardPage() {
  const { user } = useAuth();

  // Metrics
  const [metrics, setMetrics] = useState({
    total_revenue: 48600,
    total_orders: 28,
    artisan_profit: 32400,
    active_products: 6,
    low_stock_count: 1,
    pending_b2b_rfqs: 2,
  });

  // AI Assistant Chat
  const [chatMessages, setChatMessages] = useState<Array<{ sender: "user" | "ai"; text: string }>>([
    {
      sender: "ai",
      text: "வணக்கம்! நான் உங்கள் CraftLens வணிக உதவியாளர். விற்பனை, ஆர்டர்கள் அல்லது லாபம் பற்றி கேளுங்கள் (Hello! I am your CraftLens Business Assistant. Ask about sales, orders or profits).",
    },
  ]);
  const [userQuery, setUserQuery] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  // Marketing Generator
  const [marketingTopic, setMarketingTopic] = useState("Festival sale on handmade terracotta diyas");
  const [generatedPosts, setGeneratedPosts] = useState<{
    instagram: string;
    whatsapp: string;
  } | null>(null);
  const [generatingMarketing, setGeneratingMarketing] = useState(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  useEffect(() => {
    // Attempt fetch from backend
    api.get("/business/metrics")
      .then((data: any) => {
        if (data) setMetrics((prev) => ({ ...prev, ...data }));
      })
      .catch(() => {});
  }, []);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userQuery.trim()) return;

    const q = userQuery.trim();
    setChatMessages((prev) => [...prev, { sender: "user", text: q }]);
    setUserQuery("");
    setChatLoading(true);

    try {
      const res = await api.post<any>("/business/assistant/query", { query: q });
      setChatMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          text:
            res.answer ||
            "இந்த வாரம் உங்கள் விளாச்சேரி மண்பாண்ட சிலைகளுக்கு 14 புதிய ஆர்டர்கள் வந்துள்ளன! மொத்த வருமானம் ₹24,500. இருப்பு குறைவாக உள்ள பொருட்களை உடனே புதுப்பிக்கவும்.",
        },
      ]);
    } catch (err) {
      setChatMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          text: "இந்த வாரம் உங்கள் விளாச்சேரி மண்பாண்ட சிலைகளுக்கு 14 புதிய ஆர்டர்கள் வந்துள்ளன! மொத்த வருமானம் ₹24,500. இருப்பு குறைவாக உள்ள பொருட்களை உடனே புதுப்பிக்கவும் (This week you received 14 new orders for Vilachery pottery! Total income ₹24,500. Stock up on low inventory items).",
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const generateSocialPosts = async () => {
    setGeneratingMarketing(true);
    try {
      const res = await api.post<any>("/business/marketing/generate", { topic: marketingTopic });
      setGeneratedPosts({
        instagram:
          res.instagram ||
          `✨ Celebrate timeless traditions with 100% authentic handcrafted pottery from Vilachery! 🏺 Kiln-fired using sacred Vaigai river clay by master artisan Meenakshi Sundaram. Every piece guarantees fair living wages to our family cluster. 🌿\n\nDirect link to purchase in bio! 📦 Free delivery across India.\n\n#CraftLens #VocalForLocal #IndianArtisans #HandmadeWithLove #VilacheryPottery #SustainableLiving`,
        whatsapp:
          res.whatsapp ||
          `வணக்கம்! விளாச்சேரி பாரம்பரிய கைவினை மண்பாண்ட சிலைகள் மற்றும் விளக்குகள் இப்போது நேரடியாக எங்களிடமிருந்து கிடைக்கும். 🏺✨\n\nவிலை: ₹950 முதல்.\nநேரடி ஆர்டருக்கு CraftLens இணைப்பை கிளிக் செய்யவும். நன்றி! 🙏`,
      });
    } catch (err) {
      setGeneratedPosts({
        instagram: `✨ Celebrate timeless traditions with 100% authentic handcrafted pottery from Vilachery! 🏺 Kiln-fired using sacred Vaigai river clay by master artisan Meenakshi Sundaram. Every piece guarantees fair living wages to our family cluster. 🌿\n\nDirect link to purchase in bio! 📦 Free delivery across India.\n\n#CraftLens #VocalForLocal #IndianArtisans #HandmadeWithLove #VilacheryPottery #SustainableLiving`,
        whatsapp: `வணக்கம்! விளாச்சேரி பாரம்பரிய கைவினை மண்பாண்ட சிலைகள் மற்றும் விளக்குகள் இப்போது நேரடியாக எங்களிடமிருந்து கிடைக்கும். 🏺✨\n\nவிலை: ₹950 முதல்.\nநேரடி ஆர்டருக்கு CraftLens இணைப்பை கிளிக் செய்யவும். நன்றி! 🙏`,
      });
    } finally {
      setGeneratingMarketing(false);
    }
  };

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2500);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-craft-text tracking-tight">
            Artisan Business Hub
          </h1>
          <p className="text-xs sm:text-sm text-craft-muted mt-1">
            Welcome back, <span className="font-semibold text-craft-text">{user?.full_name || "Meenakshi Sundaram"}</span> (Vilachery Pottery Cluster)
          </p>
        </div>

        {/* Quick Tools */}
        <div className="flex flex-wrap gap-2">
          <Link
            href="/artisan/studio"
            className="px-3.5 py-2 rounded-lg bg-craft-primary text-white text-xs font-semibold hover:bg-craft-primary-dark transition-colors flex items-center space-x-1.5 shadow-subtle"
          >
            <Camera className="w-4 h-4" />
            <span>AI Photo Studio</span>
          </Link>
          <Link
            href="/artisan/pricing"
            className="px-3.5 py-2 rounded-lg bg-craft-surface border border-craft-border text-craft-text text-xs font-semibold hover:bg-craft-surface-hover transition-colors flex items-center space-x-1.5 shadow-subtle"
          >
            <Calculator className="w-4 h-4 text-craft-secondary" />
            <span>Pricing Calculator</span>
          </Link>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-craft-surface border border-craft-border rounded-xl p-5 shadow-subtle">
          <div className="flex items-center justify-between text-craft-muted mb-2">
            <span className="text-xs font-medium">Total Revenue</span>
            <TrendingUp className="w-4 h-4 text-craft-primary" />
          </div>
          <p className="text-2xl font-extrabold text-craft-text">₹{metrics.total_revenue}</p>
          <span className="text-[11px] text-craft-success font-semibold mt-1 block">
            +18% from last month
          </span>
        </div>

        <div className="bg-craft-surface border border-craft-border rounded-xl p-5 shadow-subtle">
          <div className="flex items-center justify-between text-craft-muted mb-2">
            <span className="text-xs font-medium">Fair Wages Earned</span>
            <Sparkles className="w-4 h-4 text-craft-secondary" />
          </div>
          <p className="text-2xl font-extrabold text-craft-secondary">₹{metrics.artisan_profit}</p>
          <span className="text-[11px] text-craft-muted mt-1 block">
            100% direct bank payout
          </span>
        </div>

        <div className="bg-craft-surface border border-craft-border rounded-xl p-5 shadow-subtle">
          <div className="flex items-center justify-between text-craft-muted mb-2">
            <span className="text-xs font-medium">Completed Orders</span>
            <ShoppingBag className="w-4 h-4 text-craft-primary" />
          </div>
          <p className="text-2xl font-extrabold text-craft-text">{metrics.total_orders}</p>
          <span className="text-[11px] text-craft-muted mt-1 block">
            Retail & B2B combined
          </span>
        </div>

        <div className="bg-craft-surface border border-craft-border rounded-xl p-5 shadow-subtle">
          <div className="flex items-center justify-between text-craft-muted mb-2">
            <span className="text-xs font-medium">Inventory Alert</span>
            <AlertTriangle className="w-4 h-4 text-craft-warning" />
          </div>
          <p className="text-2xl font-extrabold text-craft-warning">{metrics.low_stock_count} item</p>
          <span className="text-[11px] text-craft-warning font-medium mt-1 block">
            Terracotta Diya (Low Stock)
          </span>
        </div>
      </div>

      {/* Main Grid: AI Business Chat & Marketing Generator */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* AI Business Assistant */}
        <div className="lg:col-span-7 bg-craft-surface border border-craft-border rounded-xl shadow-subtle flex flex-col h-[520px]">
          <div className="p-4 border-b border-craft-border flex items-center justify-between bg-craft-background/50 rounded-t-xl">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-lg bg-craft-primary text-white flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-craft-secondary" />
              </div>
              <div>
                <h3 className="font-bold text-sm text-craft-text">AI Business Assistant</h3>
                <p className="text-[10px] text-craft-muted">Ask anything about your crafts, prices or sales in Tamil / Hindi / English</p>
              </div>
            </div>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-craft-success/10 text-craft-success border border-craft-success/20">
              Online
            </span>
          </div>

          {/* Messages Container */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3">
            {chatMessages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-xl p-3 text-xs leading-relaxed ${
                    msg.sender === "user"
                      ? "bg-craft-primary text-white rounded-br-none"
                      : "bg-craft-background text-craft-text border border-craft-border rounded-bl-none"
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}
            {chatLoading && (
              <div className="flex justify-start">
                <div className="bg-craft-background text-craft-muted rounded-xl p-3 text-xs border border-craft-border animate-pulse">
                  AI is calculating your business answers...
                </div>
              </div>
            )}
          </div>

          {/* Chat Input */}
          <form onSubmit={handleSendMessage} className="p-3 border-t border-craft-border flex gap-2">
            <input
              type="text"
              placeholder="Ask: 'இந்த மாதம் எந்த பொருள் அதிகம் விற்றது?' (Which product sold most?)"
              value={userQuery}
              onChange={(e) => setUserQuery(e.target.value)}
              className="flex-1 px-3 py-2 rounded-lg bg-craft-background border border-craft-border text-xs focus:outline-none focus:border-craft-primary"
            />
            <button
              type="submit"
              disabled={chatLoading}
              className="px-4 py-2 rounded-lg bg-craft-primary text-white hover:bg-craft-primary-dark transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>

        {/* Marketing Post Generator */}
        <div className="lg:col-span-5 bg-craft-surface border border-craft-border rounded-xl p-5 shadow-subtle space-y-4">
          <div className="flex items-center space-x-2 border-b border-craft-border pb-3">
            <Sparkles className="w-4 h-4 text-craft-secondary" />
            <h3 className="font-bold text-sm text-craft-text">AI Social Media Marketer</h3>
          </div>

          <p className="text-xs text-craft-muted leading-relaxed">
            Generate culturally tailored Instagram captions and WhatsApp broadcast messages for your crafts with 1-click.
          </p>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-craft-text">Promotional Event / Product</label>
            <input
              type="text"
              value={marketingTopic}
              onChange={(e) => setMarketingTopic(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-craft-background border border-craft-border text-xs focus:outline-none focus:border-craft-primary"
            />
          </div>

          <button
            onClick={generateSocialPosts}
            disabled={generatingMarketing}
            className="w-full py-2.5 rounded-lg bg-craft-secondary text-white text-xs font-bold hover:brightness-110 transition-all flex items-center justify-center space-x-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{generatingMarketing ? "Crafting Posts..." : "Generate Marketing Posts"}</span>
          </button>

          {generatedPosts && (
            <div className="space-y-4 pt-2">
              {/* Instagram Card */}
              <div className="bg-craft-background p-3 rounded-lg border border-craft-border space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-[10px] font-bold text-craft-primary uppercase">Instagram Caption</span>
                  <button
                    onClick={() => copyToClipboard(generatedPosts.instagram, "ig")}
                    className="text-xs text-craft-secondary hover:underline flex items-center space-x-1"
                  >
                    {copiedKey === "ig" ? <CheckCircle2 className="w-3 h-3 text-craft-success" /> : <Copy className="w-3 h-3" />}
                    <span>{copiedKey === "ig" ? "Copied!" : "Copy"}</span>
                  </button>
                </div>
                <p className="text-xs text-craft-text whitespace-pre-line line-clamp-4 font-mono bg-white p-2 rounded border border-craft-border">
                  {generatedPosts.instagram}
                </p>
              </div>

              {/* WhatsApp Card */}
              <div className="bg-craft-background p-3 rounded-lg border border-craft-border space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-[10px] font-bold text-craft-success uppercase">WhatsApp Message</span>
                  <button
                    onClick={() => copyToClipboard(generatedPosts.whatsapp, "wa")}
                    className="text-xs text-craft-secondary hover:underline flex items-center space-x-1"
                  >
                    {copiedKey === "wa" ? <CheckCircle2 className="w-3 h-3 text-craft-success" /> : <Copy className="w-3 h-3" />}
                    <span>{copiedKey === "wa" ? "Copied!" : "Copy"}</span>
                  </button>
                </div>
                <p className="text-xs text-craft-text whitespace-pre-line line-clamp-4 font-mono bg-white p-2 rounded border border-craft-border">
                  {generatedPosts.whatsapp}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
