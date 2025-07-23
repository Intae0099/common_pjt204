<template>
  <div class="login-wrapper">
    <h1>로그인</h1>
    <div class="social-login-box">
      <p>간편 로그인</p>
      <button @click="login('kakao')">카카오 로그인</button>
      <button @click="login('naver')">네이버 로그인</button>
      <div class="divider">변호사이신가요?</div>
      <button>변호사로 로그인</button>
    </div>

    <div class="footer-links">
      <router-link to="/reset-password">비밀번호 찾기</router-link>
      <router-link :to="{ name: 'SignUpFirst' }">변호사 회원가입하기</router-link>
    </div>
  </div>
</template>

<script setup>
  const login = (provider) => {
    window.location.href = `/api/auth/users/oauth2/social/${provider}/login`
  }
</script>

<style scoped>

</style>
