"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { formsApi, submissionsApi } from "@/lib/api-client";
import type { Form, FormField, Submission, Analytics, AnalyticsFilters } from "@/types";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calender";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { BarChart3, Download, Eye, FileText, TrendingUp, Calendar as CalendarIcon, Filter, RefreshCw, X, ArrowUpRight, ArrowDownRight } from "lucide-react";
import { toast } from "sonner";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format, subDays, startOfDay, endOfDay } from 'date-fns';
import { cn } from "@/lib/utils";

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c43', '#665191', '#2f4b7c', '#a05195', '#d45087'];

const DATE_PRESETS = [
  { label: 'Last 7 days', days: 7 },
  { label: 'Last 14 days', days: 14 },
  { label: 'Last 30 days', days: 30 },
  { label: 'Last 90 days', days: 90 },
];

export default function FormAnalyticsPage() {
  const params = useParams();
  const router = useRouter();
  const formId = params.id as string;

  const [form, setForm] = useState<Form | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [filteredSubmissions, setFilteredSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Date filter state
  const [dateFrom, setDateFrom] = useState<Date | undefined>(subDays(new Date(), 30));
  const [dateTo, setDateTo] = useState<Date | undefined>(new Date());
  const [showDateFilter, setShowDateFilter] = useState(false);
  
  // Submission detail modal
  const [selectedSubmission, setSelectedSubmission] = useState<Submission | null>(null);

  const loadData = useCallback(async () => {
    try {
      const filters: AnalyticsFilters = {};
      if (dateFrom) filters.date_from = format(dateFrom, 'yyyy-MM-dd');
      if (dateTo) filters.date_to = format(dateTo, 'yyyy-MM-dd');
      
      const [formData, analyticsData, submissionsData] = await Promise.all([
        formsApi.get(formId),
        formsApi.getAnalytics(formId, filters),
        submissionsApi.list(formId),
      ]);
      setForm(formData);
      setAnalytics(analyticsData);
      setSubmissions(submissionsData);
    } catch {
      toast.error("Failed to load analytics");
    } finally {
      setLoading(false);
    }
  }, [dateFrom, dateTo, formId]);

  const filterSubmissions = useCallback(() => {
    let filtered = submissions;
    
    if (dateFrom) {
      filtered = filtered.filter(s => new Date(s.created_at) >= startOfDay(dateFrom));
    }
    if (dateTo) {
      filtered = filtered.filter(s => new Date(s.created_at) <= endOfDay(dateTo));
    }
    
    setFilteredSubmissions(filtered);
  }, [submissions, dateFrom, dateTo]);

  useEffect(() => {
    loadData();
  }, [formId, loadData]);

  useEffect(() => {
    filterSubmissions();
  }, [submissions, dateFrom, dateTo, filterSubmissions]);

  const applyDatePreset = (days: number) => {
    setDateFrom(subDays(new Date(), days));
    setDateTo(new Date());
  };

  const clearFilters = () => {
    setDateFrom(subDays(new Date(), 30));
    setDateTo(new Date());
  };

  // Calculate comparison with previous period
  const getComparisonData = () => {
    if (!dateFrom || !dateTo) return null;
    
    const currentPeriodDays = Math.ceil((dateTo.getTime() - dateFrom.getTime()) / (1000 * 60 * 60 * 24));
    const previousPeriodStart = subDays(dateFrom, currentPeriodDays);
    const previousPeriodEnd = subDays(dateFrom, 1);
    
    const currentPeriodSubmissions = filteredSubmissions.length;
    const previousPeriodSubmissions = submissions.filter(s => {
      const date = new Date(s.created_at);
      return date >= previousPeriodStart && date <= previousPeriodEnd;
    }).length;
    
    const change = previousPeriodSubmissions > 0 
      ? ((currentPeriodSubmissions - previousPeriodSubmissions) / previousPeriodSubmissions * 100).toFixed(1)
      : currentPeriodSubmissions > 0 ? '100' : '0';
    
    return {
      current: currentPeriodSubmissions,
      previous: previousPeriodSubmissions,
      change: parseFloat(change),
      isPositive: parseFloat(change) >= 0
    };
  };

  // Prepare chart data - submissions by day
  const getSubmissionsByDay = () => {
    if (!dateFrom || !dateTo) return [];
    
    const days = Math.ceil((dateTo.getTime() - dateFrom.getTime()) / (1000 * 60 * 60 * 24)) + 1;
    const dates = Array.from({ length: Math.min(days, 90) }, (_, i) => {
      const date = new Date(dateFrom);
      date.setDate(date.getDate() + i);
      return date.toISOString().split('T')[0];
    });

    const submissionCounts = dates.map(date => {
      const count = filteredSubmissions.filter(s => 
        s.created_at.split('T')[0] === date
      ).length;
      
      return {
        date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        submissions: count
      };
    });

    return submissionCounts;
  };

  // Field completion analysis
  const getFieldCompletion = () => {
    if (!form || filteredSubmissions.length === 0) return [];

    return form.schema_json.fields.map((field: FormField) => {
      const completedCount = filteredSubmissions.filter(s => 
        s.payload_json[field.id] !== undefined && s.payload_json[field.id] !== ''
      ).length;
      
      const completionRate = ((completedCount / filteredSubmissions.length) * 100).toFixed(1);

      return {
        field: field.label.length > 20 ? field.label.substring(0, 20) + '...' : field.label,
        fullLabel: field.label,
        rate: parseFloat(completionRate),
        count: completedCount,
        total: filteredSubmissions.length
      };
    }).slice(0, 10);
  };

  // Field value distribution for select/radio fields
  const getFieldDistribution = (fieldId: string) => {
    const field = form?.schema_json.fields.find(f => f.id === fieldId);
    if (!field || !field.options) return [];

    const distribution = field.options.map(option => {
      const count = filteredSubmissions.filter(s => {
        const value = s.payload_json[fieldId];
        return Array.isArray(value) ? value.includes(option) : value === option;
      }).length;
      
      return {
        name: option,
        value: count,
        percentage: filteredSubmissions.length > 0 ? ((count / filteredSubmissions.length) * 100).toFixed(1) : '0'
      };
    });

    return distribution;
  };

  const exportToCSV = () => {
    if (!form || filteredSubmissions.length === 0) return;
    // Get all unique field IDs
    const fieldIds = form.schema_json.fields.map((f: FormField) => f.id);
    const fieldLabels = form.schema_json.fields.reduce((acc: Record<string, string>, f: FormField) => {
      acc[f.id] = f.label;
      return acc;
    }, {} as Record<string, string>);

    // Create CSV header
    const headers = ['Submission ID', 'Created At', ...fieldIds.map((id: string) => fieldLabels[id])];
    
    // Create CSV rows
    const rows = filteredSubmissions.map((sub: Submission) => [
      sub.id,
      new Date(sub.created_at).toLocaleString(),
      ...fieldIds.map(id => {
        const value = sub.payload_json[id];
        if (Array.isArray(value)) return value.join('; ');
        return value || '';
      })
    ]);

    // Combine into CSV string
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    ].join('\n');

    // Download
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${form.slug}-submissions-${format(new Date(), 'yyyy-MM-dd')}.csv`;
    link.click();
    URL.revokeObjectURL(url);

    toast.success(`Exported ${filteredSubmissions.length} submissions!`);
  };

  const comparisonData = getComparisonData();
  const selectFields = form?.schema_json.fields.filter(f => 
    f.type === 'select' || f.type === 'radio' || f.type === 'multiselect'
  ) || [];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Button variant="ghost" onClick={() => router.push("/dashboard")}>
          ← Back to Dashboard
        </Button>
        <h1 className="text-3xl font-bold mt-2">{form?.title}</h1>
        <p className="text-muted-foreground">Analytics & Submissions</p>
      </div>

      {/* Date Filter */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">Date Range:</span>
            </div>
            
            {/* Quick presets */}
            <div className="flex flex-wrap gap-2">
              {DATE_PRESETS.map((preset) => (
                <Button
                  key={preset.days}
                  variant="outline"
                  size="sm"
                  onClick={() => applyDatePreset(preset.days)}
                  className={cn(
                    dateFrom && dateTo && 
                    Math.ceil((dateTo.getTime() - dateFrom.getTime()) / (1000 * 60 * 60 * 24)) === preset.days
                      ? "bg-primary text-primary-foreground"
                      : ""
                  )}
                >
                  {preset.label}
                </Button>
              ))}
            </div>
            
            {/* Custom date range */}
            <div className="flex items-center gap-2">
              <Input
                type="date"
                value={dateFrom ? format(dateFrom, 'yyyy-MM-dd') : ''}
                onChange={(e) => setDateFrom(e.target.value ? new Date(e.target.value) : undefined)}
                className="w-36"
              />
              <span className="text-muted-foreground">to</span>
              <Input
                type="date"
                value={dateTo ? format(dateTo, 'yyyy-MM-dd') : ''}
                onChange={(e) => setDateTo(e.target.value ? new Date(e.target.value) : undefined)}
                className="w-36"
              />
            </div>
            
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              <RefreshCw className="h-4 w-4 mr-1" />
              Reset
            </Button>
            
            <div className="ml-auto text-sm text-muted-foreground">
              Showing {filteredSubmissions.length} of {submissions.length} submissions
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Views</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.views || 0}</div>
            <p className="text-xs text-muted-foreground">
              All time views
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Submissions (Period)</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{filteredSubmissions.length}</div>
            {comparisonData && (
              <p className={cn(
                "text-xs flex items-center gap-1",
                comparisonData.isPositive ? "text-green-600" : "text-red-600"
              )}>
                {comparisonData.isPositive ? (
                  <ArrowUpRight className="h-3 w-3" />
                ) : (
                  <ArrowDownRight className="h-3 w-3" />
                )}
                {Math.abs(comparisonData.change)}% vs previous period
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.conversion_rate || 0}%</div>
            <p className="text-xs text-muted-foreground">
              Submissions / Views
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recent (30d)</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics?.recent_submissions || 0}</div>
            <p className="text-xs text-muted-foreground">
              Last 30 days
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      {submissions.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Submissions Over Time */}
          <Card>
            <CardHeader>
              <CardTitle>Submissions Trend</CardTitle>
              <CardDescription>Last 30 days</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={getSubmissionsByDay()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="submissions" stroke="#8884d8" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Field Completion Rates */}
          <Card>
            <CardHeader>
              <CardTitle>Field Completion Rates</CardTitle>
              <CardDescription>Percentage of submissions with each field filled</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={getFieldCompletion()} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" domain={[0, 100]} />
                  <YAxis dataKey="field" type="category" width={120} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="rate" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Submissions Table */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Submissions</CardTitle>
              <CardDescription>
                All form responses ({submissions.length} total)
              </CardDescription>
            </div>
            <Button onClick={exportToCSV} disabled={submissions.length === 0}>
              <Download className="mr-2 h-4 w-4" />
              Export CSV
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {submissions.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="mx-auto h-12 w-12 text-muted-foreground opacity-50" />
              <p className="mt-4 text-muted-foreground">No submissions yet</p>
              <p className="text-sm text-muted-foreground mt-2">
                Submissions will appear here once people start filling out your form
              </p>
            </div>
          ) : (
            <div className="rounded-md border overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Submitted</TableHead>
                    <TableHead>IP Address</TableHead>
                    {form?.schema_json.fields.slice(0, 3).map((field: FormField) => (
                      <TableHead key={field.id}>{field.label}</TableHead>
                    ))}
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {submissions.map((submission) => (
                    <TableRow key={submission.id}>
                      <TableCell className="font-medium">
                        {new Date(submission.created_at).toLocaleDateString()}
                        <br />
                        <span className="text-xs text-muted-foreground">
                          {new Date(submission.created_at).toLocaleTimeString()}
                        </span>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {submission.ip_address || 'N/A'}
                      </TableCell>
                      {form?.schema_json.fields.slice(0, 3).map(field => {
                        const fieldValue = (submission.payload_json as Record<string, unknown>)[field.id];
                        return (
                          <TableCell key={field.id} className="max-w-xs truncate">
                            {Array.isArray(fieldValue)
                              ? fieldValue.join(', ')
                              : String(fieldValue || '-')}
                          </TableCell>
                        );
                      })}
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            // Show full submission in modal (to be implemented)
                            toast.info("Full submission view coming soon!");
                          }}
                        >
                          View Details
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
