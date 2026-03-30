import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useEditorStore } from "@/stores/editorStore";
import type { OperationParamSchema, PipelineOperation } from "@/types/operation";

interface ParameterControlsProps {
  operation: PipelineOperation;
}

export function ParameterControls({ operation }: ParameterControlsProps) {
  const { availableOperations, updateOperationParams } = useEditorStore();
  const opDef = availableOperations.find((o) => o.name === operation.type);

  if (!opDef || Object.keys(opDef.params).length === 0) {
    return <p className="text-sm text-muted-foreground">No parameters</p>;
  }

  const handleChange = (key: string, value: number | string) => {
    updateOperationParams(operation.id, { [key]: value });
  };

  return (
    <div className="space-y-4">
      {Object.entries(opDef.params).map(([key, schema]) => (
        <ParameterField key={key} name={key} schema={schema} value={operation.params[key]} onChange={(v) => handleChange(key, v)} />
      ))}
    </div>
  );
}

interface ParameterFieldProps {
  name: string;
  schema: OperationParamSchema;
  value: number | string | undefined;
  onChange: (value: number | string) => void;
}

function ParameterField({ name, schema, value, onChange }: ParameterFieldProps) {
  const label = schema.label || name;

  if (schema.type === "select" && schema.options) {
    return (
      <div className="space-y-2">
        <Label className="text-xs">{label}</Label>
        <Select value={String(value ?? schema.default)} onValueChange={(v) => onChange(isNaN(Number(v)) ? v : Number(v))}>
          <SelectTrigger><SelectValue /></SelectTrigger>
          <SelectContent>
            {schema.options.map((opt) => (
              <SelectItem key={String(opt)} value={String(opt)}>{String(opt)}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    );
  }

  if ((schema.type === "int" || schema.type === "float") && schema.min !== undefined && schema.max !== undefined) {
    const numValue = Number(value ?? schema.default ?? schema.min);
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label className="text-xs">{label}</Label>
          <span className="text-xs text-muted-foreground">{numValue}</span>
        </div>
        <Slider min={schema.min} max={schema.max} step={schema.step || (schema.type === "float" ? 0.1 : 1)} value={[numValue]} onValueChange={([v]) => onChange(v)} />
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <Label className="text-xs">{label}</Label>
      <Input type="number" value={value ?? schema.default ?? ""} onChange={(e) => onChange(Number(e.target.value))} />
    </div>
  );
}
