import http from "./http";

// ========== Couple ==========
export interface Couple {
  id: number;
  name: string;
  partner_a_name?: string | null;
  partner_b_name?: string | null;
  partner_a_avatar?: string | null;
  partner_b_avatar?: string | null;
  partner_a_birthday?: string | null;
  partner_b_birthday?: string | null;
  partner_a_location?: string | null;
  partner_b_location?: string | null;
  start_date?: string | null;
  created_at: string;
}

export interface CoupleCreate {
  name: string;
  partner_a_name?: string | null;
  partner_b_name?: string | null;
  partner_a_avatar?: string | null;
  partner_b_avatar?: string | null;
  partner_a_birthday?: string | null;
  partner_b_birthday?: string | null;
  partner_a_location?: string | null;
  partner_b_location?: string | null;
  start_date?: string | null;
}

export async function createCouple(payload: CoupleCreate): Promise<Couple> {
  const { data } = await http.post<Couple>("/api/v1/couples", payload);
  return data;
}

export async function fetchMyCouple(): Promise<Couple | null> {
  const { data } = await http.get<Couple | null>("/api/v1/couples/me");
  return data;
}

// ========== Note ==========
export interface Note {
  id: number;
  title: string;
  content_md: string;
  created_at: string;
}

export interface NoteCreate {
  title: string;
  content_md: string;
}

export async function addNote(coupleId: number, payload: NoteCreate): Promise<Note> {
  const { data } = await http.post<Note>(`/api/v1/couples/${coupleId}/notes`, payload);
  return data;
}

export async function listNotes(coupleId: number): Promise<Note[]> {
  const { data } = await http.get<Note[]>(`/api/v1/couples/${coupleId}/notes`);
  return data;
}

export async function updateNote(coupleId: number, noteId: number, payload: NoteCreate): Promise<Note> {
  const { data } = await http.patch<Note>(`/api/v1/couples/${coupleId}/notes/${noteId}`, payload);
  return data;
}

export async function deleteNote(coupleId: number, noteId: number): Promise<void> {
  await http.delete(`/api/v1/couples/${coupleId}/notes/${noteId}`);
}

// ========== Message (留言板) ==========
export interface Message {
  id: number;
  author: string;
  content: string;
  created_at: string;
}

export interface MessageCreate {
  author: string;
  content: string;
}

export async function addMessage(coupleId: number, payload: MessageCreate): Promise<Message> {
  const { data } = await http.post<Message>(`/api/v1/couples/${coupleId}/messages`, payload);
  return data;
}

export async function listMessages(coupleId: number): Promise<Message[]> {
  const { data } = await http.get<Message[]>(`/api/v1/couples/${coupleId}/messages`);
  return data;
}

export async function deleteMessage(coupleId: number, messageId: number): Promise<void> {
  await http.delete(`/api/v1/couples/${coupleId}/messages/${messageId}`);
}

// ========== Countdown (倒计时) ==========
export interface Countdown {
  id: number;
  title: string;
  target_date: string;
  is_yearly: boolean;
  is_pinned: boolean;
  created_at: string;
}

export interface CountdownCreate {
  title: string;
  target_date: string;
  is_yearly?: boolean;
}

export interface CountdownUpdate {
  title?: string;
  target_date?: string;
  is_yearly?: boolean;
  is_pinned?: boolean;
}

export async function addCountdown(coupleId: number, payload: CountdownCreate): Promise<Countdown> {
  const { data } = await http.post<Countdown>(`/api/v1/couples/${coupleId}/countdowns`, payload);
  return data;
}

export async function listCountdowns(coupleId: number): Promise<Countdown[]> {
  const { data } = await http.get<Countdown[]>(`/api/v1/couples/${coupleId}/countdowns`);
  return data;
}

export async function updateCountdown(coupleId: number, countdownId: number, payload: CountdownUpdate): Promise<Countdown> {
  const { data } = await http.patch<Countdown>(`/api/v1/couples/${coupleId}/countdowns/${countdownId}`, payload);
  return data;
}

export async function deleteCountdown(coupleId: number, countdownId: number): Promise<void> {
  await http.delete(`/api/v1/couples/${coupleId}/countdowns/${countdownId}`);
}

// ========== Wish (愿望清单) ==========
export interface Wish {
  id: number;
  title: string;
  progress: number;
  completed: boolean;
  is_pinned: boolean;
  created_at: string;
}

export interface WishCreate {
  title: string;
  progress?: number;
}

export interface WishUpdate {
  title?: string;
  progress?: number;
  completed?: boolean;
  is_pinned?: boolean;
}

export async function addWish(coupleId: number, payload: WishCreate): Promise<Wish> {
  const { data } = await http.post<Wish>(`/api/v1/couples/${coupleId}/wishes`, payload);
  return data;
}

export async function listWishes(coupleId: number): Promise<Wish[]> {
  const { data } = await http.get<Wish[]>(`/api/v1/couples/${coupleId}/wishes`);
  return data;
}

export async function updateWish(coupleId: number, wishId: number, payload: WishUpdate): Promise<Wish> {
  const { data } = await http.patch<Wish>(`/api/v1/couples/${coupleId}/wishes/${wishId}`, payload);
  return data;
}

export async function deleteWish(coupleId: number, wishId: number): Promise<void> {
  await http.delete(`/api/v1/couples/${coupleId}/wishes/${wishId}`);
}
