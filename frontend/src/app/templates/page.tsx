"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { templatesApi } from "@/lib/api-client";
import type { FormTemplate, FormSchema } from "@/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { 
  Search, 
  Camera, 
  Heart, 
  Dumbbell, 
  Home, 
  Briefcase, 
  Calendar, 
  LayoutGrid, 
  Star,
  Eye,
  FileText,
  Users,
  Loader2,
  ArrowLeft
} from "lucide-react";
import { toast } from "sonner";

const CATEGORIES = [
  { value: 'all', label: 'All Templates', icon: LayoutGrid },
  { value: 'photography', label: 'Photography', icon: Camera },
  { value: 'health', label: 'Health & Wellness', icon: Heart },
  { value: 'fitness', label: 'Fitness & Gym', icon: Dumbbell },
  { value: 'real_estate', label: 'Real Estate', icon: Home },
  { value: 'consulting', label: 'Consulting', icon: Briefcase },
  { value: 'events', label: 'Events & Catering', icon: Calendar },
  { value: 'general', label: 'General', icon: FileText },
];

export default function TemplatesPage() {
  const router = useRouter();
  const [templates, setTemplates] = useState<FormTemplate[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<FormTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [previewTemplate, setPreviewTemplate] = useState<FormTemplate | null>(null);
  const [usingTemplate, setUsingTemplate] = useState(false);

  useEffect(() => {
    loadTemplates();
  }, []);

  useEffect(() => {
    filterTemplates();
  }, [templates, selectedCategory, searchQuery]);

  const loadTemplates = async () => {
    try {
      const data = await templatesApi.list();
      setTemplates(data);
    } catch (error) {
      toast.error("Failed to load templates");
    } finally {
      setLoading(false);
    }
  };

  const filterTemplates = () => {
    let filtered = templates;

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(t => t.category === selectedCategory);
    }

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(t => 
        t.name.toLowerCase().includes(query) || 
        t.description.toLowerCase().includes(query)
      );
    }

    setFilteredTemplates(filtered);
  };

  const handleUseTemplate = async (templateId: string) => {
    setUsingTemplate(true);
    try {
      const form = await templatesApi.use(templateId);
      toast.success("Form created from template!");
      router.push(`/forms/${form.id}/edit`);
    } catch (error) {
      toast.error("Failed to create form from template");
    } finally {
      setUsingTemplate(false);
    }
  };

  const getCategoryIcon = (category: string) => {
    const cat = CATEGORIES.find(c => c.value === category);
    if (cat) {
      const Icon = cat.icon;
      return <Icon className="h-4 w-4" />;
    }
    return <FileText className="h-4 w-4" />;
  };

  const getCategoryLabel = (category: string) => {
    const cat = CATEGORIES.find(c => c.value === category);
    return cat?.label || category;
  };

  // Sample templates for demo (in case no templates exist in DB)
  const sampleTemplates: FormTemplate[] = [
    {
      id: 'sample-1',
      name: 'Wedding Photography Inquiry',
      description: 'Capture essential details from couples planning their wedding. Includes event date, venue, package preferences, and budget range.',
      category: 'photography',
      schema_json: {
        title: 'Wedding Photography Inquiry',
        description: 'Tell us about your special day',
        fields: [
          { id: 'f1', type: 'text', label: 'Your Name', required: true },
          { id: 'f2', type: 'email', label: 'Email Address', required: true },
          { id: 'f3', type: 'date', label: 'Wedding Date', required: true },
          { id: 'f4', type: 'text', label: 'Venue Location', required: true },
          { id: 'f5', type: 'number', label: 'Expected Guest Count' },
          { id: 'f6', type: 'select', label: 'Package Interest', options: ['Basic', 'Standard', 'Premium', 'Custom'] },
          { id: 'f7', type: 'textarea', label: 'Tell us about your vision' },
        ],
        settings: { consent_text: 'By submitting, you agree to be contacted about our services.' }
      },
      thumbnail_url: '',
      usage_count: 1245,
      is_featured: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'sample-2',
      name: 'Gym Membership Application',
      description: 'Streamlined signup form for new gym members with health screening questions and membership tier selection.',
      category: 'fitness',
      schema_json: {
        title: 'Join Our Gym',
        description: 'Start your fitness journey today',
        fields: [
          { id: 'f1', type: 'text', label: 'Full Name', required: true },
          { id: 'f2', type: 'email', label: 'Email', required: true },
          { id: 'f3', type: 'phone', label: 'Phone Number', required: true },
          { id: 'f4', type: 'date', label: 'Date of Birth' },
          { id: 'f5', type: 'select', label: 'Membership Type', options: ['Monthly', 'Quarterly', 'Annual'], required: true },
          { id: 'f6', type: 'multiselect', label: 'Fitness Goals', options: ['Weight Loss', 'Muscle Building', 'General Fitness', 'Sports Training'] },
          { id: 'f7', type: 'checkbox', label: 'I confirm I have no medical conditions that prevent me from exercising', required: true },
        ],
        settings: {}
      },
      thumbnail_url: '',
      usage_count: 892,
      is_featured: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'sample-3',
      name: 'Property Viewing Request',
      description: 'Real estate lead capture form for scheduling property viewings with budget and preference details.',
      category: 'real_estate',
      schema_json: {
        title: 'Schedule a Property Viewing',
        description: 'Find your dream home',
        fields: [
          { id: 'f1', type: 'text', label: 'Your Name', required: true },
          { id: 'f2', type: 'email', label: 'Email', required: true },
          { id: 'f3', type: 'phone', label: 'Phone', required: true },
          { id: 'f4', type: 'select', label: 'Budget Range', options: ['Under $200K', '$200K-$400K', '$400K-$600K', '$600K-$1M', 'Over $1M'] },
          { id: 'f5', type: 'multiselect', label: 'Property Type', options: ['House', 'Apartment', 'Condo', 'Townhouse'] },
          { id: 'f6', type: 'number', label: 'Minimum Bedrooms' },
          { id: 'f7', type: 'textarea', label: 'Additional Requirements' },
        ],
        settings: {}
      },
      thumbnail_url: '',
      usage_count: 567,
      is_featured: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'sample-4',
      name: 'Patient Intake Form',
      description: 'Comprehensive health intake form for new patients with medical history and insurance details.',
      category: 'health',
      schema_json: {
        title: 'New Patient Registration',
        description: 'Please provide your health information',
        fields: [
          { id: 'f1', type: 'text', label: 'Full Name', required: true },
          { id: 'f2', type: 'date', label: 'Date of Birth', required: true },
          { id: 'f3', type: 'email', label: 'Email', required: true },
          { id: 'f4', type: 'phone', label: 'Phone', required: true },
          { id: 'f5', type: 'textarea', label: 'Current Medications' },
          { id: 'f6', type: 'textarea', label: 'Known Allergies' },
          { id: 'f7', type: 'text', label: 'Insurance Provider' },
          { id: 'f8', type: 'text', label: 'Insurance ID' },
        ],
        settings: { consent_text: 'Your information is protected under HIPAA regulations.' }
      },
      thumbnail_url: '',
      usage_count: 2341,
      is_featured: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'sample-5',
      name: 'Consultation Booking',
      description: 'Professional services consultation request form with availability and project scope questions.',
      category: 'consulting',
      schema_json: {
        title: 'Book a Consultation',
        description: 'Let us help you achieve your goals',
        fields: [
          { id: 'f1', type: 'text', label: 'Name', required: true },
          { id: 'f2', type: 'email', label: 'Email', required: true },
          { id: 'f3', type: 'text', label: 'Company Name' },
          { id: 'f4', type: 'select', label: 'Service Interest', options: ['Strategy', 'Marketing', 'Technology', 'Operations', 'Other'] },
          { id: 'f5', type: 'select', label: 'Project Timeline', options: ['ASAP', '1-3 months', '3-6 months', '6+ months'] },
          { id: 'f6', type: 'textarea', label: 'Describe your project or challenge', required: true },
        ],
        settings: {}
      },
      thumbnail_url: '',
      usage_count: 456,
      is_featured: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: 'sample-6',
      name: 'Event RSVP',
      description: 'Event registration and RSVP form with dietary preferences and accessibility requirements.',
      category: 'events',
      schema_json: {
        title: 'Event RSVP',
        description: 'We look forward to seeing you!',
        fields: [
          { id: 'f1', type: 'text', label: 'Your Name', required: true },
          { id: 'f2', type: 'email', label: 'Email', required: true },
          { id: 'f3', type: 'number', label: 'Number of Guests', required: true },
          { id: 'f4', type: 'select', label: 'Dietary Preferences', options: ['None', 'Vegetarian', 'Vegan', 'Gluten-Free', 'Kosher', 'Halal'] },
          { id: 'f5', type: 'textarea', label: 'Allergies or Special Requirements' },
          { id: 'f6', type: 'checkbox', label: 'I require wheelchair accessibility' },
        ],
        settings: {}
      },
      thumbnail_url: '',
      usage_count: 789,
      is_featured: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ];

  const displayTemplates = filteredTemplates.length > 0 ? filteredTemplates : 
    (templates.length === 0 && !loading ? sampleTemplates.filter(t => 
      selectedCategory === 'all' || t.category === selectedCategory
    ).filter(t => 
      !searchQuery.trim() || 
      t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.description.toLowerCase().includes(searchQuery.toLowerCase())
    ) : filteredTemplates);

  const featuredTemplates = displayTemplates.filter(t => t.is_featured);
  const otherTemplates = displayTemplates.filter(t => !t.is_featured);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto" />
          <p className="mt-4 text-muted-foreground">Loading templates...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <Button variant="ghost" onClick={() => router.push("/forms/new")} className="mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Create Form
        </Button>
        <h1 className="text-4xl font-bold">Template Marketplace</h1>
        <p className="text-muted-foreground mt-2">
          Choose from professionally designed templates to get started quickly
        </p>
      </div>

      {/* Search and Categories */}
      <div className="flex flex-col lg:flex-row gap-6 mb-8">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Category Tabs */}
      <Tabs value={selectedCategory} onValueChange={setSelectedCategory} className="mb-8">
        <TabsList className="flex flex-wrap h-auto gap-2 bg-transparent">
          {CATEGORIES.map((category) => (
            <TabsTrigger
              key={category.value}
              value={category.value}
              className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground"
            >
              <category.icon className="mr-2 h-4 w-4" />
              {category.label}
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>

      {/* Featured Templates */}
      {featuredTemplates.length > 0 && (
        <div className="mb-10">
          <div className="flex items-center gap-2 mb-4">
            <Star className="h-5 w-5 text-yellow-500 fill-yellow-500" />
            <h2 className="text-2xl font-semibold">Featured Templates</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredTemplates.map((template) => (
              <TemplateCard
                key={template.id}
                template={template}
                onPreview={() => setPreviewTemplate(template)}
                onUse={() => handleUseTemplate(template.id)}
                getCategoryIcon={getCategoryIcon}
                getCategoryLabel={getCategoryLabel}
                featured
              />
            ))}
          </div>
        </div>
      )}

      {/* All Templates */}
      <div>
        <h2 className="text-2xl font-semibold mb-4">
          {selectedCategory === 'all' ? 'All Templates' : getCategoryLabel(selectedCategory)}
        </h2>
        {otherTemplates.length === 0 && featuredTemplates.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <FileText className="mx-auto h-16 w-16 text-muted-foreground mb-4" />
              <h3 className="text-xl font-semibold mb-2">No templates found</h3>
              <p className="text-muted-foreground">
                {searchQuery ? 'Try a different search term' : 'No templates in this category yet'}
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {otherTemplates.map((template) => (
              <TemplateCard
                key={template.id}
                template={template}
                onPreview={() => setPreviewTemplate(template)}
                onUse={() => handleUseTemplate(template.id)}
                getCategoryIcon={getCategoryIcon}
                getCategoryLabel={getCategoryLabel}
              />
            ))}
          </div>
        )}
      </div>

      {/* Preview Dialog */}
      <Dialog open={!!previewTemplate} onOpenChange={() => setPreviewTemplate(null)}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          {previewTemplate && (
            <>
              <DialogHeader>
                <DialogTitle>{previewTemplate.name}</DialogTitle>
                <DialogDescription>{previewTemplate.description}</DialogDescription>
              </DialogHeader>
              
              <div className="py-4">
                <div className="flex items-center gap-4 mb-4">
                  <Badge variant="outline">
                    {getCategoryIcon(previewTemplate.category)}
                    <span className="ml-1">{getCategoryLabel(previewTemplate.category)}</span>
                  </Badge>
                  <span className="text-sm text-muted-foreground flex items-center">
                    <Users className="h-4 w-4 mr-1" />
                    {previewTemplate.usage_count.toLocaleString()} uses
                  </span>
                </div>

                <div className="border rounded-lg p-4 bg-gray-50">
                  <h4 className="font-medium mb-3">Form Preview</h4>
                  <div className="space-y-3">
                    {previewTemplate.schema_json.fields.map((field, index) => (
                      <div key={index} className="flex items-center gap-2 text-sm">
                        <Badge variant="secondary" className="text-xs">
                          {field.type}
                        </Badge>
                        <span>{field.label}</span>
                        {field.required && (
                          <span className="text-red-500">*</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setPreviewTemplate(null)}>
                  Cancel
                </Button>
                <Button 
                  onClick={() => {
                    setPreviewTemplate(null);
                    handleUseTemplate(previewTemplate.id);
                  }}
                  disabled={usingTemplate}
                >
                  {usingTemplate ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    'Use This Template'
                  )}
                </Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

// Template Card Component
function TemplateCard({
  template,
  onPreview,
  onUse,
  getCategoryIcon,
  getCategoryLabel,
  featured = false,
}: {
  template: FormTemplate;
  onPreview: () => void;
  onUse: () => void;
  getCategoryIcon: (category: string) => JSX.Element;
  getCategoryLabel: (category: string) => string;
  featured?: boolean;
}) {
  return (
    <Card className={`hover:shadow-lg transition-all duration-200 ${featured ? 'ring-2 ring-yellow-400/50' : ''}`}>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <CardTitle className="line-clamp-1 flex items-center gap-2">
              {template.name}
              {featured && <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />}
            </CardTitle>
            <CardDescription className="line-clamp-2 mt-1">
              {template.description}
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <Badge variant="outline" className="flex items-center gap-1">
            {getCategoryIcon(template.category)}
            {getCategoryLabel(template.category)}
          </Badge>
          <span className="flex items-center gap-1">
            <Users className="h-3 w-3" />
            {template.usage_count.toLocaleString()}
          </span>
        </div>
        
        <div className="mt-3 text-sm">
          <span className="text-muted-foreground">
            {template.schema_json.fields.length} fields
          </span>
        </div>
      </CardContent>
      
      <CardFooter className="gap-2">
        <Button variant="outline" size="sm" className="flex-1" onClick={onPreview}>
          <Eye className="mr-1 h-4 w-4" />
          Preview
        </Button>
        <Button size="sm" className="flex-1" onClick={onUse}>
          Use Template
        </Button>
      </CardFooter>
    </Card>
  );
}
