'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  Sparkles,
  Brain,
  Target,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Loader2,
  ArrowUpRight,
  ArrowDownRight,
  Lightbulb,
  BarChart3,
  Shuffle,
  Wand2,
  RefreshCw,
  Play,
  Pause,
  Eye,
  Users,
  Clock,
  Zap,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';

interface OptimizationSuggestion {
  id: string;
  suggestion_type: string;
  field_id: string;
  description: string;
  expected_impact: number;
  confidence: number;
  status: 'pending' | 'applied' | 'dismissed';
  created_at: string;
}

interface ConversionPrediction {
  id: string;
  form_id: string;
  predicted_rate: number;
  confidence_interval_low: number;
  confidence_interval_high: number;
  factors: { name: string; impact: number }[];
  created_at: string;
}

interface ABTest {
  id: string;
  name: string;
  status: 'draft' | 'running' | 'paused' | 'completed';
  variant_a_id: string;
  variant_b_id: string;
  variant_a_conversions: number;
  variant_b_conversions: number;
  variant_a_views: number;
  variant_b_views: number;
  statistical_significance: number;
  winner: string | null;
  created_at: string;
}

interface AIOptimizationProps {
  formId: string;
}

export function AIOptimization({ formId }: AIOptimizationProps) {
  const [suggestions, setSuggestions] = useState<OptimizationSuggestion[]>([]);
  const [prediction, setPrediction] = useState<ConversionPrediction | null>(null);
  const [abTests, setAbTests] = useState<ABTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [autoOptimize, setAutoOptimize] = useState(false);

  const fetchSuggestions = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/ai/suggestions/?form_id=${formId}`);
      const data = await response.json();
      setSuggestions(data.results || data);
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
    }
  }, [formId]);

  const fetchPrediction = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/ai/predictions/?form_id=${formId}`);
      const data = await response.json();
      if (data.results?.length > 0) {
        setPrediction(data.results[0]);
      } else if (data.length > 0) {
        setPrediction(data[0]);
      }
    } catch (error) {
      console.error('Failed to fetch prediction:', error);
    }
  }, [formId]);

  const fetchABTests = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/ai/ab-tests/?form_id=${formId}`);
      const data = await response.json();
      setAbTests(data.results || data);
    } catch (error) {
      console.error('Failed to fetch A/B tests:', error);
    }
  }, [formId]);

  useEffect(() => {
    const loadAll = async () => {
      setLoading(true);
      await Promise.all([fetchSuggestions(), fetchPrediction(), fetchABTests()]);
      setLoading(false);
    };
    loadAll();
  }, [fetchSuggestions, fetchPrediction, fetchABTests]);

  const generateSuggestions = async () => {
    setGenerating(true);
    try {
      const response = await fetch(`/api/v1/features/ai/suggestions/generate/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ form_id: formId }),
      });
      const data = await response.json();
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Failed to generate suggestions:', error);
    } finally {
      setGenerating(false);
    }
  };

  const applySuggestion = async (suggestionId: string) => {
    try {
      await fetch(`/api/v1/features/ai/suggestions/${suggestionId}/apply/`, {
        method: 'POST',
      });
      fetchSuggestions();
    } catch (error) {
      console.error('Failed to apply suggestion:', error);
    }
  };

  const dismissSuggestion = async (suggestionId: string) => {
    try {
      await fetch(`/api/v1/features/ai/suggestions/${suggestionId}/dismiss/`, {
        method: 'POST',
      });
      fetchSuggestions();
    } catch (error) {
      console.error('Failed to dismiss suggestion:', error);
    }
  };

  const createAutoABTest = async () => {
    try {
      await fetch(`/api/v1/features/ai/ab-tests/auto_create/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ form_id: formId }),
      });
      fetchABTests();
    } catch (error) {
      console.error('Failed to create A/B test:', error);
    }
  };

  const toggleABTest = async (testId: string, action: 'start' | 'pause' | 'complete') => {
    try {
      await fetch(`/api/v1/features/ai/ab-tests/${testId}/${action}/`, {
        method: 'POST',
      });
      fetchABTests();
    } catch (error) {
      console.error('Failed to toggle A/B test:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const pendingSuggestions = suggestions.filter(s => s.status === 'pending');
  const appliedSuggestions = suggestions.filter(s => s.status === 'applied');

  const getSuggestionIcon = (type: string) => {
    switch (type) {
      case 'field_order': return <Shuffle className="h-4 w-4" />;
      case 'validation': return <CheckCircle className="h-4 w-4" />;
      case 'label': return <Lightbulb className="h-4 w-4" />;
      case 'layout': return <BarChart3 className="h-4 w-4" />;
      default: return <Sparkles className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Brain className="h-6 w-6" />
            AI-Powered Optimization
          </h2>
          <p className="text-muted-foreground">Let AI optimize your forms for better conversions</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Switch
              checked={autoOptimize}
              onCheckedChange={setAutoOptimize}
            />
            <Label>Auto-Optimize</Label>
          </div>
          <Button onClick={generateSuggestions} disabled={generating}>
            {generating ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Wand2 className="h-4 w-4 mr-2" />
            )}
            Generate Suggestions
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Target className="h-4 w-4 text-blue-500" />
              Predicted Conversion
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold">
                {prediction ? `${(prediction.predicted_rate * 100).toFixed(1)}%` : 'N/A'}
              </span>
              {prediction && (
                <span className="text-xs text-muted-foreground">
                  ±{((prediction.confidence_interval_high - prediction.confidence_interval_low) * 50).toFixed(1)}%
                </span>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Lightbulb className="h-4 w-4 text-yellow-500" />
              Pending Suggestions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-3xl font-bold">{pendingSuggestions.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              Applied Suggestions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-3xl font-bold">{appliedSuggestions.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-purple-500" />
              Active A/B Tests
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-3xl font-bold">
              {abTests.filter(t => t.status === 'running').length}
            </span>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="suggestions">
        <TabsList>
          <TabsTrigger value="suggestions">
            <Lightbulb className="h-4 w-4 mr-2" />
            Suggestions
          </TabsTrigger>
          <TabsTrigger value="predictions">
            <TrendingUp className="h-4 w-4 mr-2" />
            Predictions
          </TabsTrigger>
          <TabsTrigger value="ab-tests">
            <BarChart3 className="h-4 w-4 mr-2" />
            A/B Tests
          </TabsTrigger>
        </TabsList>

        {/* Suggestions Tab */}
        <TabsContent value="suggestions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Optimization Suggestions</CardTitle>
              <CardDescription>AI-generated recommendations to improve your form</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {pendingSuggestions.map((suggestion) => (
                  <div key={suggestion.id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-primary/10 rounded-lg">
                          {getSuggestionIcon(suggestion.suggestion_type)}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">{suggestion.suggestion_type}</Badge>
                            <Badge variant="secondary">
                              Field: {suggestion.field_id}
                            </Badge>
                          </div>
                          <p className="mt-1 text-sm">{suggestion.description}</p>
                          <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <TrendingUp className="h-3 w-3" />
                              +{(suggestion.expected_impact * 100).toFixed(1)}% expected
                            </span>
                            <span className="flex items-center gap-1">
                              <Target className="h-3 w-3" />
                              {(suggestion.confidence * 100).toFixed(0)}% confidence
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => dismissSuggestion(suggestion.id)}
                        >
                          Dismiss
                        </Button>
                        <Button size="sm" onClick={() => applySuggestion(suggestion.id)}>
                          <Zap className="h-4 w-4 mr-1" />
                          Apply
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
                {pendingSuggestions.length === 0 && (
                  <div className="text-center py-8">
                    <Brain className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
                    <p className="font-medium">No pending suggestions</p>
                    <p className="text-sm text-muted-foreground mb-4">
                      Click &quot;Generate Suggestions&quot; to get AI recommendations
                    </p>
                    <Button onClick={generateSuggestions} disabled={generating}>
                      {generating ? (
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <Sparkles className="h-4 w-4 mr-2" />
                      )}
                      Generate Now
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Predictions Tab */}
        <TabsContent value="predictions" className="space-y-4">
          {prediction && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Conversion Rate Prediction</CardTitle>
                  <CardDescription>AI-predicted conversion rates based on current form configuration</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-center py-8">
                    <div className="text-center">
                      <div className="text-6xl font-bold text-primary mb-2">
                        {(prediction.predicted_rate * 100).toFixed(1)}%
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Confidence Interval: {(prediction.confidence_interval_low * 100).toFixed(1)}% - {(prediction.confidence_interval_high * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Impact Factors</CardTitle>
                  <CardDescription>Factors affecting your predicted conversion rate</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={prediction.factors}
                        layout="vertical"
                        margin={{ left: 100 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" domain={[-100, 100]} />
                        <YAxis dataKey="name" type="category" />
                        <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
                        <Bar
                          dataKey="impact"
                          fill="#8884d8"
                          radius={4}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
          {!prediction && (
            <Card>
              <CardContent className="py-8">
                <div className="text-center">
                  <TrendingUp className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
                  <p className="text-muted-foreground">No prediction data available yet</p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* A/B Tests Tab */}
        <TabsContent value="ab-tests" className="space-y-4">
          <div className="flex justify-end">
            <Button onClick={createAutoABTest}>
              <Sparkles className="h-4 w-4 mr-2" />
              Auto-Create A/B Test
            </Button>
          </div>

          <div className="space-y-4">
            {abTests.map((test) => (
              <Card key={test.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        {test.name}
                        <Badge variant={
                          test.status === 'running' ? 'default' :
                          test.status === 'completed' ? 'secondary' :
                          test.status === 'paused' ? 'outline' : 'secondary'
                        }>
                          {test.status}
                        </Badge>
                      </CardTitle>
                      <CardDescription>
                        Created {new Date(test.created_at).toLocaleDateString()}
                      </CardDescription>
                    </div>
                    <div className="flex gap-2">
                      {test.status === 'running' ? (
                        <Button size="sm" variant="outline" onClick={() => toggleABTest(test.id, 'pause')}>
                          <Pause className="h-4 w-4 mr-1" />
                          Pause
                        </Button>
                      ) : test.status === 'paused' || test.status === 'draft' ? (
                        <Button size="sm" onClick={() => toggleABTest(test.id, 'start')}>
                          <Play className="h-4 w-4 mr-1" />
                          Start
                        </Button>
                      ) : null}
                      {test.status === 'running' && (
                        <Button size="sm" onClick={() => toggleABTest(test.id, 'complete')}>
                          Complete
                        </Button>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">Variant A (Control)</span>
                        {test.winner === 'A' && (
                          <Badge className="bg-green-500">Winner</Badge>
                        )}
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-muted-foreground flex items-center gap-1">
                            <Eye className="h-3 w-3" /> Views
                          </p>
                          <p className="text-xl font-bold">{test.variant_a_views}</p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground flex items-center gap-1">
                            <Users className="h-3 w-3" /> Conversions
                          </p>
                          <p className="text-xl font-bold">{test.variant_a_conversions}</p>
                        </div>
                      </div>
                      <div className="mt-2">
                        <p className="text-sm text-muted-foreground">Rate</p>
                        <p className="text-lg font-medium">
                          {test.variant_a_views > 0
                            ? ((test.variant_a_conversions / test.variant_a_views) * 100).toFixed(2)
                            : 0}%
                        </p>
                      </div>
                    </div>

                    <div className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">Variant B</span>
                        {test.winner === 'B' && (
                          <Badge className="bg-green-500">Winner</Badge>
                        )}
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-muted-foreground flex items-center gap-1">
                            <Eye className="h-3 w-3" /> Views
                          </p>
                          <p className="text-xl font-bold">{test.variant_b_views}</p>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground flex items-center gap-1">
                            <Users className="h-3 w-3" /> Conversions
                          </p>
                          <p className="text-xl font-bold">{test.variant_b_conversions}</p>
                        </div>
                      </div>
                      <div className="mt-2">
                        <p className="text-sm text-muted-foreground">Rate</p>
                        <p className="text-lg font-medium">
                          {test.variant_b_views > 0
                            ? ((test.variant_b_conversions / test.variant_b_views) * 100).toFixed(2)
                            : 0}%
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 p-3 bg-muted rounded-lg">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Statistical Significance</span>
                      <span className="font-medium">
                        {(test.statistical_significance * 100).toFixed(1)}%
                      </span>
                    </div>
                    <Progress value={test.statistical_significance * 100} className="mt-2" />
                    {test.statistical_significance >= 0.95 && (
                      <p className="text-xs text-green-600 mt-1">
                        ✓ Results are statistically significant
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
            {abTests.length === 0 && (
              <Card>
                <CardContent className="py-8">
                  <div className="text-center">
                    <BarChart3 className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
                    <p className="font-medium">No A/B tests yet</p>
                    <p className="text-sm text-muted-foreground mb-4">
                      Create an A/B test to optimize your form
                    </p>
                    <Button onClick={createAutoABTest}>
                      <Sparkles className="h-4 w-4 mr-2" />
                      Auto-Create A/B Test
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default AIOptimization;
