'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  TrendingUp,
  Zap,
  AlertCircle,
  CheckCircle,
  RefreshCw,
  Sparkles,
  Target,
  ArrowUpRight,
  ChevronRight,
} from 'lucide-react';

interface OptimizationSuggestion {
  id: string;
  category: string;
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  expected_impact: string;
  target_field_id: string;
}

interface OptimizationAnalysis {
  optimization_score: number;
  total_views: number;
  total_submissions: number;
  conversion_rate: number;
  abandonment_rate: number;
  field_analytics: {
    field_id: string;
    label: string;
    avg_time_spent: number;
    drop_off_rate: number;
    error_rate: number;
  }[];
}

interface FormOptimizationDashboardProps {
  formId: string;
  onApplySuggestion?: (suggestionId: string) => void;
}

export function FormOptimizationDashboard({ formId, onApplySuggestion }: FormOptimizationDashboardProps) {
  const [analysis, setAnalysis] = useState<OptimizationAnalysis | null>(null);
  const [suggestions, setSuggestions] = useState<OptimizationSuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [autoOptimizing, setAutoOptimizing] = useState(false);

  useEffect(() => {
    fetchAnalysis();
    fetchSuggestions();
  }, [formId]);

  const fetchAnalysis = async () => {
    try {
      const response = await fetch(`/api/v1/automation/forms/${formId}/optimization/analyze/`);
      const data = await response.json();
      setAnalysis(data);
    } catch (error) {
      console.error('Failed to fetch analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSuggestions = async () => {
    try {
      const response = await fetch(`/api/v1/automation/forms/${formId}/optimization/suggestions/`);
      const data = await response.json();
      setSuggestions(data);
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
    }
  };

  const generateSuggestions = async () => {
    setGenerating(true);
    try {
      const response = await fetch(`/api/v1/automation/forms/${formId}/optimization/generate-suggestions/`, {
        method: 'POST',
      });
      const data = await response.json();
      setSuggestions(data.suggestions);
    } catch (error) {
      console.error('Failed to generate suggestions:', error);
    } finally {
      setGenerating(false);
    }
  };

  const applySuggestion = async (suggestionId: string) => {
    try {
      await fetch(`/api/v1/automation/forms/${formId}/optimization/apply/${suggestionId}/`, {
        method: 'POST',
      });
      setSuggestions(prev => prev.filter(s => s.id !== suggestionId));
      onApplySuggestion?.(suggestionId);
    } catch (error) {
      console.error('Failed to apply suggestion:', error);
    }
  };

  const autoOptimize = async () => {
    setAutoOptimizing(true);
    try {
      await fetch(`/api/v1/automation/forms/${formId}/optimization/auto-optimize/`, {
        method: 'POST',
      });
      await fetchAnalysis();
      await fetchSuggestions();
    } catch (error) {
      console.error('Failed to auto-optimize:', error);
    } finally {
      setAutoOptimizing(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'destructive';
      case 'medium': return 'secondary';
      case 'low': return 'outline';
      default: return 'outline';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary" />
            Form Optimization
          </h2>
          <p className="text-muted-foreground">AI-powered analysis and suggestions</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={generateSuggestions} disabled={generating}>
            {generating ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <Zap className="mr-2 h-4 w-4" />}
            Generate Suggestions
          </Button>
          <Button onClick={autoOptimize} disabled={autoOptimizing}>
            {autoOptimizing ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <Target className="mr-2 h-4 w-4" />}
            Auto-Optimize
          </Button>
        </div>
      </div>

      {/* Score Card */}
      {analysis && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Optimization Score</span>
              <span className={`text-4xl font-bold ${getScoreColor(analysis.optimization_score)}`}>
                {analysis.optimization_score}%
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Progress value={analysis.optimization_score} className="h-3 mb-4" />
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold">{analysis.total_views}</p>
                <p className="text-sm text-muted-foreground">Views</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">{analysis.total_submissions}</p>
                <p className="text-sm text-muted-foreground">Submissions</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-500">{analysis.conversion_rate}%</p>
                <p className="text-sm text-muted-foreground">Conversion</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-red-500">{analysis.abandonment_rate}%</p>
                <p className="text-sm text-muted-foreground">Abandonment</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Suggestions */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Optimization Suggestions ({suggestions.length})
        </h3>

        {suggestions.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-8">
              <CheckCircle className="h-12 w-12 text-green-500 mb-4" />
              <p className="text-lg font-medium">Great job!</p>
              <p className="text-muted-foreground">No optimization suggestions at this time.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {suggestions.map((suggestion) => (
              <Card key={suggestion.id} className="hover:shadow-md transition-shadow">
                <CardContent className="flex items-center justify-between p-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant={getPriorityColor(suggestion.priority)}>
                        {suggestion.priority}
                      </Badge>
                      <Badge variant="outline">{suggestion.category}</Badge>
                    </div>
                    <h4 className="font-medium">{suggestion.title}</h4>
                    <p className="text-sm text-muted-foreground">{suggestion.description}</p>
                    <p className="text-sm text-green-600 mt-1 flex items-center gap-1">
                      <ArrowUpRight className="h-3 w-3" />
                      Expected: {suggestion.expected_impact}
                    </p>
                  </div>
                  <Button
                    size="sm"
                    onClick={() => applySuggestion(suggestion.id)}
                    className="ml-4"
                  >
                    Apply
                    <ChevronRight className="ml-1 h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Field Analytics */}
      {analysis?.field_analytics && analysis.field_analytics.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Field Performance</CardTitle>
            <CardDescription>Analytics for each form field</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {analysis.field_analytics.map((field) => (
                <div key={field.field_id} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <div>
                    <p className="font-medium">{field.label}</p>
                    <p className="text-sm text-muted-foreground">
                      Avg. time: {field.avg_time_spent.toFixed(1)}s
                    </p>
                  </div>
                  <div className="flex gap-4 text-sm">
                    <div className="text-center">
                      <p className={field.drop_off_rate > 20 ? 'text-red-500 font-bold' : ''}>
                        {field.drop_off_rate.toFixed(1)}%
                      </p>
                      <p className="text-muted-foreground">Drop-off</p>
                    </div>
                    <div className="text-center">
                      <p className={field.error_rate > 10 ? 'text-orange-500 font-bold' : ''}>
                        {field.error_rate.toFixed(1)}%
                      </p>
                      <p className="text-muted-foreground">Errors</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default FormOptimizationDashboard;
