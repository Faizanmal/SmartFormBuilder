'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  BarChart3,
  LineChart,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  Calendar,
  Lightbulb,
  Target,
  Bell,
} from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface PredictionData {
  date: string;
  predicted_submissions: number;
  predicted_views: number;
  confidence: number;
}

interface AnomalyData {
  id: string;
  metric: string;
  expected: number;
  actual: number;
  deviation: number;
  severity: 'low' | 'medium' | 'high';
  timestamp: string;
}

interface TrendData {
  date: string;
  views: number;
  submissions: number;
  conversion_rate: number;
  abandonment_rate: number;
  avg_completion_time: number;
}

interface Insight {
  id: string;
  type: string;
  title: string;
  description: string;
  impact: string;
  action?: string;
}

interface PredictiveAnalyticsDashboardProps {
  formId: string;
}

export function PredictiveAnalyticsDashboard({ formId }: PredictiveAnalyticsDashboardProps) {
  const [predictions, setPredictions] = useState<PredictionData[]>([]);
  const [anomalies, setAnomalies] = useState<AnomalyData[]>([]);
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(true);
  const [forecastDays, setForecastDays] = useState('7');

  useEffect(() => {
    fetchAllData();
  }, [formId, forecastDays]);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchForecast(),
        fetchAnomalies(),
        fetchTrends(),
        fetchInsights(),
      ]);
    } finally {
      setLoading(false);
    }
  };

  const fetchForecast = async () => {
    try {
      const response = await fetch(
        `/api/v1/automation/forms/${formId}/analytics/forecast/?days=${forecastDays}`
      );
      const data = await response.json();
      setPredictions(data.predictions || []);
    } catch (error) {
      console.error('Failed to fetch forecast:', error);
    }
  };

  const fetchAnomalies = async () => {
    try {
      const response = await fetch(`/api/v1/automation/forms/${formId}/analytics/anomalies/`);
      const data = await response.json();
      setAnomalies(data.anomalies || []);
    } catch (error) {
      console.error('Failed to fetch anomalies:', error);
    }
  };

  const fetchTrends = async () => {
    try {
      const response = await fetch(`/api/v1/automation/forms/${formId}/analytics/trends/`);
      const data = await response.json();
      setTrends(data.data || []);
    } catch (error) {
      console.error('Failed to fetch trends:', error);
    }
  };

  const fetchInsights = async () => {
    try {
      const response = await fetch(`/api/v1/automation/forms/${formId}/analytics/insights/`);
      const data = await response.json();
      setInsights(data.insights || []);
    } catch (error) {
      console.error('Failed to fetch insights:', error);
    }
  };

  const calculateTrendChange = (data: TrendData[], metric: keyof TrendData) => {
    if (data.length < 2) return 0;
    const recent = data.slice(0, 7);
    const previous = data.slice(7, 14);
    
    const recentAvg = recent.reduce((sum, d) => sum + (d[metric] as number), 0) / recent.length;
    const previousAvg = previous.reduce((sum, d) => sum + (d[metric] as number), 0) / previous.length;
    
    if (previousAvg === 0) return 0;
    return ((recentAvg - previousAvg) / previousAvg) * 100;
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'destructive';
      case 'medium': return 'secondary';
      case 'low': return 'outline';
      default: return 'outline';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const totalPredictedSubmissions = predictions.reduce(
    (sum, p) => sum + p.predicted_submissions, 0
  );
  const avgConfidence = predictions.length > 0
    ? predictions.reduce((sum, p) => sum + p.confidence, 0) / predictions.length
    : 0;

  const submissionTrend = calculateTrendChange(trends, 'submissions');
  const conversionTrend = calculateTrendChange(trends, 'conversion_rate');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <BarChart3 className="h-6 w-6 text-primary" />
            Predictive Analytics
          </h2>
          <p className="text-muted-foreground">Forecasting and anomaly detection</p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={forecastDays} onValueChange={setForecastDays}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">7 Days</SelectItem>
              <SelectItem value="14">14 Days</SelectItem>
              <SelectItem value="30">30 Days</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={fetchAllData}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Predicted Submissions</p>
                <p className="text-2xl font-bold">{totalPredictedSubmissions}</p>
                <p className="text-xs text-muted-foreground">next {forecastDays} days</p>
              </div>
              <div className="p-3 bg-primary/10 rounded-full">
                <Target className="h-6 w-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Forecast Confidence</p>
                <p className="text-2xl font-bold">{avgConfidence.toFixed(0)}%</p>
                <p className="text-xs text-muted-foreground">average accuracy</p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <LineChart className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Submission Trend</p>
                <p className="text-2xl font-bold flex items-center gap-1">
                  {submissionTrend > 0 ? '+' : ''}{submissionTrend.toFixed(1)}%
                  {submissionTrend > 0 ? (
                    <ArrowUpRight className="h-5 w-5 text-green-500" />
                  ) : (
                    <ArrowDownRight className="h-5 w-5 text-red-500" />
                  )}
                </p>
                <p className="text-xs text-muted-foreground">vs previous week</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                {submissionTrend > 0 ? (
                  <TrendingUp className="h-6 w-6 text-blue-600" />
                ) : (
                  <TrendingDown className="h-6 w-6 text-blue-600" />
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active Anomalies</p>
                <p className="text-2xl font-bold">{anomalies.length}</p>
                <p className="text-xs text-muted-foreground">requiring attention</p>
              </div>
              <div className={`p-3 rounded-full ${anomalies.length > 0 ? 'bg-yellow-100' : 'bg-green-100'}`}>
                <AlertTriangle className={`h-6 w-6 ${anomalies.length > 0 ? 'text-yellow-600' : 'text-green-600'}`} />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Forecast Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Submission Forecast
            </CardTitle>
            <CardDescription>Predicted submissions for the next {forecastDays} days</CardDescription>
          </CardHeader>
          <CardContent>
            {predictions.length > 0 ? (
              <div className="space-y-3">
                {predictions.map((prediction, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <div>
                      <p className="font-medium">{new Date(prediction.date).toLocaleDateString()}</p>
                      <p className="text-sm text-muted-foreground">
                        {prediction.predicted_views} views expected
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xl font-bold">{prediction.predicted_submissions}</p>
                      <p className="text-xs text-muted-foreground">
                        {prediction.confidence}% confidence
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <LineChart className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Not enough data for predictions</p>
                <p className="text-sm">Need at least 7 days of data</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Anomalies */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Detected Anomalies
            </CardTitle>
            <CardDescription>Unusual patterns in your form data</CardDescription>
          </CardHeader>
          <CardContent>
            {anomalies.length > 0 ? (
              <div className="space-y-3">
                {anomalies.map((anomaly) => (
                  <div key={anomaly.id} className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <Badge variant={getSeverityColor(anomaly.severity)}>
                        {anomaly.severity}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(anomaly.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <p className="font-medium">{anomaly.metric}</p>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
                      <span>Expected: {anomaly.expected.toFixed(1)}</span>
                      <span>Actual: {anomaly.actual.toFixed(1)}</span>
                      <span className={anomaly.deviation > 0 ? 'text-red-500' : 'text-green-500'}>
                        {anomaly.deviation > 0 ? '+' : ''}{anomaly.deviation.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <AlertTriangle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No anomalies detected</p>
                <p className="text-sm">Your form is performing as expected</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* AI Insights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-yellow-500" />
            AI-Generated Insights
          </CardTitle>
          <CardDescription>Smart recommendations based on your data</CardDescription>
        </CardHeader>
        <CardContent>
          {insights.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {insights.map((insight) => (
                <div key={insight.id} className="p-4 border rounded-lg">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-yellow-100 rounded">
                      <Lightbulb className="h-4 w-4 text-yellow-600" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium">{insight.title}</h4>
                      <p className="text-sm text-muted-foreground mt-1">{insight.description}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <Badge variant="outline" className="text-xs">
                          Impact: {insight.impact}
                        </Badge>
                        {insight.action && (
                          <Button variant="link" size="sm" className="p-0 h-auto text-xs">
                            {insight.action}
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Lightbulb className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No insights available yet</p>
              <p className="text-sm">Insights will appear as more data is collected</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Trend Data Table */}
      {trends.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Historical Trends</CardTitle>
            <CardDescription>Daily performance metrics for the last 30 days</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">Date</th>
                    <th className="text-right p-2">Views</th>
                    <th className="text-right p-2">Submissions</th>
                    <th className="text-right p-2">Conversion</th>
                    <th className="text-right p-2">Abandonment</th>
                    <th className="text-right p-2">Avg. Time</th>
                  </tr>
                </thead>
                <tbody>
                  {trends.slice(0, 10).map((day, index) => (
                    <tr key={index} className="border-b">
                      <td className="p-2">{new Date(day.date).toLocaleDateString()}</td>
                      <td className="text-right p-2">{day.views}</td>
                      <td className="text-right p-2">{day.submissions}</td>
                      <td className="text-right p-2">{day.conversion_rate.toFixed(1)}%</td>
                      <td className="text-right p-2">{day.abandonment_rate.toFixed(1)}%</td>
                      <td className="text-right p-2">{day.avg_completion_time.toFixed(0)}s</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default PredictiveAnalyticsDashboard;
