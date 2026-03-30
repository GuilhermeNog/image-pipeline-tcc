import { useEditorStore } from "@/stores/editorStore";
import { motion } from "framer-motion";

export function ProgressOverlay() {
  const { isExecuting, operations, stepPreviews } = useEditorStore();
  if (!isExecuting) return null;

  const completedSteps = Object.keys(stepPreviews).length;
  const totalSteps = operations.length;
  const progress = totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0;

  return (
    <div className="absolute inset-x-0 bottom-0 border-t border-border bg-background/95 p-4 backdrop-blur">
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">Processing step {completedSteps}/{totalSteps}</span>
        <span className="font-mono text-xs">{Math.round(progress)}%</span>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-secondary">
        <motion.div className="h-full bg-primary" initial={{ width: 0 }} animate={{ width: `${progress}%` }} transition={{ duration: 0.3 }} />
      </div>
    </div>
  );
}
