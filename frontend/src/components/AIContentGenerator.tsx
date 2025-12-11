'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Sparkles,
  FileText,
  Mail,
  MessageSquare,
  Globe,
  Shield,
  HelpCircle,
  RefreshCw,
  Copy,
  Check,
  Wand2,
} from 'lucide-react';

interface AIContentGeneratorProps {
  formId: string;
  formSchema?: Record<string, unknown>;
}

export function AIContentGenerator({ formId, formSchema }: AIContentGeneratorProps) {
  const [activeTab, setActiveTab] = useState('description');
  const [loading, setLoading] = useState(false);
  const [generatedContent, setGeneratedContent] = useState<Record<string, unknown> | string | null>(null);
  const [copied, setCopied] = useState(false);

  // Form state for various generators
  const [tone, setTone] = useState('professional');
  const [context, setContext] = useState('');
  const [templateType, setTemplateType] = useState('confirmation');
  const [brandName, setBrandName] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('Spanish');
  const [topic, setTopic] = useState('');
  const [questionCount, setQuestionCount] = useState('5');
  const [companyName, setCompanyName] = useState('');

  const generateContent = async (endpoint: string, body: Record<string, unknown>) => {
    setLoading(true);
    setGeneratedContent(null);
    try {
      const response = await fetch(`/api/v1/automation/forms/${formId}/content/${endpoint}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await response.json();
      setGeneratedContent(data);
    } catch (error) {
      console.error('Failed to generate content:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const renderGeneratedContent = () => {
    if (!generatedContent) return null;

    if (typeof generatedContent === 'string') {
      return (
        <div className="mt-4 p-4 bg-muted rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <Badge variant="secondary">Generated</Badge>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(generatedContent)}
            >
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </Button>
          </div>
          <p className="whitespace-pre-wrap">{generatedContent}</p>
        </div>
      );
    }

    return (
      <div className="mt-4 p-4 bg-muted rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <Badge variant="secondary">Generated</Badge>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => copyToClipboard(JSON.stringify(generatedContent, null, 2))}
          >
            {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
          </Button>
        </div>
        <pre className="text-sm overflow-x-auto whitespace-pre-wrap">
          {JSON.stringify(generatedContent, null, 2)}
        </pre>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-primary" />
          AI Content Generator
        </h2>
        <p className="text-muted-foreground">Generate form content, emails, and more with AI</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-1">
          <TabsTrigger value="description" className="text-xs">
            <FileText className="h-3 w-3 mr-1" />
            Description
          </TabsTrigger>
          <TabsTrigger value="email" className="text-xs">
            <Mail className="h-3 w-3 mr-1" />
            Email
          </TabsTrigger>
          <TabsTrigger value="thankYou" className="text-xs">
            <MessageSquare className="h-3 w-3 mr-1" />
            Thank You
          </TabsTrigger>
          <TabsTrigger value="translate" className="text-xs">
            <Globe className="h-3 w-3 mr-1" />
            Translate
          </TabsTrigger>
          <TabsTrigger value="consent" className="text-xs">
            <Shield className="h-3 w-3 mr-1" />
            Consent
          </TabsTrigger>
          <TabsTrigger value="questions" className="text-xs">
            <HelpCircle className="h-3 w-3 mr-1" />
            Questions
          </TabsTrigger>
          <TabsTrigger value="improve" className="text-xs">
            <Wand2 className="h-3 w-3 mr-1" />
            Improve
          </TabsTrigger>
        </TabsList>

        {/* Description Generator */}
        <TabsContent value="description">
          <Card>
            <CardHeader>
              <CardTitle>Generate Form Description</CardTitle>
              <CardDescription>Create an engaging description for your form</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Tone</Label>
                  <Select value={tone} onValueChange={setTone}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="professional">Professional</SelectItem>
                      <SelectItem value="friendly">Friendly</SelectItem>
                      <SelectItem value="casual">Casual</SelectItem>
                      <SelectItem value="formal">Formal</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Context (optional)</Label>
                  <Input
                    placeholder="e.g., B2B software company"
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                  />
                </div>
              </div>
              <Button
                onClick={() => generateContent('description', { tone, context })}
                disabled={loading}
                className="w-full"
              >
                {loading ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
                Generate Description
              </Button>
              {activeTab === 'description' && renderGeneratedContent()}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Email Template Generator */}
        <TabsContent value="email">
          <Card>
            <CardHeader>
              <CardTitle>Generate Email Template</CardTitle>
              <CardDescription>Create email templates for form responses</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Template Type</Label>
                  <Select value={templateType} onValueChange={setTemplateType}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="confirmation">Confirmation</SelectItem>
                      <SelectItem value="notification">Notification</SelectItem>
                      <SelectItem value="follow_up">Follow-up</SelectItem>
                      <SelectItem value="reminder">Reminder</SelectItem>
                      <SelectItem value="welcome">Welcome</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Brand Name</Label>
                  <Input
                    placeholder="Your Company Name"
                    value={brandName}
                    onChange={(e) => setBrandName(e.target.value)}
                  />
                </div>
              </div>
              <Button
                onClick={() => generateContent('email', { template_type: templateType, brand_name: brandName })}
                disabled={loading}
                className="w-full"
              >
                {loading ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <Mail className="mr-2 h-4 w-4" />}
                Generate Email Template
              </Button>
              {activeTab === 'email' && renderGeneratedContent()}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Thank You Message Generator */}
        <TabsContent value="thankYou">
          <Card>
            <CardHeader>
              <CardTitle>Generate Thank You Message</CardTitle>
              <CardDescription>Create a thank you page message</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Brand Name</Label>
                <Input
                  placeholder="Your Company Name"
                  value={brandName}
                  onChange={(e) => setBrandName(e.target.value)}
                />
              </div>
              <Button
                onClick={() => generateContent('thank-you', { brand_name: brandName })}
                disabled={loading}
                className="w-full"
              >
                {loading ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <MessageSquare className="mr-2 h-4 w-4" />}
                Generate Thank You Message
              </Button>
              {activeTab === 'thankYou' && renderGeneratedContent()}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Translation */}
        <TabsContent value="translate">
          <Card>
            <CardHeader>
              <CardTitle>Translate Form</CardTitle>
              <CardDescription>Translate your form to another language</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Target Language</Label>
                <Select value={targetLanguage} onValueChange={setTargetLanguage}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Spanish">Spanish</SelectItem>
                    <SelectItem value="French">French</SelectItem>
                    <SelectItem value="German">German</SelectItem>
                    <SelectItem value="Portuguese">Portuguese</SelectItem>
                    <SelectItem value="Italian">Italian</SelectItem>
                    <SelectItem value="Japanese">Japanese</SelectItem>
                    <SelectItem value="Chinese">Chinese</SelectItem>
                    <SelectItem value="Korean">Korean</SelectItem>
                    <SelectItem value="Arabic">Arabic</SelectItem>
                    <SelectItem value="Hindi">Hindi</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={() => generateContent('translate', { language: targetLanguage })}
                disabled={loading}
                className="w-full"
              >
                {loading ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <Globe className="mr-2 h-4 w-4" />}
                Translate Form
              </Button>
              {activeTab === 'translate' && renderGeneratedContent()}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Consent Text */}
        <TabsContent value="consent">
          <Card>
            <CardHeader>
              <CardTitle>Generate Consent Text</CardTitle>
              <CardDescription>Create GDPR-compliant consent text</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Company Name</Label>
                <Input
                  placeholder="Your Company Name"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                />
              </div>
              <Button
                onClick={() => generateContent('consent', { 
                  company_name: companyName,
                  purposes: ['data processing', 'marketing', 'analytics']
                })}
                disabled={loading}
                className="w-full"
              >
                {loading ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <Shield className="mr-2 h-4 w-4" />}
                Generate Consent Text
              </Button>
              {activeTab === 'consent' && renderGeneratedContent()}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Questions Generator */}
        <TabsContent value="questions">
          <Card>
            <CardHeader>
              <CardTitle>Generate Survey Questions</CardTitle>
              <CardDescription>Create questions for surveys or quizzes</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Topic</Label>
                  <Input
                    placeholder="e.g., Customer satisfaction"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Number of Questions</Label>
                  <Select value={questionCount} onValueChange={setQuestionCount}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="3">3 questions</SelectItem>
                      <SelectItem value="5">5 questions</SelectItem>
                      <SelectItem value="10">10 questions</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label>Context (optional)</Label>
                <Textarea
                  placeholder="Additional context about the survey..."
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                />
              </div>
              <Button
                onClick={() => generateContent('questions', { 
                  topic,
                  count: parseInt(questionCount),
                  context
                })}
                disabled={loading || !topic}
                className="w-full"
              >
                {loading ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <HelpCircle className="mr-2 h-4 w-4" />}
                Generate Questions
              </Button>
              {activeTab === 'questions' && renderGeneratedContent()}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Improve Copy */}
        <TabsContent value="improve">
          <Card>
            <CardHeader>
              <CardTitle>Improve Form Copy</CardTitle>
              <CardDescription>Get AI suggestions to improve your form text</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                AI will analyze your form and suggest improvements for clarity, engagement, and brevity.
              </p>
              <Button
                onClick={() => generateContent('suggestions', {})}
                disabled={loading}
                className="w-full"
              >
                {loading ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <Wand2 className="mr-2 h-4 w-4" />}
                Get Improvement Suggestions
              </Button>
              {activeTab === 'improve' && renderGeneratedContent()}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default AIContentGenerator;
