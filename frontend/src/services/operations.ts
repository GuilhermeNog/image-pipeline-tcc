import type { OperationDefinition } from "@/types/operation";
import api from "./api";

export const operationService = {
  list: () => api.get<{ operations: OperationDefinition[] }>("/operations").then((r) => r.data.operations),
};
