import { create } from "zustand";

type AuthState = {
  accessToken: string | null;
  role: string | null;
  setSession: (token: string, role: string) => void;
  clear: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: localStorage.getItem("access_token"),
  role: localStorage.getItem("role"),
  setSession: (token, role) => {
    localStorage.setItem("access_token", token);
    localStorage.setItem("role", role);
    set({ accessToken: token, role });
  },
  clear: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("role");
    set({ accessToken: null, role: null });
  }
}));
