import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api',
});

// Add API Key to every request
api.interceptors.request.use((config) => {
  const apiKey = import.meta.env.VITE_API_KEY;
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey;
  }
  return config;
});

export default api;
