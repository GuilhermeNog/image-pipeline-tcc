export interface JobStep {
  id: string;
  step_number: number;
  operation_type: string;
  operation_params: Record<string, unknown>;
  result_image_path: string | null;
  processing_time_ms: number | null;
  status: "pending" | "processing" | "completed" | "failed";
  created_at: string;
}

export interface Job {
  id: string;
  user_id: string;
  pipeline_id: string | null;
  image_id: string;
  status: "pending" | "processing" | "completed" | "failed";
  current_step: number;
  total_steps: number;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  steps?: JobStep[];
}

export interface JobProgress {
  job_id: string;
  step?: number;
  total?: number;
  operation?: string;
  result_path?: string;
  status: "processing" | "completed" | "failed";
  error?: string;
}
