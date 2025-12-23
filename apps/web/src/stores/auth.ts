import { defineStore } from "pinia";
import { fetchMe } from "@/api/auth";

export interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  role?: string;
  allowed_spaces?: string;
}

interface Token {
  access_token: string;
  token_type: string;
}

interface LoginResponse {
  token: Token;
  user: User;
}

const STORAGE_KEY = "app_auth";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: (JSON.parse(localStorage.getItem(STORAGE_KEY) || "null") as { token?: string })?.token || "",
    user: (JSON.parse(localStorage.getItem(STORAGE_KEY) || "null") as { user?: User })?.user || null,
  }),
  actions: {
    setSession(payload: LoginResponse) {
      this.token = payload.token.access_token;
      this.user = payload.user;
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ token: this.token, user: this.user }),
      );
    },
    clear() {
      this.token = "";
      this.user = null;
      localStorage.removeItem(STORAGE_KEY);
    },
    async ensureUser() {
      if (!this.token) return;
      if (this.user) return;
      try {
        this.user = await fetchMe();
        localStorage.setItem(STORAGE_KEY, JSON.stringify({ token: this.token, user: this.user }));
      } catch {
        this.clear();
      }
    },
  },
});
