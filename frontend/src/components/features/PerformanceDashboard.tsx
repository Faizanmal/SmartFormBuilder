'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
} from 'recharts';
import {
  Zap,
  Clock,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Settings,
  Activity,
  HardDrive,
  Image,
  Loader2,
} from 'lucide-react';

interface PerformanceMetric {
  metric_type: string;
  avg_value: number;
  min_value: number;
  max_value: number;
  count: number;
}

interface FieldMetric {
  field_id: string;
  field_label: string;
  avg_completion_time: number;
  drop_off_rate: number;
  error_count: number;
}

interface PerformanceAlert {
  id: string;
  alert_type: string;
  severity: 'warning' | 'critical';
  message: string;
  metric_value: number;
  threshold_value: number;
  acknowledged: boolean;
  created_at: string;
  form_id: string;
}

interface TimeSeriesData {
  date: string;
  load_time: number;
  fcp: number;
  lcp: number;
}

interface PerformanceDashboardProps {
  formId: string;
}

const METRIC_THRESHOLDS = {
  load_time: { good: 2000, warning: 4000 },
  fcp: { good: 1800, warning: 3000 },
  lcp: { good: 2500, warning: 4000 },
  fid: { good: 100, warning: 300 },
  cls: { good: 0.1, warning: 0.25 },
  tti: { good: 3800, warning: 7300 },
};

const getMetricStatus = (type: string, value: number) => {
  const thresholds = METRIC_THRESHOLDS[type as keyof typeof METRIC_THRESHOLDS];
  if (!thresholds) return 'unknown';
  if (value <= thresholds.good) return 'good';
  if (value <= thresholds.warning) return 'warning';
  return 'critical';
};

