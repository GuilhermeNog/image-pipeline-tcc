import { Card } from "@/components/ui/card";
import type { OperationDefinition } from "@/types/operation";
import { motion } from "framer-motion";
import { Contrast, Crop, Eye, Maximize, RotateCw, ScanLine, Shrink, Sparkles, Sun, Waves } from "lucide-react";

const OPERATION_ICONS: Record<string, React.ReactNode> = {
  grayscale: <Contrast className="h-4 w-4" />,
  blur: <Waves className="h-4 w-4" />,
  threshold: <ScanLine className="h-4 w-4" />,
  canny: <Eye className="h-4 w-4" />,
  dilate: <Maximize className="h-4 w-4" />,
  erode: <Shrink className="h-4 w-4" />,
  brightness: <Sun className="h-4 w-4" />,
  contrast: <Sparkles className="h-4 w-4" />,
  resize: <Crop className="h-4 w-4" />,
  rotate: <RotateCw className="h-4 w-4" />,
};

interface OperationCardProps {
  operation: OperationDefinition;
  onAdd: () => void;
}

export function OperationCard({ operation, onAdd }: OperationCardProps) {
  return (
    <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
      <Card className="cursor-pointer p-3 transition-colors hover:bg-accent" onClick={onAdd}>
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
            {OPERATION_ICONS[operation.name] || <Sparkles className="h-4 w-4" />}
          </div>
          <div>
            <p className="text-sm font-medium capitalize">{operation.name}</p>
            <p className="text-xs text-muted-foreground">{Object.keys(operation.params).length} params</p>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
