"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { apiRequest } from "../lib/api";

export interface User {
  id: string;
  email: string;
  phone?: string;
  full_name: string;
  preferred_language: string;
  is_active: boolean;
  is_verified: boolean;
  roles: Array<{ id: string; code: string; name: string }>;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  language: string;
  setLanguage: (lang: string) => void;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  register: (payload: any) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [language, setLanguageState] = useState<string>("ta");

  const setLanguage = (lang: string) => {
    setLanguageState(lang);
    if (typeof window !== "undefined") {
      localStorage.setItem("craftlens_lang", lang);
    }
  };

  useEffect(() => {
    const savedToken = localStorage.getItem("craftlens_token");
    const savedLang = localStorage.getItem("craftlens_lang");
    if (savedLang) setLanguageState(savedLang);

    if (savedToken) {
      setToken(savedToken);
      fetchUserProfile(savedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserProfile = async (authToken: string) => {
    try {
      const res = await apiRequest<User>("/auth/me", { token: authToken });
      if (res.success && res.data) {
        setUser(res.data);
        if (res.data.preferred_language) {
          setLanguageState(res.data.preferred_language);
        }
      } else {
        logout();
      }
    } catch {
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const formBody = new URLSearchParams();
    formBody.append("username", email);
    formBody.append("password", password);

    const res = await fetch("http://127.0.0.1:8000/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formBody.toString(),
    });

    const data = await res.json();
    if (!res.ok) {
      return { success: false, error: data.detail || "Authentication failed" };
    }

    const accessToken = data.access_token;
    setToken(accessToken);
    localStorage.setItem("craftlens_token", accessToken);
    if (data.refresh_token) {
      localStorage.setItem("craftlens_refresh_token", data.refresh_token);
    }

    await fetchUserProfile(accessToken);
    return { success: true };
  };

  const register = async (payload: any) => {
    const res = await apiRequest("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    if (!res.success) {
      return { success: false, error: res.error };
    }

    // Automatically login on registration
    return login(payload.email, payload.password);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    if (typeof window !== "undefined") {
      localStorage.removeItem("craftlens_token");
      localStorage.removeItem("craftlens_refresh_token");
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        language,
        setLanguage,
        login,
        register,
        logout,
        refreshUser: () => fetchUserProfile(token || ""),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
