import type { CreatePipelineRequest, Pipeline } from "@/types/pipeline";
import api from "./api";

export const pipelineService = {
  list: () => api.get<Pipeline[]>("/pipelines").then((r) => r.data),
  get: (id: string) => api.get<Pipeline>(`/pipelines/${id}`).then((r) => r.data),
  create: (data: CreatePipelineRequest) => api.post<Pipeline>("/pipelines", data).then((r) => r.data),
  update: (id: string, data: Partial<CreatePipelineRequest>) => api.put<Pipeline>(`/pipelines/${id}`, data).then((r) => r.data),
  delete: (id: string) => api.delete(`/pipelines/${id}`),
};
