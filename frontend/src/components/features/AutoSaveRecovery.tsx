'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Save,
  History,
  AlertTriangle,
  CheckCircle,
  Clock,
  RefreshCw,
  Calendar,
  Trash2,
  Download,
  Loader2,
  CloudOff,
  Cloud,
  RotateCcw,
  FileText,
  X,
} from 'lucide-react';

interface AutoSave {
  id: string;
  form_id?: string;
  temp_id?: string;
  title: string;
  schema_json: Record<string, unknown>;
  settings_json: Record<string, unknown>;
  editor_state: Record<string, unknown>;
  is_recovered: boolean;
  last_saved_at: string;
}

interface CrashRecovery {
  id: string;
  form_id?: string;
  autosave_id: string;
  status: 'pending' | 'recovered' | 'dismissed';
  crash_reason: string;
  created_at: string;
}

interface DraftSchedule {
  id: string;
  form_id: string;
  form_title: string;
  scheduled_at: string;
  status: 'pending' | 'published' | 'cancelled';
}

interface AutoSaveRecoveryProps {
  formId?: string;
  currentSchema?: Record<string, unknown>;
  currentSettings?: Record<string, unknown>;
  onRecover?: (schema: Record<string, unknown>, settings: Record<string, unknown>) => void;
}

const AUTOSAVE_INTERVAL = 30000; // 30 seconds
const CRASH_REASONS = {
  browser_crash: 'Browser Crash',
  tab_closed: 'Tab Closed',
  session_expired: 'Session Expired',
  network_error: 'Network Error',
  unknown: 'Unknown',
};

