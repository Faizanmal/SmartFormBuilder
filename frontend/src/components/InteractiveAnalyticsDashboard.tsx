/**
 * Interactive Analytics Dashboard with Drill-Down
 * Clickable charts and detailed analytics views
 */
'use client';

import React, { useState, useCallback, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Treemap,
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Users,
  Eye,
  MousePointer,
  CheckCircle,
  Clock,
  MapPin,
  Smartphone,
  Monitor,
  Tablet,
  Globe,
  Calendar,
  Download,
  Filter,
  RefreshCw,
  ArrowRight,
  ArrowLeft,
  ZoomIn,
  X,
  Info,
  AlertTriangle,
  BarChart3,
  Activity,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Types
interface TimeSeriesData {
  date: string;
  views: number;
  starts: number;
  submissions: number;
  conversionRate: number;
}

interface FieldAnalytics {
  fieldId: string;
  fieldLabel: string;
  type: string;
  interactions: number;
  averageTime: number;
  errorRate: number;
  dropOffRate: number;
  completionRate: number;
}

interface DeviceData {
  device: string;
  count: number;
  percentage: number;
}

interface GeographyData {
  country: string;
  code: string;
  count: number;
  percentage: number;
}

interface SubmissionDetail {
  id: string;
  timestamp: string;
  device: string;
  country: string;
  duration: number;
  fields: Record<string, unknown>;
}

interface DrillDownState {
  isOpen: boolean;
  type: 'time' | 'field' | 'device' | 'geography' | 'submission' | null;
  data: unknown;
  title: string;
}

interface InteractiveAnalyticsDashboardProps {
  formId: string;
  timeSeriesData: TimeSeriesData[];
  fieldAnalytics: FieldAnalytics[];
  deviceData: DeviceData[];
  geographyData: GeographyData[];
  submissions: SubmissionDetail[];
  summary: {
    totalViews: number;
    totalStarts: number;
    totalSubmissions: number;
    conversionRate: number;
    averageCompletionTime: number;
    bounceRate: number;
  };
}

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#fa709a', '#43e97b', '#f5576c', '#4481eb'];

// Custom tooltip component
const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number; color: string }>; label?: string }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 border rounded-lg shadow-lg">
        <p className="font-medium text-sm mb-2">{label}</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="capitalize">{entry.name}:</span>
            <span className="font-medium">{entry.value.toLocaleString()}</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export function InteractiveAnalyticsDashboard({
  formId,
  timeSeriesData,
  fieldAnalytics,
  deviceData,
  geographyData,
  submissions,
  summary,
}: InteractiveAnalyticsDashboardProps) {
  const [dateRange, setDateRange] = useState('30');
  const [drillDown, setDrillDown] = useState<DrillDownState>({
    isOpen: false,
    type: null,
    data: null,
    title: '',
  });
  const [selectedMetric, setSelectedMetric] = useState<'views' | 'starts' | 'submissions'>('submissions');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Calculate trend percentages
  const calculateTrend = useCallback((current: number, previous: number) => {
    if (previous === 0) return current > 0 ? 100 : 0;
    return Math.round(((current - previous) / previous) * 100);
  }, []);

  // Handle chart click for drill-down
  const handleChartClick = useCallback((type: DrillDownState['type'], data: unknown, title: string) => {
    setDrillDown({
      isOpen: true,
      type,
      data,
      title,
    });
  }, []);

  // Close drill-down
  const closeDrillDown = useCallback(() => {
    setDrillDown({
      isOpen: false,
      type: null,
      data: null,
      title: '',
    });
  }, []);

  // Refresh data
  const refreshData = useCallback(async () => {
    setIsRefreshing(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsRefreshing(false);
  }, []);

  // Export data
  const exportData = useCallback(() => {
    const csvData = timeSeriesData.map(row => 
      `${row.date},${row.views},${row.starts},${row.submissions},${row.conversionRate}`
    ).join('\n');
    
    const blob = new Blob(
      [`Date,Views,Starts,Submissions,Conversion Rate\n${csvData}`],
      { type: 'text/csv' }
    );
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytics-${formId}-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }, [timeSeriesData, formId]);

  // Field performance radar data
  const radarData = useMemo(() => 
    fieldAnalytics.slice(0, 8).map(field => ({
      field: field.fieldLabel.slice(0, 10),
      completion: field.completionRate,
      engagement: Math.min(100, field.interactions / 10),
      speed: Math.max(0, 100 - field.averageTime * 10),
    })),
  [fieldAnalytics]);

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <BarChart3 className="h-6 w-6" />
            Interactive Analytics
          </h2>
          <p className="text-muted-foreground">
            Click on any chart element for detailed insights
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Select value={dateRange} onValueChange={setDateRange}>
            <SelectTrigger className="w-40">
              <Calendar className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
              <SelectItem value="365">Last year</SelectItem>
            </SelectContent>
          </Select>
          
          <Button
            variant="outline"
            size="icon"
            onClick={refreshData}
            disabled={isRefreshing}
          >
            <RefreshCw className={cn('h-4 w-4', isRefreshing && 'animate-spin')} />
          </Button>
          
          <Button variant="outline" onClick={exportData}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <SummaryCard
          title="Total Views"
          value={summary.totalViews}
          icon={<Eye className="h-5 w-5" />}
          trend={12}
          onClick={() => handleChartClick('time', timeSeriesData, 'Views Over Time')}
        />
        <SummaryCard
          title="Form Starts"
          value={summary.totalStarts}
          icon={<MousePointer className="h-5 w-5" />}
          trend={8}
          onClick={() => handleChartClick('time', timeSeriesData, 'Form Starts Over Time')}
        />
        <SummaryCard
          title="Submissions"
          value={summary.totalSubmissions}
          icon={<CheckCircle className="h-5 w-5" />}
          trend={15}
          onClick={() => handleChartClick('submission', submissions, 'All Submissions')}
        />
        <SummaryCard
          title="Conversion"
          value={`${summary.conversionRate}%`}
          icon={<TrendingUp className="h-5 w-5" />}
          trend={5}
          onClick={() => handleChartClick('time', timeSeriesData, 'Conversion Rate Trend')}
        />
        <SummaryCard
          title="Avg Time"
          value={`${Math.round(summary.averageCompletionTime / 60)}m`}
          icon={<Clock className="h-5 w-5" />}
          trend={-10}
          onClick={() => handleChartClick('field', fieldAnalytics, 'Field Timing Analysis')}
        />
        <SummaryCard
          title="Bounce Rate"
          value={`${summary.bounceRate}%`}
          icon={<AlertTriangle className="h-5 w-5" />}
          trend={-3}
          trendReversed
          onClick={() => handleChartClick('field', fieldAnalytics, 'Drop-off Analysis')}
        />
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Time Series Chart */}
        <Card className="col-span-1 lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Performance Over Time</CardTitle>
              <CardDescription>Click on data points for details</CardDescription>
            </div>
            <div className="flex gap-1">
              {(['views', 'starts', 'submissions'] as const).map(metric => (
                <Button
                  key={metric}
                  variant={selectedMetric === metric ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedMetric(metric)}
                  className="capitalize"
                >
                  {metric}
                </Button>
              ))}
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart
                data={timeSeriesData}
                onClick={(e) => {
                  if (e?.activePayload?.[0]) {
                    handleChartClick('time', e.activePayload[0].payload, `Details for ${e.activeLabel}`);
                  }
                }}
              >
                <defs>
                  <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#667eea" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#667eea" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorSubmissions" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#43e97b" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#43e97b" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Area
                  type="monotone"
                  dataKey={selectedMetric}
                  stroke={selectedMetric === 'submissions' ? '#43e97b' : '#667eea'}
                  fillOpacity={1}
                  fill={selectedMetric === 'submissions' ? 'url(#colorSubmissions)' : 'url(#colorViews)'}
                  className="cursor-pointer"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Field Analytics */}
        <Card>
          <CardHeader>
            <CardTitle>Field Performance</CardTitle>
            <CardDescription>Click on bars for field details</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={fieldAnalytics.slice(0, 8)}
                layout="vertical"
                onClick={(e) => {
                  if (e?.activePayload?.[0]) {
                    handleChartClick('field', e.activePayload[0].payload, `Field: ${e.activePayload[0].payload.fieldLabel}`);
                  }
                }}
              >
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis type="number" domain={[0, 100]} />
                <YAxis 
                  type="category" 
                  dataKey="fieldLabel" 
                  tick={{ fontSize: 11 }}
                  width={100}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar
                  dataKey="completionRate"
                  fill="#667eea"
                  radius={[0, 4, 4, 0]}
                  className="cursor-pointer"
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Radar Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Field Engagement Radar</CardTitle>
            <CardDescription>Multi-dimensional field analysis</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="field" tick={{ fontSize: 10 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} />
                <Radar
                  name="Completion"
                  dataKey="completion"
                  stroke="#667eea"
                  fill="#667eea"
                  fillOpacity={0.3}
                />
                <Radar
                  name="Engagement"
                  dataKey="engagement"
                  stroke="#f093fb"
                  fill="#f093fb"
                  fillOpacity={0.3}
                />
                <Radar
                  name="Speed"
                  dataKey="speed"
                  stroke="#43e97b"
                  fill="#43e97b"
                  fillOpacity={0.3}
                />
                <Legend />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Device & Geography */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Device Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle>Device Breakdown</CardTitle>
            <CardDescription>Click segments for device details</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center">
              <ResponsiveContainer width="50%" height={200}>
                <PieChart>
                  <Pie
                    data={deviceData}
                    dataKey="count"
                    nameKey="device"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    onClick={(_, index) => handleChartClick('device', deviceData[index], `${deviceData[index].device} Users`)}
                    className="cursor-pointer"
                  >
                    {deviceData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              
              <div className="w-1/2 space-y-2">
                {deviceData.map((device, index) => (
                  <div
                    key={device.device}
                    className="flex items-center justify-between p-2 rounded hover:bg-muted cursor-pointer"
                    onClick={() => handleChartClick('device', device, `${device.device} Users`)}
                  >
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      />
                      {device.device === 'Desktop' && <Monitor className="h-4 w-4" />}
                      {device.device === 'Mobile' && <Smartphone className="h-4 w-4" />}
                      {device.device === 'Tablet' && <Tablet className="h-4 w-4" />}
                      <span className="text-sm">{device.device}</span>
                    </div>
                    <div className="text-sm">
                      <span className="font-medium">{device.percentage}%</span>
                      <span className="text-muted-foreground ml-2">({device.count})</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Geography */}
        <Card>
          <CardHeader>
            <CardTitle>Top Countries</CardTitle>
            <CardDescription>Click for country details</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {geographyData.slice(0, 6).map((country, index) => (
                <div
                  key={country.code}
                  className="flex items-center justify-between p-2 rounded hover:bg-muted cursor-pointer"
                  onClick={() => handleChartClick('geography', country, `${country.country} Traffic`)}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{getCountryFlag(country.code)}</span>
                    <span>{country.country}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-32 h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full"
                        style={{
                          width: `${country.percentage}%`,
                          backgroundColor: COLORS[index % COLORS.length],
                        }}
                      />
                    </div>
                    <span className="text-sm font-medium w-12 text-right">
                      {country.percentage}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Submissions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Submissions</CardTitle>
          <CardDescription>Click on rows for full submission details</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Time</TableHead>
                <TableHead>Device</TableHead>
                <TableHead>Country</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {submissions.slice(0, 5).map((submission) => (
                <TableRow
                  key={submission.id}
                  className="cursor-pointer hover:bg-muted"
                  onClick={() => handleChartClick('submission', submission, 'Submission Details')}
                >
                  <TableCell>
                    {new Date(submission.timestamp).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      {submission.device === 'Desktop' && <Monitor className="h-4 w-4" />}
                      {submission.device === 'Mobile' && <Smartphone className="h-4 w-4" />}
                      {submission.device === 'Tablet' && <Tablet className="h-4 w-4" />}
                      {submission.device}
                    </div>
                  </TableCell>
                  <TableCell>{submission.country}</TableCell>
                  <TableCell>{Math.round(submission.duration / 60)}m {submission.duration % 60}s</TableCell>
                  <TableCell>
                    <Button variant="ghost" size="sm">
                      <ZoomIn className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Drill-Down Dialog */}
      <Dialog open={drillDown.isOpen} onOpenChange={closeDrillDown}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              {drillDown.title}
            </DialogTitle>
            <DialogDescription>
              Detailed analytics breakdown
            </DialogDescription>
          </DialogHeader>
          
          <DrillDownContent type={drillDown.type} data={drillDown.data} />
        </DialogContent>
      </Dialog>
    </div>
  );
}

// Summary Card Component
interface SummaryCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend: number;
  trendReversed?: boolean;
  onClick?: () => void;
}

function SummaryCard({ title, value, icon, trend, trendReversed, onClick }: SummaryCardProps) {
  const isPositive = trendReversed ? trend < 0 : trend > 0;
  
  return (
    <Card
      className="cursor-pointer hover:shadow-md transition-shadow"
      onClick={onClick}
    >
      <CardContent className="pt-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-muted-foreground">{icon}</span>
          <Badge
            variant={isPositive ? 'default' : 'destructive'}
            className="text-xs"
          >
            {trend > 0 ? '+' : ''}{trend}%
          </Badge>
        </div>
        <div className="text-2xl font-bold">{value}</div>
        <div className="text-xs text-muted-foreground">{title}</div>
      </CardContent>
    </Card>
  );
}

// Drill-Down Content Component
interface DrillDownContentProps {
  type: DrillDownState['type'];
  data: unknown;
}

function DrillDownContent({ type, data }: DrillDownContentProps) {
  if (!data) return null;

  switch (type) {
    case 'time': {
      const timeData = data as TimeSeriesData;
      return (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-muted rounded-lg">
              <div className="text-sm text-muted-foreground">Date</div>
              <div className="text-lg font-medium">{timeData.date}</div>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <div className="text-sm text-muted-foreground">Conversion Rate</div>
              <div className="text-lg font-medium">{timeData.conversionRate}%</div>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 border rounded-lg text-center">
              <Eye className="h-6 w-6 mx-auto mb-2 text-blue-500" />
              <div className="text-xl font-bold">{timeData.views}</div>
              <div className="text-sm text-muted-foreground">Views</div>
            </div>
            <div className="p-4 border rounded-lg text-center">
              <MousePointer className="h-6 w-6 mx-auto mb-2 text-purple-500" />
              <div className="text-xl font-bold">{timeData.starts}</div>
              <div className="text-sm text-muted-foreground">Starts</div>
            </div>
            <div className="p-4 border rounded-lg text-center">
              <CheckCircle className="h-6 w-6 mx-auto mb-2 text-green-500" />
              <div className="text-xl font-bold">{timeData.submissions}</div>
              <div className="text-sm text-muted-foreground">Submissions</div>
            </div>
          </div>
        </div>
      );
    }

    case 'field': {
      const fieldData = data as FieldAnalytics;
      return (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Badge>{fieldData.type}</Badge>
            <span className="text-lg font-medium">{fieldData.fieldLabel}</span>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <MetricRow label="Interactions" value={fieldData.interactions} />
            <MetricRow label="Avg Time" value={`${fieldData.averageTime}s`} />
            <MetricRow label="Error Rate" value={`${fieldData.errorRate}%`} warning={fieldData.errorRate > 10} />
            <MetricRow label="Drop-off Rate" value={`${fieldData.dropOffRate}%`} warning={fieldData.dropOffRate > 20} />
            <MetricRow label="Completion Rate" value={`${fieldData.completionRate}%`} success={fieldData.completionRate > 90} />
          </div>
          <div className="pt-4 border-t">
            <h4 className="font-medium mb-2">Recommendations</h4>
            <ul className="space-y-1 text-sm text-muted-foreground">
              {fieldData.errorRate > 10 && (
                <li className="flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-yellow-500" />
                  High error rate - consider adding helper text
                </li>
              )}
              {fieldData.averageTime > 30 && (
                <li className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-blue-500" />
                  Users spend long time here - consider simplifying
                </li>
              )}
              {fieldData.dropOffRate > 20 && (
                <li className="flex items-center gap-2">
                  <TrendingDown className="h-4 w-4 text-red-500" />
                  High drop-off - consider making optional or removing
                </li>
              )}
            </ul>
          </div>
        </div>
      );
    }

    case 'submission': {
      const submission = data as SubmissionDetail;
      return (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="p-3 bg-muted rounded-lg">
              <div className="text-xs text-muted-foreground">Submitted</div>
              <div className="text-sm font-medium">
                {new Date(submission.timestamp).toLocaleString()}
              </div>
            </div>
            <div className="p-3 bg-muted rounded-lg">
              <div className="text-xs text-muted-foreground">Device</div>
              <div className="text-sm font-medium">{submission.device}</div>
            </div>
            <div className="p-3 bg-muted rounded-lg">
              <div className="text-xs text-muted-foreground">Duration</div>
              <div className="text-sm font-medium">
                {Math.round(submission.duration / 60)}m {submission.duration % 60}s
              </div>
            </div>
          </div>
          <div className="border-t pt-4">
            <h4 className="font-medium mb-2">Field Values</h4>
            <div className="space-y-2">
              {Object.entries(submission.fields).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between p-2 bg-muted rounded">
                  <span className="text-sm text-muted-foreground">{key}</span>
                  <span className="text-sm font-medium">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    }

    case 'device': {
      const deviceInfo = data as DeviceData;
      return (
        <div className="space-y-4">
          <div className="flex items-center gap-4 p-4 bg-muted rounded-lg">
            {deviceInfo.device === 'Desktop' && <Monitor className="h-12 w-12" />}
            {deviceInfo.device === 'Mobile' && <Smartphone className="h-12 w-12" />}
            {deviceInfo.device === 'Tablet' && <Tablet className="h-12 w-12" />}
            <div>
              <div className="text-2xl font-bold">{deviceInfo.device}</div>
              <div className="text-muted-foreground">{deviceInfo.percentage}% of traffic</div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <MetricRow label="Total Users" value={deviceInfo.count} />
            <MetricRow label="Share" value={`${deviceInfo.percentage}%`} />
          </div>
        </div>
      );
    }

    case 'geography': {
      const geoInfo = data as GeographyData;
      return (
        <div className="space-y-4">
          <div className="flex items-center gap-4 p-4 bg-muted rounded-lg">
            <span className="text-4xl">{getCountryFlag(geoInfo.code)}</span>
            <div>
              <div className="text-2xl font-bold">{geoInfo.country}</div>
              <div className="text-muted-foreground">{geoInfo.percentage}% of traffic</div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <MetricRow label="Total Views" value={geoInfo.count} />
            <MetricRow label="Share" value={`${geoInfo.percentage}%`} />
          </div>
        </div>
      );
    }

    default:
      return <div>No data available</div>;
  }
}

// Helper Components
function MetricRow({ 
  label, 
  value, 
  warning, 
  success 
}: { 
  label: string; 
  value: string | number; 
  warning?: boolean; 
  success?: boolean;
}) {
  return (
    <div className={cn(
      'p-3 rounded-lg border',
      warning && 'border-yellow-200 bg-yellow-50',
      success && 'border-green-200 bg-green-50'
    )}>
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className={cn(
        'text-lg font-medium',
        warning && 'text-yellow-700',
        success && 'text-green-700'
      )}>
        {value}
      </div>
    </div>
  );
}

// Country flag helper
function getCountryFlag(code: string): string {
  const codePoints = code
    .toUpperCase()
    .split('')
    .map(char => 127397 + char.charCodeAt(0));
  return String.fromCodePoint(...codePoints);
}

export default InteractiveAnalyticsDashboard;
