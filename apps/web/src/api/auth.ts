import http from "./http";
import type { User } from "@/stores/auth";

export interface LoginPayload {
  username: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  invite_code: string;
  is_admin?: boolean;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface LoginResponse {
  token: Token;
  user: User;
}

export interface ApiKeyPayload {
  provider?: string;
  key: string;
}

export interface ApiKey {
  provider: string;
  key: string;
}

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const form = new FormData();
  form.append("username", payload.username);
  form.append("password", payload.password);
  const { data } = await http.post<LoginResponse>("/api/v1/auth/login", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function register(payload: RegisterPayload): Promise<User> {
  const { data } = await http.post<User>("/api/v1/auth/register", payload);
  return data;
}

export async function fetchMe(): Promise<User> {
  const { data } = await http.get<User>("/api/v1/auth/me");
  return data;
}

export async function setApiKey(payload: ApiKeyPayload): Promise<ApiKey> {
  const body = { provider: payload.provider || "qwen", key: payload.key };
  const { data } = await http.post<ApiKey>("/api/v1/auth/apikey", body);
  return data;
}

export async function getApiKey(provider = "qwen"): Promise<ApiKey> {
  const { data } = await http.get<ApiKey>(`/api/v1/auth/apikey/${provider}`);
  return data;
}
