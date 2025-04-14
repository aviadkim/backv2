import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Check if user is logged in
    const checkAuth = async () => {
      try {
        // Simulate API call to check authentication
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // For testing purposes, create a mock user
        const mockUser = {
          id: '1',
          name: 'Test User',
          email: 'test@example.com',
          role: 'admin'
        };
        
        setUser(mockUser);
      } catch (error) {
        console.error('Error checking authentication:', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    
    checkAuth();
  }, []);
  
  const login = async (email, password) => {
    try {
      // Simulate API call to login
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // For testing purposes, create a mock user
      const mockUser = {
        id: '1',
        name: 'Test User',
        email,
        role: 'admin'
      };
      
      setUser(mockUser);
      return { success: true };
    } catch (error) {
      console.error('Error logging in:', error);
      return { success: false, error: error.message };
    }
  };
  
  const logout = async () => {
    try {
      // Simulate API call to logout
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setUser(null);
      return { success: true };
    } catch (error) {
      console.error('Error logging out:', error);
      return { success: false, error: error.message };
    }
  };
  
  const register = async (name, email, password) => {
    try {
      // Simulate API call to register
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // For testing purposes, create a mock user
      const mockUser = {
        id: '1',
        name,
        email,
        role: 'user'
      };
      
      setUser(mockUser);
      return { success: true };
    } catch (error) {
      console.error('Error registering:', error);
      return { success: false, error: error.message };
    }
  };
  
  const value = {
    user,
    loading,
    login,
    logout,
    register,
    isAuthenticated: !!user
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
