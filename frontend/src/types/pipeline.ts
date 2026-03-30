export interface Pipeline {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  operations: { type: string; params: Record<string, unknown> }[];
  created_at: string;
  updated_at: string;
}

export interface CreatePipelineRequest {
  name: string;
  description?: string;
  operations: { type: string; params: Record<string, unknown> }[];
}
