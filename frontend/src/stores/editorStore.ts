import type { OperationDefinition, PipelineOperation } from "@/types/operation";
import { create } from "zustand";

interface EditorState {
  operations: PipelineOperation[];
  availableOperations: OperationDefinition[];
  selectedStepId: string | null;
  uploadedImageId: string | null;
  uploadedImageUrl: string | null;
  jobId: string | null;
  isExecuting: boolean;
  stepPreviews: Record<number, string>;
  setAvailableOperations: (ops: OperationDefinition[]) => void;
  addOperation: (type: string, defaults: Record<string, number | string>) => void;
  removeOperation: (id: string) => void;
  reorderOperations: (operations: PipelineOperation[]) => void;
  updateOperationParams: (id: string, params: Record<string, number | string>) => void;
  selectStep: (id: string | null) => void;
  setUploadedImage: (id: string, url: string) => void;
  setJobId: (id: string | null) => void;
  setIsExecuting: (v: boolean) => void;
  setStepPreview: (stepNumber: number, url: string) => void;
  clearStepPreviews: () => void;
  reset: () => void;
}

let nextId = 0;

export const useEditorStore = create<EditorState>((set) => ({
  operations: [],
  availableOperations: [],
  selectedStepId: null,
  uploadedImageId: null,
  uploadedImageUrl: null,
  jobId: null,
  isExecuting: false,
  stepPreviews: {},
  setAvailableOperations: (ops) => set({ availableOperations: ops }),
  addOperation: (type, defaults) =>
    set((state) => ({
      operations: [...state.operations, { id: `op-${++nextId}`, type, params: { ...defaults } }],
    })),
  removeOperation: (id) =>
    set((state) => ({
      operations: state.operations.filter((op) => op.id !== id),
      selectedStepId: state.selectedStepId === id ? null : state.selectedStepId,
    })),
  reorderOperations: (operations) => set({ operations }),
  updateOperationParams: (id, params) =>
    set((state) => ({
      operations: state.operations.map((op) => op.id === id ? { ...op, params: { ...op.params, ...params } } : op),
    })),
  selectStep: (id) => set({ selectedStepId: id }),
  setUploadedImage: (id, url) => set({ uploadedImageId: id, uploadedImageUrl: url }),
  setJobId: (id) => set({ jobId: id }),
  setIsExecuting: (v) => set({ isExecuting: v }),
  setStepPreview: (stepNumber, url) =>
    set((state) => ({ stepPreviews: { ...state.stepPreviews, [stepNumber]: url } })),
  clearStepPreviews: () => set({ stepPreviews: {} }),
  reset: () => set({ operations: [], selectedStepId: null, uploadedImageId: null, uploadedImageUrl: null, jobId: null, isExecuting: false, stepPreviews: {} }),
}));
