export interface OperationParamSchema {
  type: string;
  min?: number;
  max?: number;
  default?: number | string;
  step?: number;
  label?: string;
  options?: (string | number)[];
}

export interface OperationDefinition {
  name: string;
  params: Record<string, OperationParamSchema>;
}

export interface PipelineOperation {
  id: string;
  type: string;
  params: Record<string, number | string>;
}
