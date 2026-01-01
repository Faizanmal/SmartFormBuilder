/**
 * Interactive Form Preview Component with Drag-and-Drop
 * Allows real-time field reordering with smooth animations
 */
'use client';

import React, { useState, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import {
  GripVertical,
  Trash2,
  Copy,
  Settings,
  Eye,
  EyeOff,
  Lock,
  Unlock,
  ChevronUp,
  ChevronDown,
  Maximize2,
  Minimize2,
  Smartphone,
  Monitor,
  Tablet,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface FormField {
  id: string;
  type: string;
  label: string;
  placeholder?: string;
  required?: boolean;
  options?: string[];
  help?: string;
  validation?: Record<string, unknown>;
}

interface InteractiveFormPreviewProps {
  title: string;
  description?: string;
  fields: FormField[];
  onFieldsChange: (fields: FormField[]) => void;
  onFieldSelect?: (fieldId: string | null) => void;
  onFieldDelete?: (fieldId: string) => void;
  onFieldDuplicate?: (fieldId: string) => void;
  selectedFieldId?: string | null;
  readOnly?: boolean;
}

type DeviceType = 'desktop' | 'tablet' | 'mobile';

export function InteractiveFormPreview({
  title,
  description,
  fields,
  onFieldsChange,
  onFieldSelect,
  onFieldDelete,
  onFieldDuplicate,
  selectedFieldId,
  readOnly = false,
}: InteractiveFormPreviewProps) {
  const [draggedFieldId, setDraggedFieldId] = useState<string | null>(null);
  const [dragOverFieldId, setDragOverFieldId] = useState<string | null>(null);
  const [dragPosition, setDragPosition] = useState<'above' | 'below'>('below');
  const [hoveredFieldId, setHoveredFieldId] = useState<string | null>(null);
  const [lockedFields, setLockedFields] = useState<Set<string>>(new Set());
  const [collapsedFields, setCollapsedFields] = useState<Set<string>>(new Set());
  const [deviceView, setDeviceView] = useState<DeviceType>('desktop');
  const [showFieldValues, setShowFieldValues] = useState(true);
  
  const dragRef = useRef<{ startY: number; fieldId: string } | null>(null);

  // Handle drag start
  const handleDragStart = useCallback((e: React.DragEvent, fieldId: string) => {
    if (lockedFields.has(fieldId) || readOnly) {
      e.preventDefault();
      return;
    }
    
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', fieldId);
    setDraggedFieldId(fieldId);
    
    // Set custom drag image
    const dragImage = document.createElement('div');
    dragImage.className = 'bg-primary text-white px-3 py-1 rounded shadow-lg';
    dragImage.textContent = fields.find(f => f.id === fieldId)?.label || 'Field';
    dragImage.style.position = 'absolute';
    dragImage.style.top = '-1000px';
    document.body.appendChild(dragImage);
    e.dataTransfer.setDragImage(dragImage, 0, 0);
    setTimeout(() => document.body.removeChild(dragImage), 0);
  }, [fields, lockedFields, readOnly]);

  // Handle drag over
  const handleDragOver = useCallback((e: React.DragEvent, fieldId: string) => {
    e.preventDefault();
    if (!draggedFieldId || draggedFieldId === fieldId || lockedFields.has(fieldId)) return;
    
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const midY = rect.top + rect.height / 2;
    const position = e.clientY < midY ? 'above' : 'below';
    
    setDragOverFieldId(fieldId);
    setDragPosition(position);
  }, [draggedFieldId, lockedFields]);

  // Handle drop
  const handleDrop = useCallback((e: React.DragEvent, targetFieldId: string) => {
    e.preventDefault();
    
    if (!draggedFieldId || draggedFieldId === targetFieldId) {
      setDraggedFieldId(null);
      setDragOverFieldId(null);
      return;
    }
    
    const draggedIndex = fields.findIndex(f => f.id === draggedFieldId);
    const targetIndex = fields.findIndex(f => f.id === targetFieldId);
    
    if (draggedIndex === -1 || targetIndex === -1) return;
    
    const newFields = [...fields];
    const [draggedField] = newFields.splice(draggedIndex, 1);
    
    let insertIndex = targetIndex;
    if (dragPosition === 'below') {
      insertIndex = draggedIndex < targetIndex ? targetIndex : targetIndex + 1;
    } else {
      insertIndex = draggedIndex < targetIndex ? targetIndex - 1 : targetIndex;
    }
    
    newFields.splice(insertIndex, 0, draggedField);
    onFieldsChange(newFields);
    
    setDraggedFieldId(null);
    setDragOverFieldId(null);
  }, [draggedFieldId, dragPosition, fields, onFieldsChange]);

  // Handle drag end
  const handleDragEnd = useCallback(() => {
    setDraggedFieldId(null);
    setDragOverFieldId(null);
  }, []);

  // Move field up/down with keyboard
  const moveField = useCallback((fieldId: string, direction: 'up' | 'down') => {
    const index = fields.findIndex(f => f.id === fieldId);
    if (index === -1) return;
    if (direction === 'up' && index === 0) return;
    if (direction === 'down' && index === fields.length - 1) return;
    
    const newFields = [...fields];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    [newFields[index], newFields[targetIndex]] = [newFields[targetIndex], newFields[index]];
    onFieldsChange(newFields);
  }, [fields, onFieldsChange]);

  // Toggle field lock
  const toggleLock = useCallback((fieldId: string) => {
    setLockedFields(prev => {
      const updated = new Set(prev);
      if (updated.has(fieldId)) {
        updated.delete(fieldId);
      } else {
        updated.add(fieldId);
      }
      return updated;
    });
  }, []);

  // Toggle field collapse
  const toggleCollapse = useCallback((fieldId: string) => {
    setCollapsedFields(prev => {
      const updated = new Set(prev);
      if (updated.has(fieldId)) {
        updated.delete(fieldId);
      } else {
        updated.add(fieldId);
      }
      return updated;
    });
  }, []);

  // Get device width class
  const getDeviceClass = () => {
    switch (deviceView) {
      case 'mobile': return 'max-w-sm';
      case 'tablet': return 'max-w-xl';
      default: return 'max-w-3xl';
    }
  };

  // Render field input based on type
  const renderFieldInput = (field: FormField) => {
    if (collapsedFields.has(field.id)) {
      return (
        <div className="text-sm text-muted-foreground italic">
          Field collapsed - click to expand
        </div>
      );
    }

    switch (field.type) {
      case 'textarea':
        return (
          <Textarea 
            placeholder={field.placeholder} 
            disabled={!showFieldValues}
            rows={3}
            className="transition-all"
          />
        );
      
      case 'select':
        return (
          <select 
            className="w-full p-2 border rounded-md bg-background"
            disabled={!showFieldValues}
          >
            <option value="">{field.placeholder || 'Select an option'}</option>
            {(field.options || []).map((opt, i) => (
              <option key={i} value={opt}>{opt}</option>
            ))}
          </select>
        );
      
      case 'checkbox':
        return (
          <div className="flex items-center gap-2">
            <input type="checkbox" disabled={!showFieldValues} className="h-4 w-4" />
            <span className="text-sm">{field.placeholder || field.label}</span>
          </div>
        );
      
      case 'radio':
        return (
          <div className="space-y-2">
            {(field.options || ['Option 1', 'Option 2']).map((opt, i) => (
              <div key={i} className="flex items-center gap-2">
                <input 
                  type="radio" 
                  name={field.id} 
                  disabled={!showFieldValues}
                  className="h-4 w-4"
                />
                <span className="text-sm">{opt}</span>
              </div>
            ))}
          </div>
        );
      
      case 'file':
        return (
          <div className="border-2 border-dashed rounded-md p-4 text-center text-muted-foreground">
            <p className="text-sm">Drag & drop files here or click to upload</p>
          </div>
        );
      
      case 'rating':
        return (
          <div className="flex gap-1">
            {[1, 2, 3, 4, 5].map((star) => (
              <button key={star} className="text-2xl text-gray-300 hover:text-yellow-400 transition-colors">
                ★
              </button>
            ))}
          </div>
        );
      
      case 'slider':
        return (
          <div className="space-y-2">
            <input 
              type="range" 
              className="w-full" 
              disabled={!showFieldValues}
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>0</span>
              <span>100</span>
            </div>
          </div>
        );
      
      default:
        return (
          <Input 
            type={field.type === 'email' ? 'email' : field.type === 'number' ? 'number' : 'text'}
            placeholder={field.placeholder}
            disabled={!showFieldValues}
            className="transition-all"
          />
        );
    }
  };

  return (
    <TooltipProvider>
      <Card className="h-full">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <div>
            <CardTitle>Form Preview</CardTitle>
            <CardDescription>
              Drag fields to reorder • Click to select • Double-click to edit
            </CardDescription>
          </div>
          
          <div className="flex items-center gap-2">
            {/* Device Toggle */}
            <div className="flex border rounded-md">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant={deviceView === 'desktop' ? 'secondary' : 'ghost'}
                    size="sm"
                    onClick={() => setDeviceView('desktop')}
                  >
                    <Monitor className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Desktop View</TooltipContent>
              </Tooltip>
              
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant={deviceView === 'tablet' ? 'secondary' : 'ghost'}
                    size="sm"
                    onClick={() => setDeviceView('tablet')}
                  >
                    <Tablet className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Tablet View</TooltipContent>
              </Tooltip>
              
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant={deviceView === 'mobile' ? 'secondary' : 'ghost'}
                    size="sm"
                    onClick={() => setDeviceView('mobile')}
                  >
                    <Smartphone className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Mobile View</TooltipContent>
              </Tooltip>
            </div>
            
            {/* Toggle Field Values */}
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowFieldValues(!showFieldValues)}
                >
                  {showFieldValues ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                {showFieldValues ? 'Hide' : 'Show'} Field Inputs
              </TooltipContent>
            </Tooltip>
          </div>
        </CardHeader>
        
        <CardContent>
          <div className={cn(
            'mx-auto transition-all duration-300 border rounded-lg p-6 bg-white shadow-sm',
            getDeviceClass()
          )}>
            {/* Form Title */}
            <h3 className="text-xl font-semibold mb-2">{title || 'Untitled Form'}</h3>
            {description && (
              <p className="text-muted-foreground mb-6">{description}</p>
            )}
            
            {/* Fields List */}
            <div className="space-y-4">
              {fields.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground border-2 border-dashed rounded-lg">
                  <p>No fields yet. Add fields from the sidebar.</p>
                </div>
              ) : (
                fields.map((field, index) => {
                  const isSelected = selectedFieldId === field.id;
                  const isDragging = draggedFieldId === field.id;
                  const isDragOver = dragOverFieldId === field.id;
                  const isLocked = lockedFields.has(field.id);
                  const isHovered = hoveredFieldId === field.id;
                  
                  return (
                    <div
                      key={field.id}
                      draggable={!isLocked && !readOnly}
                      onDragStart={(e) => handleDragStart(e, field.id)}
                      onDragOver={(e) => handleDragOver(e, field.id)}
                      onDragEnd={handleDragEnd}
                      onDrop={(e) => handleDrop(e, field.id)}
                      onMouseEnter={() => setHoveredFieldId(field.id)}
                      onMouseLeave={() => setHoveredFieldId(null)}
                      onClick={() => onFieldSelect?.(field.id)}
                      className={cn(
                        'relative group p-4 border rounded-lg transition-all duration-200',
                        isSelected && 'ring-2 ring-primary border-primary',
                        isDragging && 'opacity-50 scale-95',
                        isDragOver && dragPosition === 'above' && 'border-t-4 border-t-primary',
                        isDragOver && dragPosition === 'below' && 'border-b-4 border-b-primary',
                        isLocked && 'bg-muted/30',
                        !isLocked && !readOnly && 'cursor-move hover:border-primary/50 hover:shadow-md',
                        'animate-in fade-in-0 slide-in-from-left-2'
                      )}
                      style={{
                        animationDelay: `${index * 50}ms`,
                      }}
                    >
                      {/* Drag Handle & Controls */}
                      <div className={cn(
                        'absolute -left-2 top-1/2 -translate-y-1/2 flex flex-col gap-1 transition-opacity',
                        isHovered || isSelected ? 'opacity-100' : 'opacity-0'
                      )}>
                        {!readOnly && !isLocked && (
                          <div className="bg-background border rounded p-1 shadow-sm cursor-grab active:cursor-grabbing">
                            <GripVertical className="h-4 w-4 text-muted-foreground" />
                          </div>
                        )}
                      </div>
                      
                      {/* Field Content */}
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <Label className="flex items-center gap-2">
                            {field.label}
                            {field.required && <span className="text-red-500">*</span>}
                            {isLocked && <Lock className="h-3 w-3 text-muted-foreground" />}
                          </Label>
                          
                          <Badge variant="secondary" className="text-xs">
                            {field.type}
                          </Badge>
                        </div>
                        
                        {renderFieldInput(field)}
                        
                        {field.help && (
                          <p className="text-xs text-muted-foreground">{field.help}</p>
                        )}
                      </div>
                      
                      {/* Action Buttons */}
                      <div className={cn(
                        'absolute -right-2 top-2 flex flex-col gap-1 transition-opacity',
                        isHovered || isSelected ? 'opacity-100' : 'opacity-0'
                      )}>
                        {!readOnly && (
                          <>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  variant="outline"
                                  size="icon"
                                  className="h-7 w-7 bg-background shadow-sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    moveField(field.id, 'up');
                                  }}
                                  disabled={index === 0}
                                >
                                  <ChevronUp className="h-3 w-3" />
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>Move Up</TooltipContent>
                            </Tooltip>
                            
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  variant="outline"
                                  size="icon"
                                  className="h-7 w-7 bg-background shadow-sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    moveField(field.id, 'down');
                                  }}
                                  disabled={index === fields.length - 1}
                                >
                                  <ChevronDown className="h-3 w-3" />
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>Move Down</TooltipContent>
                            </Tooltip>
                            
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  variant="outline"
                                  size="icon"
                                  className="h-7 w-7 bg-background shadow-sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    toggleLock(field.id);
                                  }}
                                >
                                  {isLocked ? (
                                    <Lock className="h-3 w-3" />
                                  ) : (
                                    <Unlock className="h-3 w-3" />
                                  )}
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>{isLocked ? 'Unlock' : 'Lock'} Field</TooltipContent>
                            </Tooltip>
                            
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  variant="outline"
                                  size="icon"
                                  className="h-7 w-7 bg-background shadow-sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    toggleCollapse(field.id);
                                  }}
                                >
                                  {collapsedFields.has(field.id) ? (
                                    <Maximize2 className="h-3 w-3" />
                                  ) : (
                                    <Minimize2 className="h-3 w-3" />
                                  )}
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>
                                {collapsedFields.has(field.id) ? 'Expand' : 'Collapse'}
                              </TooltipContent>
                            </Tooltip>
                            
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  variant="outline"
                                  size="icon"
                                  className="h-7 w-7 bg-background shadow-sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    onFieldDuplicate?.(field.id);
                                  }}
                                >
                                  <Copy className="h-3 w-3" />
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>Duplicate</TooltipContent>
                            </Tooltip>
                            
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  variant="outline"
                                  size="icon"
                                  className="h-7 w-7 bg-background shadow-sm text-red-500 hover:text-red-600"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    onFieldDelete?.(field.id);
                                  }}
                                >
                                  <Trash2 className="h-3 w-3" />
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>Delete</TooltipContent>
                            </Tooltip>
                          </>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
            
            {/* Submit Button Preview */}
            {fields.length > 0 && (
              <div className="mt-6">
                <Button className="w-full">Submit</Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </TooltipProvider>
  );
}

export default InteractiveFormPreview;
