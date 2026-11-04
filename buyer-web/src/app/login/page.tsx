"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "../../context/AuthContext";
import { Sparkles, ArrowRight, ShieldCheck } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const res = await login(email, password);
    setLoading(false);

    if (res.success) {
      router.push("/");
    } else {
      setError(res.error || "Incorrect credentials");
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
          Sign In to CraftLens
        </h2>
        <p className="mt-2 text-sm text-craft-muted">
          Access your artisan studio or manage your handmade craft orders
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-craft-surface py-8 px-4 shadow-card sm:rounded-xl sm:px-10 border border-craft-border">
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-craft-error/10 border border-craft-error/20 text-xs text-craft-error font-medium">
              {error}
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-semibold text-craft-text uppercase tracking-wider">
                Email Address
              </label>
              <div className="mt-1">
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="artisan@craftlens.org"
                  className="appearance-none block w-full px-3 py-2 border border-craft-border rounded-md shadow-sm placeholder-craft-muted/60 text-sm focus:outline-none focus:ring-craft-primary focus:border-craft-primary"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-craft-text uppercase tracking-wider">
                Password
              </label>
              <div className="mt-1">
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="appearance-none block w-full px-3 py-2 border border-craft-border rounded-md shadow-sm placeholder-craft-muted/60 text-sm focus:outline-none focus:ring-craft-primary focus:border-craft-primary"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center items-center py-2.5 px-4 border border-transparent rounded-md shadow-subtle text-sm font-semibold text-white bg-craft-primary hover:bg-craft-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-craft-primary transition-colors disabled:opacity-50"
              >
                {loading ? "Authenticating..." : "Sign In"}
                {!loading && <ArrowRight className="w-4 h-4 ml-2" />}
              </button>
            </div>
          </form>

          <div className="mt-6 border-t border-craft-border pt-4 text-center">
            <p className="text-xs text-craft-muted">
              Don&apos;t have an account yet?{" "}
              <Link href="/register" className="font-semibold text-craft-secondary hover:underline">
                Create Account
              </Link>
            </p>
          </div>

          <div className="mt-6 flex items-center justify-center space-x-1.5 text-[11px] text-craft-muted">
            <ShieldCheck className="w-3.5 h-3.5 text-craft-success" />
            <span>Encrypted with Argon2id & RFC 7519 JWT standards</span>
          </div>
        </div>
      </div>
    </div>
  );
}
