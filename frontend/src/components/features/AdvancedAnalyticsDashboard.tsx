'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  MousePointerClick,
  Video,
  TrendingDown,
  BarChart3,
  FlaskConical,
  Lightbulb,
  Play,
  Pause,
  SkipForward,
  Filter,
  Download,
  Eye,
  Loader2,
  AlertCircle,
  CheckCircle,
} from 'lucide-react';

interface HeatmapPoint {
  x_position: number;
  y_position: number;
  field_id: string;
  interaction_type: string;
  count: number;
  avg_duration: number;
}

interface SessionRecording {
  id: string;
  session_id: string;
  device_type: string;
  browser: string;
  duration_seconds: number;
  completed_form: boolean;
  drop_off_field: string;
  rage_clicks_count: number;
  started_at: string;
}

interface DropOffData {
  field_id: string;
  field_label: string;
  drop_off_count: number;
  drop_off_rate: number;
  avg_time_before_drop: number;
}

interface ABTestResult {
  id: string;
  variant_name: string;
  visitors: number;
  conversions: number;
  conversion_rate: number;
  improvement: number;
  confidence_level: number;
  is_winner: boolean;
}

interface BehaviorInsight {
  id: string;
  insight_type: string;
  title: string;
  description: string;
  severity: 'high' | 'medium' | 'low';
  recommendation: string;
  potential_impact: string;
}

interface AdvancedAnalyticsProps {
  formId: string;
}

