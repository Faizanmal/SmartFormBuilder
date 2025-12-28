'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  plan: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export function useAuth(requireAuth = true) {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setState({ user: null, isAuthenticated: false, isLoading: false });
    router.push('/login');
  }, [router]);

  const checkAuth = useCallback(async function checkAuthImpl() {
    if (typeof window === 'undefined') return;
    
    const accessToken = localStorage.getItem('access_token');
    
    if (!accessToken) {
      setState({ user: null, isAuthenticated: false, isLoading: false });
      if (requireAuth) {
        router.push('/login');
      }
      return;
    }

    try {
      // Try to fetch user profile
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/users/me/`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (response.ok) {
        const user = await response.json();
        setState({ user, isAuthenticated: true, isLoading: false });
      } else if (response.status === 401) {
        // Try to refresh token
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const refreshResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/auth/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken }),
          });

          if (refreshResponse.ok) {
            const { access } = await refreshResponse.json();
            localStorage.setItem('access_token', access);
            // Retry fetching user
            checkAuthImpl();
            return;
          }
        }
        
        // Token refresh failed, logout
        logout();
        if (requireAuth) {
          router.push('/login');
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setState({ user: null, isAuthenticated: false, isLoading: false });
      if (requireAuth) {
        router.push('/login');
      }
    }
  }, [logout, requireAuth, router]);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = useCallback(async (email: string, password: string) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const { access, refresh } = await response.json();
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    
    await checkAuth();
    return true;
  }, [checkAuth]);

  const register = useCallback(async (data: {
    email: string;
    username: string;
    password: string;
    password2: string;
    first_name?: string;
    last_name?: string;
  }) => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/users/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw error;
    }

    const result = await response.json();
    const { tokens } = result;
    
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    
    await checkAuth();
    return result;
  }, [checkAuth]);

  return {
    ...state,
    login,
    logout,
    register,
    checkAuth,
  };
}

export default useAuth;
