'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Search,
  Filter,
  Download,
  RefreshCw,
  Loader2,
  Mail,
  Phone,
  MapPin,
  Copy,
  Merge,
  Trash2,
  Shield,
  Sparkles,
  FileText,
  BarChart3,
} from 'lucide-react';

interface DataQualityRule {
  id: string;
  field_id: string;
  rule_type: string;
  rule_config: Record<string, unknown>;
  severity: 'error' | 'warning' | 'info';
  error_message: string;
  is_active: boolean;
}

interface SubmissionQualityScore {
  id: string;
  submission_id: string;
  overall_score: number;
  completeness_score: number;
  accuracy_score: number;
  consistency_score: number;
  issues_found: string[];
  calculated_at: string;
}

interface DuplicateSubmission {
  id: string;
  original_id: string;
  duplicate_id: string;
  similarity_score: number;
  matching_fields: string[];
  status: 'pending' | 'merged' | 'dismissed';
}

interface ExternalValidation {
  id: string;
  field_id: string;
  validation_type: string;
  original_value: string;
  is_valid: boolean;
  validation_result: Record<string, unknown> | null;
  provider: string;
}

interface DataQualityDashboardProps {
  formId: string;
}

const RULE_TYPES = [
  { value: 'format', label: 'Format Validation' },
  { value: 'range', label: 'Range Check' },
  { value: 'required', label: 'Required Field' },
  { value: 'unique', label: 'Uniqueness' },
  { value: 'reference', label: 'Reference Check' },
  { value: 'custom', label: 'Custom Rule' },
];

