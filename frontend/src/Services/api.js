import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL, // 'http://localhost:8080'
  withCredentials: true // caso use cookies (JWT via cookie, por exemplo)
});

export default api;