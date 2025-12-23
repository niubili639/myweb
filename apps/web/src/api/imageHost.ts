import axios from "axios";

const IMAGE_BASE = import.meta.env.VITE_IMAGE_API_BASE || "http://114.55.55.110:7791/api/v1";
const STORAGE_KEY = "lsky_token";

const client = axios.create({
  baseURL: IMAGE_BASE,
  headers: {
    Accept: "application/json",
  },
});

// 获取存储的 Token
export function getStoredToken(): string {
  return localStorage.getItem(STORAGE_KEY) || "";
}

// 保存 Token
export function saveToken(token: string) {
  localStorage.setItem(STORAGE_KEY, token);
}

// 清除 Token
export function clearToken() {
  localStorage.removeItem(STORAGE_KEY);
}

// 检查是否已登录
export function isLoggedIn(): boolean {
  return !!getStoredToken();
}

function authHeaders() {
  const token = getStoredToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// 登录获取 Token
export async function login(email: string, password: string) {
  const { data } = await client.post<{
    status: boolean;
    message: string;
    data: { token: string };
  }>("/tokens", { email, password });
  
  if (data.status && data.data.token) {
    saveToken(data.data.token);
  }
  return data;
}

// 登出（清空 Token）
export async function logout() {
  try {
    await client.delete("/tokens", { headers: authHeaders() });
  } catch {
    // 忽略错误
  }
  clearToken();
}

// 图片链接信息
export interface ImageLinks {
  url: string;
  html?: string;
  bbcode?: string;
  markdown?: string;
  markdown_with_link?: string;
  thumbnail_url?: string;
}

// 上传返回的图片信息
export interface UploadedImage {
  key: string;
  name: string;
  pathname: string;
  origin_name: string;
  size: number;
  mimetype: string;
  extension: string;
  md5: string;
  sha1: string;
  links: ImageLinks;
}

// 图片列表项
export interface ImageItem {
  key: string;
  name: string;
  origin_name: string;
  pathname: string;
  size: number;
  width: number;
  height: number;
  md5: string;
  sha1: string;
  human_date: string;
  date: string;
  links: ImageLinks;
}

// 分页响应
export interface ImageListResponse {
  current_page: number;
  last_page: number;
  per_page: number;
  total: number;
  data: ImageItem[];
}

// 相册信息
export interface Album {
  id: number;
  name: string;
  intro: string;
  image_num: number;
}

export interface AlbumListResponse {
  current_page: number;
  last_page: number;
  per_page: number;
  total: number;
  data: Album[];
}

// 上传图片
export async function uploadImage(file: File, strategyId?: number) {
  const formData = new FormData();
  formData.append("file", file);
  if (strategyId) formData.append("strategy_id", String(strategyId));

  const { data } = await client.post<{ status: boolean; message: string; data: UploadedImage }>("/upload", formData, {
    headers: {
      ...authHeaders(),
      "Content-Type": "multipart/form-data",
    },
  });
  return data;
}

// 获取图片列表
export async function listImages(params?: {
  page?: number;
  order?: "newest" | "earliest" | "utmost" | "least";
  permission?: "public" | "private";
  album_id?: number;
  keyword?: string;
}) {
  const { data } = await client.get<{ status: boolean; message: string; data: ImageListResponse }>("/images", {
    headers: authHeaders(),
    params,
  });
  return data;
}

// 删除图片
export async function deleteImage(key: string) {
  const { data } = await client.delete<{ status: boolean; message: string }>(`/images/${key}`, {
    headers: authHeaders(),
  });
  return data;
}

// 获取相册列表
export async function listAlbums(params?: {
  page?: number;
  order?: "newest" | "earliest" | "most" | "least";
  keyword?: string;
}) {
  const { data } = await client.get<{ status: boolean; message: string; data: AlbumListResponse }>("/albums", {
    headers: authHeaders(),
    params,
  });
  return data;
}

// 删除相册
export async function deleteAlbum(id: number) {
  const { data } = await client.delete<{ status: boolean; message: string }>(`/albums/${id}`, {
    headers: authHeaders(),
  });
  return data;
}

// 获取用户资料
export async function getProfile() {
  const { data } = await client.get<{
    status: boolean;
    message: string;
    data: {
      name: string;
      avatar: string;
      email: string;
      capacity: number;
      used_capacity: number;
      url: string;
      image_num: number;
      album_num: number;
    };
  }>("/profile", {
    headers: authHeaders(),
  });
  return data;
}
