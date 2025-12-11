"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { formsApi, submissionsApi, draftsApi } from "@/lib/api-client";
import type { Form, FormField, FormStep } from "@/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, Loader2, ChevronLeft, ChevronRight, Save, Mail } from "lucide-react";
import { toast } from "sonner";
import { FormProgress, FormProgressBar } from "@/components/form-progress";
import {
  SliderField,
  RatingField,
  FileUploadField,
  SignatureField,
  CalculatedField,
  AddressField,
  type AddressValue
} from "@/components/form-fields";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

export default function PublicFormPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const slug = params.slug as string;
  const draftToken = searchParams.get('draft');
  
  const [form, setForm] = useState<Form | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState<Record<string, unknown>>({});
  const [visibleFields, setVisibleFields] = useState<Set<string>>(new Set());
  
  // Multi-step form state
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [isMultiStep, setIsMultiStep] = useState(false);
  const [steps, setSteps] = useState<FormStep[]>([]);
  
  // Save & Resume state
  const [currentDraftToken, setCurrentDraftToken] = useState<string | null>(null);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [saveEmail, setSaveEmail] = useState('');
  const [savingDraft, setSavingDraft] = useState(false);

  useEffect(() => {
    loadForm();
  }, [slug]);

  useEffect(() => {
    if (form) {
      updateVisibleFields();
      
      // Check if multi-step
      const multiStep = form.schema_json.settings?.multiStep || false;
      setIsMultiStep(multiStep);
      
      if (multiStep && form.schema_json.settings?.steps) {
        setSteps(form.schema_json.settings.steps);
      }
    }
  }, [formData, form]);

  // Load draft if token is provided
  useEffect(() => {
    if (draftToken && form) {
      loadDraft(draftToken);
    }
  }, [draftToken, form]);

  const loadForm = async () => {
    try {
      // Try public endpoint first
      try {
        const foundForm = await formsApi.getBySlug(slug);
        setForm(foundForm);
        initializeForm(foundForm);
      } catch {
        // Fallback to list API
        const forms = await formsApi.list();
        const foundForm = forms.find(f => f.slug === slug);
        
        if (foundForm) {
          setForm(foundForm);
          initializeForm(foundForm);
        } else {
          toast.error("Form not found");
        }
      }
    } catch {
      toast.error("Failed to load form");
    } finally {
      setLoading(false);
    }
  };

  const initializeForm = (foundForm: Form) => {
    const initialVisible = new Set<string>();
    foundForm.schema_json.fields.forEach((field: FormField) => {
      initialVisible.add(field.id);
    });
    setVisibleFields(initialVisible);
  };

  const loadDraft = async (token: string) => {
    try {
      const draft = await draftsApi.get(token);
      if (draft && !draft.is_expired) {
        setFormData(draft.payload_json as Record<string, unknown>);
        setCurrentStep(draft.current_step);
        setCurrentDraftToken(draft.draft_token);
        
        // Mark previous steps as completed
        const completed = [];
        for (let i = 0; i < draft.current_step; i++) {
          completed.push(i);
        }
        setCompletedSteps(completed);
        
        toast.success("Your progress has been restored!");
      }
    } catch (err) {
      console.error("Failed to load draft:", err);
    }
  };

  // Save draft functionality
  const saveDraft = async (email?: string) => {
    if (!form) return;
    
    setSavingDraft(true);
    try {
      const draft = await draftsApi.save(slug, {
        payload: formData,
        current_step: currentStep,
        email: email,
        draft_token: currentDraftToken || undefined,
      });
      
      setCurrentDraftToken(draft.draft_token);
      
      if (email) {
        await draftsApi.sendResumeLink(draft.draft_token, email);
        toast.success("Resume link sent to your email!");
      } else {
        // Copy resume link to clipboard
        const resumeLink = `${window.location.origin}/form/${slug}?draft=${draft.draft_token}`;
        await navigator.clipboard.writeText(resumeLink);
        toast.success("Progress saved! Link copied to clipboard.");
      }
      
      setShowSaveDialog(false);
    } catch {
      toast.error("Failed to save progress");
    } finally {
      setSavingDraft(false);
    }
  };

  const updateVisibleFields = () => {
    if (!form) return;

    const newVisible = new Set<string>();
    
    // Start with all fields visible
    form.schema_json.fields.forEach(field => {
      newVisible.add(field.id);
    });

    // Apply conditional logic
    if (form.schema_json.logic) {
      form.schema_json.logic.forEach(rule => {
        const fieldValue = formData[rule.if.field];
        let conditionMet = false;

        switch (rule.if.operator) {
          case 'equals':
            conditionMet = fieldValue === rule.if.value;
            break;
          case 'contains':
            conditionMet = Array.isArray(fieldValue) 
              ? fieldValue.includes(rule.if.value)
              : String(fieldValue).includes(String(rule.if.value));
            break;
          case 'gte':
            conditionMet = Number(fieldValue) >= Number(rule.if.value);
            break;
          case 'lte':
            conditionMet = Number(fieldValue) <= Number(rule.if.value);
            break;
        }

        if (conditionMet) {
          rule.show?.forEach(fieldId => newVisible.add(fieldId));
          rule.hide?.forEach(fieldId => newVisible.delete(fieldId));
        } else {
          rule.hide?.forEach(fieldId => newVisible.add(fieldId));
          rule.show?.forEach(fieldId => newVisible.delete(fieldId));
        }
      });
    }

    setVisibleFields(newVisible);
  };

  // Get fields for current step in multi-step form
  const getCurrentStepFields = useCallback(() => {
    if (!form || !isMultiStep || steps.length === 0) {
      return form?.schema_json.fields || [];
    }
    
    const currentStepData = steps[currentStep];
    if (!currentStepData) return [];
    
    return form.schema_json.fields.filter(field => 
      currentStepData.fields.includes(field.id)
    );
  }, [form, isMultiStep, steps, currentStep]);

  // Validate current step fields
  const validateCurrentStep = (): boolean => {
    const fieldsToValidate = isMultiStep ? getCurrentStepFields() : (form?.schema_json.fields || []);
    const requiredFields = fieldsToValidate.filter(f => f.required && visibleFields.has(f.id));
    const missingFields = requiredFields.filter(f => !formData[f.id]);
    
    if (missingFields.length > 0) {
      toast.error(`Please fill in: ${missingFields.map(f => f.label).join(', ')}`);
      return false;
    }
    return true;
  };

  // Navigate to next step
  const goToNextStep = () => {
    if (!validateCurrentStep()) return;
    
    if (!completedSteps.includes(currentStep)) {
      setCompletedSteps([...completedSteps, currentStep]);
    }
    
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // Navigate to previous step
  const goToPreviousStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // Handle step click in progress bar
  const handleStepClick = (stepIndex: number) => {
    if (completedSteps.includes(stepIndex) || stepIndex === currentStep || stepIndex <= Math.max(...completedSteps, -1) + 1) {
      setCurrentStep(stepIndex);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // For multi-step forms, validate only final step on submit
    if (!validateCurrentStep()) return;
    
    // Also validate all required fields across all steps
    const requiredFields = form?.schema_json.fields.filter(f => f.required && visibleFields.has(f.id));
    const missingFields = requiredFields?.filter(f => !formData[f.id]);
    
    if (missingFields && missingFields.length > 0) {
      toast.error(`Please complete all required fields: ${missingFields.map(f => f.label).join(', ')}`);
      return;
    }

    setSubmitting(true);

    try {
      const response = await submissionsApi.submit(slug, formData);
      setSubmitted(true);
      toast.success(response.message || "Form submitted successfully!");
      
      // Redirect if specified
      if (response.redirect && response.redirect !== '/thank-you') {
        setTimeout(() => {
          window.location.href = response.redirect;
        }, 2000);
      }
    } catch (error: unknown) {
      // Handle rate limiting
      const err = error as { isRateLimit?: boolean; message?: string; retryAfter?: number };
      if (err?.isRateLimit) {
        toast.error(err.message || "Too many submissions. Please try again later.", {
          description: err.retryAfter ? `Please wait ${err.retryAfter} seconds before trying again.` : undefined,
          duration: 5000,
        });
      } else {
        toast.error("Failed to submit form. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const renderField = (field: FormField) => {
    if (!visibleFields.has(field.id)) return null;

    const value = formData[field.id] ?? '';

    switch (field.type) {
      case 'text':
      case 'email':
      case 'phone':
      case 'url':
      case 'number':
      case 'date':
      case 'time':
        return (
          <div key={field.id} className="space-y-2">
            <Label htmlFor={field.id}>
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </Label>
            <Input
              id={field.id}
              type={field.type}
              placeholder={field.placeholder}
              value={value as string}
              onChange={(e) => setFormData({ ...formData, [field.id]: e.target.value })}
              required={field.required}
            />
            {field.help && <p className="text-xs text-muted-foreground">{field.help}</p>}
          </div>
        );

      case 'textarea':
        return (
          <div key={field.id} className="space-y-2">
            <Label htmlFor={field.id}>
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </Label>
            <Textarea
              id={field.id}
              placeholder={field.placeholder}
              value={value as string}
              onChange={(e) => setFormData({ ...formData, [field.id]: e.target.value })}
              required={field.required}
              rows={4}
            />
            {field.help && <p className="text-xs text-muted-foreground">{field.help}</p>}
          </div>
        );

      case 'select':
        return (
          <div key={field.id} className="space-y-2">
            <Label htmlFor={field.id}>
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </Label>
            <Select
              value={value as string}
              onValueChange={(val: string) => setFormData({ ...formData, [field.id]: val })}
            >
              <SelectTrigger>
                <SelectValue placeholder={field.placeholder || "Select..."} />
              </SelectTrigger>
              <SelectContent>
                {field.options?.map((option) => (
                  <SelectItem key={option} value={option}>
                    {option}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {field.help && <p className="text-xs text-muted-foreground">{field.help}</p>}
          </div>
        );

      case 'checkbox':
        return (
          <div key={field.id} className="flex items-center space-x-2">
            <Checkbox
              id={field.id}
              checked={value === true}
              onCheckedChange={(checked: boolean | "indeterminate") => setFormData({ ...formData, [field.id]: checked })}
            />
            <Label htmlFor={field.id} className="text-sm font-normal">
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </Label>
          </div>
        );

      case 'radio':
        return (
          <div key={field.id} className="space-y-2">
            <Label>
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </Label>
            <RadioGroup
              value={value as string}
              onValueChange={(val: string) => setFormData({ ...formData, [field.id]: val })}
            >
              {field.options?.map((option) => (
                <div key={option} className="flex items-center space-x-2">
                  <RadioGroupItem value={option} id={`${field.id}-${option}`} />
                  <Label htmlFor={`${field.id}-${option}`} className="font-normal">
                    {option}
                  </Label>
                </div>
              ))}
            </RadioGroup>
            {field.help && <p className="text-xs text-muted-foreground">{field.help}</p>}
          </div>
        );

      case 'multiselect':
        return (
          <div key={field.id} className="space-y-2">
            <Label>
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </Label>
            <div className="space-y-2">
              {field.options?.map((option) => (
                <div key={option} className="flex items-center space-x-2">
                  <Checkbox
                    id={`${field.id}-${option}`}
                    checked={Array.isArray(value) && value.includes(option)}
                    onCheckedChange={(checked: boolean | "indeterminate") => {
                      const currentValues = Array.isArray(value) ? value : [];
                      const newValues = checked
                        ? [...currentValues, option]
                        : currentValues.filter((v: string) => v !== option);
                      setFormData({ ...formData, [field.id]: newValues });
                    }}
                  />
                  <Label htmlFor={`${field.id}-${option}`} className="text-sm font-normal">
                    {option}
                  </Label>
                </div>
              ))}
            </div>
            {field.help && <p className="text-xs text-muted-foreground">{field.help}</p>}
          </div>
        );

      // New field types
      case 'slider':
        return (
          <SliderField
            key={field.id}
            field={field}
            value={value as number}
            onChange={(val) => setFormData({ ...formData, [field.id]: val })}
          />
        );

      case 'rating':
        return (
          <RatingField
            key={field.id}
            field={field}
            value={value as number}
            onChange={(val) => setFormData({ ...formData, [field.id]: val })}
          />
        );

      case 'file':
        return (
          <FileUploadField
            key={field.id}
            field={field}
            value={(value || null) as File | File[] | null}
            onChange={(val) => setFormData({ ...formData, [field.id]: val })}
          />
        );

      case 'signature':
        return (
          <SignatureField
            key={field.id}
            field={field}
            value={value as string | null}
            onChange={(val) => setFormData({ ...formData, [field.id]: val })}
          />
        );

      case 'calculated':
        return (
          <CalculatedField
            key={field.id}
            field={field}
            formData={formData}
          />
        );

      case 'address':
        return (
          <AddressField
            key={field.id}
            field={field}
            value={value as AddressValue || {}}
            onChange={(val) => setFormData({ ...formData, [field.id]: val })}
          />
        );

      case 'heading':
        const HeadingTag = field.headingLevel || 'h2';
        return (
          <div key={field.id} className="pt-4">
            {HeadingTag === 'h1' && <h1 className="text-2xl font-bold">{field.label}</h1>}
            {HeadingTag === 'h2' && <h2 className="text-xl font-semibold">{field.label}</h2>}
            {HeadingTag === 'h3' && <h3 className="text-lg font-medium">{field.label}</h3>}
            {HeadingTag === 'h4' && <h4 className="text-base font-medium">{field.label}</h4>}
            {field.help && <p className="text-sm text-muted-foreground mt-1">{field.help}</p>}
          </div>
        );

      case 'divider':
        return (
          <div key={field.id} className="py-4">
            <hr className="border-t border-gray-200" />
            {field.label && (
              <p className="text-xs text-muted-foreground text-center -mt-3 bg-white px-2 mx-auto w-fit">
                {field.label}
              </p>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  // Get fields to render based on multi-step or single form
  const fieldsToRender = isMultiStep ? getCurrentStepFields() : (form?.schema_json.fields || []);
  const isLastStep = !isMultiStep || currentStep === steps.length - 1;
  const isFirstStep = currentStep === 0;
  const showSaveButton = form?.schema_json.settings?.allowSaveAndResume || false;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!form) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">Form not found</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100 dark:from-gray-900 dark:to-gray-800 p-4">
        <Card className="max-w-md w-full">
          <CardContent className="pt-6 text-center">
            <CheckCircle2 className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Thank You!</h2>
            <p className="text-muted-foreground">
              Your response has been recorded successfully.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">{form.schema_json.title || form.title}</CardTitle>
            {form.schema_json.description && (
              <CardDescription>{form.schema_json.description}</CardDescription>
            )}
            
            {/* Multi-step progress */}
            {isMultiStep && steps.length > 0 && (
              <div className="mt-6">
                {steps.length <= 5 ? (
                  <FormProgress
                    steps={steps}
                    currentStep={currentStep}
                    completedSteps={completedSteps}
                    onStepClick={handleStepClick}
                    allowNavigation={true}
                  />
                ) : (
                  <FormProgressBar
                    currentStep={currentStep}
                    totalSteps={steps.length}
                    showPercentage={true}
                  />
                )}
              </div>
            )}
          </CardHeader>
          
          <CardContent>
            {/* Current step title for multi-step forms */}
            {isMultiStep && steps[currentStep] && (
              <div className="mb-6 pb-4 border-b">
                <h3 className="text-lg font-semibold">{steps[currentStep].title}</h3>
                {steps[currentStep].description && (
                  <p className="text-sm text-muted-foreground mt-1">
                    {steps[currentStep].description}
                  </p>
                )}
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-6">
              {fieldsToRender.map(renderField)}
              
              {/* Consent text - only show on last step */}
              {isLastStep && form.schema_json.settings?.consent_text && (
                <div className="pt-4 border-t">
                  <p className="text-xs text-muted-foreground">
                    {form.schema_json.settings.consent_text}
                  </p>
                </div>
              )}

              {/* Navigation buttons */}
              <div className="flex gap-3 pt-4">
                {/* Save button */}
                {showSaveButton && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowSaveDialog(true)}
                    className="flex-shrink-0"
                  >
                    <Save className="mr-2 h-4 w-4" />
                    Save
                  </Button>
                )}
                
                {/* Previous button - multi-step */}
                {isMultiStep && !isFirstStep && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={goToPreviousStep}
                    className="flex-1"
                  >
                    <ChevronLeft className="mr-2 h-4 w-4" />
                    Previous
                  </Button>
                )}
                
                {/* Next/Submit button */}
                {isMultiStep && !isLastStep ? (
                  <Button
                    type="button"
                    onClick={goToNextStep}
                    className="flex-1"
                  >
                    Next
                    <ChevronRight className="ml-2 h-4 w-4" />
                  </Button>
                ) : (
                  <Button
                    type="submit"
                    className="flex-1"
                    size="lg"
                    disabled={submitting}
                  >
                    {submitting ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Submitting...
                      </>
                    ) : (
                      "Submit"
                    )}
                  </Button>
                )}
              </div>
            </form>
          </CardContent>
        </Card>
      </div>

      {/* Save & Resume Dialog */}
      <Dialog open={showSaveDialog} onOpenChange={setShowSaveDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Save Your Progress</DialogTitle>
            <DialogDescription>
              Save your progress and continue later. We&apos;ll send you a link to resume.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="save-email">Email (optional)</Label>
              <Input
                id="save-email"
                type="email"
                placeholder="your@email.com"
                value={saveEmail}
                onChange={(e) => setSaveEmail(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Enter your email to receive a resume link, or leave blank to copy the link.
              </p>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSaveDialog(false)}>
              Cancel
            </Button>
            <Button onClick={() => saveDraft(saveEmail || undefined)} disabled={savingDraft}>
              {savingDraft ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : saveEmail ? (
                <>
                  <Mail className="mr-2 h-4 w-4" />
                  Send Link
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save & Copy Link
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
