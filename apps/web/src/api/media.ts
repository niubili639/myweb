import http from "./http";

export interface Photo {
  id: number;
  url: string;
  thumbnail_url?: string | null;
  caption?: string | null;
  image_key?: string | null;
  space_type: string;
  space_id?: number | null;
  created_at: string;
}

export interface PhotoCreate {
  url: string;
  thumbnail_url?: string | null;
  caption?: string | null;
  image_key?: string | null;
  space_type?: string;
  space_id?: number | null;
}

// 新接口：按空间类型
export async function createPhoto(payload: PhotoCreate): Promise<Photo> {
  const { data } = await http.post<Photo>("/api/v1/media/photos", payload);
  return data;
}

export async function getPhotos(spaceType: string = "couple"): Promise<Photo[]> {
  const { data } = await http.get<Photo[]>("/api/v1/media/photos", {
    params: { space_type: spaceType },
  });
  return data;
}

export async function deletePhoto(photoId: number): Promise<void> {
  await http.delete(`/api/v1/media/photos/${photoId}`);
}

// 旧接口：兼容
export async function addPhoto(coupleId: number, payload: { url: string; caption?: string | null }): Promise<Photo> {
  const { data } = await http.post<Photo>(`/api/v1/media/${coupleId}/photos`, payload);
  return data;
}

export async function listPhotos(coupleId: number): Promise<Photo[]> {
  const { data } = await http.get<Photo[]>(`/api/v1/media/${coupleId}/photos`);
  return data;
}
