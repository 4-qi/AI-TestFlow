import axios from 'axios';

export const api = axios.create({
  baseURL: 'http://127.0.0.1:5000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

export function getErrorMessage(error) {
  return error.response?.data?.message || '请求失败，请稍后重试';
}

