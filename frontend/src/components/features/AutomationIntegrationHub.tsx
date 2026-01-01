'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { 
  useWebhookTransformers,
  useMarketplaceIntegrations,
  useSSOConfigurations,
  useSmartRoutingConfig,
  useUpdateSmartRoutingConfig,
  useApprovalWorkflows,
  useRuleEngines,
  useUpdateRuleEngine
} from '@/hooks/use-emerging-features';
import { 
  Webhook, ShoppingBag, Key, GitBranch, 
  CheckSquare, Zap, Settings, ArrowRight,
  Play, Pause, Edit, Plus, Loader2
} from 'lucide-react';

interface AutomationIntegrationHubProps {
  formId: string;
}

export function AutomationIntegrationHub({ formId }: AutomationIntegrationHubProps) {
  const { data: webhooks } = useWebhookTransformers();
  const { data: integrations } = useMarketplaceIntegrations();
  const { data: ssoConfigs } = useSSOConfigurations(formId);
  const { data: routing } = useSmartRoutingConfig(formId);
  const updateRouting = useUpdateSmartRoutingConfig();
  const { data: workflows } = useApprovalWorkflows(formId);
  const { data: ruleEngines } = useRuleEngines(formId);
  const updateRuleEngine = useUpdateRuleEngine();

  const [selectedIntegration, setSelectedIntegration] = useState<string>('');

  return (
    <div className="space-y-6">
      <Tabs defaultValue="webhooks" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="webhooks">Webhooks</TabsTrigger>
          <TabsTrigger value="marketplace">Marketplace</TabsTrigger>
          <TabsTrigger value="sso">SSO</TabsTrigger>
          <TabsTrigger value="routing">Routing</TabsTrigger>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
        </TabsList>

        {/* Webhooks Tab */}
        <TabsContent value="webhooks" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Webhook className="h-5 w-5 text-blue-500" />
                    Webhook Transformers
                  </CardTitle>
                  <CardDescription>
                    Transform and map form data for external systems
                  </CardDescription>
                </div>
                <Button size="sm">
                  <Plus className="mr-2 h-4 w-4" />
                  Add Webhook
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {webhooks?.map((webhook) => (
                  <div key={webhook.id} className="p-4 border rounded-lg space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium">{webhook.name}</h4>
                        <p className="text-sm text-muted-foreground">{webhook.target_url}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={webhook.is_active ? 'default' : 'secondary'}>
                          {webhook.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                        <Button variant="ghost" size="icon">
                          <Edit className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Method</p>
                        <Badge variant="outline">{webhook.http_method}</Badge>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Events</p>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {webhook.trigger_events.slice(0, 2).map((event: string) => (
                            <Badge key={event} variant="secondary" className="text-xs">
                              {event}
                            </Badge>
                          ))}
                          {webhook.trigger_events.length > 2 && (
                            <Badge variant="secondary" className="text-xs">
                              +{webhook.trigger_events.length - 2}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>

                    {webhook.field_mappings && Object.keys(webhook.field_mappings).length > 0 && (
                      <div className="text-xs bg-muted p-2 rounded">
                        <p className="font-medium mb-1">Field Mappings:</p>
                        <code className="text-xs">
                          {JSON.stringify(webhook.field_mappings, null, 2).slice(0, 100)}...
                        </code>
                      </div>
                    )}
                  </div>
                ))}

                {(!webhooks || webhooks.length === 0) && (
                  <div className="text-center py-8 text-muted-foreground">
                    No webhook transformers configured
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Marketplace Tab */}
        <TabsContent value="marketplace" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShoppingBag className="h-5 w-5 text-purple-500" />
                Integration Marketplace
              </CardTitle>
              <CardDescription>
                Browse and connect third-party integrations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                {integrations?.map((integration) => (
                  <Card key={integration.id} className="overflow-hidden">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <CardTitle className="text-base">{integration.name}</CardTitle>
                          <p className="text-xs text-muted-foreground mt-1">
                            {integration.category}
                          </p>
                        </div>
                        <Badge variant={integration.is_active ? 'default' : 'outline'}>
                          {integration.is_active ? 'Connected' : 'Available'}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <p className="text-sm">{integration.description}</p>
                      
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary" className="text-xs">
                          v{integration.version}
                        </Badge>
                        {integration.pricing_model && (
                          <Badge variant="outline" className="text-xs">
                            {integration.pricing_model}
                          </Badge>
                        )}
                      </div>

                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>{integration.installs_count} installs</span>
                        <span>★ {integration.rating}/5</span>
                      </div>

                      <Button 
                        size="sm" 
                        className="w-full"
                        variant={integration.is_active ? 'outline' : 'default'}
                      >
                        {integration.is_active ? 'Configure' : 'Install'}
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* SSO Tab */}
        <TabsContent value="sso" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Key className="h-5 w-5 text-green-500" />
                    Single Sign-On (SSO)
                  </CardTitle>
                  <CardDescription>
                    Configure SSO providers for authentication
                  </CardDescription>
                </div>
                <Button size="sm">
                  <Plus className="mr-2 h-4 w-4" />
                  Add Provider
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {ssoConfigs?.map((config) => (
                  <div key={config.id} className="p-4 border rounded-lg space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium">{config.provider_name}</h4>
                        <Badge variant="outline" className="mt-1">
                          {config.protocol}
                        </Badge>
                      </div>
                      <Switch checked={config.is_enabled} />
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Entity ID</p>
                        <code className="text-xs bg-muted px-2 py-1 rounded block mt-1 truncate">
                          {config.entity_id}
                        </code>
                      </div>
                      {config.auto_create_users && (
                        <div className="flex items-center gap-2">
                          <CheckSquare className="h-4 w-4 text-green-600" />
                          <span className="text-xs">Auto-create users</span>
                        </div>
                      )}
                    </div>

                    {config.user_attribute_mapping && (
                      <div className="text-xs bg-muted p-2 rounded">
                        <p className="font-medium mb-1">Attribute Mapping:</p>
                        <div className="space-y-1">
                          {Object.entries(config.user_attribute_mapping).slice(0, 3).map(([key, value]) => (
                            <div key={key} className="flex items-center gap-2">
                              <span className="text-muted-foreground">{key}:</span>
                              <code>{value as string}</code>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Smart Routing Tab */}
        <TabsContent value="routing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GitBranch className="h-5 w-5 text-orange-500" />
                Smart Routing
              </CardTitle>
              <CardDescription>
                Automatically route submissions based on intelligent rules
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="routing-enabled">Enable Smart Routing</Label>
                <Switch
                  id="routing-enabled"
                  checked={routing?.is_enabled}
                  onCheckedChange={(checked) => {
                    updateRouting.mutate({
                      formId,
                      config: { is_enabled: checked }
                    });
                  }}
                />
              </div>

              {routing?.is_enabled && (
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="routing-strategy">Routing Strategy</Label>
                    <Select
                      value={routing.strategy}
                      onValueChange={(value) => {
                        updateRouting.mutate({
                          formId,
                          config: { strategy: value }
                        });
                      }}
                    >
                      <SelectTrigger id="routing-strategy">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="round_robin">Round Robin</SelectItem>
                        <SelectItem value="load_balanced">Load Balanced</SelectItem>
                        <SelectItem value="priority_based">Priority Based</SelectItem>
                        <SelectItem value="skill_matched">Skill Matched</SelectItem>
                        <SelectItem value="ml_predicted">ML Predicted</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {routing.routing_rules.length > 0 && (
                    <div className="space-y-2">
                      <Label>Routing Rules</Label>
                      {(routing.routing_rules as Record<string, unknown>[]).map((rule, index: number) => (
                        <div key={index} className="flex items-center gap-2 p-3 bg-muted rounded-lg">
                          <ArrowRight className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm flex-1">
                            {String(rule.condition || `Rule ${index + 1}`)} → {String(rule.destination || '')}
                          </span>
                          <Badge variant="secondary">{String(rule.priority || '')}</Badge>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Rule Engines */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-500" />
                Rule Engines
              </CardTitle>
              <CardDescription>
                Define business logic and conditional workflows
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {ruleEngines?.map((engine) => (
                  <div key={engine.id} className="p-4 border rounded-lg space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium">{engine.name}</h4>
                        <p className="text-sm text-muted-foreground">{engine.description}</p>
                      </div>
                      <Switch
                        checked={engine.is_active}
                        onCheckedChange={(checked) => {
                          updateRuleEngine.mutate({
                            formId,
                            engineId: engine.id,
                            config: { is_active: checked }
                          });
                        }}
                      />
                    </div>

                    <div className="flex items-center gap-4 text-sm">
                      <Badge variant="outline">{engine.rules.length} rules</Badge>
                      <Badge variant={engine.execution_priority === 'high' ? 'default' : 'secondary'}>
                        Priority: {engine.execution_priority}
                      </Badge>
                    </div>

                    {engine.rules.length > 0 && (
                      <div className="space-y-1 text-xs">
                        {engine.rules.slice(0, 2).map((rule: Record<string, unknown>, index: number) => (
                          <div key={index} className="flex items-center gap-2 p-2 bg-muted rounded">
                            <Play className="h-3 w-3" />
                            <code className="flex-1">{String(rule.condition || '')}</code>
                            <ArrowRight className="h-3 w-3" />
                            <span>{String(rule.action || '')}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Workflows Tab */}
        <TabsContent value="workflows" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <CheckSquare className="h-5 w-5 text-indigo-500" />
                    Approval Workflows
                  </CardTitle>
                  <CardDescription>
                    Multi-step approval processes with notifications
                  </CardDescription>
                </div>
                <Button size="sm">
                  <Plus className="mr-2 h-4 w-4" />
                  Create Workflow
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {workflows?.map((workflow) => (
                  <div key={workflow.id} className="p-4 border rounded-lg space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium">{workflow.name}</h4>
                        <p className="text-sm text-muted-foreground">{workflow.description}</p>
                      </div>
                      <Badge variant={workflow.is_active ? 'default' : 'secondary'}>
                        {workflow.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>

                    <div className="flex items-center gap-2">
                      {workflow.steps.map((step: Record<string, unknown>, index: number) => (
                        <React.Fragment key={index}>
                          <div className="flex-1 p-2 bg-muted rounded text-xs">
                            <p className="font-medium">{String(step.name || '')}</p>
                            <p className="text-muted-foreground">
                              {Array.isArray(step.approvers) ? (step.approvers as unknown[]).length : 0} approvers
                            </p>
                          </div>
                          {index < workflow.steps.length - 1 && (
                            <ArrowRight className="h-4 w-4 text-muted-foreground" />
                          )}
                        </React.Fragment>
                      ))}
                    </div>

                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>{workflow.approval_type === 'sequential' ? '→ Sequential' : '⊕ Parallel'}</span>
                      <span>Auto-escalate: {workflow.auto_escalate ? 'Yes' : 'No'}</span>
                    </div>
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
