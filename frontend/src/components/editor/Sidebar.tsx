import { OperationCard } from "@/components/editor/OperationCard";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useEditorStore } from "@/stores/editorStore";

export function Sidebar() {
  const { availableOperations, addOperation } = useEditorStore();

  const handleAdd = (op: (typeof availableOperations)[0]) => {
    const defaults: Record<string, number | string> = {};
    for (const [key, schema] of Object.entries(op.params)) {
      if (schema.default !== undefined) {
        defaults[key] = schema.default;
      }
    }
    addOperation(op.name, defaults);
  };

  return (
    <div className="flex h-full w-64 flex-col border-r border-border bg-background">
      <div className="border-b border-border p-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Operations</h2>
      </div>
      <ScrollArea className="flex-1 p-3">
        <div className="space-y-2">
          {availableOperations.map((op) => (
            <OperationCard key={op.name} operation={op} onAdd={() => handleAdd(op)} />
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
