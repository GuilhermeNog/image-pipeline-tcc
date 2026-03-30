import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useEditorStore } from "@/stores/editorStore";
import type { PipelineOperation } from "@/types/operation";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { motion } from "framer-motion";
import { GripVertical, Trash2 } from "lucide-react";

interface StepCardProps {
  operation: PipelineOperation;
  index: number;
}

export function StepCard({ operation, index }: StepCardProps) {
  const { selectedStepId, selectStep, removeOperation, stepPreviews, isExecuting } = useEditorStore();
  const isSelected = selectedStepId === operation.id;

  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: operation.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const hasPreview = stepPreviews[index + 1] !== undefined;

  return (
    <motion.div ref={setNodeRef} style={style} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} transition={{ duration: 0.2 }}>
      <Card
        className={`flex items-center gap-3 p-3 cursor-pointer transition-all ${isSelected ? "ring-2 ring-primary border-primary" : "hover:border-primary/50"}`}
        onClick={() => selectStep(operation.id)}
      >
        <button className="cursor-grab text-muted-foreground hover:text-foreground" {...attributes} {...listeners}>
          <GripVertical className="h-4 w-4" />
        </button>
        <Badge variant="outline" className="font-mono text-xs">{index + 1}</Badge>
        <span className="flex-1 text-sm font-medium capitalize">{operation.type}</span>
        {hasPreview && <div className="h-2 w-2 rounded-full bg-green-500" />}
        {isExecuting && !hasPreview && <div className="h-2 w-2 animate-pulse rounded-full bg-yellow-500" />}
        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={(e) => { e.stopPropagation(); removeOperation(operation.id); }}>
          <Trash2 className="h-3 w-3" />
        </Button>
      </Card>
    </motion.div>
  );
}
