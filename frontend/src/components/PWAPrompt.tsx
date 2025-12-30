'use client';

import { useEffect, useState } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { WifiOff, Wifi, Download } from 'lucide-react';
import { setupOfflineDetection, showInstallPrompt, isStandalone } from '@/lib/pwa';

export function PWAPrompt() {
  const [showInstall, setShowInstall] = useState(false);
  const [isOffline, setIsOffline] = useState(false);
  const [isInstalled, setIsInstalled] = useState(isStandalone());

  useEffect(() => {
    // Setup offline detection
    setupOfflineDetection((online) => {
      setIsOffline(!online);
    });

    // Check if installable
    let deferredPrompt: any;
    const handler = (e: Event) => {
      e.preventDefault();
      deferredPrompt = e;
      if (!isStandalone()) {
        setShowInstall(true);
      }
    };

    window.addEventListener('beforeinstallprompt', handler);

    return () => {
      window.removeEventListener('beforeinstallprompt', handler);
    };
  }, []);

  const handleInstallClick = async () => {
    const installed = await showInstallPrompt();
    if (installed) {
      setShowInstall(false);
      setIsInstalled(true);
    }
  };

  return (
    <>
      {/* Offline indicator */}
      {isOffline && (
        <Alert variant="destructive" className="fixed top-4 right-4 max-w-md z-50">
          <WifiOff className="h-4 w-4" />
          <AlertTitle>You&apos;re offline</AlertTitle>
          <AlertDescription>
            Some features may not be available. Your changes will be synced when you&apos;re back online.
          </AlertDescription>
        </Alert>
      )}

      {/* Online indicator (brief show) */}
      {!isOffline && (
        <div className="fixed top-4 right-4 max-w-md z-50 pointer-events-none">
          {/* This could show briefly when coming back online */}
        </div>
      )}

      {/* Install prompt */}
      {showInstall && !isInstalled && (
        <Alert className="fixed bottom-4 right-4 max-w-md z-50">
          <Download className="h-4 w-4" />
          <AlertTitle>Install SmartFormBuilder</AlertTitle>
          <AlertDescription>
            Install our app for a better experience with offline support and faster performance.
          </AlertDescription>
          <div className="flex gap-2 mt-3">
            <Button size="sm" onClick={handleInstallClick}>
              Install Now
            </Button>
            <Button size="sm" variant="outline" onClick={() => setShowInstall(false)}>
              Maybe Later
            </Button>
          </div>
        </Alert>
      )}
    </>
  );
}