export function DataQualityDashboard({ formId }: DataQualityDashboardProps) {
  const [rules, setRules] = useState<DataQualityRule[]>([]);
  const [qualityScores, setQualityScores] = useState<SubmissionQualityScore[]>([]);
  const [duplicates, setDuplicates] = useState<DuplicateSubmission[]>([]);
  const [validations, setValidations] = useState<ExternalValidation[]>([]);
  const [loading, setLoading] = useState(true);
  const [avgScore, setAvgScore] = useState(0);
  const [validatingEmail, setValidatingEmail] = useState(false);
  const [validatingPhone, setValidatingPhone] = useState(false);
  const [validatingAddress, setValidatingAddress] = useState(false);
  const [testEmail, setTestEmail] = useState('');
  const [testPhone, setTestPhone] = useState('');
  const [testAddress, setTestAddress] = useState('');
  const [emailResult, setEmailResult] = useState<Record<string, unknown> | null>(null);
  const [phoneResult, setPhoneResult] = useState<Record<string, unknown> | null>(null);
  const [addressResult, setAddressResult] = useState<Record<string, unknown> | null>(null);

  const fetchRules = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/quality/rules/?form_id=${formId}`);
      const data = await response.json();
      setRules(data.results || data);
    } catch (error) {
      console.error('Failed to fetch rules:', error);
    }
  }, [formId]);

  const fetchQualityScores = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/quality/scores/?form_id=${formId}`);
      const data = await response.json();
      setQualityScores(data.results || data);
    } catch (error) {
      console.error('Failed to fetch quality scores:', error);
    }
  }, [formId]);

  const fetchAvgScore = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/quality/scores/form_average/?form_id=${formId}`);
      const data = await response.json();
      setAvgScore(data.average_score || 0);
    } catch (error) {
      console.error('Failed to fetch average score:', error);
    }
  }, [formId]);

  const fetchDuplicates = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/quality/duplicates/?form_id=${formId}`);
      const data = await response.json();
      setDuplicates(data.results || data);
    } catch (error) {
      console.error('Failed to fetch duplicates:', error);
    }
  }, [formId]);

  useEffect(() => {
    const loadAll = async () => {
      setLoading(true);
      await Promise.all([
        fetchRules(),
        fetchQualityScores(),
        fetchAvgScore(),
        fetchDuplicates(),
      ]);
      setLoading(false);
    };
    loadAll();
  }, [fetchRules, fetchQualityScores, fetchAvgScore, fetchDuplicates]);

  const detectDuplicates = async () => {
    try {
      const response = await fetch(`/api/v1/features/quality/duplicates/detect/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ form_id: formId }),
      });
      const data = await response.json();
      setDuplicates(data.duplicates || []);
    } catch (error) {
      console.error('Failed to detect duplicates:', error);
    }
  };

  const mergeDuplicate = async (duplicateId: string, keep: 'original' | 'duplicate') => {
    try {
      await fetch(`/api/v1/features/quality/duplicates/${duplicateId}/merge/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keep }),
      });
      fetchDuplicates();
    } catch (error) {
      console.error('Failed to merge duplicate:', error);
    }
  };

  const validateEmail = async () => {
    setValidatingEmail(true);
    try {
      const response = await fetch(`/api/v1/features/quality/validations/validate_email/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: testEmail }),
      });
      const data = await response.json();
      setEmailResult(data);
    } catch (error) {
      console.error('Failed to validate email:', error);
    } finally {
      setValidatingEmail(false);
    }
  };

  const validatePhone = async () => {
    setValidatingPhone(true);
    try {
      const response = await fetch(`/api/v1/features/quality/validations/validate_phone/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone: testPhone, country: 'US' }),
      });
      const data = await response.json();
      setPhoneResult(data);
    } catch (error) {
      console.error('Failed to validate phone:', error);
    } finally {
      setValidatingPhone(false);
    }
  };

  const validateAddress = async () => {
    setValidatingAddress(true);
    try {
      const response = await fetch(`/api/v1/features/quality/validations/validate_address/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address: { street: testAddress } }),
      });
      const data = await response.json();
      setAddressResult(data);
    } catch (error) {
      console.error('Failed to validate address:', error);
    } finally {
      setValidatingAddress(false);
    }
  };

  const exportWithQuality = async (format: string) => {
    try {
      const response = await fetch(`/api/v1/features/quality/export/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          form_id: formId,
          format: format,
          include_quality: true,
          min_quality_score: 0,
        }),
      });
      const data = await response.json();
      
      if (data.download_url) {
        window.open(data.download_url, '_blank');
      }
    } catch (error) {
      console.error('Failed to export:', error);
    }
  };

  const toggleRule = async (ruleId: string, isActive: boolean) => {
    try {
      await fetch(`/api/v1/features/quality/rules/${ruleId}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: isActive }),
      });
      fetchRules();
    } catch (error) {
      console.error('Failed to toggle rule:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const pendingDuplicates = duplicates.filter(d => d.status === 'pending');
  const scoreColor = avgScore >= 80 ? 'text-green-500' : avgScore >= 60 ? 'text-yellow-500' : 'text-red-500';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Shield className="h-6 w-6" />
            Data Quality
          </h2>
          <p className="text-muted-foreground">Ensure accurate and clean data</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={detectDuplicates}>
            <Search className="h-4 w-4 mr-2" />
            Detect Duplicates
          </Button>
          <Select onValueChange={exportWithQuality}>
            <SelectTrigger className="w-[160px]">
              <Download className="h-4 w-4 mr-2" />
              <SelectValue placeholder="Export" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="csv">Export CSV</SelectItem>
              <SelectItem value="json">Export JSON</SelectItem>
              <SelectItem value="excel">Export Excel</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Average Quality Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className={`text-3xl font-bold ${scoreColor}`}>{avgScore.toFixed(1)}</span>
              <span className="text-sm text-muted-foreground">/100</span>
            </div>
            <Progress value={avgScore} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Active Rules</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-3xl font-bold">
              {rules.filter(r => r.is_active).length}
            </span>
            <span className="text-sm text-muted-foreground ml-2">
              / {rules.length} total
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Copy className="h-4 w-4 text-yellow-500" />
              Pending Duplicates
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-3xl font-bold text-yellow-500">
              {pendingDuplicates.length}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Submissions Scored</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-3xl font-bold">{qualityScores.length}</span>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="rules">
        <TabsList>
          <TabsTrigger value="rules">Quality Rules</TabsTrigger>
          <TabsTrigger value="validation">External Validation</TabsTrigger>
          <TabsTrigger value="duplicates">
            Duplicates
            {pendingDuplicates.length > 0 && (
              <Badge variant="secondary" className="ml-2">
                {pendingDuplicates.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="scores">Submission Scores</TabsTrigger>
        </TabsList>

        {/* Quality Rules Tab */}
        <TabsContent value="rules" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Data Quality Rules</CardTitle>
                  <CardDescription>Define validation and quality rules for your data</CardDescription>
                </div>
                <Button>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Add Rule
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {rules.map((rule) => (
                  <div key={rule.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className={`p-2 rounded-full ${
                        rule.severity === 'error' ? 'bg-red-100 text-red-600' :
                        rule.severity === 'warning' ? 'bg-yellow-100 text-yellow-600' :
                        'bg-blue-100 text-blue-600'
                      }`}>
                        {rule.severity === 'error' ? <XCircle className="h-4 w-4" /> :
                         rule.severity === 'warning' ? <AlertTriangle className="h-4 w-4" /> :
                         <CheckCircle className="h-4 w-4" />}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{rule.field_id}</span>
                          <Badge variant="outline">{rule.rule_type}</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{rule.error_message}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Switch
                        checked={rule.is_active}
                        onCheckedChange={(checked) => toggleRule(rule.id, checked)}
                      />
                      <Button variant="ghost" size="icon">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
                {rules.length === 0 && (
                  <div className="text-center py-8">
                    <Shield className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
                    <p className="text-muted-foreground">No quality rules defined yet</p>
                    <Button className="mt-4" variant="outline">Create First Rule</Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* External Validation Tab */}
        <TabsContent value="validation" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mail className="h-5 w-5" />
                  Email Validation
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  placeholder="Enter email to validate"
                  value={testEmail}
                  onChange={(e) => setTestEmail(e.target.value)}
                />
                <Button
                  className="w-full"
                  onClick={validateEmail}
                  disabled={validatingEmail || !testEmail}
                >
                  {validatingEmail ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <CheckCircle className="h-4 w-4 mr-2" />
                  )}
                  Validate Email
                </Button>
                {emailResult && (
                  <div className={`p-3 rounded-lg ${
                    emailResult.is_valid ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                  }`}>
                    <div className="flex items-center gap-2">
                      {emailResult.is_valid ? (
                        <CheckCircle className="h-4 w-4" />
                      ) : (
                        <XCircle className="h-4 w-4" />
                      )}
                      <span className="font-medium">
                        {emailResult.is_valid ? 'Valid Email' : 'Invalid Email'}
                      </span>
                    </div>
                    {emailResult.details ? (
                      <p className="text-sm mt-1">{String(emailResult.details)}</p>
                    ) : null}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Phone className="h-5 w-5" />
                  Phone Validation
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  placeholder="Enter phone to validate"
                  value={testPhone}
                  onChange={(e) => setTestPhone(e.target.value)}
                />
                <Button
                  className="w-full"
                  onClick={validatePhone}
                  disabled={validatingPhone || !testPhone}
                >
                  {validatingPhone ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <CheckCircle className="h-4 w-4 mr-2" />
                  )}
                  Validate Phone
                </Button>
                {phoneResult && (
                  <div className={`p-3 rounded-lg ${
                    phoneResult.is_valid ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                  }`}>
                    <div className="flex items-center gap-2">
                      {phoneResult.is_valid ? (
                        <CheckCircle className="h-4 w-4" />
                      ) : (
                        <XCircle className="h-4 w-4" />
                      )}
                      <span className="font-medium">
                        {phoneResult.is_valid ? 'Valid Phone' : 'Invalid Phone'}
                      </span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="h-5 w-5" />
                  Address Validation
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  placeholder="Enter address to validate"
                  value={testAddress}
                  onChange={(e) => setTestAddress(e.target.value)}
                />
                <Button
                  className="w-full"
                  onClick={validateAddress}
                  disabled={validatingAddress || !testAddress}
                >
                  {validatingAddress ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <CheckCircle className="h-4 w-4 mr-2" />
                  )}
                  Validate Address
                </Button>
                {addressResult && (
                  <div className={`p-3 rounded-lg ${
                    addressResult.is_valid ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                  }`}>
                    <div className="flex items-center gap-2">
                      {addressResult.is_valid ? (
                        <CheckCircle className="h-4 w-4" />
                      ) : (
                        <XCircle className="h-4 w-4" />
                      )}
                      <span className="font-medium">
                        {addressResult.is_valid ? 'Valid Address' : 'Invalid Address'}
                      </span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Duplicates Tab */}
        <TabsContent value="duplicates" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Duplicate Detection</CardTitle>
              <CardDescription>Review and manage duplicate submissions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {pendingDuplicates.map((dup) => (
                  <div key={dup.id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary">
                            {(dup.similarity_score * 100).toFixed(0)}% match
                          </Badge>
                          <span className="text-sm text-muted-foreground">
                            {dup.matching_fields.length} matching fields
                          </span>
                        </div>
                        <div className="mt-2 flex flex-wrap gap-1">
                          {dup.matching_fields.map((field) => (
                            <Badge key={field} variant="outline" className="text-xs">
                              {field}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => mergeDuplicate(dup.id, 'original')}
                        >
                          Keep Original
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => mergeDuplicate(dup.id, 'duplicate')}
                        >
                          Keep Duplicate
                        </Button>
                        <Button size="sm">
                          <Merge className="h-4 w-4 mr-1" />
                          Merge
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
                {pendingDuplicates.length === 0 && (
                  <div className="text-center py-8">
                    <CheckCircle className="h-12 w-12 mx-auto text-green-500 mb-2" />
                    <p className="font-medium">No duplicates found</p>
                    <p className="text-sm text-muted-foreground">Your data is clean!</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Submission Scores Tab */}
        <TabsContent value="scores" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Submission Quality Scores</CardTitle>
              <CardDescription>Quality assessment for each submission</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {qualityScores.slice(0, 20).map((score) => (
                  <div key={score.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className={`text-2xl font-bold ${
                        score.overall_score >= 80 ? 'text-green-500' :
                        score.overall_score >= 60 ? 'text-yellow-500' : 'text-red-500'
                      }`}>
                        {score.overall_score.toFixed(0)}
                      </div>
                      <div>
                        <p className="font-medium">Submission {score.submission_id.slice(0, 8)}...</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(score.calculated_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-center">
                        <p className="text-xs text-muted-foreground">Completeness</p>
                        <p className="font-medium">{score.completeness_score.toFixed(0)}%</p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-muted-foreground">Accuracy</p>
                        <p className="font-medium">{score.accuracy_score.toFixed(0)}%</p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-muted-foreground">Consistency</p>
                        <p className="font-medium">{score.consistency_score.toFixed(0)}%</p>
                      </div>
                      {score.issues_found.length > 0 && (
                        <Badge variant="secondary">
                          {score.issues_found.length} issues
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
                {qualityScores.length === 0 && (
                  <p className="text-center text-muted-foreground py-8">
                    No submissions scored yet
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default DataQualityDashboard;
