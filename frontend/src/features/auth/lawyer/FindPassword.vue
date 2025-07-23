<template>
  <div>
    <!-- 상단 제목 -->
    <div>
      <h2>비밀번호 찾기</h2>
      <p>가입하신 이메일을 입력하시면, 임시 비밀번호를 보내드립니다.</p>
    </div>

    <!-- 이메일 입력 폼 -->
    <form @submit.prevent="handleFindPassword">
      <div>
        <label for="email">이메일</label>
        <input
          id="email"
          type="email"
          v-model="email"
          placeholder="예시) lawyer@example.com"
          required
        />
      </div>

      <button type="submit">임시 비밀번호 발송</button>
    </form>

    <!-- 뒤로 가기 -->
    <div>
      <router-link to="/login/lawyer">로그인 화면으로 돌아가기</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FindPassword',
  data() {
    return {
      email: ''
    };
  },
  methods: {
    handleFindPassword() {
      console.log('비밀번호 찾기 요청 이메일:', this.email);
      // 실제 API 요청은 여기서 처리
      alert('입력하신 이메일로 임시 비밀번호를 전송했습니다.');
      this.$router.push('/login/lawyer');
    }
  }
};
</script>
