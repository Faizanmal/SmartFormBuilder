"use client";

import React, { useState } from "react";
import { FormStep, FormField } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Plus, Trash2, GripVertical } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface MultiStepConfigProps {
  fields: FormField[];
  steps: FormStep[];
  enabled: boolean;
  onEnabledChange: (enabled: boolean) => void;
  onStepsChange: (steps: FormStep[]) => void;
}

export function MultiStepConfig({ 
  fields, 
  steps, 
  enabled, 
  onEnabledChange, 
  onStepsChange 
}: MultiStepConfigProps) {
  const [editingStep, setEditingStep] = useState<string | null>(null);

  const addStep = () => {
    const newStep: FormStep = {
      id: `step_${steps.length + 1}`,
      title: `Step ${steps.length + 1}`,
      description: '',
      fields: [],
    };
    onStepsChange([...steps, newStep]);
  };

  const updateStep = (stepId: string, updates: Partial<FormStep>) => {
    onStepsChange(steps.map(s => s.id === stepId ? { ...s, ...updates } : s));
  };

  const deleteStep = (stepId: string) => {
    onStepsChange(steps.filter(s => s.id !== stepId));
  };

  const assignFieldToStep = (fieldId: string, stepId: string) => {
    // Remove field from all steps
    const clearedSteps = steps.map(s => ({
      ...s,
      fields: s.fields.filter(fid => fid !== fieldId)
    }));
    
    // Add field to target step
    const updatedSteps = clearedSteps.map(s => 
      s.id === stepId ? { ...s, fields: [...s.fields, fieldId] } : s
    );
    
    onStepsChange(updatedSteps);
  };

  const getUnassignedFields = () => {
    const assignedFieldIds = new Set(steps.flatMap(s => s.fields));
    return fields.filter(f => !assignedFieldIds.has(f.id));
  };

  const getFieldById = (fieldId: string) => fields.find(f => f.id === fieldId);

  return (
    <div className="space-y-4">
      {/* Enable Multi-step Toggle */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold">Multi-step Form</h3>
              <p className="text-sm text-muted-foreground">
                Break your form into multiple steps for better user experience
              </p>
            </div>
            <Switch checked={enabled} onCheckedChange={onEnabledChange} />
          </div>
        </CardContent>
      </Card>

      {enabled && (
        <>
          {/* Steps List */}
          <div className="space-y-4">
            {steps.map((step, index) => (
              <Card key={step.id}>
                <CardHeader>
                  <div className="flex items-center gap-2">
                    <GripVertical className="h-5 w-5 text-muted-foreground cursor-grab" />
                    <CardTitle className="text-lg">Step {index + 1}</CardTitle>
                    <div className="flex-1" />
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteStep(step.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Step Title */}
                  <div>
                    <Label>Step Title</Label>
                    <Input
                      value={step.title}
                      onChange={(e) => updateStep(step.id, { title: e.target.value })}
                      placeholder="e.g., Personal Information"
                    />
                  </div>

                  {/* Step Description */}
                  <div>
                    <Label>Description (Optional)</Label>
                    <Textarea
                      value={step.description || ''}
                      onChange={(e) => updateStep(step.id, { description: e.target.value })}
                      placeholder="Brief description of this step"
                      rows={2}
                    />
                  </div>

                  {/* Assigned Fields */}
                  <div>
                    <Label>Fields in this step</Label>
                    <div className="space-y-2 mt-2">
                      {step.fields.length === 0 ? (
                        <p className="text-sm text-muted-foreground">No fields assigned yet</p>
                      ) : (
                        step.fields.map(fieldId => {
                          const field = getFieldById(fieldId);
                          return field ? (
                            <div key={fieldId} className="flex items-center gap-2 p-2 bg-muted rounded">
                              <span className="flex-1 text-sm">{field.label}</span>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => {
                                  updateStep(step.id, {
                                    fields: step.fields.filter(fid => fid !== fieldId)
                                  });
                                }}
                              >
                                Remove
                              </Button>
                            </div>
                          ) : null;
                        })
                      )}
                    </div>
                  </div>

                  {/* Add Field to Step */}
                  <div>
                    <Label>Add field to this step</Label>
                    <Select
                      onValueChange={(fieldId) => assignFieldToStep(fieldId, step.id)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select a field..." />
                      </SelectTrigger>
                      <SelectContent>
                        {fields.map(field => (
                          <SelectItem key={field.id} value={field.id}>
                            {field.label} ({field.type})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Add Step Button */}
          <Button onClick={addStep} variant="outline" className="w-full">
            <Plus className="h-4 w-4 mr-2" />
            Add Step
          </Button>

          {/* Unassigned Fields Warning */}
          {getUnassignedFields().length > 0 && (
            <Card className="border-amber-500">
              <CardContent className="pt-6">
                <p className="text-sm font-medium text-amber-600">
                  ⚠️ {getUnassignedFields().length} field(s) not assigned to any step
                </p>
                <ul className="text-sm text-muted-foreground mt-2">
                  {getUnassignedFields().map(field => (
                    <li key={field.id}>• {field.label}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
