import { create } from 'zustand';
import api from '../utils/api';

export const useAuthStore = create((set, get) => ({
  user: null,
  token: localStorage.getItem('token') || null,
  isAuthenticated: !!localStorage.getItem('token'),
  
  login: async (email, password) => {
    try {
      // In a real implementation this would hit the API
      // const response = await api.post('/auth/login', { email, password });
      // const { user, token } = response.data;
      
      // Mock implementation for now as the backend may not be ready
      const token = 'mock-jwt-token';
      const user = { id: '1', email, role: email.includes('doctor') ? 'DOCTOR' : 'PATIENT', name: 'Demo User' };
      
      localStorage.setItem('token', token);
      set({ user, token, isAuthenticated: true });
      return user;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  },
  
  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null, isAuthenticated: false });
  },
  
  refreshToken: async () => {
    try {
      // const response = await api.post('/auth/refresh');
      // const { token } = response.data;
      // localStorage.setItem('token', token);
      // set({ token });
    } catch (error) {
      get().logout();
    }
  }
}));
