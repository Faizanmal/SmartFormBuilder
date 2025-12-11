'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Shield,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Eye,
  Accessibility,
  Lock,
  FileText,
  RefreshCw,
  Wrench,
  Download,
} from 'lucide-react';

interface ComplianceIssue {
  id: string;
  type: string;
  severity: 'critical' | 'warning' | 'info';
  message: string;
  field_id?: string;
  auto_fixable: boolean;
  fix_description?: string;
}

interface ComplianceScan {
  id: string;
  scan_type: string;
  overall_score: number;
  issues_found: number;
  issues_fixed: number;
  gdpr_score: number;
  wcag_score: number;
  hipaa_score?: number;
  pci_score?: number;
  issues: ComplianceIssue[];
}

interface ComplianceScannerProps {
  formId: string;
}

const SCAN_TYPES = [
  { id: 'gdpr', name: 'GDPR', icon: Lock, description: 'General Data Protection Regulation' },
  { id: 'wcag', name: 'WCAG', icon: Accessibility, description: 'Web Content Accessibility Guidelines' },
  { id: 'hipaa', name: 'HIPAA', icon: Shield, description: 'Health Insurance Portability' },
  { id: 'pci', name: 'PCI-DSS', icon: Lock, description: 'Payment Card Industry Standard' },
];

