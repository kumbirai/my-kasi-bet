import axios from 'axios';

// Use relative URLs if VITE_API_BASE_URL is empty/undefined (for Docker nginx proxy)
// Otherwise use the provided URL (for local development)
// In Docker: VITE_API_BASE_URL should be unset or empty, so we use relative URLs
// In local dev: VITE_API_BASE_URL is set to http://localhost:8000
const envApiUrl = import.meta.env.VITE_API_BASE_URL;

// Debug logging (remove in production if needed)
if (typeof window !== 'undefined') {
  console.log('VITE_API_BASE_URL:', envApiUrl, 'Type:', typeof envApiUrl);
}

// If envApiUrl is undefined, null, empty string, or just whitespace, use empty string (relative URLs)
// This works for Docker where nginx proxies /api to backend
let API_BASE_URL = '';
if (envApiUrl && typeof envApiUrl === 'string') {
  const trimmed = envApiUrl.trim();
  // Only use if it's a valid URL (starts with http:// or https://)
  if (trimmed !== '' && (trimmed.startsWith('http://') || trimmed.startsWith('https://'))) {
    API_BASE_URL = trimmed;
  }
}

if (typeof window !== 'undefined') {
  console.log('API_BASE_URL:', API_BASE_URL || '(empty - using relative URLs)');
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem('admin_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
