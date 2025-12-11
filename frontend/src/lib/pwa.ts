/**
 * PWA utilities for service worker registration and offline support
 */

export function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', async () => {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js');
        console.log('Service Worker registered:', registration);

        // Check for updates periodically
        setInterval(() => {
          registration.update();
        }, 60 * 60 * 1000); // Every hour

        // Handle updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                // New service worker available
                showUpdateNotification();
              }
            });
          }
        });
      } catch (error) {
        console.error('Service Worker registration failed:', error);
      }
    });
  }
}

export function unregisterServiceWorker() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then((registrations) => {
      for (const registration of registrations) {
        registration.unregister();
      }
    });
  }
}

export function showUpdateNotification() {
  const updateBanner = document.createElement('div');
  updateBanner.innerHTML = `
    <div style="position: fixed; bottom: 20px; right: 20px; background: #667eea; color: white; padding: 16px 24px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 9999;">
      <p style="margin: 0 0 12px 0; font-weight: 600;">New version available!</p>
      <button id="update-app-btn" style="background: white; color: #667eea; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: 600;">
        Update Now
      </button>
      <button id="dismiss-update-btn" style="background: transparent; color: white; border: 1px solid white; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin-left: 8px;">
        Later
      </button>
    </div>
  `;
  document.body.appendChild(updateBanner);

  document.getElementById('update-app-btn')?.addEventListener('click', () => {
    window.location.reload();
  });

  document.getElementById('dismiss-update-btn')?.addEventListener('click', () => {
    updateBanner.remove();
  });
}

export async function checkOnlineStatus(): Promise<boolean> {
  if (!navigator.onLine) {
    return false;
  }

  try {
    const response = await fetch('/api/health', { method: 'HEAD' });
    return response.ok;
  } catch {
    return false;
  }
}

export function setupOfflineDetection(callback: (isOnline: boolean) => void) {
  window.addEventListener('online', () => callback(true));
  window.addEventListener('offline', () => callback(false));

  // Initial check
  checkOnlineStatus().then(callback);
}

export async function requestNotificationPermission(): Promise<NotificationPermission> {
  if (!('Notification' in window)) {
    console.warn('Notifications not supported');
    return 'denied';
  }

  if (Notification.permission === 'granted') {
    return 'granted';
  }

  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission();
    return permission;
  }

  return Notification.permission;
}

export async function subscribeToPushNotifications(): Promise<PushSubscription | null> {
  try {
    const registration = await navigator.serviceWorker.ready;
    
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY,
    });

    // Send subscription to backend
    await fetch('/api/push/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(subscription),
    });

    return subscription;
  } catch (error) {
    console.error('Push subscription failed:', error);
    return null;
  }
}

export async function unsubscribeFromPushNotifications(): Promise<boolean> {
  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    
    if (subscription) {
      await subscription.unsubscribe();
      
      // Notify backend
      await fetch('/api/push/unsubscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ endpoint: subscription.endpoint }),
      });
      
      return true;
    }
    return false;
  } catch (error) {
    console.error('Push unsubscription failed:', error);
    return false;
  }
}

type BeforeInstallPromptEvent = Event & {
  prompt?: () => void | Promise<void>;
  userChoice?: Promise<{ outcome: 'accepted' | 'dismissed' }>;
};

export function checkInstallability(): Promise<boolean> {
  return new Promise((resolve) => {
    let deferredPrompt: BeforeInstallPromptEvent | null = null;

    window.addEventListener('beforeinstallprompt', (e: BeforeInstallPromptEvent) => {
      e.preventDefault();
      deferredPrompt = e;
      resolve(true);
    });

    // If event doesn't fire in 1 second, app is not installable
    setTimeout(() => resolve(false), 1000);
  });
}

export function showInstallPrompt(): Promise<boolean> {
  return new Promise((resolve) => {
    let deferredPrompt: BeforeInstallPromptEvent | null = null;

    const handler = (e: BeforeInstallPromptEvent) => {
      e.preventDefault();
      deferredPrompt = e;

      deferredPrompt.prompt?.();

      deferredPrompt.userChoice?.then((choiceResult: { outcome: 'accepted' | 'dismissed' }) => {
        if (choiceResult.outcome === 'accepted') {
          console.log('User accepted install prompt');
          resolve(true);
        } else {
          console.log('User dismissed install prompt');
          resolve(false);
        }
        deferredPrompt = null;
      });
    };

    window.addEventListener('beforeinstallprompt', handler);
  });
}

export function isStandalone(): boolean {
  return window.matchMedia('(display-mode: standalone)').matches ||
         ((window.navigator as Navigator & { standalone?: boolean }).standalone === true);
}

// IndexedDB for offline data
export class OfflineStorage {
  private db: IDBDatabase | null = null;
  private dbName = 'FormBuilderDB';
  private version = 1;

  async init() {
    return new Promise<void>((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

          request.onupgradeneeded = (event: IDBVersionChangeEvent) => {
        const db = (event.target as IDBOpenDBRequest).result;
        
        if (!db.objectStoreNames.contains('pendingSubmissions')) {
          db.createObjectStore('pendingSubmissions', { keyPath: 'id', autoIncrement: true });
        }
        
        if (!db.objectStoreNames.contains('forms')) {
          db.createObjectStore('forms', { keyPath: 'id' });
        }
      };
    });
  }

  async saveSubmission(formId: string, data: Record<string, unknown>): Promise<number> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['pendingSubmissions'], 'readwrite');
      const store = transaction.objectStore('pendingSubmissions');
      
      const request = store.add({
        formId,
        data,
        timestamp: new Date().toISOString(),
      });

      request.onsuccess = () => resolve(request.result as number);
      request.onerror = () => reject(request.error);
    });
  }

  async getPendingSubmissions(): Promise<Array<{ id: number; data: Record<string, unknown>; timestamp: string }>> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['pendingSubmissions'], 'readonly');
      const store = transaction.objectStore('pendingSubmissions');
      const request = store.getAll();

      request.onsuccess = () => resolve(request.result as Array<{ id: number; data: Record<string, unknown>; timestamp: string }>);
      request.onerror = () => reject(request.error);
    });
  }

  async removeSubmission(id: number): Promise<void> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['pendingSubmissions'], 'readwrite');
      const store = transaction.objectStore('pendingSubmissions');
      const request = store.delete(id);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async saveForm(form: Record<string, unknown>): Promise<void> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['forms'], 'readwrite');
      const store = transaction.objectStore('forms');
      const request = store.put(form);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  async getForm(id: string): Promise<Record<string, unknown> | undefined> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['forms'], 'readonly');
      const store = transaction.objectStore('forms');
      const request = store.get(id);

      request.onsuccess = () => resolve(request.result as Record<string, unknown> | undefined);
      request.onerror = () => reject(request.error);
    });
  }
}
