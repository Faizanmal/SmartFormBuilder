"use client";

import React from "react";
import { FormField } from "@/types";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FieldTypeSelector } from "./FieldTypeSelector";
import { Plus, Trash2, GripVertical } from "lucide-react";

interface FieldEditorProps {
  field: FormField;
  index: number;
  onUpdate: (updates: Partial<FormField>) => void;
  onDelete: () => void;
  onDuplicate: () => void;
  onMoveUp?: () => void;
  onMoveDown?: () => void;
  isFirst?: boolean;
  isLast?: boolean;
  isSelected?: boolean;
  onSelect?: () => void;
}

export function FieldEditor({ 
  field, 
  index,
  onUpdate, 
  onDelete, 
  onDuplicate,
  onMoveUp,
  onMoveDown,
  isFirst,
  isLast,
  isSelected,
  onSelect
}: FieldEditorProps) {
  const hasOptions = ['select', 'multiselect', 'radio'].includes(field.type);
  const hasSlider = field.type === 'slider';
  const hasRating = field.type === 'rating';
  const hasFile = field.type === 'file';
  const hasAddress = field.type === 'address';
  const hasHeading = field.type === 'heading';
  const hasPayment = field.type === 'payment';
  const hasCalculated = field.type === 'calculated';
  const isNonInput = ['heading', 'divider'].includes(field.type);

  return (
    <Card>
      <CardContent className="pt-6 space-y-4">
        {/* Header with drag handle */}
        <div className="flex items-center gap-2">
          <GripVertical className="h-5 w-5 text-muted-foreground cursor-grab" />
          <div className="flex-1 font-medium">
            {field.label}
            <span className="text-sm text-muted-foreground ml-2">({field.type})</span>
          </div>
          <div className="flex gap-1">
            {!isFirst && onMoveUp && (
              <Button variant="ghost" size="sm" onClick={onMoveUp} title="Move up">
                ↑
              </Button>
            )}
            {!isLast && onMoveDown && (
              <Button variant="ghost" size="sm" onClick={onMoveDown} title="Move down">
                ↓
              </Button>
            )}
            <Button variant="ghost" size="sm" onClick={onDuplicate} title="Duplicate">
              <Plus className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={onDelete} title="Delete">
              <Trash2 className="h-4 w-4 text-destructive" />
            </Button>
          </div>
        </div>

        {/* Field Type */}
        <div>
          <Label>Field Type</Label>
          <FieldTypeSelector 
            value={field.type} 
            onChange={(type) => onUpdate({ type })}
          />
        </div>

        {/* Label */}
        {!isNonInput && (
          <div>
            <Label>Label</Label>
            <Input 
              value={field.label} 
              onChange={(e) => onUpdate({ label: e.target.value })}
              placeholder="Field label"
            />
          </div>
        )}

        {/* Heading Level */}
        {hasHeading && (
          <div>
            <Label>Heading Level</Label>
            <select
              className="w-full border rounded-md p-2"
              value={field.headingLevel || 'h2'}
              onChange={(e) => onUpdate({ headingLevel: e.target.value as any })}
            >
              <option value="h1">H1 - Main Title</option>
              <option value="h2">H2 - Section Title</option>
              <option value="h3">H3 - Subsection</option>
              <option value="h4">H4 - Minor Heading</option>
            </select>
          </div>
        )}

        {/* Placeholder */}
        {!isNonInput && !['checkbox', 'radio', 'file', 'rating', 'signature'].includes(field.type) && (
          <div>
            <Label>Placeholder</Label>
            <Input 
              value={field.placeholder || ''} 
              onChange={(e) => onUpdate({ placeholder: e.target.value })}
              placeholder="Placeholder text"
            />
          </div>
        )}

        {/* Help Text */}
        {!isNonInput && (
          <div>
            <Label>Help Text (Optional)</Label>
            <Input 
              value={field.help || ''} 
              onChange={(e) => onUpdate({ help: e.target.value })}
              placeholder="Additional help for users"
            />
          </div>
        )}

        {/* Options for select/radio/multiselect */}
        {hasOptions && (
          <div>
            <Label>Options</Label>
            {(field.options || []).map((option, idx) => {
              const label = typeof option === 'string' ? option : option.label;
              
              return (
                <div key={idx} className="flex gap-2 mb-2">
                  <Input 
                    value={label} 
                    onChange={(e) => {
                      const newOptions = [...(field.options || [])];
                      // Always use FieldOption format
                      const newValue = e.target.value;
                      newOptions[idx] = { 
                        label: newValue, 
                        value: newValue.toLowerCase().replace(/\s+/g, '_') 
                      };
                      onUpdate({ options: newOptions });
                    }}
                    placeholder={`Option ${idx + 1}`}
                  />
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      const newOptions = (field.options || []).filter((_, i) => i !== idx);
                      onUpdate({ options: newOptions });
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              );
            })}
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const newOption = { 
                  label: `Option ${(field.options?.length || 0) + 1}`, 
                  value: `option_${(field.options?.length || 0) + 1}` 
                };
                onUpdate({ options: [...(field.options || []), newOption] });
              }}
            >
              <Plus className="h-4 w-4 mr-1" /> Add Option
            </Button>
          </div>
        )}

        {/* Slider Settings */}
        {hasSlider && (
          <div className="space-y-2">
            <div className="grid grid-cols-3 gap-2">
              <div>
                <Label>Min</Label>
                <Input 
                  type="number" 
                  value={field.sliderMin || 0}
                  onChange={(e) => onUpdate({ sliderMin: Number(e.target.value) })}
                />
              </div>
              <div>
                <Label>Max</Label>
                <Input 
                  type="number" 
                  value={field.sliderMax || 100}
                  onChange={(e) => onUpdate({ sliderMax: Number(e.target.value) })}
                />
              </div>
              <div>
                <Label>Step</Label>
                <Input 
                  type="number" 
                  value={field.sliderStep || 1}
                  onChange={(e) => onUpdate({ sliderStep: Number(e.target.value) })}
                />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Switch 
                checked={field.showValue !== false}
                onCheckedChange={(checked) => onUpdate({ showValue: checked })}
              />
              <Label>Show value</Label>
            </div>
          </div>
        )}

        {/* Rating Settings */}
        {hasRating && (
          <div className="space-y-2">
            <div>
              <Label>Max Rating</Label>
              <Input 
                type="number" 
                value={field.maxRating || 5}
                onChange={(e) => onUpdate({ maxRating: Number(e.target.value) })}
                min="1"
                max="10"
              />
            </div>
            <div>
              <Label>Icon</Label>
              <select
                className="w-full border rounded-md p-2"
                value={field.ratingIcon || 'star'}
                onChange={(e) => onUpdate({ ratingIcon: e.target.value as any })}
              >
                <option value="star">Star</option>
                <option value="heart">Heart</option>
                <option value="thumbsup">Thumbs Up</option>
              </select>
            </div>
          </div>
        )}

        {/* File Settings */}
        {hasFile && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Switch 
                checked={field.allowMultiple || false}
                onCheckedChange={(checked) => onUpdate({ allowMultiple: checked })}
              />
              <Label>Allow multiple files</Label>
            </div>
            {field.allowMultiple && (
              <div>
                <Label>Max Files</Label>
                <Input 
                  type="number" 
                  value={field.maxFiles || 5}
                  onChange={(e) => onUpdate({ maxFiles: Number(e.target.value) })}
                  min="1"
                />
              </div>
            )}
          </div>
        )}

        {/* Address Settings */}
        {hasAddress && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Switch 
                checked={field.includeCountry !== false}
                onCheckedChange={(checked) => onUpdate({ includeCountry: checked })}
              />
              <Label>Include country</Label>
            </div>
            <div className="flex items-center gap-2">
              <Switch 
                checked={field.includeZip !== false}
                onCheckedChange={(checked) => onUpdate({ includeZip: checked })}
              />
              <Label>Include ZIP code</Label>
            </div>
          </div>
        )}

        {/* Payment Settings */}
        {hasPayment && (
          <div className="space-y-2">
            <div>
              <Label>Amount (cents)</Label>
              <Input 
                type="number" 
                value={field.amount || 0}
                onChange={(e) => onUpdate({ amount: Number(e.target.value) })}
                placeholder="e.g., 5000 for $50.00"
              />
            </div>
            <div>
              <Label>Currency</Label>
              <Input 
                value={field.currency || 'USD'}
                onChange={(e) => onUpdate({ currency: e.target.value })}
                placeholder="USD"
              />
            </div>
          </div>
        )}

        {/* Calculated Field Settings */}
        {hasCalculated && (
          <div className="space-y-2">
            <div>
              <Label>Formula</Label>
              <Textarea 
                value={field.formula || ''}
                onChange={(e) => onUpdate({ formula: e.target.value })}
                placeholder="e.g., {field_1} * {field_2} + 100"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Use {"{field_id}"} to reference other fields
              </p>
            </div>
            <div>
              <Label>Display Format</Label>
              <select
                className="w-full border rounded-md p-2"
                value={field.displayFormat || 'number'}
                onChange={(e) => onUpdate({ displayFormat: e.target.value as any })}
              >
                <option value="number">Number</option>
                <option value="currency">Currency</option>
                <option value="percentage">Percentage</option>
              </select>
            </div>
          </div>
        )}

        {/* Required Toggle */}
        {!isNonInput && (
          <div className="flex items-center gap-2 pt-2 border-t">
            <Switch 
              checked={field.required || false}
              onCheckedChange={(checked) => onUpdate({ required: checked })}
            />
            <Label>Required field</Label>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
