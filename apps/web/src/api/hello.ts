import http from "./http";

export interface HelloResponse {
  status: string;
  data: {
    greeting: string;
  };
}

export async function sayHello(name: string): Promise<HelloResponse> {
  const { data } = await http.get<HelloResponse>("/api/v1/hello", {
    params: { name },
  });
  return data;
}
