"use client";

import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import type { FormField } from "@/types";

interface SliderFieldProps {
  field: FormField;
  value: number;
  onChange: (value: number) => void;
}

export function SliderField({ field, value, onChange }: SliderFieldProps) {
  const min = field.sliderMin ?? 0;
  const max = field.sliderMax ?? 100;
  const step = field.sliderStep ?? 1;
  const showValue = field.showValue !== false;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <Label htmlFor={field.id}>
          {field.label}
          {field.required && <span className="text-red-500 ml-1">*</span>}
        </Label>
        {showValue && (
          <span className="text-sm font-medium bg-primary/10 text-primary px-2 py-1 rounded">
            {value ?? min}
          </span>
        )}
      </div>
      <div className="px-2">
        <Slider
          id={field.id}
          min={min}
          max={max}
          step={step}
          value={[value ?? min]}
          onValueChange={(values) => onChange(values[0])}
          className="w-full"
        />
        <div className="flex justify-between mt-1">
          <span className="text-xs text-muted-foreground">{min}</span>
          <span className="text-xs text-muted-foreground">{max}</span>
        </div>
      </div>
      {field.help && (
        <p className="text-xs text-muted-foreground">{field.help}</p>
      )}
    </div>
  );
}
