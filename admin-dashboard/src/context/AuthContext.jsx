import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [admin, setAdmin] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('admin_token');
    if (token) {
      // Verify token is still valid by fetching admin info
      fetchAdminInfo();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchAdminInfo = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      if (!token) {
        setLoading(false);
        return;
      }

      // Decode token to get admin info (basic check)
      // In production, you might want to call an endpoint to verify token
      const payload = JSON.parse(atob(token.split('.')[1]));
      setAdmin({
        id: payload.sub,
        email: payload.email,
        role: payload.role,
      });
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Error fetching admin info:', error);
      localStorage.removeItem('admin_token');
      setIsAuthenticated(false);
      setAdmin(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await api.post('/api/admin/login', {
        email,
        password,
      });

      const { access_token } = response.data;
      localStorage.setItem('admin_token', access_token);

      // Decode token to get admin info
      const payload = JSON.parse(atob(access_token.split('.')[1]));
      const adminData = {
        id: payload.sub,
        email: payload.email,
        role: payload.role,
      };

      setAdmin(adminData);
      setIsAuthenticated(true);

      return { success: true, admin: adminData };
    } catch (error) {
      const message =
        error.response?.data?.detail || 'Login failed. Please check your credentials.';
      return { success: false, error: message };
    }
  };

  const logout = () => {
    localStorage.removeItem('admin_token');
    setAdmin(null);
    setIsAuthenticated(false);
  };

  const value = {
    admin,
    loading,
    isAuthenticated,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
