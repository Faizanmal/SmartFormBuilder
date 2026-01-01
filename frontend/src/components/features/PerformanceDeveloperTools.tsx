'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { 
  useEdgeComputingConfig,
  useUpdateEdgeComputingConfig,
  useCDNConfig,
  usePerformanceMonitor,
  useAPIKeys,
  useCreateAPIKey,
  usePlugins,
  useDeveloperPortals
} from '@/hooks/use-emerging-features';
import { 
  Zap, Globe, Activity, Key, 
  Puzzle, Code, TrendingUp, AlertCircle,
  CheckCircle2, Clock, Download, Copy,
  Eye, EyeOff, Plus, Trash2
} from 'lucide-react';

interface PerformanceDeveloperToolsProps {
  formId: string;
}

export function PerformanceDeveloperTools({ formId }: PerformanceDeveloperToolsProps) {
  const { data: edgeConfig } = useEdgeComputingConfig(formId);
  const updateEdgeConfig = useUpdateEdgeComputingConfig();

  const { data: cdnConfig } = useCDNConfig(formId);
  const { data: performanceData } = usePerformanceMonitor(formId);
  const { data: apiKeys } = useAPIKeys();
  const createAPIKey = useCreateAPIKey();
  const { data: plugins } = usePlugins();
  const { data: developerPortal } = useDeveloperPortals();

  const [showApiKey, setShowApiKey] = React.useState<string | null>(null);

  return (
    <div className="space-y-6">
      <Tabs defaultValue="edge" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="edge">Edge Computing</TabsTrigger>
          <TabsTrigger value="cdn">CDN</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="api">API Keys</TabsTrigger>
          <TabsTrigger value="plugins">Plugins</TabsTrigger>
        </TabsList>

        {/* Edge Computing Tab */}
        <TabsContent value="edge" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-500" />
                Edge Computing
              </CardTitle>
              <CardDescription>
                Deploy form processing to edge locations for ultra-low latency
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="edge-enabled">Enable Edge Computing</Label>
                <Switch
                  id="edge-enabled"
                  checked={edgeConfig?.is_enabled}
                  onCheckedChange={(checked) => {
                    updateEdgeConfig.mutate({
                      formId,
                      config: { is_enabled: checked }
                    });
                  }}
                />
              </div>

              {edgeConfig?.is_enabled && (
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="edge-provider">Edge Provider</Label>
                    <Select
                      value={edgeConfig.provider}
                      onValueChange={(value) => {
                        updateEdgeConfig.mutate({
                          formId,
                          config: { provider: value }
                        });
                      }}
                    >
                      <SelectTrigger id="edge-provider">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="cloudflare">Cloudflare Workers</SelectItem>
                        <SelectItem value="vercel">Vercel Edge Functions</SelectItem>
                        <SelectItem value="aws_lambda_edge">AWS Lambda@Edge</SelectItem>
                        <SelectItem value="fastly">Fastly Compute@Edge</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Edge Locations */}
                  {edgeConfig.edge_locations && edgeConfig.edge_locations.length > 0 && (
                    <div className="space-y-2">
                      <Label>Active Edge Locations ({edgeConfig.edge_locations.length})</Label>
                      <div className="grid grid-cols-4 gap-2">
                        {edgeConfig.edge_locations.map((location: string) => (
                          <Badge key={location} variant="outline" className="justify-center">
                            <Globe className="h-3 w-3 mr-1" />
                            {location}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Functions */}
                  <div className="space-y-2">
                    <Label>Edge Functions</Label>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-2">
                          <Zap className="h-4 w-4 text-yellow-500" />
                          <span className="text-sm">Form validation</span>
                        </div>
                        <Switch checked={edgeConfig.functions?.includes('validation')} />
                      </div>
                      <div className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-2">
                          <Zap className="h-4 w-4 text-yellow-500" />
                          <span className="text-sm">Data transformation</span>
                        </div>
                        <Switch checked={edgeConfig.functions?.includes('transformation')} />
                      </div>
                      <div className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-2">
                          <Zap className="h-4 w-4 text-yellow-500" />
                          <span className="text-sm">Geo-routing</span>
                        </div>
                        <Switch checked={edgeConfig.functions?.includes('routing')} />
                      </div>
                    </div>
                  </div>

                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <TrendingUp className="h-4 w-4 text-blue-600" />
                      <span className="font-medium text-sm">Performance Impact</span>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Avg. latency reduction: ~40-60% • Edge cache hit rate: 85%
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* CDN Tab */}
        <TabsContent value="cdn" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5 text-blue-500" />
                Content Delivery Network
              </CardTitle>
              <CardDescription>
                Global CDN for static assets and media files
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {cdnConfig && (
                <>
                  <div className="flex items-center justify-between">
                    <Label>CDN Status</Label>
                    <Badge variant={cdnConfig.is_enabled ? 'default' : 'secondary'}>
                      {cdnConfig.is_enabled ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>

                  {cdnConfig.is_enabled && (
                    <>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div className="p-3 border rounded-lg">
                          <p className="text-muted-foreground mb-1">Provider</p>
                          <p className="font-medium capitalize">{cdnConfig.provider}</p>
                        </div>
                        <div className="p-3 border rounded-lg">
                          <p className="text-muted-foreground mb-1">Custom Domain</p>
                          <code className="text-xs bg-muted px-2 py-1 rounded">
                            {cdnConfig.custom_domain || 'Not configured'}
                          </code>
                        </div>
                      </div>

                      {/* Asset Types */}
                      <div className="space-y-2">
                        <Label>Cached Asset Types</Label>
                        <div className="flex flex-wrap gap-2">
                          {cdnConfig.asset_types_to_cache?.map((type: string) => (
                            <Badge key={type} variant="secondary">
                              {type}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      {/* Cache Settings */}
                      <div className="grid grid-cols-3 gap-4">
                        <div className="p-3 border rounded-lg text-center">
                          <p className="text-2xl font-bold text-blue-600">{cdnConfig.cache_ttl_seconds / 3600}h</p>
                          <p className="text-xs text-muted-foreground">Cache TTL</p>
                        </div>
                        <div className="p-3 border rounded-lg text-center">
                          <p className="text-2xl font-bold text-green-600">
                            {cdnConfig.compression_enabled ? 'Yes' : 'No'}
                          </p>
                          <p className="text-xs text-muted-foreground">Compression</p>
                        </div>
                        <div className="p-3 border rounded-lg text-center">
                          <p className="text-2xl font-bold text-purple-600">
                            {cdnConfig.image_optimization ? 'Yes' : 'No'}
                          </p>
                          <p className="text-xs text-muted-foreground">Image Opt</p>
                        </div>
                      </div>

                      {cdnConfig.purge_on_update && (
                        <div className="flex items-center gap-2 p-3 bg-muted rounded-lg">
                          <CheckCircle2 className="h-4 w-4 text-green-600" />
                          <span className="text-sm">Auto-purge cache on form updates</span>
                        </div>
                      )}
                    </>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-green-500" />
                Performance Monitor
              </CardTitle>
              <CardDescription>
                Real-time performance metrics and Core Web Vitals
              </CardDescription>
            </CardHeader>
            <CardContent>
              {performanceData && (
                <div className="space-y-6">
                  {/* Core Web Vitals */}
                  <div className="space-y-4">
                    <h4 className="font-medium text-sm">Core Web Vitals</h4>
                    
                    {/* LCP */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label className="text-sm">Largest Contentful Paint (LCP)</Label>
                        <Badge variant={performanceData.lcp < 2500 ? 'default' : 'destructive'}>
                          {performanceData.lcp}ms
                        </Badge>
                      </div>
                      <Progress 
                        value={(performanceData.lcp / 4000) * 100} 
                        className="h-2"
                      />
                      <p className="text-xs text-muted-foreground">Good: &lt; 2.5s, Poor: &gt; 4s</p>
                    </div>

                    {/* FID */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label className="text-sm">First Input Delay (FID)</Label>
                        <Badge variant={performanceData.fid < 100 ? 'default' : 'destructive'}>
                          {performanceData.fid}ms
                        </Badge>
                      </div>
                      <Progress 
                        value={(performanceData.fid / 300) * 100} 
                        className="h-2"
                      />
                      <p className="text-xs text-muted-foreground">Good: &lt; 100ms, Poor: &gt; 300ms</p>
                    </div>

                    {/* CLS */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label className="text-sm">Cumulative Layout Shift (CLS)</Label>
                        <Badge variant={performanceData.cls < 0.1 ? 'default' : 'destructive'}>
                          {performanceData.cls?.toFixed(3)}
                        </Badge>
                      </div>
                      <Progress 
                        value={(performanceData.cls / 0.25) * 100} 
                        className="h-2"
                      />
                      <p className="text-xs text-muted-foreground">Good: &lt; 0.1, Poor: &gt; 0.25</p>
                    </div>
                  </div>

                  {/* Additional Metrics */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="p-3 border rounded-lg text-center">
                      <p className="text-2xl font-bold">{performanceData.ttfb}ms</p>
                      <p className="text-xs text-muted-foreground">TTFB</p>
                    </div>
                    <div className="p-3 border rounded-lg text-center">
                      <p className="text-2xl font-bold">{performanceData.load_time}ms</p>
                      <p className="text-xs text-muted-foreground">Load Time</p>
                    </div>
                    <div className="p-3 border rounded-lg text-center">
                      <p className="text-2xl font-bold">{(performanceData.bundle_size / 1024).toFixed(0)}KB</p>
                      <p className="text-xs text-muted-foreground">Bundle Size</p>
                    </div>
                  </div>

                  {/* Bottlenecks */}
                  {performanceData.bottlenecks && performanceData.bottlenecks.length > 0 && (
                    <div className="space-y-2">
                      <Label className="text-sm">Detected Bottlenecks</Label>
                      {(performanceData.bottlenecks as { issue: string; recommendation?: string }[]).map((bottleneck, index: number) => (
                        <div key={index} className="flex items-start gap-2 p-3 border border-orange-200 bg-orange-50 rounded-lg">
                          <AlertCircle className="h-4 w-4 text-orange-600 mt-0.5" />
                          <div className="flex-1">
                            <p className="text-sm font-medium">{bottleneck.issue}</p>
                            <p className="text-xs text-muted-foreground">{bottleneck.recommendation}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Keys Tab */}
        <TabsContent value="api" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Key className="h-5 w-5 text-purple-500" />
                    API Keys
                  </CardTitle>
                  <CardDescription>
                    Manage API keys for programmatic access
                  </CardDescription>
                </div>
                <Button 
                  size="sm"
                  onClick={() => {
                    createAPIKey.mutate({
                      name: 'New API Key',
                      scopes: ['forms:read']
                    });
                  }}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Create Key
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {apiKeys?.map((key) => (
                  <div key={key.id} className="p-4 border rounded-lg space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium">{key.name}</h4>
                        <p className="text-xs text-muted-foreground">
                          Created {new Date(key.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={key.is_active ? 'default' : 'secondary'}>
                          {key.is_active ? 'Active' : 'Revoked'}
                        </Badge>
                        <Button variant="ghost" size="icon">
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <code className="flex-1 text-xs bg-muted px-3 py-2 rounded font-mono">
                        {showApiKey === key.id ? key.key : '••••••••••••••••••••••••••••••••'}
                      </code>
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => setShowApiKey(showApiKey === key.id ? null : key.id)}
                      >
                        {showApiKey === key.id ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                      <Button variant="outline" size="icon">
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>

                    <div className="flex flex-wrap gap-1">
                      {key.scopes.map((scope: string) => (
                        <Badge key={scope} variant="outline" className="text-xs">
                          {scope}
                        </Badge>
                      ))}
                    </div>

                    {key.last_used_at && (
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        Last used {new Date(key.last_used_at).toLocaleString()}
                      </div>
                    )}

                    {key.rate_limit && (
                      <div className="text-xs">
                        <p className="text-muted-foreground">Rate Limit: {key.rate_limit.requests_per_hour} req/hr</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Plugins Tab */}
        <TabsContent value="plugins" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Puzzle className="h-5 w-5 text-indigo-500" />
                    Plugin Marketplace
                  </CardTitle>
                  <CardDescription>
                    Extend functionality with community plugins
                  </CardDescription>
                </div>
                <Button size="sm" variant="outline">
                  <Code className="mr-2 h-4 w-4" />
                  Developer Docs
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                {plugins?.map((plugin) => (
                  <Card key={plugin.id}>
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm">{plugin.name}</CardTitle>
                        <Badge variant={plugin.is_enabled ? 'default' : 'outline'}>
                          {plugin.is_enabled ? 'Enabled' : 'Disabled'}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <p className="text-xs text-muted-foreground">{plugin.description}</p>
                      
                      <div className="flex items-center justify-between text-xs">
                        <Badge variant="outline">v{plugin.version}</Badge>
                        <span className="text-muted-foreground">by {plugin.author}</span>
                      </div>

                      {plugin.manifest_url && (
                        <div className="flex items-center gap-2 text-xs">
                          <Code className="h-3 w-3" />
                          <code className="text-xs bg-muted px-2 py-1 rounded truncate flex-1">
                            {plugin.manifest_url}
                          </code>
                        </div>
                      )}

                      <div className="flex gap-2">
                        <Button size="sm" className="flex-1">
                          {plugin.is_enabled ? 'Configure' : 'Install'}
                        </Button>
                        <Button size="sm" variant="outline">
                          <Download className="h-3 w-3" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
