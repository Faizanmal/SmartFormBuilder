'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  useAILayoutSuggestions, 
  useGenerateAILayoutSuggestion,
  useHeatmapAnalysis 
} from '@/hooks/use-emerging-features';
import { Loader2, Sparkles, TrendingUp, AlertCircle, CheckCircle2 } from 'lucide-react';

interface AILayoutOptimizerProps {
  formId: string;
}

export function AILayoutOptimizer({ formId }: AILayoutOptimizerProps) {
  const [selectedProvider, setSelectedProvider] = useState<'openai' | 'anthropic' | 'google'>('openai');
  
  const { data: suggestions, isLoading: loadingSuggestions } = useAILayoutSuggestions(formId);
  const { data: heatmapData } = useHeatmapAnalysis(formId);
  const generateSuggestion = useGenerateAILayoutSuggestion();

  const handleGenerate = () => {
    generateSuggestion.mutate({ 
      formId, 
      triggerType: 'manual' 
    });
  };

  const latestSuggestion = suggestions?.[0];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-purple-500" />
                AI Layout Optimizer
              </CardTitle>
              <CardDescription>
                Get AI-powered suggestions to improve your form layout and conversion rates
              </CardDescription>
            </div>
            <Button 
              onClick={handleGenerate}
              disabled={generateSuggestion.isPending}
            >
              {generateSuggestion.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Generate Suggestions
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="suggestions">
            <TabsList>
              <TabsTrigger value="suggestions">Suggestions</TabsTrigger>
              <TabsTrigger value="heatmap">Heatmap Analysis</TabsTrigger>
              <TabsTrigger value="history">History</TabsTrigger>
            </TabsList>

            <TabsContent value="suggestions" className="space-y-4">
              {loadingSuggestions ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                </div>
              ) : latestSuggestion ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Badge variant={latestSuggestion.status === 'completed' ? 'default' : 'secondary'}>
                      {latestSuggestion.status}
                    </Badge>
                    <Badge variant="outline">
                      {latestSuggestion.ai_provider}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      {new Date(latestSuggestion.created_at).toLocaleString()}
                    </span>
                  </div>

                  {latestSuggestion.suggestions.map((suggestion, index) => (
                    <Card key={index} className="border-l-4 border-l-purple-500">
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div className="space-y-2 flex-1">
                            <div className="flex items-center gap-2">
                              <Badge>{suggestion.type}</Badge>
                              <span className="text-sm font-medium">
                                Confidence: {(suggestion.confidence * 100).toFixed(0)}%
                              </span>
                            </div>
                            <p className="text-sm">{suggestion.description}</p>
                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                              <TrendingUp className="h-4 w-4" />
                              Estimated Impact: {suggestion.impact_estimate}
                            </div>
                          </div>
                          <Button variant="outline" size="sm">
                            Apply
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Sparkles className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No suggestions yet. Click &quot;Generate Suggestions&quot; to get started.</p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="heatmap" className="space-y-4">
              {heatmapData ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-2xl font-bold">{heatmapData.session_count}</div>
                        <p className="text-sm text-muted-foreground">Sessions Analyzed</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-2xl font-bold">
                          {Object.keys(heatmapData.heatmap_data.fieldInteractions || {}).length}
                        </div>
                        <p className="text-sm text-muted-foreground">Fields Tracked</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-2xl font-bold">
                          {heatmapData.heatmap_data.clicks?.length || 0}
                        </div>
                        <p className="text-sm text-muted-foreground">Click Points</p>
                      </CardContent>
                    </Card>
                  </div>

                  <Card>
                    <CardHeader>
                      <CardTitle>Field Interactions</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {Object.entries(heatmapData.heatmap_data.fieldInteractions || {}).map(([field, count]) => (
                          <div key={field} className="flex items-center justify-between">
                            <span className="text-sm">{field}</span>
                            <div className="flex items-center gap-2">
                              <div className="w-32 bg-secondary h-2 rounded-full overflow-hidden">
                                <div 
                                  className="bg-purple-500 h-full" 
                                  style={{ width: `${Math.min((count as number / heatmapData.session_count) * 100, 100)}%` }}
                                />
                              </div>
                              <span className="text-sm font-medium w-12 text-right">{count}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No heatmap data available yet.</p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="history" className="space-y-4">
              {suggestions && suggestions.length > 0 ? (
                <div className="space-y-2">
                  {suggestions.map((suggestion) => (
                    <Card key={suggestion.id}>
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <Badge variant={suggestion.status === 'completed' ? 'default' : 'secondary'}>
                                {suggestion.status}
                              </Badge>
                              <span className="text-sm text-muted-foreground">
                                {new Date(suggestion.created_at).toLocaleString()}
                              </span>
                            </div>
                            <p className="text-sm">
                              {suggestion.suggestions.length} suggestions • {suggestion.ai_provider}
                            </p>
                          </div>
                          <Button variant="ghost" size="sm">
                            View Details
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <p>No history available.</p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
