'use client';

import { useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { WifiOff, RefreshCw, Home } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function OfflinePage() {
  const router = useRouter();

  useEffect(() => {
    // Listen for online event
    const handleOnline = () => {
      router.push('/dashboard');
    };

    window.addEventListener('online', handleOnline);
    return () => window.removeEventListener('online', handleOnline);
  }, [router]);

  const handleRetry = () => {
    if (navigator.onLine) {
      router.push('/dashboard');
    } else {
      window.location.reload();
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="max-w-md w-full">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <div className="rounded-full bg-muted p-4">
              <WifiOff className="h-12 w-12 text-muted-foreground" />
            </div>
          </div>
          <CardTitle className="text-2xl">You're Offline</CardTitle>
          <CardDescription>
            It looks like you've lost your internet connection. Don't worry, your work is saved locally.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-muted rounded-lg p-4 text-sm space-y-2">
            <p className="font-semibold">What you can do:</p>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground">
              <li>Fill out forms (they'll sync when you're online)</li>
              <li>View cached forms and data</li>
              <li>Access recently viewed pages</li>
            </ul>
          </div>

          <div className="flex gap-2">
            <Button onClick={handleRetry} className="flex-1">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry Connection
            </Button>
            <Button variant="outline" onClick={() => router.push('/')}>
              <Home className="h-4 w-4 mr-2" />
              Home
            </Button>
          </div>

          <p className="text-xs text-center text-muted-foreground">
            Your changes will automatically sync when your connection is restored.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
