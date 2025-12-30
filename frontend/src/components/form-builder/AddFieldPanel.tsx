"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { FIELD_TYPES, getDefaultFieldConfig } from "./FieldTypeSelector";
import { X } from "lucide-react";

interface AddFieldPanelProps {
  onSelect: (type: string) => void;
  onClose?: () => void;
}

export function AddFieldPanel({ onSelect, onClose }: AddFieldPanelProps) {
  // Group field types by category
  const basicFields = FIELD_TYPES.filter(t =>
    ['text', 'email', 'phone', 'textarea', 'number', 'date', 'time', 'url'].includes(t.value)
  );
  
  const choiceFields = FIELD_TYPES.filter(t =>
    ['select', 'multiselect', 'checkbox', 'radio'].includes(t.value)
  );
  
  const advancedFields = FIELD_TYPES.filter(t =>
    ['file', 'payment', 'slider', 'rating', 'signature', 'address', 'calculated'].includes(t.value)
  );
  
  const layoutFields = FIELD_TYPES.filter(t =>
    ['heading', 'divider'].includes(t.value)
  );

  const renderFieldGroup = (title: string, fields: typeof FIELD_TYPES) => (
    <div className="space-y-2">
      <h3 className="font-semibold text-sm text-muted-foreground">{title}</h3>
      <div className="grid grid-cols-1 gap-2">
        {fields.map((field) => {
          const Icon = field.icon;
          return (
            <Button
              key={field.value}
              variant="outline"
              className="justify-start h-auto py-3 px-3"
              onClick={() => onSelect(field.value)}
            >
              <div className="flex items-start gap-3 w-full">
                <Icon className="h-5 w-5 mt-0.5 shrink-0" />
                <div className="text-left flex-1">
                  <div className="font-medium">{field.label}</div>
                  <div className="text-xs text-muted-foreground">{field.description}</div>
                </div>
              </div>
            </Button>
          );
        })}
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {onClose && (
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Add Field</h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      )}
      
      {renderFieldGroup("Basic Fields", basicFields)}
      {renderFieldGroup("Choice Fields", choiceFields)}
      {renderFieldGroup("Advanced Fields", advancedFields)}
      {renderFieldGroup("Layout", layoutFields)}
    </div>
  );
}
