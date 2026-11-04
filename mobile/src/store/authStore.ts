import { create } from "zustand";

interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  preferred_language: string;
  is_verified: boolean;
  role: string;
}

interface AuthState {
  user: UserProfile | null;
  token: string | null;
  language: string;
  isAuthenticated: boolean;
  setLanguage: (lang: string) => void;
  setAuth: (user: UserProfile, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  language: "ta", // Default Tamil as primary artisan language
  isAuthenticated: false,
  setLanguage: (language: string) => set({ language }),
  setAuth: (user: UserProfile, token: string) =>
    set({ user, token, isAuthenticated: true, language: user.preferred_language || "ta" }),
  logout: () => set({ user: null, token: null, isAuthenticated: false }),
}));
