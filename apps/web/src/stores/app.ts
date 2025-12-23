import { defineStore } from "pinia";

export const useAppStore = defineStore("app", {
  state: () => ({
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL || "/api",
  }),
});