export function AdvancedAnalyticsDashboard({ formId }: AdvancedAnalyticsProps) {
  const [heatmapData, setHeatmapData] = useState<HeatmapPoint[]>([]);
  const [recordings, setRecordings] = useState<SessionRecording[]>([]);
  const [dropOffData, setDropOffData] = useState<DropOffData[]>([]);
  const [abResults, setAbResults] = useState<ABTestResult[]>([]);
  const [insights, setInsights] = useState<BehaviorInsight[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRecording, setSelectedRecording] = useState<SessionRecording | null>(null);
  const [heatmapType, setHeatmapType] = useState<string>('click');
  const [deviceFilter, setDeviceFilter] = useState<string>('all');
  const [days, setDays] = useState(30);

  const fetchHeatmapData = useCallback(async () => {
    try {
      const params = new URLSearchParams({
        form_id: formId,
        interaction_type: heatmapType,
        days: days.toString(),
      });
      if (deviceFilter !== 'all') {
        params.append('device_type', deviceFilter);
      }
      const response = await fetch(`/api/v1/features/analytics/heatmaps/?${params}`);
      const data = await response.json();
      setHeatmapData(data);
    } catch (error) {
      console.error('Failed to fetch heatmap data:', error);
    }
  }, [formId, heatmapType, deviceFilter, days]);

  const fetchRecordings = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/analytics/recordings/?form_id=${formId}`);
      const data = await response.json();
      setRecordings(data.results || data);
    } catch (error) {
      console.error('Failed to fetch recordings:', error);
    }
  }, [formId]);

  const fetchDropOffData = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/analytics/drop-off/by_form/?form_id=${formId}&days=${days}`);
      const data = await response.json();
      setDropOffData(data.fields || data);
    } catch (error) {
      console.error('Failed to fetch drop-off data:', error);
    }
  }, [formId, days]);

  const fetchABResults = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/analytics/ab-results/?form_id=${formId}`);
      const data = await response.json();
      setAbResults(data.results || data);
    } catch (error) {
      console.error('Failed to fetch A/B results:', error);
    }
  }, [formId]);

  const fetchInsights = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/analytics/insights/?form_id=${formId}`);
      const data = await response.json();
      setInsights(data.results || data);
    } catch (error) {
      console.error('Failed to fetch insights:', error);
    }
  }, [formId]);

  useEffect(() => {
    const loadAll = async () => {
      setLoading(true);
      await Promise.all([
        fetchHeatmapData(),
        fetchRecordings(),
        fetchDropOffData(),
        fetchABResults(),
        fetchInsights(),
      ]);
      setLoading(false);
    };
    loadAll();
  }, [fetchHeatmapData, fetchRecordings, fetchDropOffData, fetchABResults, fetchInsights]);

  const generateInsights = async () => {
    try {
      const response = await fetch(`/api/v1/features/analytics/insights/generate/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ form_id: formId }),
      });
      const data = await response.json();
      setInsights(data);
    } catch (error) {
      console.error('Failed to generate insights:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Advanced Analytics</h2>
          <p className="text-muted-foreground">Deep insights into user behavior and form performance</p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={days.toString()} onValueChange={(v) => setDays(Number(v))}>
            <SelectTrigger className="w-[140px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      <Tabs defaultValue="heatmaps">
        <TabsList>
          <TabsTrigger value="heatmaps" className="flex items-center gap-2">
            <MousePointerClick className="h-4 w-4" />
            Heatmaps
          </TabsTrigger>
          <TabsTrigger value="recordings" className="flex items-center gap-2">
            <Video className="h-4 w-4" />
            Session Recordings
          </TabsTrigger>
          <TabsTrigger value="dropoff" className="flex items-center gap-2">
            <TrendingDown className="h-4 w-4" />
            Drop-off Analysis
          </TabsTrigger>
          <TabsTrigger value="abtests" className="flex items-center gap-2">
            <FlaskConical className="h-4 w-4" />
            A/B Tests
          </TabsTrigger>
          <TabsTrigger value="insights" className="flex items-center gap-2">
            <Lightbulb className="h-4 w-4" />
            Insights
          </TabsTrigger>
        </TabsList>

        {/* Heatmaps Tab */}
        <TabsContent value="heatmaps" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Interaction Heatmap</CardTitle>
                  <CardDescription>Visual representation of user interactions</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Select value={heatmapType} onValueChange={setHeatmapType}>
                    <SelectTrigger className="w-[120px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="click">Clicks</SelectItem>
                      <SelectItem value="hover">Hovers</SelectItem>
                      <SelectItem value="scroll">Scrolls</SelectItem>
                      <SelectItem value="focus">Focus</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={deviceFilter} onValueChange={setDeviceFilter}>
                    <SelectTrigger className="w-[120px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Devices</SelectItem>
                      <SelectItem value="desktop">Desktop</SelectItem>
                      <SelectItem value="mobile">Mobile</SelectItem>
                      <SelectItem value="tablet">Tablet</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* Heatmap Visualization */}
              <div className="relative w-full h-[400px] bg-gray-100 dark:bg-gray-900 rounded-lg overflow-hidden">
                <div className="absolute inset-0 p-4">
                  {/* Form Preview Placeholder */}
                  <div className="w-full max-w-md mx-auto space-y-4 bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                    <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded" />
                    <div className="h-10 bg-gray-100 dark:bg-gray-600 rounded" />
                    <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded" />
                    <div className="h-10 bg-gray-100 dark:bg-gray-600 rounded" />
                    <div className="h-10 bg-gray-100 dark:bg-gray-600 rounded" />
                    <div className="h-12 bg-blue-500 rounded" />
                  </div>
                  
                  {/* Heatmap Points */}
                  {heatmapData.map((point, index) => (
                    <div
                      key={index}
                      className="absolute rounded-full transform -translate-x-1/2 -translate-y-1/2"
                      style={{
                        left: `${point.x_position}%`,
                        top: `${point.y_position}%`,
                        width: `${Math.min(point.count * 2, 40)}px`,
                        height: `${Math.min(point.count * 2, 40)}px`,
                        backgroundColor: `rgba(255, 0, 0, ${Math.min(point.count / 100, 0.7)})`,
                      }}
                      title={`${point.count} interactions`}
                    />
                  ))}
                </div>
              </div>
              
              {/* Heatmap Legend */}
              <div className="flex items-center justify-center gap-4 mt-4">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-red-200" />
                  <span className="text-sm text-muted-foreground">Low</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-red-400" />
                  <span className="text-sm text-muted-foreground">Medium</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-red-600" />
                  <span className="text-sm text-muted-foreground">High</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Session Recordings Tab */}
        <TabsContent value="recordings" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="md:col-span-1">
              <Card className="h-full">
                <CardHeader>
                  <CardTitle className="text-lg">Recordings</CardTitle>
                  <CardDescription>{recordings.length} sessions captured</CardDescription>
                </CardHeader>
                <CardContent className="space-y-2 max-h-[400px] overflow-y-auto">
                  {recordings.map((recording) => (
                    <div
                      key={recording.id}
                      className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                        selectedRecording?.id === recording.id
                          ? 'border-primary bg-primary/5'
                          : 'hover:bg-muted'
                      }`}
                      onClick={() => setSelectedRecording(recording)}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">
                          {recording.session_id.slice(0, 8)}...
                        </span>
                        <Badge variant={recording.completed_form ? 'default' : 'secondary'}>
                          {recording.completed_form ? 'Completed' : 'Abandoned'}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                        <span>{recording.device_type}</span>
                        <span>•</span>
                        <span>{Math.round(recording.duration_seconds / 60)}m</span>
                        {recording.rage_clicks_count > 0 && (
                          <>
                            <span>•</span>
                            <span className="text-red-500">
                              {recording.rage_clicks_count} rage clicks
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                  {recordings.length === 0 && (
                    <p className="text-center text-muted-foreground py-4">
                      No recordings available yet
                    </p>
                  )}
                </CardContent>
              </Card>
            </div>
            
            <div className="md:col-span-2">
              <Card className="h-full">
                <CardHeader>
                  <CardTitle className="text-lg">Session Playback</CardTitle>
                </CardHeader>
                <CardContent>
                  {selectedRecording ? (
                    <div className="space-y-4">
                      {/* Video Player Placeholder */}
                      <div className="aspect-video bg-gray-900 rounded-lg flex items-center justify-center">
                        <div className="text-center text-white">
                          <Video className="h-12 w-12 mx-auto mb-2 opacity-50" />
                          <p className="text-sm opacity-75">Session recording playback</p>
                        </div>
                      </div>
                      
                      {/* Playback Controls */}
                      <div className="flex items-center justify-center gap-4">
                        <Button variant="outline" size="icon">
                          <SkipForward className="h-4 w-4 rotate-180" />
                        </Button>
                        <Button size="icon">
                          <Play className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="icon">
                          <SkipForward className="h-4 w-4" />
                        </Button>
                      </div>
                      
                      {/* Session Details */}
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">Duration:</span>
                          <span className="ml-2">{Math.round(selectedRecording.duration_seconds)}s</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Device:</span>
                          <span className="ml-2">{selectedRecording.device_type}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Browser:</span>
                          <span className="ml-2">{selectedRecording.browser}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Status:</span>
                          <span className="ml-2">
                            {selectedRecording.completed_form ? 'Completed' : `Dropped at ${selectedRecording.drop_off_field}`}
                          </span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                      Select a recording to view playback
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Drop-off Analysis Tab */}
        <TabsContent value="dropoff" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Field-Level Drop-off Analysis</CardTitle>
              <CardDescription>Identify where users abandon your form</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dropOffData.map((field, index) => (
                  <div key={field.field_id} className="flex items-center gap-4">
                    <span className="w-8 text-center text-muted-foreground">{index + 1}</span>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium">{field.field_label}</span>
                        <span className="text-sm text-muted-foreground">
                          {field.drop_off_count} drop-offs ({(field.drop_off_rate * 100).toFixed(1)}%)
                        </span>
                      </div>
                      <Progress
                        value={field.drop_off_rate * 100}
                        className={`h-2 ${
                          field.drop_off_rate > 0.2 ? 'bg-red-100' :
                          field.drop_off_rate > 0.1 ? 'bg-yellow-100' : 'bg-green-100'
                        }`}
                      />
                      <p className="text-xs text-muted-foreground mt-1">
                        Avg. time before drop: {field.avg_time_before_drop.toFixed(1)}s
                      </p>
                    </div>
                    {field.drop_off_rate > 0.15 && (
                      <Badge variant="destructive">High risk</Badge>
                    )}
                  </div>
                ))}
                {dropOffData.length === 0 && (
                  <p className="text-center text-muted-foreground py-8">
                    No drop-off data available yet
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* A/B Tests Tab */}
        <TabsContent value="abtests" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>A/B Test Results</CardTitle>
                  <CardDescription>Statistical analysis of form variants</CardDescription>
                </div>
                <Button size="sm">
                  <FlaskConical className="h-4 w-4 mr-2" />
                  New Test
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {abResults.map((result) => (
                  <div key={result.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{result.variant_name}</span>
                        {result.is_winner && (
                          <Badge className="bg-green-500">Winner</Badge>
                        )}
                      </div>
                      <Badge variant={result.confidence_level >= 95 ? 'default' : 'secondary'}>
                        {result.confidence_level.toFixed(1)}% confidence
                      </Badge>
                    </div>
                    <div className="grid grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Visitors</p>
                        <p className="font-medium">{result.visitors.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Conversions</p>
                        <p className="font-medium">{result.conversions.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Conversion Rate</p>
                        <p className="font-medium">{(result.conversion_rate * 100).toFixed(2)}%</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Improvement</p>
                        <p className={`font-medium ${result.improvement > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {result.improvement > 0 ? '+' : ''}{result.improvement.toFixed(1)}%
                        </p>
                      </div>
                    </div>
                    {result.confidence_level >= 95 && (
                      <div className="mt-3 flex items-center gap-2 text-sm text-green-600">
                        <CheckCircle className="h-4 w-4" />
                        Statistically significant result
                      </div>
                    )}
                  </div>
                ))}
                {abResults.length === 0 && (
                  <div className="text-center py-8">
                    <FlaskConical className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
                    <p className="text-muted-foreground">No A/B tests running</p>
                    <Button className="mt-4" variant="outline">Create your first test</Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Insights Tab */}
        <TabsContent value="insights" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Behavior Insights</CardTitle>
                  <CardDescription>AI-generated recommendations based on user behavior</CardDescription>
                </div>
                <Button onClick={generateInsights}>
                  <Lightbulb className="h-4 w-4 mr-2" />
                  Generate Insights
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {insights.map((insight) => (
                  <div key={insight.id} className="border rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <div className={`p-2 rounded-full ${
                        insight.severity === 'high' ? 'bg-red-100 text-red-600' :
                        insight.severity === 'medium' ? 'bg-yellow-100 text-yellow-600' :
                        'bg-blue-100 text-blue-600'
                      }`}>
                        {insight.severity === 'high' ? (
                          <AlertCircle className="h-5 w-5" />
                        ) : (
                          <Lightbulb className="h-5 w-5" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium">{insight.title}</h4>
                          <Badge variant={
                            insight.severity === 'high' ? 'destructive' :
                            insight.severity === 'medium' ? 'secondary' : 'outline'
                          }>
                            {insight.severity}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                          {insight.description}
                        </p>
                        <div className="mt-3 p-3 bg-muted rounded-lg">
                          <p className="text-sm font-medium">Recommendation</p>
                          <p className="text-sm text-muted-foreground">{insight.recommendation}</p>
                          <p className="text-xs text-green-600 mt-1">
                            Potential impact: {insight.potential_impact}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {insights.length === 0 && (
                  <div className="text-center py-8">
                    <Lightbulb className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
                    <p className="text-muted-foreground">No insights generated yet</p>
                    <Button className="mt-4" onClick={generateInsights}>
                      Generate Insights
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

export default AdvancedAnalyticsDashboard;
