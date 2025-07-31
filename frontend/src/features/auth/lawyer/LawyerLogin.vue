<template>
  <div>
    <!-- 상단 제목 -->
    <div>
      <h2>변호사 로그인</h2>
      <p>이메일과 비밀번호를 입력해주세요</p>
    </div>

    <!-- 로그인 폼 -->
    <form @submit.prevent="handleLogin">
      <div>
        <label for="email">이메일</label>
        <input
          id="email"
          type="email"
          v-model="form.loginEmail"
          placeholder="예시) lawyer@example.com"
          required
        />
      </div>

      <div>
        <label for="password">비밀번호</label>
        <input
          id="password"
          type="password"
          v-model="form.password"
          placeholder="비밀번호 입력"
          required
        />
      </div>

      <button type="submit">로그인</button>
    </form>

    <!-- 하단 링크 -->
    <div>
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
      }
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

        this.$router.push('/lawyer/mypage');     // ✅ 변호사 마이페이지로 이동
      } catch (err) {
        const status = err.response?.status;
        const msg = err.response?.data?.error;

        if (status === 403 && msg === '계정 승인 대기 중입니다.') {
          this.$router.push('/pending-notice');
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
