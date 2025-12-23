import axios from "axios";
import { useAuthStore } from "@/stores/auth";

const baseURL = import.meta.env.VITE_API_BASE_URL || "/api";

const http = axios.create({
  baseURL,
  // 长耗时的千问图片/对话请求，适当放宽超时时间
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || "Request failed";
    return Promise.reject(new Error(message));
  },
);

http.interceptors.request.use((config) => {
  try {
    const auth = useAuthStore();
    if (auth.token) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${auth.token}`,
      };
    }
  } catch {
    // Pinia not ready; skip attaching token
  }
  return config;
});

export default http;
