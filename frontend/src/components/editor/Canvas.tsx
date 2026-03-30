import { StepCard } from "@/components/editor/StepCard";
import { Button } from "@/components/ui/button";
import { useEditorStore } from "@/stores/editorStore";
import { imageService } from "@/services/images";
import { jobService } from "@/services/jobs";
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors, type DragEndEvent } from "@dnd-kit/core";
import { SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy, arrayMove } from "@dnd-kit/sortable";
import { AnimatePresence, motion } from "framer-motion";
import { Loader2, Play, Upload } from "lucide-react";
import { useCallback, useRef } from "react";

interface CanvasProps {
  onExecute: (jobId: string) => void;
}

export function Canvas({ onExecute }: CanvasProps) {
  const { operations, reorderOperations, uploadedImageId, uploadedImageUrl, setUploadedImage, isExecuting, setIsExecuting, clearStepPreviews } = useEditorStore();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      const oldIndex = operations.findIndex((op) => op.id === active.id);
      const newIndex = operations.findIndex((op) => op.id === over.id);
      reorderOperations(arrayMove(operations, oldIndex, newIndex));
    }
  };

  const handleUpload = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const image = await imageService.upload(file);
      setUploadedImage(image.id, imageService.getImageUrl(image.id));
    } catch (err) {
      console.error("Upload failed:", err);
    }
  }, [setUploadedImage]);

  const handleExecute = async () => {
    if (!uploadedImageId || operations.length === 0) return;
    setIsExecuting(true);
    clearStepPreviews();
    try {
      const { job_id } = await jobService.execute({
        image_id: uploadedImageId,
        operations: operations.map((op) => ({ type: op.type, params: op.params })),
      });
      onExecute(job_id);
    } catch (err) {
      console.error("Execute failed:", err);
      setIsExecuting(false);
    }
  };

  return (
    <div className="flex flex-1 flex-col">
      <div className="flex items-center justify-between border-b border-border p-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Pipeline</h2>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleExecute} disabled={isExecuting || !uploadedImageId || operations.length === 0}>
            {isExecuting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
            Execute
          </Button>
        </div>
      </div>
      <div className="flex-1 overflow-auto p-4">
        <motion.div
          className={`mb-4 rounded-lg border-2 border-dashed p-4 text-center transition-colors ${uploadedImageUrl ? "border-primary/30 bg-primary/5" : "border-border hover:border-primary/50"}`}
          whileHover={{ scale: uploadedImageUrl ? 1 : 1.01 }}
        >
          {uploadedImageUrl ? (
            <div className="flex items-center gap-3">
              <img src={uploadedImageUrl} alt="Uploaded" className="h-16 w-16 rounded-md object-cover" />
              <div className="flex-1 text-left">
                <p className="text-sm font-medium">Image uploaded</p>
                <Button variant="link" size="sm" className="h-auto p-0" onClick={() => fileInputRef.current?.click()}>Change image</Button>
              </div>
            </div>
          ) : (
            <button className="flex w-full flex-col items-center gap-2 py-4" onClick={() => fileInputRef.current?.click()}>
              <Upload className="h-8 w-8 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">Click to upload an image</p>
            </button>
          )}
          <input ref={fileInputRef} type="file" accept="image/jpeg,image/png,image/bmp,image/tiff" className="hidden" onChange={handleUpload} />
        </motion.div>
        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
          <SortableContext items={operations.map((op) => op.id)} strategy={verticalListSortingStrategy}>
            <div className="space-y-2">
              <AnimatePresence>
                {operations.map((op, index) => (
                  <StepCard key={op.id} operation={op} index={index} />
                ))}
              </AnimatePresence>
            </div>
          </SortableContext>
        </DndContext>
        {operations.length === 0 && (
          <p className="mt-8 text-center text-sm text-muted-foreground">Click operations on the sidebar to add them to your pipeline</p>
        )}
      </div>
    </div>
  );
}