export function ComplianceScanner({ formId }: ComplianceScannerProps) {
  const [scan, setScan] = useState<ComplianceScan | null>(null);
  const [scanning, setScanning] = useState(false);
  const [fixing, setFixing] = useState(false);
  const [selectedTypes, setSelectedTypes] = useState(['gdpr', 'wcag']);
  const [generatingPolicy, setGeneratingPolicy] = useState(false);

  useEffect(() => {
    fetchLatestScan();
  }, [formId]);

  const fetchLatestScan = async () => {
    try {
      const response = await fetch(`/api/v1/automation/forms/${formId}/compliance/history/`);
      const data = await response.json();
      if (data.length > 0) {
        setScan(data[0]);
      }
    } catch (error) {
      console.error('Failed to fetch scan history:', error);
    }
  };

  const runScan = async () => {
    setScanning(true);
    try {
      const response = await fetch(`/api/v1/automation/forms/${formId}/compliance/scan/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scan_types: selectedTypes }),
      });
      const data = await response.json();
      setScan(data);
    } catch (error) {
      console.error('Failed to run scan:', error);
    } finally {
      setScanning(false);
    }
  };

  const applyAutoFixes = async () => {
    setFixing(true);
    try {
      const response = await fetch(`/api/v1/automation/forms/${formId}/compliance/auto-fix/`, {
        method: 'POST',
      });
      const data = await response.json();
      await runScan(); // Re-scan after fixes
    } catch (error) {
      console.error('Failed to apply fixes:', error);
    } finally {
      setFixing(false);
    }
  };

  const generatePrivacyPolicy = async () => {
    setGeneratingPolicy(true);
    try {
      const response = await fetch(`/api/v1/automation/forms/${formId}/compliance/privacy-policy/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_name: 'Your Company' }),
      });
      const data = await response.json();
      // Download or display policy
      const blob = new Blob([data.policy], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'privacy-policy.md';
      a.click();
    } catch (error) {
      console.error('Failed to generate policy:', error);
    } finally {
      setGeneratingPolicy(false);
    }
  };

  const toggleScanType = (type: string) => {
    setSelectedTypes(prev => 
      prev.includes(type)
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <XCircle className="h-5 w-5 text-red-500" />;
      case 'warning': return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'info': return <Eye className="h-5 w-5 text-blue-500" />;
      default: return null;
    }
  };

  const autoFixableCount = scan?.issues.filter(i => i.auto_fixable).length || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Shield className="h-6 w-6 text-primary" />
            Compliance Scanner
          </h2>
          <p className="text-muted-foreground">GDPR, WCAG, and accessibility compliance</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={generatePrivacyPolicy} disabled={generatingPolicy}>
            {generatingPolicy ? (
              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <FileText className="mr-2 h-4 w-4" />
            )}
            Generate Privacy Policy
          </Button>
          <Button onClick={runScan} disabled={scanning || selectedTypes.length === 0}>
            {scanning ? (
              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Shield className="mr-2 h-4 w-4" />
            )}
            Run Scan
          </Button>
        </div>
      </div>

      {/* Scan Type Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Compliance Standards</CardTitle>
          <CardDescription>Select which standards to check</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {SCAN_TYPES.map((type) => {
              const Icon = type.icon;
              const isSelected = selectedTypes.includes(type.id);
              return (
                <button
                  key={type.id}
                  onClick={() => toggleScanType(type.id)}
                  className={`p-4 rounded-lg border-2 transition-all text-left ${
                    isSelected 
                      ? 'border-primary bg-primary/5' 
                      : 'border-transparent bg-muted hover:border-muted-foreground/20'
                  }`}
                >
                  <Icon className={`h-6 w-6 mb-2 ${isSelected ? 'text-primary' : 'text-muted-foreground'}`} />
                  <p className="font-medium">{type.name}</p>
                  <p className="text-xs text-muted-foreground">{type.description}</p>
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Scan Results */}
      {scan && (
        <>
          {/* Overall Score */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Compliance Score</span>
                <span className={`text-4xl font-bold ${getScoreColor(scan.overall_score)}`}>
                  {scan.overall_score}%
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Progress value={scan.overall_score} className="h-3 mb-4" />
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {scan.gdpr_score !== undefined && (
                  <div className="text-center">
                    <p className={`text-2xl font-bold ${getScoreColor(scan.gdpr_score)}`}>
                      {scan.gdpr_score}%
                    </p>
                    <p className="text-sm text-muted-foreground">GDPR</p>
                  </div>
                )}
                {scan.wcag_score !== undefined && (
                  <div className="text-center">
                    <p className={`text-2xl font-bold ${getScoreColor(scan.wcag_score)}`}>
                      {scan.wcag_score}%
                    </p>
                    <p className="text-sm text-muted-foreground">WCAG</p>
                  </div>
                )}
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-500">{scan.issues_found}</p>
                  <p className="text-sm text-muted-foreground">Issues Found</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-500">{scan.issues_fixed}</p>
                  <p className="text-sm text-muted-foreground">Issues Fixed</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Issues List */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Issues ({scan.issues.length})</CardTitle>
                  <CardDescription>
                    {autoFixableCount} issues can be automatically fixed
                  </CardDescription>
                </div>
                {autoFixableCount > 0 && (
                  <Button onClick={applyAutoFixes} disabled={fixing}>
                    {fixing ? (
                      <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Wrench className="mr-2 h-4 w-4" />
                    )}
                    Auto-Fix ({autoFixableCount})
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="all">
                <TabsList>
                  <TabsTrigger value="all">All</TabsTrigger>
                  <TabsTrigger value="critical">Critical</TabsTrigger>
                  <TabsTrigger value="warning">Warnings</TabsTrigger>
                  <TabsTrigger value="fixable">Auto-Fixable</TabsTrigger>
                </TabsList>

                <TabsContent value="all" className="mt-4 space-y-3">
                  {scan.issues.map((issue, index) => (
                    <IssueCard key={index} issue={issue} />
                  ))}
                </TabsContent>

                <TabsContent value="critical" className="mt-4 space-y-3">
                  {scan.issues.filter(i => i.severity === 'critical').map((issue, index) => (
                    <IssueCard key={index} issue={issue} />
                  ))}
                </TabsContent>

                <TabsContent value="warning" className="mt-4 space-y-3">
                  {scan.issues.filter(i => i.severity === 'warning').map((issue, index) => (
                    <IssueCard key={index} issue={issue} />
                  ))}
                </TabsContent>

                <TabsContent value="fixable" className="mt-4 space-y-3">
                  {scan.issues.filter(i => i.auto_fixable).map((issue, index) => (
                    <IssueCard key={index} issue={issue} />
                  ))}
                </TabsContent>
              </Tabs>

              {scan.issues.length === 0 && (
                <div className="flex flex-col items-center justify-center py-8">
                  <CheckCircle className="h-12 w-12 text-green-500 mb-4" />
                  <p className="text-lg font-medium">All Clear!</p>
                  <p className="text-muted-foreground">No compliance issues found.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* No Scan Yet */}
      {!scan && !scanning && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Shield className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-lg font-medium">No scan results yet</p>
            <p className="text-muted-foreground mb-4">Run a compliance scan to check your form</p>
            <Button onClick={runScan} disabled={selectedTypes.length === 0}>
              <Shield className="mr-2 h-4 w-4" />
              Run First Scan
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function IssueCard({ issue }: { issue: ComplianceIssue }) {
  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <XCircle className="h-5 w-5 text-red-500" />;
      case 'warning': return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'info': return <Eye className="h-5 w-5 text-blue-500" />;
      default: return null;
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'critical': return 'destructive';
      case 'warning': return 'secondary';
      default: return 'outline';
    }
  };

  return (
    <div className="flex items-start gap-3 p-3 border rounded-lg">
      {getSeverityIcon(issue.severity)}
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-1">
          <Badge variant={getSeverityBadge(issue.severity) as any}>
            {issue.severity}
          </Badge>
          <Badge variant="outline">{issue.type}</Badge>
          {issue.auto_fixable && (
            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
              <Wrench className="h-3 w-3 mr-1" />
              Auto-fixable
            </Badge>
          )}
        </div>
        <p className="text-sm">{issue.message}</p>
        {issue.fix_description && (
          <p className="text-sm text-muted-foreground mt-1">
            Fix: {issue.fix_description}
          </p>
        )}
        {issue.field_id && (
          <p className="text-xs text-muted-foreground mt-1">
            Field: {issue.field_id}
          </p>
        )}
      </div>
    </div>
  );
}

export default ComplianceScanner;
