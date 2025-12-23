import http from "./http";

export interface Couple {
  id: number;
  name: string;
  partner_a_name?: string | null;
  partner_b_name?: string | null;
  start_date?: string | null;
  created_at: string;
}

export interface CoupleCreate {
  name: string;
  partner_a_name?: string | null;
  partner_b_name?: string | null;
  start_date?: string | null;
}

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

export async function createCouple(payload: CoupleCreate): Promise<Couple> {
  const { data } = await http.post<Couple>("/api/v1/couples", payload);
  return data;
}

export async function fetchMyCouple(): Promise<Couple | null> {
  const { data } = await http.get<Couple | null>("/api/v1/couples/me");
  return data;
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
