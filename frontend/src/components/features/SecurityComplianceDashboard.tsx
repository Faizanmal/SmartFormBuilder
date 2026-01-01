'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  useZeroKnowledgeEncryption,
  useUpdateZeroKnowledgeEncryption,
  useBlockchainConfig,
  useUpdateBlockchainConfig,
  useThreatDetectionConfig,
  useComplianceFrameworks,
  useComplianceScans,
  useRunComplianceScan
} from '@/hooks/use-emerging-features';
import { 
  Shield, Lock, Activity, AlertTriangle, 
  CheckCircle2, XCircle, Loader2, FileText,
  Link2, Eye 
} from 'lucide-react';

interface SecurityComplianceDashboardProps {
  formId: string;
}

export function SecurityComplianceDashboard({ formId }: SecurityComplianceDashboardProps) {
  const { data: zeroKnowledge } = useZeroKnowledgeEncryption(formId);
  const updateZeroKnowledge = useUpdateZeroKnowledgeEncryption();

  const { data: blockchain } = useBlockchainConfig(formId);
  const updateBlockchain = useUpdateBlockchainConfig();

  const { data: threatDetection } = useThreatDetectionConfig(formId);
  const { data: frameworks } = useComplianceFrameworks();
  const { data: scans } = useComplianceScans(formId);
  const runScan = useRunComplianceScan();

  const latestScan = scans?.[0];

  return (
    <div className="space-y-6">
      <Tabs defaultValue="encryption" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="encryption">Encryption</TabsTrigger>
          <TabsTrigger value="blockchain">Blockchain</TabsTrigger>
          <TabsTrigger value="threats">Threats</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
        </TabsList>

        {/* Encryption Tab */}
        <TabsContent value="encryption" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="h-5 w-5 text-blue-500" />
                Zero-Knowledge Encryption
              </CardTitle>
              <CardDescription>
                End-to-end encryption with client-side key management
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="encryption-enabled">Enable Zero-Knowledge Encryption</Label>
                <Switch
                  id="encryption-enabled"
                  checked={zeroKnowledge?.is_enabled}
                  onCheckedChange={(checked) => {
                    updateZeroKnowledge.mutate({
                      formId,
                      config: { is_enabled: checked }
                    });
                  }}
                />
              </div>

              {zeroKnowledge?.is_enabled && (
                <div className="space-y-4 p-4 border rounded-lg bg-blue-50/50">
                  <div className="flex items-center gap-2">
                    <Shield className="h-5 w-5 text-blue-600" />
                    <span className="font-medium text-sm">Encryption Active</span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Algorithm</p>
                      <p className="font-medium">{zeroKnowledge.encryption_algorithm}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Key Derivation</p>
                      <p className="font-medium">{zeroKnowledge.key_derivation}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    <span className="text-sm text-muted-foreground">
                      {zeroKnowledge.client_side_only ? 'Client-side only' : 'Hybrid encryption'}
                    </span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Blockchain Tab */}
        <TabsContent value="blockchain" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Link2 className="h-5 w-5 text-purple-500" />
                Blockchain Audit Trail
              </CardTitle>
              <CardDescription>
                Immutable audit logs on blockchain
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="blockchain-enabled">Enable Blockchain Audit Trail</Label>
                <Switch
                  id="blockchain-enabled"
                  checked={blockchain?.is_enabled}
                  onCheckedChange={(checked) => {
                    updateBlockchain.mutate({
                      formId,
                      config: { is_enabled: checked }
                    });
                  }}
                />
              </div>

              {blockchain?.is_enabled && (
                <div className="space-y-4 p-4 border rounded-lg bg-purple-50/50">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Chain Type</p>
                      <p className="font-medium capitalize">{blockchain.chain_type}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Events Tracked</p>
                      <p className="font-medium">{blockchain.audit_events.length}</p>
                    </div>
                  </div>

                  {blockchain.smart_contract_address && (
                    <div>
                      <p className="text-muted-foreground text-sm mb-1">Smart Contract</p>
                      <code className="text-xs bg-muted px-2 py-1 rounded break-all">
                        {blockchain.smart_contract_address}
                      </code>
                    </div>
                  )}

                  <div className="flex flex-wrap gap-2">
                    {blockchain.audit_events.map((event: string) => (
                      <Badge key={event} variant="outline">{event}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Threat Detection Tab */}
        <TabsContent value="threats" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-red-500" />
                AI Threat Detection
              </CardTitle>
              <CardDescription>
                Real-time security threat monitoring and prevention
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {threatDetection && (
                <>
                  <div className="flex items-center justify-between">
                    <Label>Threat Detection Status</Label>
                    <Badge variant={threatDetection.is_enabled ? 'default' : 'secondary'}>
                      {threatDetection.is_enabled ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <Activity className="h-4 w-4 text-orange-500" />
                        <span className="text-sm">SQL Injection</span>
                      </div>
                      {threatDetection.sql_injection_detection ? (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      ) : (
                        <XCircle className="h-4 w-4 text-gray-400" />
                      )}
                    </div>

                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <Activity className="h-4 w-4 text-red-500" />
                        <span className="text-sm">XSS Detection</span>
                      </div>
                      {threatDetection.xss_detection ? (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      ) : (
                        <XCircle className="h-4 w-4 text-gray-400" />
                      )}
                    </div>

                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <Activity className="h-4 w-4 text-blue-500" />
                        <span className="text-sm">Bot Detection</span>
                      </div>
                      {threatDetection.bot_detection ? (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      ) : (
                        <XCircle className="h-4 w-4 text-gray-400" />
                      )}
                    </div>

                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <Activity className="h-4 w-4 text-purple-500" />
                        <span className="text-sm">Rate Limiting</span>
                      </div>
                      {threatDetection.rate_limiting ? (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      ) : (
                        <XCircle className="h-4 w-4 text-gray-400" />
                      )}
                    </div>
                  </div>

                  <div className="p-3 border rounded-lg bg-muted">
                    <p className="text-sm text-muted-foreground">
                      Threat Level Threshold: <span className="font-medium capitalize">{threatDetection.threat_level_threshold}</span>
                    </p>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Compliance Tab */}
        <TabsContent value="compliance" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-green-500" />
                    Compliance Scanning
                  </CardTitle>
                  <CardDescription>
                    Automated compliance checks for major frameworks
                  </CardDescription>
                </div>
                {frameworks && frameworks.length > 0 && (
                  <Button
                    onClick={() => {
                      const activeFramework = frameworks.find(f => f.is_active);
                      if (activeFramework) {
                        runScan.mutate({ formId, frameworkId: activeFramework.id });
                      }
                    }}
                    disabled={runScan.isPending}
                  >
                    {runScan.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Run Scan
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Latest Scan Results */}
              {latestScan && (
                <div className="p-4 border rounded-lg space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant={latestScan.result === 'compliant' ? 'default' : 'destructive'}>
                        {latestScan.result}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        {new Date(latestScan.created_at).toLocaleString()}
                      </span>
                    </div>
                    <div className="text-2xl font-bold">{latestScan.overall_score}%</div>
                  </div>

                  <Progress value={latestScan.overall_score} className="h-2" />

                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Passed</p>
                      <p className="text-2xl font-bold text-green-600">{latestScan.checks_passed}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Failed</p>
                      <p className="text-2xl font-bold text-red-600">{latestScan.checks_failed}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Issues</p>
                      <p className="text-2xl font-bold text-orange-600">{latestScan.issues.length}</p>
                    </div>
                  </div>

                  {latestScan.recommendations.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-medium text-sm">Recommendations</h4>
                      {latestScan.recommendations.slice(0, 3).map((rec: unknown, index: number) => {
                        const desc = typeof rec === 'string' ? rec : String((rec as Record<string, unknown>).description || '');
                        return (
                          <div key={index} className="text-sm p-2 bg-muted rounded">
                            {desc}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              {/* Available Frameworks */}
              <div className="space-y-2">
                <h4 className="font-medium text-sm">Available Frameworks</h4>
                <div className="grid grid-cols-2 gap-2">
                  {frameworks?.map((framework) => (
                    <div
                      key={framework.id}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div>
                        <p className="font-medium text-sm">{framework.code}</p>
                        <p className="text-xs text-muted-foreground">{framework.name}</p>
                      </div>
                      <Badge variant={framework.is_active ? 'default' : 'outline'}>
                        {framework.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
