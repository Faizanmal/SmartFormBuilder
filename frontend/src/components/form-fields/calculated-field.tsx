"use client";

import { useMemo } from "react";
import { Label } from "@/components/ui/label";
import { Calculator } from "lucide-react";
import type { FormField } from "@/types";

interface CalculatedFieldProps {
  field: FormField;
  formData: Record<string, unknown>;
}

export function CalculatedField({ field, formData }: CalculatedFieldProps) {
  const calculatedValue = useMemo(() => {
    if (!field.formula) {
      return null;
    }

    try {
      // Replace field references with actual values
      let expression = field.formula;
      const fieldMatches = expression.match(/\{([^}]+)\}/g);
      
      if (fieldMatches) {
        for (const match of fieldMatches) {
          const fieldId = match.slice(1, -1); // Remove { and }
          const value = formData[fieldId];
          
          if (value === undefined || value === '' || isNaN(Number(value))) {
            return null;
          }
          
          expression = expression.replace(match, String(Number(value)));
        }
      }

      // Evaluate the expression safely
      // Only allow numbers, operators, and parentheses
      if (!/^[\d\s+\-*/().]+$/.test(expression)) {
        return null;
      }

      // Use Function constructor for safe evaluation
      const result = new Function(`return ${expression}`)();
      
      if (typeof result === 'number' && !isNaN(result) && isFinite(result)) {
        return result;
      } else {
        return null;
      }
    } catch {
      return null;
    }
  }, [field.formula, formData]);

  const formatValue = (value: number | null) => {
    if (value === null) return '—';

    switch (field.displayFormat) {
      case 'currency':
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD'
        }).format(value);
      case 'percentage':
        return `${value.toFixed(2)}%`;
      default:
        return value.toLocaleString('en-US', { maximumFractionDigits: 2 });
    }
  };

  return (
    <div className="space-y-2">
      <Label>
        {field.label}
        <Calculator className="inline-block w-4 h-4 ml-2 text-muted-foreground" />
      </Label>
      
      <div className="p-4 bg-gray-50 rounded-lg border">
        <div className="text-2xl font-bold text-primary">
          {formatValue(calculatedValue)}
        </div>
        {field.help && (
          <p className="text-xs text-muted-foreground mt-1">{field.help}</p>
        )}
      </div>
    </div>
  );
}