export function AutoSaveRecovery({
  formId,
  currentSchema,
  currentSettings,
  onRecover,
}: AutoSaveRecoveryProps) {
  const [autoSaves, setAutoSaves] = useState<AutoSave[]>([]);
  const [pendingRecoveries, setPendingRecoveries] = useState<CrashRecovery[]>([]);
  const [draftSchedules, setDraftSchedules] = useState<DraftSchedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [saving, setSaving] = useState(false);
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true);
  const [showRecoveryDialog, setShowRecoveryDialog] = useState(false);
  const [selectedRecovery, setSelectedRecovery] = useState<CrashRecovery | null>(null);
  const [syncStatus, setSyncStatus] = useState<'synced' | 'syncing' | 'offline'>('synced');
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const tempIdRef = useRef<string>(
    formId || `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  );

  const fetchAutoSaves = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (formId) params.append('form_id', formId);
      else params.append('temp_id', tempIdRef.current);
      
      const response = await fetch(`/api/v1/features/autosave/builder/?${params}`);
      const data = await response.json();
      setAutoSaves(data.results || data);
    } catch (error) {
      console.error('Failed to fetch auto-saves:', error);
    }
  }, [formId]);

  const fetchPendingRecoveries = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/autosave/recovery/pending/`);
      const data = await response.json();
      setPendingRecoveries(data);
      
      // Show recovery dialog if there are pending recoveries
      if (data.length > 0) {
        setSelectedRecovery(data[0]);
        setShowRecoveryDialog(true);
      }
    } catch (error) {
      console.error('Failed to fetch pending recoveries:', error);
    }
  }, []);

  const fetchDraftSchedules = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/features/autosave/schedules/`);
      const data = await response.json();
      setDraftSchedules(data.results || data);
    } catch (error) {
      console.error('Failed to fetch draft schedules:', error);
    }
  }, []);

  useEffect(() => {
    const loadAll = async () => {
      setLoading(true);
      await Promise.all([
        fetchAutoSaves(),
        fetchPendingRecoveries(),
        fetchDraftSchedules(),
      ]);
      setLoading(false);
    };
    loadAll();
  }, [fetchAutoSaves, fetchPendingRecoveries, fetchDraftSchedules]);

  // Auto-save functionality
  const performAutoSave = useCallback(async () => {
    if (!currentSchema || !autoSaveEnabled) return;
    
    setSaving(true);
    setSyncStatus('syncing');
    
    try {
      const response = await fetch(`/api/v1/features/autosave/builder/save/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          form_id: formId || null,
          temp_id: formId ? null : tempIdRef.current,
          schema_json: currentSchema,
          settings_json: currentSettings || {},
          title: currentSchema?.title || 'Untitled Form',
          editor_state: {},
          browser_session_id: sessionStorage.getItem('browser_session_id') || '',
          device_info: {
            userAgent: navigator.userAgent,
            screen: { width: window.innerWidth, height: window.innerHeight },
          },
        }),
      });
      
      const data = await response.json();
      setLastSaved(new Date(data.saved_at));
      setSyncStatus('synced');
      fetchAutoSaves();
    } catch (error) {
      console.error('Auto-save failed:', error);
      setSyncStatus('offline');
    } finally {
      setSaving(false);
    }
  }, [currentSchema, currentSettings, formId, autoSaveEnabled, fetchAutoSaves]);

  // Set up auto-save interval
  useEffect(() => {
    if (autoSaveEnabled && currentSchema) {
      intervalRef.current = setInterval(performAutoSave, AUTOSAVE_INTERVAL);
    }
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [autoSaveEnabled, performAutoSave, currentSchema]);

  // Handle page visibility changes
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden && currentSchema) {
        performAutoSave();
      }
    };
    
    const handleBeforeUnload = () => {
      if (currentSchema) {
        // Synchronous save attempt
        navigator.sendBeacon(
          '/api/v1/features/autosave/builder/save/',
          JSON.stringify({
            form_id: formId,
            temp_id: tempIdRef.current,
            schema_json: currentSchema,
            settings_json: currentSettings,
          })
        );
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [currentSchema, currentSettings, formId, performAutoSave]);

  const recoverSession = async (recovery: CrashRecovery) => {
    try {
      const response = await fetch(`/api/v1/features/autosave/recovery/${recovery.id}/recover/`, {
        method: 'POST',
      });
      const data = await response.json();
      
      if (onRecover) {
        onRecover(data.schema_json, data.settings_json);
      }
      
      setShowRecoveryDialog(false);
      setPendingRecoveries(prev => prev.filter(r => r.id !== recovery.id));
    } catch (error) {
      console.error('Failed to recover session:', error);
    }
  };

  const dismissRecovery = async (recovery: CrashRecovery) => {
    try {
      await fetch(`/api/v1/features/autosave/recovery/${recovery.id}/dismiss/`, {
        method: 'POST',
      });
      
      setShowRecoveryDialog(false);
      setPendingRecoveries(prev => prev.filter(r => r.id !== recovery.id));
    } catch (error) {
      console.error('Failed to dismiss recovery:', error);
    }
  };

  const restoreAutoSave = async (autoSave: AutoSave) => {
    if (onRecover) {
      onRecover(autoSave.schema_json, autoSave.settings_json);
    }
  };

  const deleteAutoSave = async (autoSaveId: string) => {
    try {
      await fetch(`/api/v1/features/autosave/builder/${autoSaveId}/`, {
        method: 'DELETE',
      });
      setAutoSaves(prev => prev.filter(a => a.id !== autoSaveId));
    } catch (error) {
      console.error('Failed to delete auto-save:', error);
    }
  };

  const scheduleDraft = async (scheduledAt: string) => {
    if (!formId) return;
    
    try {
      await fetch(`/api/v1/features/autosave/schedules/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          form_id: formId,
          draft_schema: currentSchema,
          draft_settings: currentSettings,
          scheduled_at: scheduledAt,
        }),
      });
      fetchDraftSchedules();
    } catch (error) {
      console.error('Failed to schedule draft:', error);
    }
  };

  const cancelSchedule = async (scheduleId: string) => {
    try {
      await fetch(`/api/v1/features/autosave/schedules/${scheduleId}/cancel/`, {
        method: 'POST',
      });
      fetchDraftSchedules();
    } catch (error) {
      console.error('Failed to cancel schedule:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Recovery Dialog */}
      <Dialog open={showRecoveryDialog} onOpenChange={setShowRecoveryDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-yellow-500" />
              Unsaved Work Detected
            </DialogTitle>
            <DialogDescription>
              We found unsaved changes from a previous session. Would you like to recover them?
            </DialogDescription>
          </DialogHeader>
          
          {selectedRecovery && (
            <div className="space-y-4">
              <div className="p-4 bg-muted rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Reason</span>
                  <Badge variant="secondary">
                    {CRASH_REASONS[selectedRecovery.crash_reason as keyof typeof CRASH_REASONS]}
                  </Badge>
                </div>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-sm text-muted-foreground">Time</span>
                  <span className="text-sm">
                    {new Date(selectedRecovery.created_at).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          )}
          
          <DialogFooter>
            <Button variant="outline" onClick={() => selectedRecovery && dismissRecovery(selectedRecovery)}>
              Discard
            </Button>
            <Button onClick={() => selectedRecovery && recoverSession(selectedRecovery)}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Recover
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Header with sync status */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Save className="h-6 w-6" />
            Auto-Save & Recovery
          </h2>
          <p className="text-muted-foreground">Never lose your work</p>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Sync Status */}
          <div className="flex items-center gap-2">
            {syncStatus === 'synced' && (
              <>
                <Cloud className="h-4 w-4 text-green-500" />
                <span className="text-sm text-green-600">Synced</span>
              </>
            )}
            {syncStatus === 'syncing' && (
              <>
                <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />
                <span className="text-sm text-blue-600">Syncing...</span>
              </>
            )}
            {syncStatus === 'offline' && (
              <>
                <CloudOff className="h-4 w-4 text-yellow-500" />
                <span className="text-sm text-yellow-600">Offline</span>
              </>
            )}
          </div>
          
          {/* Last saved time */}
          {lastSaved && (
            <span className="text-sm text-muted-foreground">
              Last saved: {lastSaved.toLocaleTimeString()}
            </span>
          )}
          
          {/* Manual save button */}
          <Button
            variant="outline"
            size="sm"
            onClick={performAutoSave}
            disabled={saving}
          >
            {saving ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            Save Now
          </Button>
        </div>
      </div>

      {/* Auto-save settings */}
      <Card>
        <CardHeader>
          <CardTitle>Auto-Save Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Enable Auto-Save</p>
              <p className="text-sm text-muted-foreground">
                Automatically save every {AUTOSAVE_INTERVAL / 1000} seconds
              </p>
            </div>
            <Switch
              checked={autoSaveEnabled}
              onCheckedChange={setAutoSaveEnabled}
            />
          </div>
        </CardContent>
      </Card>

      {/* Pending recoveries */}
      {pendingRecoveries.length > 0 && (
        <Card className="border-yellow-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-yellow-600">
              <AlertTriangle className="h-5 w-5" />
              Pending Recoveries
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {pendingRecoveries.map((recovery) => (
                <div key={recovery.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">Unsaved Session</p>
                    <p className="text-sm text-muted-foreground">
                      {CRASH_REASONS[recovery.crash_reason as keyof typeof CRASH_REASONS]} •{' '}
                      {new Date(recovery.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={() => dismissRecovery(recovery)}>
                      Discard
                    </Button>
                    <Button size="sm" onClick={() => recoverSession(recovery)}>
                      Recover
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Auto-save history */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            Save History
          </CardTitle>
          <CardDescription>Recent auto-saved versions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {autoSaves.slice(0, 10).map((autoSave) => (
              <div key={autoSave.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-full bg-muted">
                    <FileText className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="font-medium">{autoSave.title || 'Untitled'}</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(autoSave.last_saved_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {autoSave.is_recovered && (
                    <Badge variant="secondary">Recovered</Badge>
                  )}
                  <Button size="sm" variant="outline" onClick={() => restoreAutoSave(autoSave)}>
                    <RotateCcw className="h-4 w-4 mr-1" />
                    Restore
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => deleteAutoSave(autoSave.id)}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
            {autoSaves.length === 0 && (
              <p className="text-center text-muted-foreground py-4">
                No auto-saves yet
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Scheduled publications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Scheduled Publications
          </CardTitle>
          <CardDescription>Drafts scheduled to be published</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {draftSchedules.filter(d => d.status === 'pending').map((schedule) => (
              <div key={schedule.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-full bg-blue-100 text-blue-600">
                    <Clock className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="font-medium">{schedule.form_title}</p>
                    <p className="text-sm text-muted-foreground">
                      Scheduled for: {new Date(schedule.scheduled_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <Button size="sm" variant="outline" onClick={() => cancelSchedule(schedule.id)}>
                  <X className="h-4 w-4 mr-1" />
                  Cancel
                </Button>
              </div>
            ))}
            {draftSchedules.filter(d => d.status === 'pending').length === 0 && (
              <p className="text-center text-muted-foreground py-4">
                No scheduled publications
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default AutoSaveRecovery;
