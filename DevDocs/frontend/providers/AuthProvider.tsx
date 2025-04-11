import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../models/types';
import { Session, AuthError } from '@supabase/supabase-js';
import { useRouter } from 'next/router';
import getSupabaseClient from '../lib/supabaseClient';

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  error: string | null;
  signIn: (email: string, password: string) => Promise<{ error: AuthError | null }>;
  signUp: (email: string, password: string, fullName: string) => Promise<{ error: AuthError | null }>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<{ error: AuthError | null }>;
  updatePassword: (password: string) => Promise<{ error: AuthError | null }>;
  updateProfile: (data: Partial<User>) => Promise<{ error: Error | null }>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const router = useRouter();

  // Check if we're in a browser environment
  const isBrowser = typeof window !== 'undefined';

  useEffect(() => {
    // Skip auth initialization on server-side
    if (!isBrowser) return;
    // Check for existing session
    const checkSession = async () => {
      const supabase = getSupabaseClient();

      if (!supabase) {
        setLoading(false);
        return;
      }

      try {
        const { data: { session }, error } = await supabase.auth.getSession();

        if (error) {
          throw error;
        }

        if (session) {
          // Get user profile
          const { data: profile, error: profileError } = await supabase
            .from('profiles')
            .select('*')
            .eq('id', session.user.id)
            .single();

          if (profileError && profileError.code !== 'PGRST116') {
            throw profileError;
          }

          setUser({
            id: session.user.id,
            email: session.user.email || '',
            fullName: profile?.full_name || '',
            avatarUrl: profile?.avatar_url || '',
            organizationId: profile?.organization_id || '',
            role: (profile?.role as 'user' | 'admin' | 'owner') || 'user',
            createdAt: profile?.created_at || new Date().toISOString(),
            updatedAt: profile?.updated_at || new Date().toISOString()
          });
        }
      } catch (err) {
        console.error('Error checking session:', err);
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    };

    checkSession();

    // Set up auth state change listener
    const supabase = getSupabaseClient();
    if (supabase) {
      const { data: { subscription } } = supabase.auth.onAuthStateChange(
        async (event, session) => {
          if (event === 'SIGNED_IN' && session) {
            // Get user profile
            const { data: profile, error: profileError } = await supabase
              .from('profiles')
              .select('*')
              .eq('id', session.user.id)
              .single();

            if (profileError && profileError.code !== 'PGRST116') {
              console.error('Error fetching profile:', profileError);
            }

            setUser({
              id: session.user.id,
              email: session.user.email || '',
              fullName: profile?.full_name || '',
              avatarUrl: profile?.avatar_url || '',
              organizationId: profile?.organization_id || '',
              role: (profile?.role as 'user' | 'admin' | 'owner') || 'user',
              createdAt: profile?.created_at || new Date().toISOString(),
              updatedAt: profile?.updated_at || new Date().toISOString()
            });
          } else if (event === 'SIGNED_OUT') {
            setUser(null);
          }
        }
      );

      // Cleanup subscription on unmount
      return () => {
        subscription.unsubscribe();
      };
    }
  }, []);

  const signIn = async (email: string, password: string) => {
    setLoading(true);
    setError(null);

    const supabase = getSupabaseClient();
    if (!supabase) {
      setError('Supabase client not available');
      setLoading(false);
      return { error: new Error('Supabase client not available') as AuthError };
    }

    try {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password
      });

      if (error) {
        throw error;
      }

      return { error: null };
    } catch (err) {
      console.error('Error signing in:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      return { error: err as AuthError };
    } finally {
      setLoading(false);
    }
  };

  const signUp = async (email: string, password: string, fullName: string) => {
    setLoading(true);
    setError(null);

    const supabase = getSupabaseClient();
    if (!supabase) {
      setError('Supabase client not available');
      setLoading(false);
      return { error: new Error('Supabase client not available') as AuthError };
    }

    try {
      // 1. Sign up the user
      const { data: { user: authUser }, error: signUpError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName
          }
        }
      });

      if (signUpError) {
        throw signUpError;
      }

      if (authUser) {
        // 2. Create a profile for the user
        const { error: profileError } = await supabase
          .from('profiles')
          .insert({
            id: authUser.id,
            email,
            full_name: fullName,
            role: 'user'
          });

        if (profileError) {
          throw profileError;
        }
      }

      return { error: null };
    } catch (err) {
      console.error('Error signing up:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      return { error: err as AuthError };
    } finally {
      setLoading(false);
    }
  };

  const signOut = async () => {
    setLoading(true);
    setError(null);

    const supabase = getSupabaseClient();
    if (!supabase) {
      setError('Supabase client not available');
      setLoading(false);
      return;
    }

    try {
      const { error } = await supabase.auth.signOut();

      if (error) {
        throw error;
      }

      setUser(null);
    } catch (err) {
      console.error('Error signing out:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const resetPassword = async (email: string) => {
    setLoading(true);
    setError(null);

    const supabase = getSupabaseClient();
    if (!supabase) {
      setError('Supabase client not available');
      setLoading(false);
      return { error: new Error('Supabase client not available') as AuthError };
    }

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: isBrowser ? `${window.location.origin}/reset-password` : 'http://localhost:3002/reset-password'
      });

      if (error) {
        throw error;
      }

      return { error: null };
    } catch (err) {
      console.error('Error resetting password:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      return { error: err as AuthError };
    } finally {
      setLoading(false);
    }
  };

  // Update password function
  const updatePassword = async (password: string) => {
    const supabase = getSupabaseClient();
    if (!supabase) {
      return { error: new Error('Supabase client not available') as AuthError };
    }

    try {
      setLoading(true);
      setError(null);

      const { error } = await supabase.auth.updateUser({
        password
      });

      if (error) throw error;

      return { error: null };
    } catch (err) {
      console.error('Error updating password:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      return { error: err as AuthError };
    } finally {
      setLoading(false);
    }
  };

  // Update profile function
  const updateProfile = async (data: Partial<User>) => {
    const supabase = getSupabaseClient();
    if (!supabase || !user) {
      return { error: new Error('Not authenticated') };
    }

    try {
      setLoading(true);
      setError(null);

      // Convert from camelCase to snake_case for database
      const dbData: any = {};
      if (data.fullName !== undefined) dbData.full_name = data.fullName;
      if (data.avatarUrl !== undefined) dbData.avatar_url = data.avatarUrl;
      if (data.organizationId !== undefined) dbData.organization_id = data.organizationId;

      // Update profile in database
      const { error } = await supabase
        .from('profiles')
        .update(dbData)
        .eq('id', user.id);

      if (error) throw error;

      // Update local user state
      setUser({
        ...user,
        ...data
      });

      return { error: null };
    } catch (err) {
      console.error('Error updating profile:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      return { error: err as Error };
    } finally {
      setLoading(false);
    }
  };

  const value = {
    user,
    session,
    loading,
    error,
    signIn,
    signUp,
    signOut,
    resetPassword,
    updatePassword,
    updateProfile
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
