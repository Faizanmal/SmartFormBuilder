'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Accessibility,
  Eye,
  Keyboard,
  Volume2,
  AlertCircle,
  CheckCircle,
  XCircle,
  Wand2,
  FileText,
  Download,
  RefreshCw,
  Loader2,
  Type,
  Contrast,
  MousePointer,
} from 'lucide-react';

interface AccessibilityConfig {
  id: string;
  target_wcag_level: 'A' | 'AA' | 'AAA';
  screen_reader_optimized: boolean;
  keyboard_nav_enabled: boolean;
  high_contrast_mode: boolean;
  font_scaling_enabled: boolean;
  min_font_size: number;
  focus_indicators: boolean;
  skip_links_enabled: boolean;
  aria_live_regions: boolean;
  error_announcements: boolean;
}

interface AccessibilityAudit {
  id: string;
  status: 'running' | 'completed' | 'failed';
  wcag_level_tested: string;
  issues_count: number;
  warnings_count: number;
  passed_count: number;
  score: number;
  started_at: string;
  completed_at: string;
}

interface AccessibilityIssue {
  id: string;
  issue_type: string;
  severity: 'error' | 'warning' | 'info';
  wcag_criterion: string;
  field_id: string;
  description: string;
  recommendation: string;
  auto_fix_available: boolean;
  status: 'open' | 'fixed' | 'ignored';
}

interface ComplianceReport {
  id: string;
  standards_tested: string[];
  overall_compliance: number;
  generated_at: string;
  report_url: string;
}

interface AccessibilityComplianceProps {
  formId: string;
}

const WCAG_LEVELS = {
  'A': { label: 'Level A', description: 'Essential accessibility features' },
  'AA': { label: 'Level AA', description: 'Enhanced accessibility (recommended)' },
  'AAA': { label: 'Level AAA', description: 'Maximum accessibility' },
};

