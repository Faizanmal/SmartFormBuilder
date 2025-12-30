/**
 * Multi-Step Form Component with Progress Bar
 */
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ChevronLeft, ChevronRight, Save, CheckCircle2 } from 'lucide-react';

interface FormStep {
  step_number: number;
  title: string;
  description: string;
  fields: string[];
  conditional_logic?: unknown;
}

interface MultiStepFormProps {
  formSchema: {
    id: string;
    title: string;
    description: string;
    steps: FormStep[];
    fields: unknown[];
  };
  onSubmit: (data: unknown) => Promise<void>;
  autoSave?: boolean;
  resumeData?: unknown;
}

export function MultiStepForm({ formSchema, onSubmit, autoSave = true, resumeData }: MultiStepFormProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<Record<string, unknown>>(resumeData?.payload_json || {});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');
  const [resumeToken, setResumeToken] = useState<string | null>(resumeData?.resume_token || null);

  const totalSteps = formSchema.steps.length;
  const progress = Math.round((currentStep / totalSteps) * 100);
  const currentStepData = formSchema.steps[currentStep - 1];

  // Auto-save functionality
  useEffect(() => {
    if (!autoSave) return;

    const saveTimer = setTimeout(() => {
      handleAutoSave();
    }, 3000); // Auto-save after 3 seconds of inactivity

    return () => clearTimeout(saveTimer);
  }, [formData, currentStep, autoSave, handleAutoSave]);

  const handleAutoSave = useCallback(async () => {
    if (Object.keys(formData).length === 0) return;

    setIsSaving(true);
    try {
      const response = await fetch('/api/partial-submissions/save_progress/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          form_slug: formSchema.id,
          email: formData.email || '',
          payload: formData,
          current_step: currentStep,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResumeToken(data.resume_token);
        setSaveMessage('Progress saved ✓');
        setTimeout(() => setSaveMessage(''), 2000);
      }
    } catch (error) {
      console.error('Auto-save failed:', error);
    } finally {
      setIsSaving(false);
    }
  }, [formData, formSchema.id, currentStep]);

  const validateStep = (): boolean => {
    const stepErrors: Record<string, string> = {};
    const stepFields = currentStepData.fields;

    // Validate required fields in current step
    stepFields.forEach((fieldId) => {
      const field = formSchema.fields.find((f) => f.id === fieldId);
      if (field?.required && !formData[fieldId]) {
        stepErrors[fieldId] = `${field.label} is required`;
      }
    });

    setErrors(stepErrors);
    return Object.keys(stepErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep()) {
      if (currentStep < totalSteps) {
        setCurrentStep(currentStep + 1);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleSubmit = async () => {
    if (!validateStep()) return;

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Submission failed:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFieldChange = (fieldId: string, value: unknown) => {
    setFormData({ ...formData, [fieldId]: value });
    // Clear error for this field
    if (errors[fieldId]) {
      setErrors({ ...errors, [fieldId]: '' });
    }
  };

  const renderField = (fieldId: string) => {
    const field = formSchema.fields.find((f) => f.id === fieldId);
    if (!field) return null;

    // Render different field types based on field.type
    // This is a simplified version - expand based on your field types
    return (
      <div key={fieldId} className="mb-4">
        <label className="block text-sm font-medium mb-2">
          {field.label}
          {field.required && <span className="text-red-500 ml-1">*</span>}
        </label>
        
        {field.type === 'text' || field.type === 'email' ? (
          <input
            type={field.type}
            value={(formData[fieldId] as string) || ''}
            onChange={(e) => handleFieldChange(fieldId, e.target.value)}
            placeholder={field.placeholder}
            className="w-full p-2 border rounded-md"
          />
        ) : field.type === 'textarea' ? (
          <textarea
            value={(formData[fieldId] as string) || ''}
            onChange={(e) => handleFieldChange(fieldId, e.target.value)}
            placeholder={field.placeholder}
            rows={4}
            className="w-full p-2 border rounded-md"
          />
        ) : field.type === 'select' ? (
          <select
            value={(formData[fieldId] as string) || ''}
            onChange={(e) => handleFieldChange(fieldId, e.target.value)}
            className="w-full p-2 border rounded-md"
          >
            <option value="">Select an option</option>
            {field.options?.map((opt: string) => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        ) : null}
        
        {errors[fieldId] && (
          <p className="text-red-500 text-sm mt-1">{errors[fieldId]}</p>
        )}
        
        {field.help && (
          <p className="text-gray-500 text-sm mt-1">{field.help}</p>
        )}
      </div>
    );
  };

  return (
    <Card className="max-w-3xl mx-auto">
      <CardHeader>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Badge variant="outline">Step {currentStep} of {totalSteps}</Badge>
            {saveMessage && (
              <span className="text-sm text-green-600">{saveMessage}</span>
            )}
            {isSaving && (
              <span className="text-sm text-gray-500">Saving...</span>
            )}
          </div>
        </div>
        
        <Progress value={progress} className="mb-4" />
        
        <CardTitle>{currentStepData.title}</CardTitle>
        {currentStepData.description && (
          <CardDescription>{currentStepData.description}</CardDescription>
        )}
      </CardHeader>

      <CardContent>
        {resumeData && (
          <Alert className="mb-6">
            <CheckCircle2 className="h-4 w-4" />
            <AlertDescription>
              Welcome back! Your progress has been restored. You&apos;re {progress}% complete.
            </AlertDescription>
          </Alert>
        )}

        <form onSubmit={(e) => { e.preventDefault(); }}>
          {currentStepData.fields.map(renderField)}

          <div className="flex justify-between mt-8">
            <Button
              type="button"
              variant="outline"
              onClick={handlePrevious}
              disabled={currentStep === 1}
            >
              <ChevronLeft className="mr-2 h-4 w-4" />
              Previous
            </Button>

            <div className="flex gap-2">
              {autoSave && (
                <Button
                  type="button"
                  variant="ghost"
                  onClick={handleAutoSave}
                  disabled={isSaving}
                >
                  <Save className="mr-2 h-4 w-4" />
                  {isSaving ? 'Saving...' : 'Save Progress'}
                </Button>
              )}

              {currentStep < totalSteps ? (
                <Button type="button" onClick={handleNext}>
                  Next
                  <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              ) : (
                <Button
                  type="button"
                  onClick={handleSubmit}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Submitting...' : 'Submit'}
                </Button>
              )}
            </div>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
