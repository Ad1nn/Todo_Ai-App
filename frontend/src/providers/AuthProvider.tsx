'use client';

import { createContext, useContext, useCallback, useEffect, useState, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import type { User, UserCreate, UserLogin, UserUpdate } from '@/lib/types';
import * as authLib from '@/lib/auth';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  register: (data: UserCreate) => Promise<User>;
  login: (data: UserLogin) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (data: UserUpdate) => Promise<User>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch user on mount
  useEffect(() => {
    const fetchUser = async () => {
      const token = authLib.getToken();

      if (!token) {
        setUser(null);
        setIsLoading(false);
        return;
      }

      try {
        const userData = await authLib.getCurrentUser();
        setUser(userData);
      } catch {
        authLib.removeToken();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUser();
  }, []);

  const register = useCallback(async (data: UserCreate): Promise<User> => {
    const newUser = await authLib.register(data);
    return newUser;
  }, []);

  const login = useCallback(async (data: UserLogin): Promise<void> => {
    await authLib.login(data);
    const userData = await authLib.getCurrentUser();
    setUser(userData);
    router.push('/tasks');
  }, [router]);

  const logout = useCallback(async (): Promise<void> => {
    await authLib.logout();
    setUser(null);
    router.push('/login');
  }, [router]);

  const updateProfile = useCallback(async (data: UserUpdate): Promise<User> => {
    const updatedUser = await authLib.updateProfile(data);
    setUser(updatedUser);
    return updatedUser;
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token: authLib.getToken(),
        isAuthenticated: !!user,
        isLoading,
        register,
        login,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
