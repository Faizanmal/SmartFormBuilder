"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { formsApi } from "@/lib/api-client";
import useAuth from "@/hooks/useAuth";
import type { Form, FormField, FormSchema, FormSettings, FormStep, ConditionalRule } from "@/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Save, Eye, Settings as SettingsIcon, Plus, Share2 } from "lucide-react";
import { toast } from "sonner";
import { AddFieldPanel } from "@/components/form-builder/AddFieldPanel";
import { FieldEditor } from "@/components/form-builder/FieldEditor";
import { MultiStepConfig } from "@/components/form-builder/MultiStepConfig";
import { ConditionalLogicBuilder } from "@/components/form-builder/ConditionalLogicBuilder";
import { Switch } from "@/components/ui/switch";

export default function FormBuilderPage() {
  const params = useParams();
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth(true);
  const formId = params.id as string;

  const [form, setForm] = useState<Form | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [schema, setSchema] = useState<FormSchema>({
    title: "",
    description: "",
    fields: [],
    settings: {},
  });
  const [showFieldSelector, setShowFieldSelector] = useState(false);
  const [selectedFieldIndex, setSelectedFieldIndex] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState("builder");

  useEffect(() => {
    if (isAuthenticated) {
      loadForm();
    }
  }, [formId, isAuthenticated]);

  if (authLoading || !isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  const loadForm = async () => {
    try {
      const data = await formsApi.get(formId);
      setForm(data);
      setSchema(data.schema_json);
    } catch (error) {
      toast.error("Failed to load form");
      router.push("/dashboard");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!schema.title.trim()) {
      toast.error("Please enter a form title");
      return;
    }

    setSaving(true);
    try {
      await formsApi.update(formId, {
        title: schema.title,
        description: schema.description,
        schema_json: schema,
      });
      toast.success("Form saved successfully!");
      loadForm();
    } catch (error) {
      toast.error("Failed to save form");
    } finally {
      setSaving(false);
    }
  };

  const handlePublish = async () => {
    try {
      await formsApi.publish(formId);
      toast.success("Form published successfully!");
      loadForm();
    } catch (error) {
      toast.error("Failed to publish form");
    }
  };

  const handleUnpublish = async () => {
    try {
      await formsApi.unpublish(formId);
      toast.success("Form unpublished successfully!");
      loadForm();
    } catch (error) {
      toast.error("Failed to unpublish form");
    }
  };

  const handlePreview = () => {
    if (form?.slug) {
      window.open(`/forms/${form.slug}`, "_blank");
    }
  };

  const addField = (type: string) => {
    const newField: FormField = {
      id: `field_${Date.now()}`,
      type: type as any,
      label: `New ${type} field`,
      required: false,
    };

    setSchema({
      ...schema,
      fields: [...schema.fields, newField],
    });
    setShowFieldSelector(false);
    setSelectedFieldIndex(schema.fields.length);
  };

  const updateField = (index: number, updates: Partial<FormField>) => {
    const newFields = [...schema.fields];
    newFields[index] = { ...newFields[index], ...updates };
    setSchema({ ...schema, fields: newFields });
  };

  const deleteField = (index: number) => {
    const newFields = schema.fields.filter((_, i) => i !== index);
    setSchema({ ...schema, fields: newFields });
    if (selectedFieldIndex === index) {
      setSelectedFieldIndex(null);
    }
  };

  const duplicateField = (index: number) => {
    const field = schema.fields[index];
    const newField = { ...field, id: `field_${Date.now()}`, label: `${field.label} (Copy)` };
    const newFields = [...schema.fields];
    newFields.splice(index + 1, 0, newField);
    setSchema({ ...schema, fields: newFields });
  };

  const moveField = (index: number, direction: "up" | "down") => {
    if (
      (direction === "up" && index === 0) ||
      (direction === "down" && index === schema.fields.length - 1)
    ) {
      return;
    }

    const newFields = [...schema.fields];
    const targetIndex = direction === "up" ? index - 1 : index + 1;
    [newFields[index], newFields[targetIndex]] = [newFields[targetIndex], newFields[index]];
    setSchema({ ...schema, fields: newFields });
  };

  const updateConditionalRules = (index: number, rules: ConditionalRule[]) => {
    updateField(index, { conditionalRules: rules });
  };

  const updateSettings = (updates: Partial<FormSettings>) => {
    setSchema({
      ...schema,
      settings: { ...schema.settings, ...updates },
    });
  };

  const updateMultiStepSettings = (enabled: boolean, steps?: FormStep[]) => {
    updateSettings({
      multiStep: enabled,
      steps: steps || schema.settings?.steps || [],
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading form...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="sticky top-0 z-50 bg-background border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <Input
                value={schema.title}
                onChange={(e) => setSchema({ ...schema, title: e.target.value })}
                className="text-2xl font-bold border-none focus-visible:ring-0 px-0"
                placeholder="Untitled Form"
              />
              <Input
                value={schema.description}
                onChange={(e) => setSchema({ ...schema, description: e.target.value })}
                className="text-sm text-muted-foreground border-none focus-visible:ring-0 px-0 mt-1"
                placeholder="Add a description..."
              />
            </div>
            <div className="flex items-center gap-2">
              {form?.published_at ? (
                <>
                  <Button variant="outline" size="sm" onClick={handlePreview}>
                    <Eye className="h-4 w-4 mr-2" />
                    Preview
                  </Button>
                  <Button variant="outline" size="sm" onClick={handleUnpublish}>
                    Unpublish
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => {
                    navigator.clipboard.writeText(`${window.location.origin}/forms/${form.slug}`);
                    toast.success("Form URL copied to clipboard!");
                  }}>
                    <Share2 className="h-4 w-4 mr-2" />
                    Share
                  </Button>
                </>
              ) : (
                <Button variant="outline" size="sm" onClick={handlePublish}>
                  Publish
                </Button>
              )}
              <Button onClick={handleSave} disabled={saving}>
                <Save className="h-4 w-4 mr-2" />
                {saving ? "Saving..." : "Save"}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full max-w-[600px] mx-auto grid-cols-4">
            <TabsTrigger value="builder">Builder</TabsTrigger>
            <TabsTrigger value="logic">Logic</TabsTrigger>
            <TabsTrigger value="steps">Multi-Step</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          {/* Builder Tab */}
          <TabsContent value="builder" className="mt-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Fields List */}
              <div className="lg:col-span-2 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold">Form Fields</h2>
                  <Button onClick={() => setShowFieldSelector(true)} size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Field
                  </Button>
                </div>

                {schema.fields.length === 0 ? (
                  <Card>
                    <CardContent className="pt-6 text-center py-12">
                      <p className="text-muted-foreground mb-4">
                        No fields yet. Click "Add Field" to get started.
                      </p>
                      <Button onClick={() => setShowFieldSelector(true)}>
                        <Plus className="h-4 w-4 mr-2" />
                        Add Your First Field
                      </Button>
                    </CardContent>
                  </Card>
                ) : (
                  schema.fields.map((field, index) => (
                    <FieldEditor
                      key={field.id}
                      field={field}
                      index={index}
                      onUpdate={(updates) => updateField(index, updates)}
                      onDelete={() => deleteField(index)}
                      onDuplicate={() => duplicateField(index)}
                      onMoveUp={() => moveField(index, "up")}
                      onMoveDown={() => moveField(index, "down")}
                      isFirst={index === 0}
                      isLast={index === schema.fields.length - 1}
                      isSelected={selectedFieldIndex === index}
                      onSelect={() => setSelectedFieldIndex(index)}
                    />
                  ))
                )}
              </div>

              {/* Field Type Selector */}
              <div className="lg:col-span-1">
                {showFieldSelector ? (
                  <Card>
                    <CardContent className="pt-6">
                      <AddFieldPanel
                        onSelect={addField}
                        onClose={() => setShowFieldSelector(false)}
                      />
                    </CardContent>
                  </Card>
                ) : selectedFieldIndex !== null ? (
                  <Card>
                    <CardHeader>
                      <CardTitle>Field Settings</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        Configure the selected field properties on the left.
                      </p>
                    </CardContent>
                  </Card>
                ) : (
                  <Card>
                    <CardHeader>
                      <CardTitle>Form Builder</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        Add fields to your form and configure them. Select a field to view its settings.
                      </p>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </TabsContent>

          {/* Logic Tab */}
          <TabsContent value="logic" className="mt-8">
            <div className="max-w-4xl mx-auto space-y-6">
              <div>
                <h2 className="text-lg font-semibold mb-2">Conditional Logic</h2>
                <p className="text-muted-foreground">
                  Control when fields are shown or hidden based on user input.
                </p>
              </div>

              {schema.fields.length === 0 ? (
                <Card>
                  <CardContent className="pt-6 text-center py-12">
                    <p className="text-muted-foreground">
                      Add fields to your form first before setting up conditional logic.
                    </p>
                  </CardContent>
                </Card>
              ) : (
                schema.fields.map((field, index) => (
                  <Card key={field.id}>
                    <CardHeader>
                      <CardTitle className="text-base">{field.label}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ConditionalLogicBuilder
                        field={field}
                        allFields={schema.fields}
                        onRulesChange={(rules) => updateConditionalRules(index, rules)}
                      />
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          {/* Multi-Step Tab */}
          <TabsContent value="steps" className="mt-8">
            <div className="max-w-4xl mx-auto">
              <MultiStepConfig
                fields={schema.fields}
                steps={schema.settings?.steps || []}
                enabled={schema.settings?.multiStep || false}
                onEnabledChange={(enabled) => updateMultiStepSettings(enabled)}
                onStepsChange={(steps) => updateMultiStepSettings(true, steps)}
              />
            </div>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="mt-8">
            <div className="max-w-4xl mx-auto space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Form Settings</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Consent Text */}
                  <div>
                    <Label>Consent Text</Label>
                    <Textarea
                      value={schema.settings?.consent_text || ""}
                      onChange={(e) => updateSettings({ consent_text: e.target.value })}
                      placeholder="I agree to the terms and conditions..."
                      rows={3}
                    />
                  </div>

                  {/* Redirect URL */}
                  <div>
                    <Label>Redirect URL (After Submission)</Label>
                    <Input
                      value={schema.settings?.redirect || ""}
                      onChange={(e) => updateSettings({ redirect: e.target.value })}
                      placeholder="https://example.com/thank-you"
                    />
                  </div>

                  {/* Progress Bar */}
                  {schema.settings?.multiStep && (
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Show Progress Bar</Label>
                        <p className="text-sm text-muted-foreground">
                          Display progress through multi-step form
                        </p>
                      </div>
                      <Switch
                        checked={schema.settings?.showProgressBar || false}
                        onCheckedChange={(checked) => updateSettings({ showProgressBar: checked })}
                      />
                    </div>
                  )}

                  {/* Save & Resume */}
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Allow Save & Resume</Label>
                      <p className="text-sm text-muted-foreground">
                        Let users save progress and continue later
                      </p>
                    </div>
                    <Switch
                      checked={schema.settings?.allowSaveAndResume || false}
                      onCheckedChange={(checked) => updateSettings({ allowSaveAndResume: checked })}
                    />
                  </div>

                  {schema.settings?.allowSaveAndResume && (
                    <div>
                      <Label>Resume Link Expiration (Days)</Label>
                      <Input
                        type="number"
                        value={schema.settings?.resumeExpirationDays || 7}
                        onChange={(e) => updateSettings({ resumeExpirationDays: parseInt(e.target.value) })}
                        min={1}
                        max={30}
                      />
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Integration Settings */}
              <Card>
                <CardHeader>
                  <CardTitle>Integrations</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Google Sheets</Label>
                      <p className="text-sm text-muted-foreground">
                        Send submissions to Google Sheets
                      </p>
                    </div>
                    <Switch
                      checked={schema.settings?.integrations?.google_sheets || false}
                      onCheckedChange={(checked) =>
                        updateSettings({
                          integrations: {
                            ...schema.settings?.integrations,
                            google_sheets: checked,
                          },
                        })
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Webhook</Label>
                      <p className="text-sm text-muted-foreground">
                        Send submissions to a webhook URL
                      </p>
                    </div>
                    <Switch
                      checked={schema.settings?.integrations?.webhook || false}
                      onCheckedChange={(checked) =>
                        updateSettings({
                          integrations: {
                            ...schema.settings?.integrations,
                            webhook: checked,
                          },
                        })
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Email Notifications</Label>
                      <p className="text-sm text-muted-foreground">
                        Receive email when form is submitted
                      </p>
                    </div>
                    <Switch
                      checked={schema.settings?.integrations?.email || false}
                      onCheckedChange={(checked) =>
                        updateSettings({
                          integrations: {
                            ...schema.settings?.integrations,
                            email: checked,
                          },
                        })
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Stripe Payments</Label>
                      <p className="text-sm text-muted-foreground">
                        Accept payments via Stripe
                      </p>
                    </div>
                    <Switch
                      checked={schema.settings?.integrations?.stripe || false}
                      onCheckedChange={(checked) =>
                        updateSettings({
                          integrations: {
                            ...schema.settings?.integrations,
                            stripe: checked,
                          },
                        })
                      }
                    />
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
