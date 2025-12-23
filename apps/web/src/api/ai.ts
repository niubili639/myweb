import http from "./http";

export interface ChatRequest {
  prompt: string;
  history?: { role: string; content: string }[];
  model?: string;
}

export interface ChatResponse {
  reply: string;
  session_id?: number;
}

export interface ImageRequest {
  prompt: string;
  model?: string;
  size?: string;
  session_id?: number;
}

export interface ImageResponse {
  images: string[];
  session_id?: number;
}

export async function chat(payload: ChatRequest): Promise<ChatResponse> {
  const { data } = await http.post<ChatResponse>("/api/v1/spaces/ai/chat", payload);
  return data;
}

export async function generateImage(payload: ImageRequest): Promise<ImageResponse> {
  const { data } = await http.post<ImageResponse>("/api/v1/spaces/ai/image", payload);
  return data;
}

export interface ChatSession {
  id: number;
  title: string | null;
  mode: string;
  model?: string | null;
  is_pinned?: number;
  created_at?: string | null;
}

export interface ChatSessionCreate {
  title?: string | null;
  mode?: string;
  model?: string | null;
}

export interface ChatMessage {
  id: number;
  role: string;
  content: string;
  message_type: string;
  created_at?: string | null;
}

export async function listSessions(): Promise<ChatSession[]> {
  const { data } = await http.get<ChatSession[]>("/api/v1/spaces/sessions");
  return data;
}

export async function createSession(payload: ChatSessionCreate): Promise<ChatSession> {
  const { data } = await http.post<ChatSession>("/api/v1/spaces/sessions", payload);
  return data;
}

export async function listMessages(sessionId: number): Promise<ChatMessage[]> {
  const { data } = await http.get<ChatMessage[]>(`/api/v1/spaces/sessions/${sessionId}/messages`);
  return data;
}

export async function setSessionPin(sessionId: number, isPinned: boolean): Promise<ChatSession> {
  const { data } = await http.post<ChatSession>(`/api/v1/spaces/sessions/${sessionId}/pin`, null, {
    params: { is_pinned: isPinned },
  });
  return data;
}

export async function deleteSession(sessionId: number): Promise<void> {
  await http.delete(`/api/v1/spaces/sessions/${sessionId}`);
}
