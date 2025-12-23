import http from "./http";

export interface Photo {
  id: number;
  url: string;
  caption?: string | null;
  created_at: string;
}

export interface PhotoCreate {
  url: string;
  caption?: string | null;
}

export async function addPhoto(coupleId: number, payload: PhotoCreate): Promise<Photo> {
  const { data } = await http.post<Photo>(`/api/v1/media/${coupleId}/photos`, payload);
  return data;
}

export async function listPhotos(coupleId: number): Promise<Photo[]> {
  const { data } = await http.get<Photo[]>(`/api/v1/media/${coupleId}/photos`);
  return data;
}
