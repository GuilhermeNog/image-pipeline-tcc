import { Canvas } from "@/components/editor/Canvas";
import { Preview } from "@/components/editor/Preview";
import { ProgressOverlay } from "@/components/editor/ProgressOverlay";
import { Sidebar } from "@/components/editor/Sidebar";
import { useEditorStore } from "@/stores/editorStore";
import { useWebSocket } from "@/hooks/useWebSocket";
import { operationService } from "@/services/operations";
import { imageService } from "@/services/images";
import type { JobProgress } from "@/types/job";
import { useCallback, useEffect } from "react";
import { toast } from "sonner";

export function EditorPage() {
  const { setAvailableOperations, setJobId, setIsExecuting, setStepPreview, jobId } = useEditorStore();

  useEffect(() => {
    operationService.list().then(setAvailableOperations);
  }, [setAvailableOperations]);

  const handleProgress = useCallback(
    (data: JobProgress) => {
      if (data.step && data.result_path) {
        const url = imageService.getStepImageUrl(data.job_id, data.step);
        setStepPreview(data.step, url);
      }
    },
    [setStepPreview]
  );

  const handleComplete = useCallback(
    (_data: JobProgress) => {
      setIsExecuting(false);
      toast.success("Pipeline executed successfully!");
    },
    [setIsExecuting]
  );

  const handleError = useCallback(
    (data: JobProgress) => {
      setIsExecuting(false);
      toast.error(data.error || "Pipeline execution failed");
    },
    [setIsExecuting]
  );

  useWebSocket({ jobId, onProgress: handleProgress, onComplete: handleComplete, onError: handleError });

  const handleExecute = (newJobId: string) => {
    setJobId(newJobId);
  };

  return (
    <div className="relative flex h-[calc(100vh-3.5rem)]">
      <Sidebar />
      <Canvas onExecute={handleExecute} />
      <Preview />
      <ProgressOverlay />
    </div>
  );
}
