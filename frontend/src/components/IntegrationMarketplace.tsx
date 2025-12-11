'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Puzzle,
  Search,
  Plus,
  CheckCircle,
  XCircle,
  RefreshCw,
  Settings,
  Trash2,
  Link,
  Zap,
  Database,
  Mail,
  MessageSquare,
  CreditCard,
  BarChart,
  FileSpreadsheet,
  Slack,
} from 'lucide-react';

interface Integration {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  auth_type: string;
  popular?: boolean;
  features?: string[];
}

interface ConfiguredIntegration {
  id: string;
  integration_id: string;
  name: string;
  status: 'pending' | 'connected' | 'error' | 'disabled';
  sync_on_submit: boolean;
  last_sync_at?: string;
  last_sync_status?: string;
}

interface IntegrationMarketplaceProps {
  formId: string;
}

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  crm: Database,
  email_marketing: Mail,
  automation: Zap,
  analytics: BarChart,
  payment: CreditCard,
  spreadsheet: FileSpreadsheet,
  communication: MessageSquare,
};

export function IntegrationMarketplace({ formId }: IntegrationMarketplaceProps) {
  const [catalog, setCatalog] = useState<Integration[]>([]);
  const [configured, setConfigured] = useState<ConfiguredIntegration[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [showSetupDialog, setShowSetupDialog] = useState(false);
  const [selectedIntegration, setSelectedIntegration] = useState<Integration | null>(null);
  const [apiKey, setApiKey] = useState('');
  const [connecting, setConnecting] = useState(false);

  useEffect(() => {
    fetchCatalog();
    fetchConfigured();
  }, [formId]);

  const fetchCatalog = async () => {
    try {
      const response = await fetch('/api/v1/automation/integrations/catalog/');
      const data = await response.json();
      setCatalog(data);

      // Extract unique categories
      const cats = [...new Set(data.map((i: Integration) => i.category))];
      setCategories(cats as string[]);
    } catch (error) {
      console.error('Failed to fetch catalog:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchConfigured = async () => {
    try {
      const response = await fetch(`/api/v1/automation/integrations/?form_id=${formId}`);
      const data = await response.json();
      setConfigured(data);
    } catch (error) {
      console.error('Failed to fetch configured integrations:', error);
    }
  };

  const setupIntegration = async () => {
    if (!selectedIntegration) return;
    
    setConnecting(true);
    try {
      // Create integration
      const createResponse = await fetch('/api/v1/automation/integrations/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          form_id: formId,
          integration_id: selectedIntegration.id,
        }),
      });
      const createData = await createResponse.json();

      // Connect with credentials
      const connectResponse = await fetch(`/api/v1/automation/integrations/${createData.id}/connect/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          credentials: { api_key: apiKey },
        }),
      });

      setShowSetupDialog(false);
      setApiKey('');
      setSelectedIntegration(null);
      fetchConfigured();
    } catch (error) {
      console.error('Failed to setup integration:', error);
    } finally {
      setConnecting(false);
    }
  };

  const syncIntegration = async (integrationId: string) => {
    try {
      await fetch(`/api/v1/automation/integrations/${integrationId}/sync/`, {
        method: 'POST',
      });
      fetchConfigured();
    } catch (error) {
      console.error('Failed to sync:', error);
    }
  };

  const removeIntegration = async (integrationId: string) => {
    if (!confirm('Remove this integration?')) return;
    try {
      await fetch(`/api/v1/automation/integrations/${integrationId}/`, {
        method: 'DELETE',
      });
      fetchConfigured();
    } catch (error) {
      console.error('Failed to remove integration:', error);
    }
  };

  const filteredCatalog = catalog.filter(integration => {
    const matchesCategory = selectedCategory === 'all' || integration.category === selectedCategory;
    const matchesSearch = !searchQuery || 
      integration.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      integration.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'default';
      case 'error': return 'destructive';
      case 'pending': return 'secondary';
      default: return 'outline';
    }
  };

  const getCategoryIcon = (category: string) => {
    return CATEGORY_ICONS[category] || Puzzle;
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
      <div>
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Puzzle className="h-6 w-6 text-primary" />
          Integration Marketplace
        </h2>
        <p className="text-muted-foreground">Connect your forms to 50+ services</p>
      </div>

      {/* Configured Integrations */}
      {configured.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Active Integrations</CardTitle>
            <CardDescription>{configured.length} integration(s) configured</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3">
              {configured.map((integration) => (
                <div
                  key={integration.id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-muted rounded">
                      <Link className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="font-medium">{integration.name}</p>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Badge variant={getStatusColor(integration.status)}>
                          {integration.status}
                        </Badge>
                        {integration.last_sync_at && (
                          <span>Last sync: {new Date(integration.last_sync_at).toLocaleString()}</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => syncIntegration(integration.id)}
                    >
                      <RefreshCw className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeIntegration(integration.id)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Search and Filter */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search integrations..."
            className="pl-10"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Select value={selectedCategory} onValueChange={setSelectedCategory}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="All Categories" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {categories.map((category) => (
              <SelectItem key={category} value={category}>
                {category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Catalog Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredCatalog.map((integration) => {
          const CategoryIcon = getCategoryIcon(integration.category);
          const isConfigured = configured.some(c => c.integration_id === integration.id);

          return (
            <Card
              key={integration.id}
              className={`hover:shadow-md transition-shadow ${isConfigured ? 'border-green-200 bg-green-50/50' : ''}`}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-muted rounded">
                      <CategoryIcon className="h-6 w-6" />
                    </div>
                    <div>
                      <h3 className="font-semibold flex items-center gap-2">
                        {integration.name}
                        {integration.popular && (
                          <Badge variant="secondary" className="text-xs">Popular</Badge>
                        )}
                      </h3>
                      <Badge variant="outline" className="text-xs">
                        {integration.category.replace('_', ' ')}
                      </Badge>
                    </div>
                  </div>
                  {isConfigured && (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  )}
                </div>

                <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                  {integration.description}
                </p>

                {integration.features && (
                  <div className="flex flex-wrap gap-1 mb-4">
                    {integration.features.slice(0, 3).map((feature, i) => (
                      <Badge key={i} variant="outline" className="text-xs">
                        {feature}
                      </Badge>
                    ))}
                  </div>
                )}

                <Dialog
                  open={showSetupDialog && selectedIntegration?.id === integration.id}
                  onOpenChange={(open) => {
                    setShowSetupDialog(open);
                    if (!open) setSelectedIntegration(null);
                  }}
                >
                  <DialogTrigger asChild>
                    <Button
                      className="w-full"
                      variant={isConfigured ? 'outline' : 'default'}
                      onClick={() => setSelectedIntegration(integration)}
                    >
                      {isConfigured ? (
                        <>
                          <Settings className="mr-2 h-4 w-4" />
                          Configure
                        </>
                      ) : (
                        <>
                          <Plus className="mr-2 h-4 w-4" />
                          Connect
                        </>
                      )}
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Connect {integration.name}</DialogTitle>
                      <DialogDescription>
                        Enter your credentials to connect this integration
                      </DialogDescription>
                    </DialogHeader>

                    <div className="space-y-4">
                      {integration.auth_type === 'api_key' && (
                        <div className="space-y-2">
                          <label className="text-sm font-medium">API Key</label>
                          <Input
                            type="password"
                            placeholder="Enter your API key"
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                          />
                          <p className="text-xs text-muted-foreground">
                            You can find your API key in your {integration.name} account settings.
                          </p>
                        </div>
                      )}

                      {integration.auth_type === 'oauth' && (
                        <div className="text-center py-4">
                          <p className="text-sm text-muted-foreground mb-4">
                            Click the button below to authorize with {integration.name}
                          </p>
                          <Button>
                            <Link className="mr-2 h-4 w-4" />
                            Authorize with {integration.name}
                          </Button>
                        </div>
                      )}
                    </div>

                    <DialogFooter>
                      <Button
                        variant="outline"
                        onClick={() => {
                          setShowSetupDialog(false);
                          setSelectedIntegration(null);
                        }}
                      >
                        Cancel
                      </Button>
                      <Button
                        onClick={setupIntegration}
                        disabled={connecting || (!apiKey && integration.auth_type === 'api_key')}
                      >
                        {connecting ? (
                          <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                        ) : (
                          <CheckCircle className="mr-2 h-4 w-4" />
                        )}
                        Connect
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {filteredCatalog.length === 0 && (
        <div className="text-center py-12">
          <Puzzle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-lg font-medium">No integrations found</p>
          <p className="text-muted-foreground">Try adjusting your search or filters</p>
        </div>
      )}
    </div>
  );
}

export default IntegrationMarketplace;
