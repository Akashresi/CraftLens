"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "../../context/AuthContext";
import { Sparkles, ArrowRight, Check } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [role, setRole] = useState<"ARTISAN" | "RETAIL_BUYER" | "WHOLESALE_BUYER">("ARTISAN");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [language, setLanguage] = useState("ta");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const res = await register({
      email,
      phone,
      password,
      full_name: fullName,
      role_code: role,
      preferred_language: language,
    });
    setLoading(false);

    if (res.success) {
      if (role === "ARTISAN") {
        router.push("/onboarding");
      } else {
        router.push("/");
      }
    } else {
      setError(res.error || "Registration failed");
    }
  };

  return (
    <div className="min-h-screen bg-craft-background flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link href="/" className="inline-flex items-center space-x-2">
          <div className="w-12 h-12 rounded-xl bg-craft-primary flex items-center justify-center text-white shadow-card">
            <Sparkles className="w-6 h-6 text-craft-secondary" />
          </div>
        </Link>
        <h2 className="mt-4 text-3xl font-bold tracking-tight text-craft-text">
          Join CraftLens
        </h2>
        <p className="mt-2 text-sm text-craft-muted">
          Select your role to personalize your artisan or marketplace experience
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-craft-surface py-8 px-4 shadow-card sm:rounded-xl sm:px-10 border border-craft-border">
          {/* Role Picker */}
          <div className="mb-6">
            <label className="block text-xs font-semibold text-craft-text uppercase tracking-wider mb-2">
              I am registering as:
            </label>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setRole("ARTISAN")}
                className={`py-2 px-1 text-center rounded-lg border text-xs font-semibold transition-all ${
                  role === "ARTISAN"
                    ? "border-craft-primary bg-craft-primary text-white shadow-subtle"
                    : "border-craft-border bg-craft-background text-craft-text hover:bg-craft-surface-hover"
                }`}
              >
                Artisan / SHG
              </button>
              <button
                type="button"
                onClick={() => setRole("RETAIL_BUYER")}
                className={`py-2 px-1 text-center rounded-lg border text-xs font-semibold transition-all ${
                  role === "RETAIL_BUYER"
                    ? "border-craft-primary bg-craft-primary text-white shadow-subtle"
                    : "border-craft-border bg-craft-background text-craft-text hover:bg-craft-surface-hover"
                }`}
              >
                Retail Buyer
              </button>
              <button
                type="button"
                onClick={() => setRole("WHOLESALE_BUYER")}
                className={`py-2 px-1 text-center rounded-lg border text-xs font-semibold transition-all ${
                  role === "WHOLESALE_BUYER"
                    ? "border-craft-primary bg-craft-primary text-white shadow-subtle"
                    : "border-craft-border bg-craft-background text-craft-text hover:bg-craft-surface-hover"
                }`}
              >
                B2B Wholesale
              </button>
            </div>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-craft-error/10 border border-craft-error/20 text-xs text-craft-error font-medium">
              {error}
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-semibold text-craft-text uppercase tracking-wider">
                Full Name / Organization
              </label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Meenakshi Devi"
                className="mt-1 block w-full px-3 py-2 border border-craft-border rounded-md shadow-sm text-sm focus:outline-none focus:ring-craft-primary focus:border-craft-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-craft-text uppercase tracking-wider">
                Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="artisan@craftlens.org"
                className="mt-1 block w-full px-3 py-2 border border-craft-border rounded-md shadow-sm text-sm focus:outline-none focus:ring-craft-primary focus:border-craft-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-craft-text uppercase tracking-wider">
                Mobile Number
              </label>
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+91 98410 12345"
                className="mt-1 block w-full px-3 py-2 border border-craft-border rounded-md shadow-sm text-sm focus:outline-none focus:ring-craft-primary focus:border-craft-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-craft-text uppercase tracking-wider">
                Preferred Regional Language
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-craft-border rounded-md shadow-sm text-sm focus:outline-none focus:ring-craft-primary focus:border-craft-primary bg-white"
              >
                <option value="ta">தமிழ் (Tamil)</option>
                <option value="hi">हिंदी (Hindi)</option>
                <option value="en">English</option>
                <option value="te">తెలుగు (Telugu)</option>
                <option value="kn">ಕನ್ನಡ (Kannada)</option>
                <option value="ml">മലയാളം (Malayalam)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-craft-text uppercase tracking-wider">
                Password
              </label>
              <input
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 6 characters"
                className="mt-1 block w-full px-3 py-2 border border-craft-border rounded-md shadow-sm text-sm focus:outline-none focus:ring-craft-primary focus:border-craft-primary"
              />
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center items-center py-2.5 px-4 border border-transparent rounded-md shadow-subtle text-sm font-semibold text-white bg-craft-primary hover:bg-craft-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-craft-primary transition-colors disabled:opacity-50"
              >
                {loading ? "Creating Account..." : "Complete Registration"}
                {!loading && <ArrowRight className="w-4 h-4 ml-2" />}
              </button>
            </div>
          </form>

          <div className="mt-6 border-t border-craft-border pt-4 text-center">
            <p className="text-xs text-craft-muted">
              Already have an account?{" "}
              <Link href="/login" className="font-semibold text-craft-secondary hover:underline">
                Sign In
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

