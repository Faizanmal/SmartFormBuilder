"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { formsApi } from "@/lib/api-client";
import type { Form } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PlusCircle, FileText, BarChart3, Settings, ExternalLink } from "lucide-react";
import { toast } from "sonner";

export default function DashboardPage() {
  const router = useRouter();
  const [forms, setForms] = useState<Form[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadForms();
  }, []);

  const loadForms = async () => {
    try {
      const data = await formsApi.list();
      setForms(data);
    } catch (error) {
      toast.error("Failed to load forms");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateForm = () => {
    router.push("/forms/new");
  };

  const handleViewForm = (slug: string) => {
    window.open(`/form/${slug}`, '_blank');
  };

  const handleEditForm = (id: string) => {
    router.push(`/forms/${id}/edit`);
  };

  const handleViewAnalytics = (id: string) => {
    router.push(`/forms/${id}/analytics`);
  };

  const handleViewIntegrations = (id: string) => {
    router.push(`/forms/${id}/integrations`);
  };

  const handleViewEmbed = (id: string) => {
    router.push(`/forms/${id}/embed`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading forms...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold">My Forms</h1>
          <p className="text-muted-foreground mt-2">
            Create and manage your smart forms
          </p>
        </div>
        <Button onClick={handleCreateForm} size="lg">
          <PlusCircle className="mr-2 h-5 w-5" />
          Create Form
        </Button>
      </div>

      {forms.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <FileText className="mx-auto h-16 w-16 text-muted-foreground mb-4" />
            <h3 className="text-xl font-semibold mb-2">No forms yet</h3>
            <p className="text-muted-foreground mb-6">
              Get started by creating your first form. Just describe what you need and AI will generate it for you.
            </p>
            <Button onClick={handleCreateForm}>
              <PlusCircle className="mr-2 h-4 w-4" />
              Create Your First Form
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {forms.map((form) => (
            <Card key={form.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <CardTitle className="line-clamp-1">{form.title}</CardTitle>
                    <CardDescription className="line-clamp-2 mt-1">
                      {form.description || "No description"}
                    </CardDescription>
                  </div>
                  <Badge variant={form.published_at ? "default" : "secondary"}>
                    {form.published_at ? "Published" : "Draft"}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <div className="text-2xl font-bold">{form.views_count}</div>
                      <div className="text-xs text-muted-foreground">Views</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{form.submissions_count}</div>
                      <div className="text-xs text-muted-foreground">Submissions</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{form.conversion_rate}%</div>
                      <div className="text-xs text-muted-foreground">Conversion</div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => handleEditForm(form.id)}
                    >
                      <Settings className="mr-1 h-4 w-4" />
                      Edit
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => handleViewAnalytics(form.id)}
                    >
                      <BarChart3 className="mr-1 h-4 w-4" />
                      Analytics
                    </Button>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => handleViewEmbed(form.id)}
                    >
                      Embed
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => handleViewIntegrations(form.id)}
                    >
                      Integrations
                    </Button>
                  </div>
                  
                  <div className="flex gap-2">
                    <Button
                      variant="default"
                      size="sm"
                      className="flex-1"
                      onClick={() => handleViewForm(form.slug)}
                    >
                      <ExternalLink className="mr-1 h-4 w-4" />
                      View Form
                    </Button>
                  </div>

                  {/* Metadata */}
                  <div className="text-xs text-muted-foreground pt-2 border-t">
                    <div>Slug: <code className="bg-muted px-1 rounded">{form.slug}</code></div>
                    <div className="mt-1">
                      Created: {new Date(form.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
