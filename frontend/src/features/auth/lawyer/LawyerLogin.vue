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
          v-model="form.loginId"
          placeholder="예시) lawyer@example.com"
          required
        />
      </div>

      <div>
        <label for="password">비밀번호</label>
        <input
          id="password"
          type="password"
          v-model="form.loginPwd"
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
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

export default {
  name: 'LawyerLogin',
  data() {
    return {
      form: {
        loginId: '',
        loginPwd: ''
      }
    };
  },
  methods: {
    async handleLogin() {
      try {
        const response = await axios.post('/api/auth/lawyers/login', this.form);

        const token = response.data?.access_token;
        if (!token) throw new Error('토큰 없음');

        const authStore = useAuthStore();
        authStore.setToken(token); // access_token 저장

        this.$router.push('/');
      } catch (error) {
        console.error('로그인 실패:', error);
        alert('이메일 또는 비밀번호가 올바르지 않습니다.');
      }
    }
  }
};
</script>