export function PerformanceDashboard({ formId }: PerformanceDashboardProps) {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [fieldMetrics, setFieldMetrics] = useState<FieldMetric[]>([]);
  const [alerts, setAlerts] = useState<PerformanceAlert[]>([]);
  const [timeSeries, setTimeSeries] = useState<TimeSeriesData[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [cacheConfig, setCacheConfig] = useState<{
    id: string;
    strategy: string;
    ttl: number;
    lazy_loading_enabled: boolean;
  } | null>(null);
  const [days, setDays] = useState(30);

  const fetchDashboard = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/performance/dashboard/${formId}/?days=${days}`);
      const data = await response.json();
      
      if (data.metrics) setMetrics(data.metrics);
      if (data.time_series) setTimeSeries(data.time_series);
      if (data.field_metrics) setFieldMetrics(data.field_metrics);
    } catch (error) {
      console.error('Failed to fetch performance dashboard:', error);
    }
  }, [formId, days]);

  const fetchAlerts = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/performance/alerts/unacknowledged/`);
      const data = await response.json();
      setAlerts(data.filter((a: PerformanceAlert) => a.form_id === formId));
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    }
  }, [formId]);

  const fetchCacheConfig = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/performance/cache-config/?form_id=${formId}`);
      const data = await response.json();
      if (data.length > 0) setCacheConfig(data[0]);
    } catch (error) {
      console.error('Failed to fetch cache config:', error);
    }
  }, [formId]);

  useEffect(() => {
    const loadAll = async () => {
      setLoading(true);
      await Promise.all([fetchDashboard(), fetchAlerts(), fetchCacheConfig()]);
      setLoading(false);
    };
    loadAll();
  }, [fetchDashboard, fetchAlerts, fetchCacheConfig]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await Promise.all([fetchDashboard(), fetchAlerts()]);
    setRefreshing(false);
  };

  const acknowledgeAlert = async (alertId: string) => {
    try {
      await fetch(`/api/v1/features/performance/alerts/${alertId}/acknowledge/`, {
        method: 'POST',
      });
      setAlerts(alerts.filter(a => a.id !== alertId));
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const invalidateCache = async () => {
    try {
      await fetch(`/api/v1/features/performance/cache-config/${cacheConfig?.id}/invalidate/`, {
        method: 'POST',
      });
      // Show success message
    } catch (error) {
      console.error('Failed to invalidate cache:', error);
    }
  };

  const warmCache = async () => {
    try {
      await fetch(`/api/v1/features/performance/cache-config/${cacheConfig?.id}/warm/`, {
        method: 'POST',
      });
      // Show success message
    } catch (error) {
      console.error('Failed to warm cache:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const avgLoadTime = metrics.find(m => m.metric_type === 'load_time')?.avg_value || 0;
  const avgFcp = metrics.find(m => m.metric_type === 'fcp')?.avg_value || 0;
  const avgLcp = metrics.find(m => m.metric_type === 'lcp')?.avg_value || 0;
  const avgFid = metrics.find(m => m.metric_type === 'fid')?.avg_value || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Performance Dashboard</h2>
          <p className="text-muted-foreground">Real-time performance metrics and optimization</p>
        </div>
        <div className="flex items-center gap-2">
          <select
            className="rounded-md border px-3 py-2"
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          <Button variant="outline" size="sm" onClick={handleRefresh} disabled={refreshing}>
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <Card className="border-yellow-500 bg-yellow-50 dark:bg-yellow-950/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-yellow-600" />
              Performance Alerts ({alerts.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {alerts.slice(0, 3).map((alert) => (
              <div key={alert.id} className="flex items-center justify-between rounded-lg bg-white dark:bg-gray-900 p-3">
                <div className="flex items-center gap-3">
                  <Badge variant={alert.severity === 'critical' ? 'destructive' : 'warning'}>
                    {alert.severity}
                  </Badge>
                  <span className="text-sm">{alert.message}</span>
                </div>
                <Button size="sm" variant="ghost" onClick={() => acknowledgeAlert(alert.id)}>
                  Dismiss
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Core Web Vitals */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Load Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold">{avgLoadTime.toFixed(0)}</span>
              <span className="text-sm text-muted-foreground">ms</span>
            </div>
            <Badge className="mt-2" variant={
              getMetricStatus('load_time', avgLoadTime) === 'good' ? 'default' :
              getMetricStatus('load_time', avgLoadTime) === 'warning' ? 'secondary' : 'destructive'
            }>
              {getMetricStatus('load_time', avgLoadTime).toUpperCase()}
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Activity className="h-4 w-4" />
              First Contentful Paint
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold">{avgFcp.toFixed(0)}</span>
              <span className="text-sm text-muted-foreground">ms</span>
            </div>
            <Badge className="mt-2" variant={
              getMetricStatus('fcp', avgFcp) === 'good' ? 'default' :
              getMetricStatus('fcp', avgFcp) === 'warning' ? 'secondary' : 'destructive'
            }>
              {getMetricStatus('fcp', avgFcp).toUpperCase()}
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Largest Contentful Paint
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold">{avgLcp.toFixed(0)}</span>
              <span className="text-sm text-muted-foreground">ms</span>
            </div>
            <Badge className="mt-2" variant={
              getMetricStatus('lcp', avgLcp) === 'good' ? 'default' :
              getMetricStatus('lcp', avgLcp) === 'warning' ? 'secondary' : 'destructive'
            }>
              {getMetricStatus('lcp', avgLcp).toUpperCase()}
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              First Input Delay
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold">{avgFid.toFixed(0)}</span>
              <span className="text-sm text-muted-foreground">ms</span>
            </div>
            <Badge className="mt-2" variant={
              getMetricStatus('fid', avgFid) === 'good' ? 'default' :
              getMetricStatus('fid', avgFid) === 'warning' ? 'secondary' : 'destructive'
            }>
              {getMetricStatus('fid', avgFid).toUpperCase()}
            </Badge>
          </CardContent>
        </Card>
      </div>

      {/* Tabs for detailed views */}
      <Tabs defaultValue="trends">
        <TabsList>
          <TabsTrigger value="trends">Performance Trends</TabsTrigger>
          <TabsTrigger value="fields">Field Metrics</TabsTrigger>
          <TabsTrigger value="caching">Caching</TabsTrigger>
          <TabsTrigger value="optimization">Optimization</TabsTrigger>
        </TabsList>

        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Load Time Trends</CardTitle>
              <CardDescription>Performance metrics over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={timeSeries}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area
                      type="monotone"
                      dataKey="load_time"
                      stroke="#8884d8"
                      fill="#8884d8"
                      fillOpacity={0.3}
                      name="Load Time (ms)"
                    />
                    <Area
                      type="monotone"
                      dataKey="lcp"
                      stroke="#82ca9d"
                      fill="#82ca9d"
                      fillOpacity={0.3}
                      name="LCP (ms)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="fields" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Field Completion Metrics</CardTitle>
              <CardDescription>How long users take to complete each field</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {fieldMetrics.map((field) => (
                  <div key={field.field_id} className="flex items-center justify-between border-b pb-4">
                    <div>
                      <p className="font-medium">{field.field_label}</p>
                      <p className="text-sm text-muted-foreground">
                        Avg: {field.avg_completion_time.toFixed(1)}s | 
                        Drop-off: {(field.drop_off_rate * 100).toFixed(1)}%
                      </p>
                    </div>
                    <div className="flex items-center gap-4">
                      {field.error_count > 0 && (
                        <Badge variant="destructive">{field.error_count} errors</Badge>
                      )}
                      {field.drop_off_rate > 0.1 && (
                        <Badge variant="warning">High drop-off</Badge>
                      )}
                    </div>
                  </div>
                ))}
                {fieldMetrics.length === 0 && (
                  <p className="text-muted-foreground text-center py-4">
                    No field metrics available yet. Data will appear after form submissions.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="caching" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <HardDrive className="h-5 w-5" />
                  Cache Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {cacheConfig ? (
                  <>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Strategy</span>
                      <Badge>{cacheConfig.strategy}</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">TTL</span>
                      <span>{cacheConfig.ttl} seconds</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Lazy Loading</span>
                      <Badge variant={cacheConfig.lazy_loading_enabled ? 'default' : 'secondary'}>
                        {cacheConfig.lazy_loading_enabled ? 'Enabled' : 'Disabled'}
                      </Badge>
                    </div>
                    <div className="flex gap-2 mt-4">
                      <Button size="sm" variant="outline" onClick={invalidateCache}>
                        Invalidate Cache
                      </Button>
                      <Button size="sm" variant="outline" onClick={warmCache}>
                        Warm Cache
                      </Button>
                    </div>
                  </>
                ) : (
                  <p className="text-muted-foreground">No cache configuration found</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Image className="h-5 w-5" />
                  Image Optimization
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Auto-optimize</span>
                  <Badge variant="default">Enabled</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Max Width</span>
                  <span>1920px</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Quality</span>
                  <span>85%</span>
                </div>
                <Button size="sm" className="w-full mt-4">
                  <Settings className="h-4 w-4 mr-2" />
                  Configure Optimization
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="optimization" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Lazy Loading Configuration</CardTitle>
              <CardDescription>
                Optimize load times for forms with many fields
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Enable Lazy Loading</p>
                  <p className="text-sm text-muted-foreground">
                    Load fields progressively as users scroll
                  </p>
                </div>
                <input type="checkbox" defaultChecked className="h-4 w-4" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Fields per Chunk</p>
                  <p className="text-sm text-muted-foreground">
                    Number of fields to load at once
                  </p>
                </div>
                <input
                  type="number"
                  defaultValue={10}
                  min={5}
                  max={50}
                  className="w-20 rounded-md border px-2 py-1"
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Preload Next Chunk</p>
                  <p className="text-sm text-muted-foreground">
                    Load the next section before users reach it
                  </p>
                </div>
                <input type="checkbox" defaultChecked className="h-4 w-4" />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default PerformanceDashboard;
