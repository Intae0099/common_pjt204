<template>
  <div class="login-wrapper">
    <h1 class="login-title">변호사 로그인</h1>
    <div class="login-box">
      <form @submit.prevent="handleLogin" class="form-area">
        <div class="form-group">
          <label for="email">이메일</label>
          <input
            id="email"
            type="email"
            v-model="form.loginEmail"
            placeholder="예시) lawyer@example.com"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">비밀번호</label>
          <input
            id="password"
            type="password"
            v-model="form.password"
            placeholder="비밀번호 입력"
            required
          />
        </div>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        <button type="submit" class="lawyer-login">로그인</button>
      </form>
    </div>

    <div class="footer-links">
      <router-link to="/signup/step1">아직 회원이 아니신가요?</router-link>
    </div>
  </div>
</template>

<script>
import axios from '@/lib/axios';
import { useAuthStore } from '@/stores/auth';

export default {
  name: 'LawyerLogin',
  data() {
    return {
      form: {
        loginEmail: '',
        password: ''
      },
      errorMessage: ''
    };
  },
  methods: {
    async handleLogin() {
      try {
        const response = await axios.post('/api/lawyers/login', this.form);

        const token = response.data?.accessToken;
        if (!token) throw new Error('토큰 없음');

        const authStore = useAuthStore();
        authStore.setToken(token);               // ✅ access_token 저장
        authStore.setUserType('LAWYER');         // ✅ userType 저장 (변호사)

        localStorage.setItem('hasRefresh', 'true');

        this.$router.push('/lawyer/mypage');     // ✅ 변호사 마이페이지로 이동
      } catch (err) {
        const status = err.response?.status;
        //const msg = err.response?.data?.error;

        if (status === 403) {
          this.errorMessage = '계정 승인 대기 중입니다.';
          //this.$router.push('/pending-notice');
        } else if (status === 401) {
          this.errorMessage = '이메일 또는 비밀번호가 올바르지 않습니다.';
        } else if (status === 404) {
          this.errorMessage = '존재하지 않는 계정입니다.';
        } else {
          this.errorMessage = '알 수 없는 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
        }
      }
    }
  }

};
</script>

<style scoped>
* {
  font-family: 'Noto Sans KR', sans-serif;
}

.login-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 200px;
  font-family: 'Pretendard', sans-serif;
}

.login-title {
  font-size: 24px;
  margin-bottom: 40px;
  font-weight: bold;
}

.login-box {
  width: 400px;
  background-color: white;
  border: 1px solid #E4EEF5;
  border-radius: 10px;
  padding: 40px 30px;
  box-shadow: 0 1px 5px #E4EEF5;
  text-align: center;
}

.form-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.form-group label {
  font-size: 14px;
  margin-bottom: 6px;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
}

.lawyer-login {
  background-color: #0c2c46;
  color: white;
  border: none;
  padding: 12px;
  width: 100%;
  border-radius: 6px;
  font-weight: bold;
  font-size: 15px;
  cursor: pointer;
}

.error-message {
  color: red;
  font-size: 13px;
  margin-bottom: 15px;
}

.footer-links {
  margin-top: 12px;
  font-size: 13px;
  color: #777;
  display: flex;
}
</style>
