import { ParameterControls } from "@/components/editor/ParameterControls";
import { Separator } from "@/components/ui/separator";
import { useEditorStore } from "@/stores/editorStore";
import { motion, AnimatePresence } from "framer-motion";

export function Preview() {
  const { operations, selectedStepId, stepPreviews, uploadedImageUrl } = useEditorStore();
  const selectedOp = operations.find((op) => op.id === selectedStepId);
  const selectedIndex = operations.findIndex((op) => op.id === selectedStepId);
  const previewUrl = selectedIndex >= 0 ? stepPreviews[selectedIndex + 1] : null;
  const imageToShow = previewUrl || uploadedImageUrl;

  return (
    <div className="flex h-full w-80 flex-col border-l border-border bg-background">
      <div className="border-b border-border p-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Preview</h2>
      </div>
      <div className="flex-1 overflow-auto p-4">
        <div className="mb-4 overflow-hidden rounded-lg border border-border bg-muted/30">
          <AnimatePresence mode="wait">
            {imageToShow ? (
              <motion.img key={imageToShow} src={imageToShow} alt="Preview" className="w-full object-contain" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }} />
            ) : (
              <motion.div className="flex h-48 items-center justify-center" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <p className="text-sm text-muted-foreground">No preview available</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        {selectedOp && (
          <>
            <Separator className="my-4" />
            <div>
              <h3 className="mb-3 text-sm font-medium capitalize">{selectedOp.type} Parameters</h3>
              <ParameterControls operation={selectedOp} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
