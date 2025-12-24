"use client";

import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import useAuth from "@/hooks/useAuth";

export default function FormEditPage() {
  const params = useParams();
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth(true);
  const formId = params.id as string;

  useEffect(() => {
    if (isAuthenticated && formId) {
      // Redirect to the new builder page
      router.replace(`/forms/${formId}/builder`);
    }
  }, [isAuthenticated, formId, router]);

  if (authLoading || !isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
        <p className="mt-4 text-muted-foreground">Redirecting to builder...</p>
      </div>
    </div>
  );
}
