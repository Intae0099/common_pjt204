<template>
  <div>
    <h2>간편 로그인</h2>
    <button @click="login('kakao')">카카오 로그인</button>
    <button @click="login('naver')">네이버 로그인</button>
  </div>
</template>

<script setup>
  const login = (provider) => {
    window.location.href = `/api/auth/users/oauth2/social/${provider}/login`
  }
</script>

<style scoped>

</style>
