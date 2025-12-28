'use client';

import { useEffect, useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Bell, BellOff, Smartphone, Download, Wifi } from 'lucide-react';
import {
  requestNotificationPermission,
  subscribeToPushNotifications,
  unsubscribeFromPushNotifications,
  checkOnlineStatus,
  OfflineStorage,
} from '@/lib/pwa';
import { toast } from '@/hooks/use-toast';

export function OfflineSettings() {
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);
  const [smsEnabled, setSmsEnabled] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [isOnline, setIsOnline] = useState(true);
  const [pendingSubmissions, setPendingSubmissions] = useState<Array<{ id: number; data: Record<string, unknown>; timestamp: string }>>([]);
  const [cacheSize, setCacheSize] = useState(0);

  const checkInitialState = useCallback(async () => {
    // Check notification permission
    if ('Notification' in window) {
      setNotificationsEnabled(Notification.permission === 'granted');
    }

    // Check online status
    const online = await checkOnlineStatus();
    setIsOnline(online);

    // Load SMS settings from API
    loadSMSSettings();
  }, []);

  async function loadSMSSettings() {
    try {
      const response = await fetch('/api/users/sms-settings');
      if (response.ok) {
        const data = await response.json();
        setSmsEnabled(data.enabled);
        setPhoneNumber(data.phone_number || '');
      }
    } catch (error) {
      console.error('Failed to load SMS settings:', error);
    }
  }

  async function checkPendingSubmissions() {
    const storage = new OfflineStorage();
    await storage.init();
    const submissions = await storage.getPendingSubmissions();
    setPendingSubmissions(submissions);
  }

  async function checkCacheSize() {
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      const estimate = await navigator.storage.estimate();
      const usage = estimate.usage || 0;
      setCacheSize(Math.round(usage / 1024 / 1024 * 10) / 10); // MB
    }
  }

  useEffect(() => {
    checkInitialState();
    checkPendingSubmissions();
    checkCacheSize();
  }, [checkInitialState]);

  const handleNotificationToggle = async (enabled: boolean) => {
    if (enabled) {
      const permission = await requestNotificationPermission();
      if (permission === 'granted') {
        await subscribeToPushNotifications();
        setNotificationsEnabled(true);
        toast({
          title: 'Notifications Enabled',
          description: 'You will now receive push notifications',
        });
      } else {
        toast({
          title: 'Permission Denied',
          description: 'Please enable notifications in your browser settings',
          variant: 'destructive',
        });
      }
    } else {
      await unsubscribeFromPushNotifications();
      setNotificationsEnabled(false);
      toast({
        title: 'Notifications Disabled',
        description: 'You will no longer receive push notifications',
      });
    }
  };

  const handleSMSToggle = async (enabled: boolean) => {
    try {
      const response = await fetch('/api/users/sms-settings', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled, phone_number: phoneNumber }),
      });

      if (response.ok) {
        setSmsEnabled(enabled);
        toast({
          title: enabled ? 'SMS Enabled' : 'SMS Disabled',
          description: enabled
            ? 'You will receive SMS notifications'
            : 'SMS notifications disabled',
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update SMS settings',
        variant: 'destructive',
      });
    }
  };

  const handlePhoneNumberSave = async () => {
    try {
      const response = await fetch('/api/users/sms-settings', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phoneNumber }),
      });

      if (response.ok) {
        toast({
          title: 'Phone Number Updated',
          description: 'Your phone number has been saved',
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update phone number',
        variant: 'destructive',
      });
    }
  };

  const syncPendingSubmissions = async () => {
    const storage = new OfflineStorage();
    await storage.init();
    const submissions = await storage.getPendingSubmissions();

    let syncedCount = 0;
    for (const submission of submissions) {
      try {
        const response = await fetch('/api/forms/submissions/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(submission.data),
        });

        if (response.ok) {
          await storage.removeSubmission(submission.id);
          syncedCount++;
        }
      } catch (error) {
        console.error('Sync failed for submission:', submission.id);
      }
    }

    await checkPendingSubmissions();
    toast({
      title: 'Sync Complete',
      description: `${syncedCount} submission(s) synced successfully`,
    });
  };

  const clearCache = async () => {
    if ('caches' in window) {
      const cacheNames = await caches.keys();
      await Promise.all(cacheNames.map((name) => caches.delete(name)));
      await checkCacheSize();
      toast({
        title: 'Cache Cleared',
        description: 'All cached data has been removed',
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Online Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Connection Status</CardTitle>
              <CardDescription>Your current network status</CardDescription>
            </div>
            <Badge variant={isOnline ? 'default' : 'destructive'}>
              {isOnline ? (
                <>
                  <Wifi className="h-3 w-3 mr-1" /> Online
                </>
              ) : (
                <>
                  <BellOff className="h-3 w-3 mr-1" /> Offline
                </>
              )}
            </Badge>
          </div>
        </CardHeader>
      </Card>

      {/* Push Notifications */}
      <Card>
        <CardHeader>
          <CardTitle>Push Notifications</CardTitle>
          <CardDescription>
            Receive instant notifications for form submissions and updates
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bell className="h-4 w-4" />
              <Label htmlFor="push-notifications">Enable Push Notifications</Label>
            </div>
            <Switch
              id="push-notifications"
              checked={notificationsEnabled}
              onCheckedChange={handleNotificationToggle}
            />
          </div>
        </CardContent>
      </Card>

      {/* SMS Notifications */}
      <Card>
        <CardHeader>
          <CardTitle>SMS Notifications</CardTitle>
          <CardDescription>
            Get SMS alerts for important form events
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Smartphone className="h-4 w-4" />
              <Label htmlFor="sms-notifications">Enable SMS Notifications</Label>
            </div>
            <Switch
              id="sms-notifications"
              checked={smsEnabled}
              onCheckedChange={handleSMSToggle}
            />
          </div>

          {smsEnabled && (
            <div className="space-y-2">
              <Label htmlFor="phone-number">Phone Number</Label>
              <div className="flex gap-2">
                <Input
                  id="phone-number"
                  type="tel"
                  placeholder="+1 (555) 123-4567"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                />
                <Button onClick={handlePhoneNumberSave}>Save</Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Enter your phone number in international format
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Offline Data */}
      <Card>
        <CardHeader>
          <CardTitle>Offline Data</CardTitle>
          <CardDescription>
            Manage your offline form submissions and cached data
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Pending Submissions</p>
              <p className="text-xs text-muted-foreground">
                Forms waiting to be synced
              </p>
            </div>
            <Badge variant="secondary">{pendingSubmissions.length}</Badge>
          </div>

          {pendingSubmissions.length > 0 && (
            <Button onClick={syncPendingSubmissions} className="w-full">
              <Download className="h-4 w-4 mr-2" />
              Sync Now
            </Button>
          )}

          <div className="flex items-center justify-between pt-4 border-t">
            <div>
              <p className="text-sm font-medium">Cache Size</p>
              <p className="text-xs text-muted-foreground">
                Stored offline data
              </p>
            </div>
            <Badge variant="outline">{cacheSize} MB</Badge>
          </div>

          <Button variant="outline" onClick={clearCache} className="w-full">
            Clear Cache
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
