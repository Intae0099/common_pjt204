<template>
  <div class="login-container">
    <div class="login-box">
      <h2>관리자 로그인</h2>
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="email">이메일</label>
          <input
            type="email"
            id="email"
            v-model="loginEmail"
            placeholder="admin@example.com"
            required
          />
        </div>
        <div class="input-group">
          <label for="password">비밀번호</label>
          <input
            type="password"
            id="password"
            v-model="password"
            placeholder="비밀번호"
            required
          />
        </div>
        <button type="submit" :disabled="isLoading">
          {{ isLoading ? '로그인 중...' : '로그인' }}
        </button>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import apiClient from '@/lib/axios' // Spring Boot API용 Axios 인스턴스

// --- 상태 관리 ---
const loginEmail = ref('')
const password = ref('')
const isLoading = ref(false)
const errorMessage = ref('')

// --- 스토어 및 라우터 인스턴스 ---
const authStore = useAuthStore()
const router = useRouter()

// --- 로그인 처리 함수 ---
const handleLogin = async () => {
  // 이전 에러 메시지 초기화
  errorMessage.value = ''
  isLoading.value = true

  try {
    // API 요청
    const response = await apiClient.post('/api/admin/login', {
      loginEmail: loginEmail.value,
      password: password.value,
    })

    // 응답 데이터에서 accessToken 추출
    const { accessToken } = response.data

    // Pinia 스토어에 accessToken 저장
    authStore.setToken(accessToken)
    authStore.setUserType('ADMIN')
    // API 명세에 따라 refresh_token은 HttpOnly 쿠키로 자동 설정됩니다.
    // axios의 withCredentials: true 설정 덕분에 브라우저가 자동으로 처리합니다.


    // 로그인 성공 후 관리자 대시보드 페이지로 이동
    router.push('/admin') // TODO: 실제 대시보드 경로로 변경하세요.

  } catch (error) {
    console.error('로그인 실패:', error)
    if (error.response) {
      // 서버에서 보낸 에러 메시지가 있는 경우
      const { status, data } = error.response
      if (status === 401) {
        errorMessage.value = data.message || '이메일 또는 비밀번호가 일치하지 않습니다.'
      } else if (status === 400) {
        errorMessage.value = data.message || '잘못된 요청입니다. 입력값을 확인해주세요.'
      } else {
        errorMessage.value = data.message || '서버에 문제가 발생했습니다. 잠시 후 다시 시도해주세요.'
      }
    } else {
      // 네트워크 오류 등 응답을 받지 못한 경우
      errorMessage.value = '네트워크 오류가 발생했습니다. 연결을 확인해주세요.'
    }
  } finally {
    // 로딩 상태 종료
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
  font-family: 'Noto Sans KR', sans-serif;
}

.login-box {
  background: white;
  padding: 2rem 3rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  text-align: center;
}

h2 {
  margin-bottom: 1.5rem;
  color: #333;
}

.input-group {
  margin-bottom: 1rem;
  text-align: left;
}

.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #555;
}

.input-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box; /* padding이 너비에 포함되도록 설정 */
}

button {
  width: 100%;
  padding: 0.75rem;
  background-color: #1d2b50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

button:hover {
  background-color: #6c9bcf;
}

button:disabled {
  background-color: #888;
  cursor: not-allowed;
}

.error-message {
  color: #d32f2f;
  margin-top: 1rem;
  font-size: 0.9rem;
}
</style>
