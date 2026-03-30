import type { Job } from "@/types/job";
import api from "./api";

export interface ExecuteJobRequest {
  image_id: string;
  pipeline_id?: string;
  operations: { type: string; params: Record<string, unknown> }[];
}

export const jobService = {
  execute: (data: ExecuteJobRequest) => api.post<{ job_id: string }>("/jobs/execute", data).then((r) => r.data),
  list: (limit = 50, offset = 0) => api.get<Job[]>(`/jobs?limit=${limit}&offset=${offset}`).then((r) => r.data),
  get: (id: string) => api.get<Job>(`/jobs/${id}`).then((r) => r.data),
  delete: (id: string) => api.delete(`/jobs/${id}`),
};
