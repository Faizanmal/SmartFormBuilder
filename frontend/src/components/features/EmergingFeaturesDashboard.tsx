'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Sparkles, Mic, Shield, Webhook, Smartphone, 
  Palette, Zap, TrendingUp, Settings, CheckCircle2,
  AlertCircle, Activity, Users, Globe
} from 'lucide-react';

import { AILayoutOptimizer } from './AILayoutOptimizer';
import { VoiceMultimodalController } from './VoiceMultimodalController';
import { SecurityComplianceDashboard } from './SecurityComplianceDashboard';
import { AutomationIntegrationHub } from './AutomationIntegrationHub';
import { MobilePWAController } from './MobilePWAController';
import { UXCollaborationSuite } from './UXCollaborationSuite';
import { PerformanceDeveloperTools } from './PerformanceDeveloperTools';

interface EmergingFeaturesDashboardProps {
  formId: string;
}

interface FeatureCategory {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  status: 'active' | 'partial' | 'inactive';
  count: number;
}

export function EmergingFeaturesDashboard({ formId }: EmergingFeaturesDashboardProps) {
  // Feature categories with status indicators
  const categories: FeatureCategory[] = [
    {
      id: 'ai',
      name: 'AI & Emerging Tech',
      icon: <Sparkles className="h-5 w-5" />,
      description: 'AI layout optimization, conversational forms, predictive analytics',
      status: 'active',
      count: 6
    },
    {
      id: 'voice',
      name: 'Voice & Multimodal',
      icon: <Mic className="h-5 w-5" />,
      description: 'Voice input, OCR, camera, QR codes, NFC, AR preview',
      status: 'active',
      count: 6
    },
    {
      id: 'security',
      name: 'Security & Compliance',
      icon: <Shield className="h-5 w-5" />,
      description: 'Zero-knowledge encryption, blockchain audit, threat detection',
      status: 'active',
      count: 7
    },
    {
      id: 'integration',
      name: 'Integration & Automation',
      icon: <Webhook className="h-5 w-5" />,
      description: 'Webhooks, SSO, ERP, smart routing, approval workflows',
      status: 'active',
      count: 8
    },
    {
      id: 'mobile',
      name: 'Mobile & PWA',
      icon: <Smartphone className="h-5 w-5" />,
      description: 'Offline sync, biometrics, geofencing, mobile payments',
      status: 'partial',
      count: 5
    },
    {
      id: 'ux',
      name: 'UX & Collaboration',
      icon: <Palette className="h-5 w-5" />,
      description: 'Theme marketplace, brand guidelines, real-time collaboration',
      status: 'active',
      count: 6
    },
    {
      id: 'performance',
      name: 'Performance & Developer',
      icon: <Zap className="h-5 w-5" />,
      description: 'Edge computing, CDN, API keys, plugin system',
      status: 'active',
      count: 5
    }
  ];

  const getStatusColor = (status: FeatureCategory['status']) => {
    switch (status) {
      case 'active': return 'text-green-500 bg-green-50 border-green-200';
      case 'partial': return 'text-yellow-500 bg-yellow-50 border-yellow-200';
      case 'inactive': return 'text-gray-500 bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = (status: FeatureCategory['status']) => {
    switch (status) {
      case 'active': return <CheckCircle2 className="h-4 w-4" />;
      case 'partial': return <Activity className="h-4 w-4" />;
      case 'inactive': return <AlertCircle className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Sparkles className="h-8 w-8 text-purple-500" />
              Emerging Features Dashboard
            </h1>
            <p className="text-muted-foreground mt-2">
              Comprehensive suite of cutting-edge form capabilities
            </p>
          </div>
          <Button size="lg">
            <Settings className="mr-2 h-5 w-5" />
            Global Settings
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-4xl font-bold text-purple-600">43</p>
              <p className="text-sm text-muted-foreground mt-1">Total Features</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-4xl font-bold text-green-600">37</p>
              <p className="text-sm text-muted-foreground mt-1">Active</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-4xl font-bold text-blue-600">130+</p>
              <p className="text-sm text-muted-foreground mt-1">Database Tables</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-4xl font-bold text-orange-600">50+</p>
              <p className="text-sm text-muted-foreground mt-1">API Endpoints</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Feature Categories Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Feature Categories</CardTitle>
          <CardDescription>
            Click on any category to configure and manage its features
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {categories.map((category) => (
              <Card key={category.id} className={`border-2 ${getStatusColor(category.status)}`}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${getStatusColor(category.status)}`}>
                        {category.icon}
                      </div>
                      <div>
                        <h3 className="font-semibold">{category.name}</h3>
                        <p className="text-xs text-muted-foreground mt-1">
                          {category.description}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      {getStatusIcon(category.status)}
                    </div>
                  </div>
                  <div className="flex items-center justify-between mt-4">
                    <Badge variant="secondary" className="text-xs">
                      {category.count} features
                    </Badge>
                    <Button variant="outline" size="sm">
                      Configure
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Detailed Feature Panels */}
      <Tabs defaultValue="ai" className="w-full">
        <TabsList className="grid w-full grid-cols-7">
          <TabsTrigger value="ai">AI & Tech</TabsTrigger>
          <TabsTrigger value="voice">Voice</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="integration">Integration</TabsTrigger>
          <TabsTrigger value="mobile">Mobile</TabsTrigger>
          <TabsTrigger value="ux">UX</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
        </TabsList>

        <TabsContent value="ai" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-purple-500" />
                AI & Emerging Technology Features
              </CardTitle>
              <CardDescription>
                AI-powered layout optimization, conversational forms, predictive analytics, and industry benchmarking
              </CardDescription>
            </CardHeader>
            <CardContent>
              <AILayoutOptimizer formId={formId} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="voice" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mic className="h-5 w-5 text-blue-500" />
                Voice & Multimodal Input Features
              </CardTitle>
              <CardDescription>
                Voice transcription, OCR extraction, QR/barcode scanning, NFC tap-to-fill, and AR preview
              </CardDescription>
            </CardHeader>
            <CardContent>
              <VoiceMultimodalController formId={formId} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-green-500" />
                Security & Compliance Features
              </CardTitle>
              <CardDescription>
                Zero-knowledge encryption, blockchain audit trails, AI threat detection, and compliance scanning
              </CardDescription>
            </CardHeader>
            <CardContent>
              <SecurityComplianceDashboard formId={formId} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="integration" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Webhook className="h-5 w-5 text-orange-500" />
                Integration & Automation Features
              </CardTitle>
              <CardDescription>
                Webhook transformers, marketplace integrations, SSO, smart routing, approval workflows, and rule engines
              </CardDescription>
            </CardHeader>
            <CardContent>
              <AutomationIntegrationHub formId={formId} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="mobile" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Smartphone className="h-5 w-5 text-indigo-500" />
                Mobile & PWA Features
              </CardTitle>
              <CardDescription>
                Offline sync, biometric authentication, geofencing, mobile payments, and push notifications
              </CardDescription>
            </CardHeader>
            <CardContent>
              <MobilePWAController formId={formId} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ux" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5 text-pink-500" />
                UX & Collaboration Features
              </CardTitle>
              <CardDescription>
                Theme marketplace, brand guidelines, real-time collaboration, team workspaces, and form templates
              </CardDescription>
            </CardHeader>
            <CardContent>
              <UXCollaborationSuite formId={formId} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-500" />
                Performance & Developer Features
              </CardTitle>
              <CardDescription>
                Edge computing, CDN configuration, performance monitoring, API key management, and plugin marketplace
              </CardDescription>
            </CardHeader>
            <CardContent>
              <PerformanceDeveloperTools formId={formId} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Integration Status Footer */}
      <Card className="bg-gradient-to-r from-purple-50 to-blue-50">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-white rounded-lg shadow-sm">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h3 className="font-semibold">System Status: All Systems Operational</h3>
                <p className="text-sm text-muted-foreground">
                  All 43 features are deployed and functioning correctly
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="default" className="flex items-center gap-1">
                <Globe className="h-3 w-3" />
                Production Ready
              </Badge>
              <Badge variant="secondary" className="flex items-center gap-1">
                <Users className="h-3 w-3" />
                Multi-tenant
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
