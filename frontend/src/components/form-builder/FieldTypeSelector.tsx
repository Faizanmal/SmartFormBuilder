"use client";

import React from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  Type, Mail, Phone, MessageSquare, Hash, Calendar, Clock, 
  List, CheckSquare, Circle, Upload, Link, CreditCard,
  SlidersHorizontal, Star, PenTool, MapPin, Heading, Minus
} from "lucide-react";

export type FieldType = 
  | 'text' | 'email' | 'phone' | 'textarea' | 'number' | 'date' | 'time'
  | 'select' | 'multiselect' | 'checkbox' | 'radio' | 'file' | 'url' | 'payment'
  | 'slider' | 'rating' | 'signature' | 'address' | 'heading' | 'divider' | 'calculated';

interface FieldTypeOption {
  value: FieldType;
  label: string;
  icon: React.ElementType;
  description: string;
}

export const FIELD_TYPES: FieldTypeOption[] = [
  { value: 'text', label: 'Text', icon: Type, description: 'Short text input' },
  { value: 'email', label: 'Email', icon: Mail, description: 'Email address' },
  { value: 'phone', label: 'Phone', icon: Phone, description: 'Phone number' },
  { value: 'textarea', label: 'Textarea', icon: MessageSquare, description: 'Long text input' },
  { value: 'number', label: 'Number', icon: Hash, description: 'Numeric input' },
  { value: 'date', label: 'Date', icon: Calendar, description: 'Date picker' },
  { value: 'time', label: 'Time', icon: Clock, description: 'Time picker' },
  { value: 'select', label: 'Select', icon: List, description: 'Dropdown menu' },
  { value: 'multiselect', label: 'Multi-select', icon: CheckSquare, description: 'Multiple choices' },
  { value: 'checkbox', label: 'Checkbox', icon: CheckSquare, description: 'Single checkbox' },
  { value: 'radio', label: 'Radio', icon: Circle, description: 'Radio buttons' },
  { value: 'file', label: 'File Upload', icon: Upload, description: 'File attachment' },
  { value: 'url', label: 'URL', icon: Link, description: 'Website URL' },
  { value: 'payment', label: 'Payment', icon: CreditCard, description: 'Payment field' },
  { value: 'slider', label: 'Slider', icon: SlidersHorizontal, description: 'Range slider' },
  { value: 'rating', label: 'Rating', icon: Star, description: 'Star rating' },
  { value: 'signature', label: 'Signature', icon: PenTool, description: 'Digital signature' },
  { value: 'address', label: 'Address', icon: MapPin, description: 'Full address' },
  { value: 'calculated', label: 'Calculated', icon: Hash, description: 'Auto-calculated field' },
  { value: 'heading', label: 'Heading', icon: Heading, description: 'Section heading' },
  { value: 'divider', label: 'Divider', icon: Minus, description: 'Visual separator' },
];

interface FieldTypeSelectorProps {
  value: FieldType;
  onChange: (value: FieldType) => void;
  disabled?: boolean;
}

export function FieldTypeSelector({ value, onChange, disabled }: FieldTypeSelectorProps) {
  const selectedType = FIELD_TYPES.find(t => t.value === value);

  return (
    <Select value={value} onValueChange={onChange} disabled={disabled}>
      <SelectTrigger className="w-full">
        <SelectValue>
          <div className="flex items-center gap-2">
            {selectedType && (
              <>
                <selectedType.icon className="h-4 w-4" />
                <span>{selectedType.label}</span>
              </>
            )}
          </div>
        </SelectValue>
      </SelectTrigger>
      <SelectContent className="max-h-[400px]">
        {FIELD_TYPES.map((type) => (
          <SelectItem key={type.value} value={type.value}>
            <div className="flex items-center gap-2">
              <type.icon className="h-4 w-4" />
              <div>
                <div className="font-medium">{type.label}</div>
                <div className="text-xs text-muted-foreground">{type.description}</div>
              </div>
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

// Helper to get default field configuration by type
export function getDefaultFieldConfig(type: FieldType, id: string) {
  const baseConfig = {
    id,
    type,
    label: FIELD_TYPES.find(t => t.value === type)?.label || 'Field',
    placeholder: '',
    required: false,
  };

  switch (type) {
    case 'select':
    case 'multiselect':
    case 'radio':
      return { ...baseConfig, options: ['Option 1', 'Option 2', 'Option 3'] };
    
    case 'slider':
      return { ...baseConfig, sliderMin: 0, sliderMax: 100, sliderStep: 1, showValue: true };
    
    case 'rating':
      return { ...baseConfig, maxRating: 5, ratingIcon: 'star' as const };
    
    case 'file':
      return { ...baseConfig, allowMultiple: false, maxFiles: 1 };
    
    case 'address':
      return { ...baseConfig, includeCountry: true, includeZip: true };
    
    case 'heading':
      return { ...baseConfig, headingLevel: 'h2' as const };
    
    case 'payment':
      return { ...baseConfig, amount: 0, currency: 'USD' };
    
    case 'calculated':
      return { ...baseConfig, formula: '', displayFormat: 'number' as const };
    
    default:
      return baseConfig;
  }
}
