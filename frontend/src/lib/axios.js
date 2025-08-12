import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const instance = axios.create({
  baseURL: 'https://i13b204.p.ssafy.io/',
  // baseURL: 'http://localhost:8080/',
  // baseURL: 'http://localhost:5173/',
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


/*
//instance -> springApiClient
const springApiClient = axios.create({
  baseURL: 'http://localhost:8080', // Spring Boot 서버 주소
  withCredentials: true, // Spring Boot와 세션/쿠키 기반 통신 시 필요
})

// Spring Boot 요청에 대한 인터셉터
springApiClient.interceptors.request.use(config => {

  const authStore = useAuthStore()
  if (authStore.accessToken) {
    config.headers.Authorization = `Bearer ${authStore.accessToken}`
  }
  return config
})
*/

// --- ✨새로 추가할 FastAPI용 인스턴스✨ ---
const fastapiApiClient = axios.create({
  // baseURL: 'http://localhost:8000', // FastAPI 서버 주소
  // baseURL: 'http://122.38.210.80:8997/api'
  baseURL: '/api-fast' // 배포용 코드
  // FastAPI는 JWT 토큰으로 인증하므로 withCredentials는 보통 false (기본값)
})

// FastAPI 요청에 JWT 토큰을 첨부하는 인터셉터
fastapiApiClient.interceptors.request.use(config => {
  // Pinia 스토어는 함수 외부에서 직접 호출하면 안되고,
  // 인터셉터 함수 내에서 매번 호출해야 합니다. (초기화 시점 문제 방지)
  const authStore = useAuthStore()
  const accessToken = authStore.accessToken

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

// FastAPI 응답 에러 처리 (401 Unauthorized 등)
fastapiApiClient.interceptors.response.use(
  response => response,
  async error => {
    if (error.response && error.response.status === 401) {
      const authStore = useAuthStore()
      console.error('인증 실패 또는 토큰 만료. 로그아웃을 시도합니다.')
      authStore.clearAuth() // 스토어의 토큰 정보 제거
      // 로그인 페이지로 강제 이동
      // router.push('/login') 또는 window.location.href 사용
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 두 인스턴스를 명시적으로 export
export { fastapiApiClient }
