'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Wifi,
  WifiOff,
  Cloud,
  CloudOff,
  Download,
  Upload,
  RefreshCw,
  Loader2,
  CheckCircle,
  AlertTriangle,
  AlertCircle,
  Clock,
  HardDrive,
  Trash2,
  Settings,
  Database,
  Smartphone,
  ArrowDownToLine,
  ArrowUpFromLine,
} from 'lucide-react';

interface OfflineForm {
  id: string;
  form_id: string;
  form_name: string;
  last_synced: string;
  local_changes: number;
  size_bytes: number;
  status: 'synced' | 'pending' | 'conflict';
}

interface SyncConflict {
  id: string;
  form_id: string;
  field_id: string;
  local_value: any;
  server_value: any;
  local_timestamp: string;
  server_timestamp: string;
}

interface OfflineStats {
  total_offline_forms: number;
  total_pending_changes: number;
  storage_used_mb: number;
  storage_limit_mb: number;
  last_sync: string;
}

interface OfflineSyncProps {
  formId?: string;
}

export function OfflineSync({ formId }: OfflineSyncProps) {
  const [isOnline, setIsOnline] = useState(true);
  const [offlineForms, setOfflineForms] = useState<OfflineForm[]>([]);
  const [conflicts, setConflicts] = useState<SyncConflict[]>([]);
  const [stats, setStats] = useState<OfflineStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncProgress, setSyncProgress] = useState(0);
  const [autoSync, setAutoSync] = useState(true);
  const [conflictDialogOpen, setConflictDialogOpen] = useState(false);
  const [selectedConflict, setSelectedConflict] = useState<SyncConflict | null>(null);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    setIsOnline(navigator.onLine);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const fetchOfflineForms = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/offline/forms/`);
      const data = await response.json();
      setOfflineForms(data.results || data);
    } catch (error) {
      console.error('Failed to fetch offline forms:', error);
    }
  }, []);

  const fetchConflicts = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/offline/conflicts/`);
      const data = await response.json();
      setConflicts(data.results || data);
    } catch (error) {
      console.error('Failed to fetch conflicts:', error);
    }
  }, []);

  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/offline/stats/`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  }, []);

  useEffect(() => {
    const loadAll = async () => {
      setLoading(true);
      await Promise.all([fetchOfflineForms(), fetchConflicts(), fetchStats()]);
      setLoading(false);
    };
    loadAll();
  }, [fetchOfflineForms, fetchConflicts, fetchStats]);

  const downloadFormOffline = async (formId: string) => {
    try {
      await fetch(`/api/v1/features/offline/forms/download/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ form_id: formId }),
      });
      fetchOfflineForms();
      fetchStats();
    } catch (error) {
      console.error('Failed to download form:', error);
    }
  };

  const removeOfflineForm = async (offlineFormId: string) => {
    try {
      await fetch(`/api/v1/features/offline/forms/${offlineFormId}/`, {
        method: 'DELETE',
      });
      fetchOfflineForms();
      fetchStats();
    } catch (error) {
      console.error('Failed to remove offline form:', error);
    }
  };

  const syncAll = async () => {
    setSyncing(true);
    setSyncProgress(0);
    
    try {
      const formsToSync = offlineForms.filter(f => f.status === 'pending');
      const total = formsToSync.length;
      
      for (let i = 0; i < total; i++) {
        await fetch(`/api/v1/features/offline/sync/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ form_id: formsToSync[i].form_id }),
        });
        setSyncProgress(((i + 1) / total) * 100);
      }
      
      await Promise.all([fetchOfflineForms(), fetchConflicts(), fetchStats()]);
    } catch (error) {
      console.error('Failed to sync:', error);
    } finally {
      setSyncing(false);
      setSyncProgress(0);
    }
  };

  const resolveConflict = async (conflictId: string, resolution: 'local' | 'server' | 'merge') => {
    try {
      await fetch(`/api/v1/features/offline/conflicts/${conflictId}/resolve/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resolution }),
      });
      setConflictDialogOpen(false);
      setSelectedConflict(null);
      fetchConflicts();
    } catch (error) {
      console.error('Failed to resolve conflict:', error);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const pendingForms = offlineForms.filter(f => f.status === 'pending');
  const conflictForms = offlineForms.filter(f => f.status === 'conflict');
  const storagePercentage = stats 
    ? (stats.storage_used_mb / stats.storage_limit_mb) * 100 
    : 0;

  return (
    <div className="space-y-6">
      {/* Connection Status Banner */}
      <div className={`p-4 rounded-lg flex items-center justify-between ${
        isOnline ? 'bg-green-50 border border-green-200' : 'bg-yellow-50 border border-yellow-200'
      }`}>
        <div className="flex items-center gap-3">
          {isOnline ? (
            <>
              <Wifi className="h-5 w-5 text-green-600" />
              <div>
                <p className="font-medium text-green-800">You&apos;re Online</p>
                <p className="text-sm text-green-600">All changes will sync automatically</p>
              </div>
            </>
          ) : (
            <>
              <WifiOff className="h-5 w-5 text-yellow-600" />
              <div>
                <p className="font-medium text-yellow-800">You&apos;re Offline</p>
                <p className="text-sm text-yellow-600">Changes will sync when you reconnect</p>
              </div>
            </>
          )}
        </div>
        {isOnline && pendingForms.length > 0 && (
          <Button onClick={syncAll} disabled={syncing}>
            {syncing ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-2" />
            )}
            Sync Now ({pendingForms.length})
          </Button>
        )}
      </div>

      {/* Sync Progress */}
      {syncing && (
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-4">
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
              <div className="flex-1">
                <div className="flex justify-between text-sm mb-1">
                  <span>Syncing changes...</span>
                  <span>{syncProgress.toFixed(0)}%</span>
                </div>
                <Progress value={syncProgress} />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Download className="h-4 w-4 text-blue-500" />
              Offline Forms
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-3xl font-bold">{stats?.total_offline_forms || 0}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Upload className="h-4 w-4 text-yellow-500" />
              Pending Changes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-3xl font-bold text-yellow-600">
              {stats?.total_pending_changes || 0}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-red-500" />
              Conflicts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-3xl font-bold text-red-600">{conflicts.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <HardDrive className="h-4 w-4 text-purple-500" />
              Storage Used
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-bold">{stats?.storage_used_mb?.toFixed(1) || 0}</span>
              <span className="text-sm text-muted-foreground">
                / {stats?.storage_limit_mb || 100} MB
              </span>
            </div>
            <Progress value={storagePercentage} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="forms">
        <TabsList>
          <TabsTrigger value="forms">
            <Database className="h-4 w-4 mr-2" />
            Offline Forms
          </TabsTrigger>
          <TabsTrigger value="conflicts">
            <AlertTriangle className="h-4 w-4 mr-2" />
            Conflicts
            {conflicts.length > 0 && (
              <Badge variant="destructive" className="ml-2">{conflicts.length}</Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="settings">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </TabsTrigger>
        </TabsList>

        {/* Offline Forms Tab */}
        <TabsContent value="forms" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Downloaded Forms</CardTitle>
                  <CardDescription>Forms available for offline editing</CardDescription>
                </div>
                {formId && (
                  <Button onClick={() => downloadFormOffline(formId)}>
                    <ArrowDownToLine className="h-4 w-4 mr-2" />
                    Download Current Form
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {offlineForms.map((form) => (
                  <div key={form.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className={`p-2 rounded-full ${
                        form.status === 'synced' ? 'bg-green-100 text-green-600' :
                        form.status === 'pending' ? 'bg-yellow-100 text-yellow-600' :
                        'bg-red-100 text-red-600'
                      }`}>
                        {form.status === 'synced' ? <CheckCircle className="h-4 w-4" /> :
                         form.status === 'pending' ? <Clock className="h-4 w-4" /> :
                         <AlertCircle className="h-4 w-4" />}
                      </div>
                      <div>
                        <p className="font-medium">{form.form_name}</p>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <span>Last synced: {new Date(form.last_synced).toLocaleString()}</span>
                          <span>•</span>
                          <span>{formatBytes(form.size_bytes)}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {form.local_changes > 0 && (
                        <Badge variant="secondary">
                          {form.local_changes} changes
                        </Badge>
                      )}
                      <Badge variant={
                        form.status === 'synced' ? 'default' :
                        form.status === 'pending' ? 'secondary' : 'destructive'
                      }>
                        {form.status}
                      </Badge>
                      <Button variant="ghost" size="icon" onClick={() => removeOfflineForm(form.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
                {offlineForms.length === 0 && (
                  <div className="text-center py-8">
                    <CloudOff className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
                    <p className="font-medium">No offline forms</p>
                    <p className="text-sm text-muted-foreground">
                      Download forms to work offline
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Conflicts Tab */}
        <TabsContent value="conflicts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Sync Conflicts</CardTitle>
              <CardDescription>Resolve conflicts between local and server changes</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {conflicts.map((conflict) => (
                  <div key={conflict.id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <AlertTriangle className="h-4 w-4 text-yellow-500" />
                          <span className="font-medium">Field: {conflict.field_id}</span>
                        </div>
                        <div className="grid grid-cols-2 gap-4 mt-3">
                          <div className="p-3 bg-blue-50 rounded-lg">
                            <p className="text-xs text-blue-600 mb-1 flex items-center gap-1">
                              <Smartphone className="h-3 w-3" /> Local Value
                            </p>
                            <p className="font-mono text-sm">{JSON.stringify(conflict.local_value)}</p>
                            <p className="text-xs text-muted-foreground mt-1">
                              {new Date(conflict.local_timestamp).toLocaleString()}
                            </p>
                          </div>
                          <div className="p-3 bg-purple-50 rounded-lg">
                            <p className="text-xs text-purple-600 mb-1 flex items-center gap-1">
                              <Cloud className="h-3 w-3" /> Server Value
                            </p>
                            <p className="font-mono text-sm">{JSON.stringify(conflict.server_value)}</p>
                            <p className="text-xs text-muted-foreground mt-1">
                              {new Date(conflict.server_timestamp).toLocaleString()}
                            </p>
                          </div>
                        </div>
                      </div>
                      <Button
                        size="sm"
                        onClick={() => {
                          setSelectedConflict(conflict);
                          setConflictDialogOpen(true);
                        }}
                      >
                        Resolve
                      </Button>
                    </div>
                  </div>
                ))}
                {conflicts.length === 0 && (
                  <div className="text-center py-8">
                    <CheckCircle className="h-12 w-12 mx-auto text-green-500 mb-2" />
                    <p className="font-medium">No conflicts</p>
                    <p className="text-sm text-muted-foreground">
                      All your data is in sync
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Offline Settings</CardTitle>
              <CardDescription>Configure offline behavior</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Auto-sync when online</Label>
                  <p className="text-sm text-muted-foreground">
                    Automatically sync changes when connected
                  </p>
                </div>
                <Switch
                  checked={autoSync}
                  onCheckedChange={setAutoSync}
                />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label>Background sync</Label>
                  <p className="text-sm text-muted-foreground">
                    Sync data in background (uses more battery)
                  </p>
                </div>
                <Switch />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label>Sync on Wi-Fi only</Label>
                  <p className="text-sm text-muted-foreground">
                    Save mobile data by syncing only on Wi-Fi
                  </p>
                </div>
                <Switch />
              </div>
              <div className="pt-4 border-t">
                <Button variant="destructive" className="w-full">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Clear All Offline Data
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Conflict Resolution Dialog */}
      <Dialog open={conflictDialogOpen} onOpenChange={setConflictDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Resolve Conflict</DialogTitle>
            <DialogDescription>
              Choose which version to keep for field &quot;{selectedConflict?.field_id}&quot;
            </DialogDescription>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-4">
            <div className="p-4 border rounded-lg">
              <p className="text-sm font-medium mb-2 flex items-center gap-2">
                <Smartphone className="h-4 w-4" /> Local Version
              </p>
              <p className="font-mono text-sm bg-muted p-2 rounded">
                {JSON.stringify(selectedConflict?.local_value, null, 2)}
              </p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm font-medium mb-2 flex items-center gap-2">
                <Cloud className="h-4 w-4" /> Server Version
              </p>
              <p className="font-mono text-sm bg-muted p-2 rounded">
                {JSON.stringify(selectedConflict?.server_value, null, 2)}
              </p>
            </div>
          </div>
          <DialogFooter className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => selectedConflict && resolveConflict(selectedConflict.id, 'local')}
            >
              Keep Local
            </Button>
            <Button
              variant="outline"
              onClick={() => selectedConflict && resolveConflict(selectedConflict.id, 'server')}
            >
              Keep Server
            </Button>
            <Button
              onClick={() => selectedConflict && resolveConflict(selectedConflict.id, 'merge')}
            >
              Merge Both
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default OfflineSync;
