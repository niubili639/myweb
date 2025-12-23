import axios from "axios";

const IMAGE_BASE = import.meta.env.VITE_IMAGE_API_BASE || "http://114.55.55.110:7791/api/v1";
const IMAGE_TOKEN = import.meta.env.VITE_IMAGE_API_TOKEN || "";

const client = axios.create({
  baseURL: IMAGE_BASE,
  headers: {
    Accept: "application/json",
  },
});

function authHeaders() {
  return IMAGE_TOKEN ? { Authorization: `Bearer ${IMAGE_TOKEN}` } : {};
}

export async function uploadImage(file: File, strategyId?: number) {
  const formData = new FormData();
  formData.append("file", file);
  if (strategyId) formData.append("strategy_id", String(strategyId));

  const { data } = await client.post("/upload", formData, {
    headers: {
      ...authHeaders(),
      "Content-Type": "multipart/form-data",
    },
  });
  return data;
}
