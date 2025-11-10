/**
 * API Configuration
 */

import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// API Base URL - configure for your environment
export const API_BASE_URL = __DEV__
  ? 'http://10.0.2.2:8000'  // Android emulator
  : 'https://api.halalscanner.com';

// Create axios instance
export const api = axios.create({
  baseURL: API_BASE_URL + '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  async config => {
    // Add user ID if available
    const userId = await AsyncStorage.getItem('userId');
    if (userId) {
      config.headers['X-User-ID'] = userId;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  },
);

// Response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  },
);

// API Methods
export const scanProduct = async (imageBase64: string, barcode?: string) => {
  const userId = await AsyncStorage.getItem('userId') || 'anonymous';

  const response = await api.post('/scan', {
    image_base64: imageBase64,
    barcode,
    user_id: userId,
    language_hint: 'en',
  });

  return response.data;
};

export const getProduct = async (productId: string) => {
  const response = await api.get(`/product/${productId}`);
  return response.data;
};

export const submitFeedback = async (
  scanId: string,
  agree: boolean,
  comment?: string,
) => {
  const userId = await AsyncStorage.getItem('userId') || 'anonymous';

  const response = await api.post('/feedback', {
    scan_id: scanId,
    user_id: userId,
    agree,
    comment,
  });

  return response.data;
};

export const contactManufacturer = async (
  scanId: string,
  productId: string,
  message?: string,
) => {
  const response = await api.post('/feedback/manufacturer-contact', {
    scan_id: scanId,
    product_id: productId,
    additional_message: message,
  });

  return response.data;
};

export default api;
