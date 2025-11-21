'use client';

import { useEffect } from 'react';
import { registerServiceWorker } from '@/lib/pwa';

export function PWAInit() {
  useEffect(() => {
    // Register service worker
    registerServiceWorker();

    // Log PWA installation
    window.addEventListener('appinstalled', () => {
      console.log('PWA installed successfully');
    });
  }, []);

  return null;
}
