/**
 * Advanced Analytics Dashboard Component
 */
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, Users, Eye, MousePointer, CheckCircle, AlertTriangle, Globe, Smartphone } from 'lucide-react';

interface AnalyticsDashboardProps {
  formId: string;
}

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#fa709a'];

interface AnalyticsData {
  funnel: {
    views: number;
    starts: number;
    submits: number;
    view_to_start_rate: number;
    start_to_submit_rate: number;
    overall_conversion: number;
    drop_off_at_start: number;
    drop_off_after_start: number;
  };
  time_series: {
    submissions: Array<{ date: string; count: number }>;
  };
  heat_map: Array<{
    field_id: string;
    field_label: string;
    engagement_score: number;
    error_rate: number;
    intensity: number;
  }>;
  devices: Array<{
    device_type: string;
    percentage?: number;
  }>;
  geography: {
    top_countries: Array<{
      country: string;
      count: number;
    }>;
  };
  field_analytics: unknown[]; // Add this
}

export function AnalyticsDashboard({ formId }: AnalyticsDashboardProps) {
  const [dateRange, setDateRange] = useState('30');
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = useCallback(async () => {
    setLoading(true);
    try {
      const daysAgo = new Date();
      daysAgo.setDate(daysAgo.getDate() - parseInt(dateRange));
      
      const response = await fetch(
        `/api/forms/${formId}/analytics/dashboard/?date_from=${daysAgo.toISOString()}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAnalyticsData(data);
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  }, [formId, dateRange]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading analytics...</div>;
  }

  if (!analyticsData) {
    return <div className="text-center text-gray-500">No analytics data available</div>;
  }

  const { funnel, devices, geography, time_series, field_analytics, heat_map } = analyticsData;

  return (
    <div className="space-y-6">
      {/* Header with Date Range Selector */}
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold">Analytics Dashboard</h2>
        <Select value={dateRange} onValueChange={setDateRange}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7">Last 7 days</SelectItem>
            <SelectItem value="30">Last 30 days</SelectItem>
            <SelectItem value="90">Last 90 days</SelectItem>
            <SelectItem value="365">Last year</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Views"
          value={funnel.views}
          icon={<Eye className="h-5 w-5" />}
          trend={null}
        />
        <MetricCard
          title="Started"
          value={funnel.starts}
          icon={<MousePointer className="h-5 w-5" />}
          trend={`${funnel.view_to_start_rate}%`}
        />
        <MetricCard
          title="Submissions"
          value={funnel.submits}
          icon={<CheckCircle className="h-5 w-5" />}
          trend={`${funnel.overall_conversion}%`}
        />
        <MetricCard
          title="Conversion Rate"
          value={`${funnel.overall_conversion}%`}
          icon={<TrendingUp className="h-5 w-5" />}
          trend={null}
        />
      </div>

      {/* Main Analytics Tabs */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="funnel">Conversion Funnel</TabsTrigger>
          <TabsTrigger value="fields">Field Analytics</TabsTrigger>
          <TabsTrigger value="devices">Devices</TabsTrigger>
          <TabsTrigger value="geography">Geography</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Submissions Over Time</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={time_series.submissions}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="period" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="count" stroke="#667eea" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Views vs Submissions</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={[
                  { name: 'Views', value: funnel.views },
                  { name: 'Started', value: funnel.starts },
                  { name: 'Submitted', value: funnel.submits },
                ]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#667eea" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="funnel">
          <Card>
            <CardHeader>
              <CardTitle>Conversion Funnel</CardTitle>
              <CardDescription>See where users drop off in your form</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <FunnelStep
                  label="Form Views"
                  count={funnel.views}
                  percentage={100}
                  color="bg-blue-500"
                />
                <FunnelStep
                  label="Form Started"
                  count={funnel.starts}
                  percentage={funnel.view_to_start_rate}
                  color="bg-purple-500"
                  dropOff={funnel.drop_off_at_start}
                />
                <FunnelStep
                  label="Form Submitted"
                  count={funnel.submits}
                  percentage={funnel.start_to_submit_rate}
                  color="bg-green-500"
                  dropOff={funnel.drop_off_after_start}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="fields">
          <Card>
            <CardHeader>
              <CardTitle>Field Engagement Heat Map</CardTitle>
              <CardDescription>See which fields get the most attention and errors</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {heat_map.slice(0, 10).map((field: { field_id: string; field_label: string; engagement_score: number; error_rate: number; intensity: number; }) => (
                  <div key={field.field_id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium">{field.field_label}</p>
                      <div className="flex gap-4 mt-1 text-sm text-gray-600">
                        <span>Interactions: {field.engagement_score}</span>
                        <span className={field.error_rate > 20 ? 'text-red-500' : ''}>
                          Error Rate: {field.error_rate}%
                        </span>
                      </div>
                    </div>
                    <div
                      className="w-20 h-8 rounded"
                      style={{
                        backgroundColor: `rgba(102, 126, 234, ${field.intensity / 100})`,
                      }}
                    />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="devices">
          <Card>
            <CardHeader>
              <CardTitle>Device Breakdown</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={devices}
                    dataKey="count"
                    nameKey="device_type"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={(entry) => `${entry.device_type} (${entry.percentage}%)`}
                  >
                    {devices.map((entry: { device_type: string; percentage?: number }, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="geography">
          <Card>
            <CardHeader>
              <CardTitle>Top Countries</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {geography.top_countries.map((country: { country: string; count: number }) => (
                  <div key={country.country} className="flex items-center justify-between p-2">
                    <div className="flex items-center gap-2">
                      <Globe className="h-4 w-4 text-gray-500" />
                      <span>{country.country || 'Unknown'}</span>
                    </div>
                    <Badge variant="secondary">{country.count} views</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: string | number | null | undefined;
  icon: React.ReactNode;
  trend?: string | null;
}

function MetricCard({ title, value, icon, trend }: MetricCardProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">{title}</p>
            <p className="text-2xl font-bold mt-1">{value}</p>
            {trend && (
              <p className="text-sm text-green-600 mt-1 flex items-center gap-1">
                <TrendingUp className="h-3 w-3" />
                {trend}
              </p>
            )}
          </div>
          <div className="text-gray-400">{icon}</div>
        </div>
      </CardContent>
    </Card>
  );
}

interface FunnelStepProps {
  label: string;
  count: number;
  percentage: number;
  color: string;
  dropOff?: number;
}

function FunnelStep({ label, count, percentage, color, dropOff }: FunnelStepProps) {
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="font-medium">{label}</span>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">{count.toLocaleString()}</span>
          <Badge variant="secondary">{percentage.toFixed(1)}%</Badge>
        </div>
      </div>
      <div className="relative h-12 bg-gray-100 rounded-lg overflow-hidden">
        <div
          className={`h-full ${color} transition-all duration-500`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
      {dropOff !== undefined && dropOff > 0 && (
        <p className="text-sm text-red-500 mt-1 flex items-center gap-1">
          <AlertTriangle className="h-3 w-3" />
          {dropOff} users dropped off
        </p>
      )}
    </div>
  );
}
