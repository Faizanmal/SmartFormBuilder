'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { 
  useOfflineSyncConfig,
  useUpdateOfflineSyncConfig,
  useBiometricConfig,
  useUpdateBiometricConfig,
  useGeolocationConfig,
  useMobilePaymentConfig,
  useUpdateMobilePaymentConfig,
  usePushNotificationConfig
} from '@/hooks/use-emerging-features';
import { 
  Wifi, WifiOff, Fingerprint, MapPin, 
  CreditCard, Bell, Smartphone, RefreshCw,
  CheckCircle2, AlertCircle, Clock, Database
} from 'lucide-react';

interface MobilePWAControllerProps {
  formId: string;
}

export function MobilePWAController({ formId }: MobilePWAControllerProps) {
  const { data: offlineSync } = useOfflineSyncConfig(formId);
  const updateOfflineSync = useUpdateOfflineSyncConfig();

  const { data: biometric } = useBiometricConfig(formId);
  const updateBiometric = useUpdateBiometricConfig();

  const { data: geolocation } = useGeolocationConfig(formId);
  const { data: mobilePayment } = useMobilePaymentConfig(formId);
  const updateMobilePayment = useUpdateMobilePaymentConfig();
  const { data: pushNotifications } = usePushNotificationConfig(formId);

  return (
    <div className="space-y-6">
      <Tabs defaultValue="offline" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="offline">Offline Sync</TabsTrigger>
          <TabsTrigger value="biometric">Biometric</TabsTrigger>
          <TabsTrigger value="geolocation">Geolocation</TabsTrigger>
          <TabsTrigger value="payments">Payments</TabsTrigger>
          <TabsTrigger value="notifications">Push</TabsTrigger>
        </TabsList>

        {/* Offline Sync Tab */}
        <TabsContent value="offline" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <WifiOff className="h-5 w-5 text-blue-500" />
                Offline Sync Configuration
              </CardTitle>
              <CardDescription>
                Enable forms to work without internet connection
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="offline-enabled">Enable Offline Mode</Label>
                <Switch
                  id="offline-enabled"
                  checked={offlineSync?.is_enabled}
                  onCheckedChange={(checked) => {
                    updateOfflineSync.mutate({
                      formId,
                      config: { is_enabled: checked }
                    });
                  }}
                />
              </div>

              {offlineSync?.is_enabled && (
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="sync-strategy">Sync Strategy</Label>
                    <Select
                      value={offlineSync.sync_strategy}
                      onValueChange={(value) => {
                        updateOfflineSync.mutate({
                          formId,
                          config: { sync_strategy: value }
                        });
                      }}
                    >
                      <SelectTrigger id="sync-strategy">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="manual">Manual - User triggered</SelectItem>
                        <SelectItem value="automatic">Automatic - When online</SelectItem>
                        <SelectItem value="scheduled">Scheduled - Periodic sync</SelectItem>
                        <SelectItem value="smart">Smart - Optimal timing</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="max-storage">Max Storage (MB)</Label>
                      <Input
                        id="max-storage"
                        type="number"
                        value={offlineSync.max_storage_mb}
                        onChange={(e) => {
                          updateOfflineSync.mutate({
                            formId,
                            config: { max_storage_mb: parseInt(e.target.value) }
                          });
                        }}
                      />
                    </div>

                    <div>
                      <Label htmlFor="sync-interval">Sync Interval (min)</Label>
                      <Input
                        id="sync-interval"
                        type="number"
                        value={offlineSync.sync_interval_minutes}
                        onChange={(e) => {
                          updateOfflineSync.mutate({
                            formId,
                            config: { sync_interval_minutes: parseInt(e.target.value) }
                          });
                        }}
                      />
                    </div>
                  </div>

                  <div className="p-4 border rounded-lg bg-blue-50/50 space-y-2">
                    <div className="flex items-center gap-2">
                      <Database className="h-4 w-4 text-blue-600" />
                      <span className="font-medium text-sm">Conflict Resolution</span>
                    </div>
                    <p className="text-sm text-muted-foreground capitalize">
                      Strategy: {offlineSync.conflict_resolution}
                    </p>
                    <div className="flex items-center gap-2">
                      {offlineSync.auto_retry && (
                        <>
                          <CheckCircle2 className="h-4 w-4 text-green-600" />
                          <span className="text-xs">Auto-retry failed syncs</span>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <div className="flex items-center gap-2">
                      <RefreshCw className="h-4 w-4" />
                      <span className="text-sm">Queue Management</span>
                    </div>
                    <Button size="sm" variant="outline">
                      View Queue
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Biometric Tab */}
        <TabsContent value="biometric" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Fingerprint className="h-5 w-5 text-purple-500" />
                Biometric Authentication
              </CardTitle>
              <CardDescription>
                Secure form access with fingerprint or face recognition
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="biometric-enabled">Enable Biometric Auth</Label>
                <Switch
                  id="biometric-enabled"
                  checked={biometric?.is_enabled}
                  onCheckedChange={(checked) => {
                    updateBiometric.mutate({
                      formId,
                      config: { is_enabled: checked }
                    });
                  }}
                />
              </div>

              {biometric?.is_enabled && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <Fingerprint className="h-4 w-4 text-purple-500" />
                        <span className="text-sm">Touch ID</span>
                      </div>
                      {biometric.allowed_types.includes('fingerprint') ? (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-gray-400" />
                      )}
                    </div>

                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <Smartphone className="h-4 w-4 text-purple-500" />
                        <span className="text-sm">Face ID</span>
                      </div>
                      {biometric.allowed_types.includes('face') ? (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-gray-400" />
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Authentication Requirements</Label>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between p-2 bg-muted rounded">
                        <span className="text-sm">Require on form open</span>
                        <Switch checked={biometric.require_on_open} />
                      </div>
                      <div className="flex items-center justify-between p-2 bg-muted rounded">
                        <span className="text-sm">Require on submission</span>
                        <Switch checked={biometric.require_on_submit} />
                      </div>
                      <div className="flex items-center justify-between p-2 bg-muted rounded">
                        <span className="text-sm">Allow fallback PIN</span>
                        <Switch checked={biometric.fallback_to_pin} />
                      </div>
                    </div>
                  </div>

                  <div className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Session timeout</span>
                      <Badge variant="outline">{biometric.session_timeout_minutes} min</Badge>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Geolocation Tab */}
        <TabsContent value="geolocation" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5 text-red-500" />
                Geolocation & Geofencing
              </CardTitle>
              <CardDescription>
                Location-based form access and data collection
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {geolocation && (
                <>
                  <div className="flex items-center justify-between">
                    <Label>Geolocation Status</Label>
                    <Badge variant={geolocation.is_enabled ? 'default' : 'secondary'}>
                      {geolocation.is_enabled ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <span className="text-sm">Auto-capture location</span>
                      <Switch checked={geolocation.auto_capture} />
                    </div>

                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <span className="text-sm">Geofencing enabled</span>
                      <Switch checked={geolocation.geofencing_enabled} />
                    </div>
                  </div>

                  {geolocation.geofencing_enabled && geolocation.allowed_zones.length > 0 && (
                    <div className="space-y-2">
                      <Label>Allowed Zones</Label>
                      <div className="space-y-2">
                        {(geolocation.allowed_zones as unknown as { name: string; latitude: number; longitude: number; radius: number }[]).map((zone, index: number) => (
                          <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                            <div>
                              <p className="font-medium text-sm">{zone.name}</p>
                              <p className="text-xs text-muted-foreground">
                                {zone.latitude}, {zone.longitude} • {zone.radius}m radius
                              </p>
                            </div>
                            <MapPin className="h-4 w-4 text-red-500" />
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm">
                    <div className="flex items-center gap-2 mb-1">
                      <AlertCircle className="h-4 w-4 text-yellow-600" />
                      <span className="font-medium">Accuracy Required</span>
                    </div>
                    <p className="text-muted-foreground capitalize">
                      {geolocation.accuracy_required} precision
                    </p>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Payments Tab */}
        <TabsContent value="payments" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CreditCard className="h-5 w-5 text-green-500" />
                Mobile Payments
              </CardTitle>
              <CardDescription>
                Apple Pay, Google Pay, and in-app purchase integration
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="payment-enabled">Enable Mobile Payments</Label>
                <Switch
                  id="payment-enabled"
                  checked={mobilePayment?.is_enabled}
                  onCheckedChange={(checked) => {
                    updateMobilePayment.mutate({
                      formId,
                      config: { is_enabled: checked }
                    });
                  }}
                />
              </div>

              {mobilePayment?.is_enabled && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <CreditCard className="h-4 w-4" />
                        <span className="text-sm">Apple Pay</span>
                      </div>
                      {mobilePayment.providers.includes('apple_pay') ? (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-gray-400" />
                      )}
                    </div>

                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <Smartphone className="h-4 w-4" />
                        <span className="text-sm">Google Pay</span>
                      </div>
                      {mobilePayment.providers.includes('google_pay') ? (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-gray-400" />
                      )}
                    </div>

                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <CreditCard className="h-4 w-4" />
                        <span className="text-sm">Samsung Pay</span>
                      </div>
                      {mobilePayment.providers.includes('samsung_pay') ? (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-gray-400" />
                      )}
                    </div>

                    <div className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-2">
                        <Smartphone className="h-4 w-4" />
                        <span className="text-sm">In-App Purchase</span>
                      </div>
                      {mobilePayment.providers.includes('in_app_purchase') ? (
                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-gray-400" />
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Merchant Configuration</Label>
                    <div className="p-3 border rounded-lg space-y-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Merchant ID</span>
                        <code className="text-xs bg-muted px-2 py-1 rounded">
                          {mobilePayment.merchant_id}
                        </code>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-muted-foreground">Currency</span>
                        <Badge variant="outline">{mobilePayment.currency}</Badge>
                      </div>
                      {mobilePayment.test_mode && (
                        <div className="flex items-center gap-2 text-orange-600">
                          <AlertCircle className="h-4 w-4" />
                          <span>Test Mode Active</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <span className="text-sm">Allow saved payment methods</span>
                    <Switch checked={mobilePayment.allow_saved_cards} />
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Push Notifications Tab */}
        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-indigo-500" />
                Push Notifications
              </CardTitle>
              <CardDescription>
                Engage users with timely mobile notifications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {pushNotifications && (
                <>
                  <div className="flex items-center justify-between">
                    <Label>Push Notifications</Label>
                    <Badge variant={pushNotifications.is_enabled ? 'default' : 'secondary'}>
                      {pushNotifications.is_enabled ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>

                  <div className="space-y-2">
                    <Label>Notification Types</Label>
                    <div className="grid grid-cols-2 gap-2">
                      {pushNotifications.notification_types.map((type: string) => (
                        <div key={type} className="flex items-center gap-2 p-2 border rounded">
                          <Bell className="h-3 w-3" />
                          <span className="text-xs capitalize">{type.replace(/_/g, ' ')}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="p-3 border rounded-lg">
                      <p className="text-muted-foreground mb-1">Default Priority</p>
                      <Badge variant="outline" className="capitalize">
                        {pushNotifications.default_priority}
                      </Badge>
                    </div>

                    <div className="p-3 border rounded-lg">
                      <p className="text-muted-foreground mb-1">TTL</p>
                      <Badge variant="outline">
                        {pushNotifications.ttl_seconds / 3600}h
                      </Badge>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-2 bg-muted rounded">
                      <span className="text-sm">Badge updates</span>
                      <Switch checked={pushNotifications.badge_enabled} />
                    </div>
                    <div className="flex items-center justify-between p-2 bg-muted rounded">
                      <span className="text-sm">Sound enabled</span>
                      <Switch checked={pushNotifications.sound_enabled} />
                    </div>
                    <div className="flex items-center justify-between p-2 bg-muted rounded">
                      <span className="text-sm">Vibration</span>
                      <Switch checked={pushNotifications.vibrate_enabled} />
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
