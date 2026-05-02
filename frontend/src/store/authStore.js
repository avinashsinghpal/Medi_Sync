import { create } from 'zustand';
import api from '../utils/api';

const initialToken = localStorage.getItem('token') || null;
let initialUser = null;
try {
  initialUser = JSON.parse(localStorage.getItem('user') || 'null');
} catch {
  initialUser = null;
}

export const useAuthStore = create((set, get) => ({
  user: initialUser,
  token: initialToken,
  isAuthenticated: !!initialToken && !!initialUser,
  
  login: async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      const { user, token } = response.data;
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      set({ user, token, isAuthenticated: true });
      return user;
    } catch (error) {
      const msg = error?.response?.data?.detail || 'Login failed';
      throw new Error(msg);
    }
  },

  registerPatient: async (payload) => {
    const response = await api.post('/auth/register/patient', payload);
    const { user, token } = response.data;
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    set({ user, token, isAuthenticated: true });
    return user;
  },
  
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
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
