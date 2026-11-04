"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useAuth } from "../context/AuthContext";
import { Globe, ShoppingBag, User as UserIcon, LogOut, Sparkles } from "lucide-react";

const LANGUAGES = [
  { code: "ta", label: "தமிழ்" },
  { code: "hi", label: "हिंदी" },
  { code: "en", label: "English" },
  { code: "te", label: "తెలుగు" },
  { code: "kn", label: "ಕನ್ನಡ" },
  { code: "ml", label: "മലയാളം" },
];

export default function Navbar() {
  const { user, logout, language, setLanguage } = useAuth();
  const [langOpen, setLangOpen] = useState(false);

  const isArtisan = user?.roles.some((r) => r.code === "ARTISAN");
  const isWholesale = user?.roles.some((r) => r.code === "WHOLESALE_BUYER");
  const isAdmin = user?.roles.some((r) => r.code === "ADMIN");

  return (
    <nav className="sticky top-0 z-50 bg-craft-surface/90 backdrop-blur-md border-b border-craft-border shadow-subtle">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Brand Identity */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 rounded-lg bg-craft-primary flex items-center justify-center text-white shadow-subtle">
              <Sparkles className="w-5 h-5 text-craft-secondary" />
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight text-craft-primary">
                Craft<span className="text-craft-secondary">Lens</span>
              </span>
              <span className="block text-[10px] tracking-wider uppercase text-craft-muted font-medium">
                Artisan Commerce 2.0
              </span>
            </div>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-6 text-sm font-medium text-craft-text">
            <Link href="/catalog" className="hover:text-craft-primary transition-colors">
              Discover Crafts
            </Link>
            <Link href="/origins" className="hover:text-craft-primary transition-colors">
              Heritage Origins
            </Link>
            <Link href="/b2b" className="hover:text-craft-primary transition-colors">
              Wholesale & B2B
            </Link>
            {isArtisan && (
              <Link
                href="/artisan/dashboard"
                className="text-craft-secondary font-semibold hover:underline"
              >
                Artisan Studio
              </Link>
            )}
            {isAdmin && (
              <Link
                href="http://localhost:3001"
                className="text-craft-primary font-semibold hover:underline"
              >
                Admin Portal
              </Link>
            )}
          </div>

          {/* Controls: Language Switcher, Cart, Profile */}
          <div className="flex items-center space-x-4">
            {/* Language Switcher */}
            <div className="relative">
              <button
                onClick={() => setLangOpen(!langOpen)}
                className="flex items-center space-x-1 px-3 py-1.5 rounded-md border border-craft-border bg-craft-background text-xs font-medium text-craft-text hover:bg-craft-surface-hover transition-colors"
                aria-label="Select Language"
              >
                <Globe className="w-3.5 h-3.5 text-craft-primary" />
                <span>{LANGUAGES.find((l) => l.code === language)?.label || "English"}</span>
              </button>

              {langOpen && (
                <div className="absolute right-0 mt-2 w-32 rounded-lg bg-craft-surface border border-craft-border shadow-card py-1 z-50">
                  {LANGUAGES.map((l) => (
                    <button
                      key={l.code}
                      onClick={() => {
                        setLanguage(l.code);
                        setLangOpen(false);
                      }}
                      className={`w-full text-left px-3 py-1.5 text-xs hover:bg-craft-surface-hover transition-colors ${
                        language === l.code ? "font-bold text-craft-primary bg-craft-background" : "text-craft-text"
                      }`}
                    >
                      {l.label}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Shopping Cart */}
            <Link
              href="/cart"
              className="p-2 rounded-md hover:bg-craft-surface-hover text-craft-text relative"
              aria-label="Cart"
            >
              <ShoppingBag className="w-5 h-5" />
            </Link>

            {/* User Account / Login */}
            {user ? (
              <div className="flex items-center space-x-2">
                <Link
                  href={isArtisan ? "/artisan/profile" : "/profile"}
                  className="flex items-center space-x-2 px-3 py-1.5 rounded-md bg-craft-background hover:bg-craft-surface-hover border border-craft-border text-xs font-medium"
                >
                  <UserIcon className="w-3.5 h-3.5 text-craft-primary" />
                  <span className="truncate max-w-[100px]">{user.full_name}</span>
                </Link>
                <button
                  onClick={logout}
                  className="p-1.5 rounded-md text-craft-muted hover:text-craft-error hover:bg-craft-surface-hover"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link
                  href="/login"
                  className="text-xs font-medium text-craft-primary hover:underline px-2 py-1"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="text-xs font-semibold px-3 py-1.5 rounded-md bg-craft-primary text-white hover:bg-craft-primary-dark shadow-subtle transition-colors"
                >
                  Join CraftLens
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
