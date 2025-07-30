import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const instance = axios.create({
  baseURL: 'http://localhost:8080',
  withCredentials: true      // ← 이걸 켜야 CORS 구문에서 쿠키 허용이 됩니다
})

instance.interceptors.request.use(config => {
  const { accessToken } = useAuthStore()
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

export default instance
