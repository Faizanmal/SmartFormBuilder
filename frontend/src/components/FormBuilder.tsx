/**
 * Form Builder Component - Drag and Drop Form Designer
 */
'use client';

import React, { useState, useCallback, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { 
  Plus, 
  Trash2, 
  GripVertical, 
  Eye, 
  Code, 
  Settings,
  Mail,
  Phone,
  Calendar,
  Hash,
  AlignLeft,
  CheckSquare,
  Circle,
  List,
  Upload,
  DollarSign
} from 'lucide-react';

// Field type configuration
const FIELD_TYPES = [
  { value: 'text', label: 'Text', icon: AlignLeft },
  { value: 'email', label: 'Email', icon: Mail },
  { value: 'phone', label: 'Phone', icon: Phone },
  { value: 'number', label: 'Number', icon: Hash },
  { value: 'textarea', label: 'Long Text', icon: AlignLeft },
  { value: 'date', label: 'Date', icon: Calendar },
  { value: 'select', label: 'Dropdown', icon: List },
  { value: 'radio', label: 'Radio', icon: Circle },
  { value: 'checkbox', label: 'Checkbox', icon: CheckSquare },
  { value: 'file', label: 'File Upload', icon: Upload },
  { value: 'payment', label: 'Payment', icon: DollarSign },
];

interface Field {
  id: string;
  type: string;
  label: string;
  placeholder?: string;
  required: boolean;
  options?: string[];
  validation?: Record<string, unknown>;
  help?: string;
}

interface FormBuilderProps {
  initialSchema?: {
    title: string;
    description: string;
    fields: Field[];
    logic?: unknown[];
  };
  onSave?: (schema: any) => void;
}

export function FormBuilder({ initialSchema, onSave }: FormBuilderProps) {
  const [title, setTitle] = useState(initialSchema?.title || 'Untitled Form');
  const [description, setDescription] = useState(initialSchema?.description || '');
  const [fields, setFields] = useState<Field[]>(initialSchema?.fields || []);
  const [selectedField, setSelectedField] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'builder' | 'preview' | 'json'>('builder');

  // Generate unique field ID using a stable counter (avoids impure calls during render)
  const idCounter = useRef(0);
  const generateFieldId = useCallback(() => {
    idCounter.current += 1;
    return `f_${idCounter.current}`;
  }, []);

  // Add new field
  const addField = (type: string) => {
    const newField: Field = {
      id: generateFieldId(),
      type,
      label: `New ${type} field`,
      placeholder: '',
      required: false,
      options: type === 'select' || type === 'radio' ? ['Option 1', 'Option 2'] : undefined,
    };
    setFields([...fields, newField]);
    setSelectedField(newField.id);
  };

  // Update field property
  const updateField = (id: string, updates: Partial<Field>) => {
    setFields(fields.map(f => f.id === id ? { ...f, ...updates } : f));
  };

  // Delete field
  const deleteField = (id: string) => {
    setFields(fields.filter(f => f.id !== id));
    if (selectedField === id) setSelectedField(null);
  };

  // Move field up/down
  const moveField = (id: string, direction: 'up' | 'down') => {
    const index = fields.findIndex(f => f.id === id);
    if (index === -1) return;
    if (direction === 'up' && index === 0) return;
    if (direction === 'down' && index === fields.length - 1) return;

    const newFields = [...fields];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    [newFields[index], newFields[targetIndex]] = [newFields[targetIndex], newFields[index]];
    setFields(newFields);
  };

  // Save schema
  const handleSave = () => {
    const schema = {
      title,
      description,
      fields,
      logic: [],
      settings: {},
    };
    onSave?.(schema);
  };

  // Get selected field object
  const selectedFieldObj = fields.find(f => f.id === selectedField);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Sidebar - Field Types */}
      <div className="w-64 bg-white border-r p-4 overflow-y-auto">
        <h3 className="font-semibold mb-4">Field Types</h3>
        <div className="space-y-2">
          {FIELD_TYPES.map(fieldType => {
            const Icon = fieldType.icon;
            return (
              <button
                key={fieldType.value}
                onClick={() => addField(fieldType.value)}
                className="w-full flex items-center gap-2 p-2 rounded hover:bg-gray-100 text-left transition"
              >
                <Icon className="w-4 h-4 text-gray-600" />
                <span className="text-sm">{fieldType.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Center - Form Canvas */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-3xl mx-auto">
          {/* Header Controls */}
          <div className="mb-6 flex items-center justify-between">
            <div className="flex gap-2">
              <Button
                variant={viewMode === 'builder' ? 'default' : 'outline'}
                onClick={() => setViewMode('builder')}
                size="sm"
              >
                <Settings className="w-4 h-4 mr-1" />
                Builder
              </Button>
              <Button
                variant={viewMode === 'preview' ? 'default' : 'outline'}
                onClick={() => setViewMode('preview')}
                size="sm"
              >
                <Eye className="w-4 h-4 mr-1" />
                Preview
              </Button>
              <Button
                variant={viewMode === 'json' ? 'default' : 'outline'}
                onClick={() => setViewMode('json')}
                size="sm"
              >
                <Code className="w-4 h-4 mr-1" />
                JSON
              </Button>
            </div>
            <Button onClick={handleSave}>Save Form</Button>
          </div>

          {viewMode === 'builder' && (
            <Card>
              <CardHeader>
                <Input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="text-2xl font-bold border-none p-0 focus:ring-0"
                  placeholder="Form Title"
                />
                <Textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="text-sm text-gray-600 border-none p-0 focus:ring-0 resize-none"
                  placeholder="Form description..."
                  rows={2}
                />
              </CardHeader>
              <CardContent className="space-y-3">
                {fields.length === 0 ? (
                  <div className="text-center py-12 text-gray-400">
                    <p>No fields yet. Add fields from the left sidebar.</p>
                  </div>
                ) : (
                  fields.map((field, index) => (
                    <div
                      key={field.id}
                      className={`border rounded-lg p-3 cursor-pointer transition ${
                        selectedField === field.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setSelectedField(field.id)}
                    >
                      <div className="flex items-center gap-2">
                        <GripVertical className="w-4 h-4 text-gray-400 cursor-move" />
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{field.label}</span>
                            <Badge variant="secondary" className="text-xs">{field.type}</Badge>
                            {field.required && <Badge variant="destructive" className="text-xs">Required</Badge>}
                          </div>
                          {field.placeholder && (
                            <p className="text-sm text-gray-500 mt-1">{field.placeholder}</p>
                          )}
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteField(field.id);
                          }}
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>
          )}

          {viewMode === 'preview' && (
            <Card>
              <CardHeader>
                <CardTitle>{title}</CardTitle>
                <p className="text-sm text-gray-600">{description}</p>
              </CardHeader>
              <CardContent className="space-y-4">
                {fields.map(field => (
                  <div key={field.id}>
                    <Label>
                      {field.label}
                      {field.required && <span className="text-red-500 ml-1">*</span>}
                    </Label>
                    {field.type === 'textarea' ? (
                      <Textarea placeholder={field.placeholder} />
                    ) : field.type === 'select' ? (
                      <Select>
                        <SelectTrigger>
                          <SelectValue placeholder={field.placeholder || 'Select...'} />
                        </SelectTrigger>
                        <SelectContent>
                          {field.options?.map((opt, i) => (
                            <SelectItem key={i} value={opt}>{opt}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    ) : (
                      <Input type={field.type} placeholder={field.placeholder} />
                    )}
                    {field.help && <p className="text-xs text-gray-500 mt-1">{field.help}</p>}
                  </div>
                ))}
                <Button className="w-full">Submit</Button>
              </CardContent>
            </Card>
          )}

          {viewMode === 'json' && (
            <Card>
              <CardHeader>
                <CardTitle>JSON Schema</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded text-xs overflow-x-auto">
                  {JSON.stringify({ title, description, fields, logic: [], settings: {} }, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Right Sidebar - Field Properties */}
      {selectedFieldObj && (
        <div className="w-80 bg-white border-l p-4 overflow-y-auto">
          <h3 className="font-semibold mb-4">Field Properties</h3>
          <div className="space-y-4">
            <div>
              <Label>Label</Label>
              <Input
                value={selectedFieldObj.label}
                onChange={(e) => updateField(selectedFieldObj.id, { label: e.target.value })}
              />
            </div>
            <div>
              <Label>Placeholder</Label>
              <Input
                value={selectedFieldObj.placeholder || ''}
                onChange={(e) => updateField(selectedFieldObj.id, { placeholder: e.target.value })}
              />
            </div>
            <div>
              <Label>Help Text</Label>
              <Input
                value={selectedFieldObj.help || ''}
                onChange={(e) => updateField(selectedFieldObj.id, { help: e.target.value })}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label>Required</Label>
              <Switch
                checked={selectedFieldObj.required}
                onCheckedChange={(checked) => updateField(selectedFieldObj.id, { required: checked })}
              />
            </div>
            {(selectedFieldObj.type === 'select' || selectedFieldObj.type === 'radio') && (
              <div>
                <Label>Options (one per line)</Label>
                <Textarea
                  value={selectedFieldObj.options?.join('\n') || ''}
                  onChange={(e) => updateField(selectedFieldObj.id, {
                    options: e.target.value.split('\n').filter(Boolean)
                  })}
                  rows={4}
                />
              </div>
            )}
            <Button
              variant="destructive"
              className="w-full"
              onClick={() => deleteField(selectedFieldObj.id)}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete Field
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