export function AccessibilityCompliance({ formId }: AccessibilityComplianceProps) {
  const [config, setConfig] = useState<AccessibilityConfig | null>(null);
  const [audits, setAudits] = useState<AccessibilityAudit[]>([]);
  const [issues, setIssues] = useState<AccessibilityIssue[]>([]);
  const [reports, setReports] = useState<ComplianceReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [runningAudit, setRunningAudit] = useState(false);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [selectedAudit, setSelectedAudit] = useState<AccessibilityAudit | null>(null);

  const fetchConfig = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/accessibility/config/?form_id=${formId}`);
      const data = await response.json();
      if (data.length > 0) setConfig(data[0]);
    } catch (error) {
      console.error('Failed to fetch accessibility config:', error);
    }
  }, [formId]);

  const fetchAudits = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/accessibility/audits/?form_id=${formId}`);
      const data = await response.json();
      setAudits(data.results || data);
      if (data.length > 0) setSelectedAudit(data[0]);
    } catch (error) {
      console.error('Failed to fetch audits:', error);
    }
  }, [formId]);

  const fetchIssues = useCallback(async (auditId: string) => {
    try {
      const response = await fetch(`/api/v1/features/accessibility/audits/${auditId}/issues/`);
      const data = await response.json();
      setIssues(data);
    } catch (error) {
      console.error('Failed to fetch issues:', error);
    }
  }, []);

  const fetchReports = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/accessibility/compliance/?form_id=${formId}`);
      const data = await response.json();
      setReports(data.results || data);
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    }
  }, [formId]);

  useEffect(() => {
    const loadAll = async () => {
      setLoading(true);
      await Promise.all([fetchConfig(), fetchAudits(), fetchReports()]);
      setLoading(false);
    };
    loadAll();
  }, [fetchConfig, fetchAudits, fetchReports]);

  useEffect(() => {
    if (selectedAudit) {
      fetchIssues(selectedAudit.id);
    }
  }, [selectedAudit, fetchIssues]);

  const updateConfig = async (updates: Partial<AccessibilityConfig>) => {
    if (!config) return;
    
    try {
      await fetch(`/api/v1/features/accessibility/config/${config.id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      setConfig({ ...config, ...updates });
    } catch (error) {
      console.error('Failed to update config:', error);
    }
  };

  const runAudit = async () => {
    setRunningAudit(true);
    try {
      const response = await fetch(`/api/v1/features/accessibility/audits/run_audit/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          form_id: formId,
          wcag_level: config?.target_wcag_level || 'AA',
        }),
      });
      const newAudit = await response.json();
      setAudits([newAudit, ...audits]);
      setSelectedAudit(newAudit);
    } catch (error) {
      console.error('Failed to run audit:', error);
    } finally {
      setRunningAudit(false);
    }
  };

  const fixIssue = async (issueId: string, autoFix: boolean) => {
    try {
      await fetch(`/api/v1/features/accessibility/issues/${issueId}/fix/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ auto_fix: autoFix }),
      });
      setIssues(issues.map(i => i.id === issueId ? { ...i, status: 'fixed' } : i));
    } catch (error) {
      console.error('Failed to fix issue:', error);
    }
  };

  const generateReport = async () => {
    setGeneratingReport(true);
    try {
      const response = await fetch(`/api/v1/features/accessibility/compliance/generate/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          form_id: formId,
          standards: ['WCAG21_AA', 'Section508'],
        }),
      });
      const newReport = await response.json();
      setReports([newReport, ...reports]);
    } catch (error) {
      console.error('Failed to generate report:', error);
    } finally {
      setGeneratingReport(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const openIssues = issues.filter(i => i.status === 'open');
  const errorCount = openIssues.filter(i => i.severity === 'error').length;
  const warningCount = openIssues.filter(i => i.severity === 'warning').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Accessibility className="h-6 w-6" />
            Accessibility & Compliance
          </h2>
          <p className="text-muted-foreground">WCAG 2.1 compliance testing and configuration</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={runAudit} disabled={runningAudit}>
            {runningAudit ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-2" />
            )}
            Run Audit
          </Button>
          <Button onClick={generateReport} disabled={generatingReport}>
            {generatingReport ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <FileText className="h-4 w-4 mr-2" />
            )}
            Generate Report
          </Button>
        </div>
      </div>

      {/* Score Overview */}
      {selectedAudit && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Accessibility Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold">{selectedAudit.score}</span>
                <span className="text-sm text-muted-foreground">/100</span>
              </div>
              <Progress value={selectedAudit.score} className="mt-2" />
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <XCircle className="h-4 w-4 text-red-500" />
                Errors
              </CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-3xl font-bold text-red-500">{errorCount}</span>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-yellow-500" />
                Warnings
              </CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-3xl font-bold text-yellow-500">{warningCount}</span>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                Passed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-3xl font-bold text-green-500">{selectedAudit.passed_count}</span>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs defaultValue="issues">
        <TabsList>
          <TabsTrigger value="issues">Issues</TabsTrigger>
          <TabsTrigger value="configuration">Configuration</TabsTrigger>
          <TabsTrigger value="preferences">User Preferences</TabsTrigger>
          <TabsTrigger value="reports">Compliance Reports</TabsTrigger>
        </TabsList>

        {/* Issues Tab */}
        <TabsContent value="issues" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Accessibility Issues</CardTitle>
              <CardDescription>Issues found during the latest audit</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {openIssues.map((issue) => (
                  <div key={issue.id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-full ${
                          issue.severity === 'error' ? 'bg-red-100 text-red-600' :
                          issue.severity === 'warning' ? 'bg-yellow-100 text-yellow-600' :
                          'bg-blue-100 text-blue-600'
                        }`}>
                          {issue.severity === 'error' ? (
                            <XCircle className="h-4 w-4" />
                          ) : (
                            <AlertCircle className="h-4 w-4" />
                          )}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">{issue.wcag_criterion}</Badge>
                            <span className="font-medium">{issue.issue_type}</span>
                          </div>
                          <p className="text-sm text-muted-foreground mt-1">
                            {issue.description}
                          </p>
                          <div className="mt-2 p-2 bg-muted rounded text-sm">
                            <strong>Recommendation:</strong> {issue.recommendation}
                          </div>
                          {issue.field_id && (
                            <p className="text-xs text-muted-foreground mt-1">
                              Field: {issue.field_id}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        {issue.auto_fix_available && (
                          <Button size="sm" onClick={() => fixIssue(issue.id, true)}>
                            <Wand2 className="h-4 w-4 mr-1" />
                            Auto-fix
                          </Button>
                        )}
                        <Button size="sm" variant="outline" onClick={() => fixIssue(issue.id, false)}>
                          Mark Fixed
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
                {openIssues.length === 0 && (
                  <div className="text-center py-8">
                    <CheckCircle className="h-12 w-12 mx-auto text-green-500 mb-2" />
                    <p className="font-medium">No accessibility issues found!</p>
                    <p className="text-sm text-muted-foreground">Your form meets the accessibility standards</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Configuration Tab */}
        <TabsContent value="configuration" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Accessibility Configuration</CardTitle>
              <CardDescription>Configure accessibility features for your form</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Target WCAG Level</p>
                  <p className="text-sm text-muted-foreground">
                    {config && WCAG_LEVELS[config.target_wcag_level]?.description}
                  </p>
                </div>
                <Select
                  value={config?.target_wcag_level}
                  onValueChange={(value) => updateConfig({ target_wcag_level: value as 'A' | 'AA' | 'AAA' })}
                >
                  <SelectTrigger className="w-[150px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="A">Level A</SelectItem>
                    <SelectItem value="AA">Level AA</SelectItem>
                    <SelectItem value="AAA">Level AAA</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="border-t pt-4 space-y-4">
                <h4 className="font-medium flex items-center gap-2">
                  <Volume2 className="h-4 w-4" />
                  Screen Reader
                </h4>
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm">Optimized for Screen Readers</p>
                    <p className="text-xs text-muted-foreground">Enhanced ARIA labels and descriptions</p>
                  </div>
                  <Switch
                    checked={config?.screen_reader_optimized}
                    onCheckedChange={(checked) => updateConfig({ screen_reader_optimized: checked })}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm">ARIA Live Regions</p>
                    <p className="text-xs text-muted-foreground">Announce dynamic content changes</p>
                  </div>
                  <Switch
                    checked={config?.aria_live_regions}
                    onCheckedChange={(checked) => updateConfig({ aria_live_regions: checked })}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm">Error Announcements</p>
                    <p className="text-xs text-muted-foreground">Vocalize validation errors</p>
                  </div>
                  <Switch
                    checked={config?.error_announcements}
                    onCheckedChange={(checked) => updateConfig({ error_announcements: checked })}
                  />
                </div>
              </div>

              <div className="border-t pt-4 space-y-4">
                <h4 className="font-medium flex items-center gap-2">
                  <Keyboard className="h-4 w-4" />
                  Keyboard Navigation
                </h4>
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm">Enhanced Keyboard Navigation</p>
                    <p className="text-xs text-muted-foreground">Full keyboard accessibility</p>
                  </div>
                  <Switch
                    checked={config?.keyboard_nav_enabled}
                    onCheckedChange={(checked) => updateConfig({ keyboard_nav_enabled: checked })}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm">Visible Focus Indicators</p>
                    <p className="text-xs text-muted-foreground">Clear focus outlines for keyboard users</p>
                  </div>
                  <Switch
                    checked={config?.focus_indicators}
                    onCheckedChange={(checked) => updateConfig({ focus_indicators: checked })}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm">Skip Links</p>
                    <p className="text-xs text-muted-foreground">Quick navigation to main content</p>
                  </div>
                  <Switch
                    checked={config?.skip_links_enabled}
                    onCheckedChange={(checked) => updateConfig({ skip_links_enabled: checked })}
                  />
                </div>
              </div>

              <div className="border-t pt-4 space-y-4">
                <h4 className="font-medium flex items-center gap-2">
                  <Eye className="h-4 w-4" />
                  Visual
                </h4>
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm">High Contrast Mode</p>
                    <p className="text-xs text-muted-foreground">Increased color contrast</p>
                  </div>
                  <Switch
                    checked={config?.high_contrast_mode}
                    onCheckedChange={(checked) => updateConfig({ high_contrast_mode: checked })}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm">Font Scaling</p>
                    <p className="text-xs text-muted-foreground">Allow users to resize text</p>
                  </div>
                  <Switch
                    checked={config?.font_scaling_enabled}
                    onCheckedChange={(checked) => updateConfig({ font_scaling_enabled: checked })}
                  />
                </div>
                
                {config?.font_scaling_enabled && (
                  <div className="space-y-2">
                    <p className="text-sm">Minimum Font Size: {config?.min_font_size}px</p>
                    <Slider
                      value={[config?.min_font_size || 14]}
                      min={12}
                      max={24}
                      step={1}
                      onValueChange={([value]) => updateConfig({ min_font_size: value })}
                    />
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* User Preferences Tab */}
        <TabsContent value="preferences" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>User Accessibility Preferences</CardTitle>
              <CardDescription>
                Allow form respondents to customize their experience
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Contrast className="h-5 w-5" />
                    <h4 className="font-medium">High Contrast</h4>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Increase color contrast for better visibility
                  </p>
                  <Button variant="outline" size="sm" className="mt-3">
                    Preview
                  </Button>
                </div>
                
                <div className="border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Type className="h-5 w-5" />
                    <h4 className="font-medium">Large Text</h4>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Increase font size throughout the form
                  </p>
                  <Button variant="outline" size="sm" className="mt-3">
                    Preview
                  </Button>
                </div>
                
                <div className="border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <MousePointer className="h-5 w-5" />
                    <h4 className="font-medium">Reduced Motion</h4>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Minimize animations and transitions
                  </p>
                  <Button variant="outline" size="sm" className="mt-3">
                    Preview
                  </Button>
                </div>
                
                <div className="border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Eye className="h-5 w-5" />
                    <h4 className="font-medium">Color Blind Mode</h4>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Adjust colors for different types of color blindness
                  </p>
                  <Button variant="outline" size="sm" className="mt-3">
                    Preview
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Compliance Reports Tab */}
        <TabsContent value="reports" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Compliance Reports</CardTitle>
              <CardDescription>Documentation for accessibility compliance</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {reports.map((report) => (
                  <div key={report.id} className="flex items-center justify-between border rounded-lg p-4">
                    <div>
                      <p className="font-medium">
                        Compliance Report - {new Date(report.generated_at).toLocaleDateString()}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        {report.standards_tested.map((standard) => (
                          <Badge key={standard} variant="outline">{standard}</Badge>
                        ))}
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">
                        Overall compliance: {report.overall_compliance}%
                      </p>
                    </div>
                    <Button variant="outline" size="sm" asChild>
                      <a href={report.report_url} target="_blank" rel="noopener noreferrer">
                        <Download className="h-4 w-4 mr-2" />
                        Download
                      </a>
                    </Button>
                  </div>
                ))}
                {reports.length === 0 && (
                  <div className="text-center py-8">
                    <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
                    <p className="text-muted-foreground">No compliance reports generated yet</p>
                    <Button className="mt-4" onClick={generateReport}>
                      Generate First Report
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default AccessibilityCompliance;
