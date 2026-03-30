import type { User } from "@/types/auth";
import { authService } from "@/services/auth";
import { create } from "zustand";

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  login: async (email, password) => {
    await authService.login({ email, password });
    const user = await authService.me();
    set({ user, isAuthenticated: true });
  },
  register: async (name, email, password) => {
    await authService.register({ name, email, password });
    const user = await authService.me();
    set({ user, isAuthenticated: true });
  },
  logout: async () => {
    await authService.logout();
    set({ user: null, isAuthenticated: false });
  },
  fetchUser: async () => {
    try {
      const user = await authService.me();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
  setUser: (user) => set({ user, isAuthenticated: !!user }),
}));
