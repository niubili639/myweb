import http from "./http";

export interface HealthResponse {
  status: string;
  data: {
    service: string;
    version: string;
    time: string;
  };
}

export async function fetchHealth(): Promise<HealthResponse> {
  const { data } = await http.get<HealthResponse>("/api/v1/health");
  return data;
}
