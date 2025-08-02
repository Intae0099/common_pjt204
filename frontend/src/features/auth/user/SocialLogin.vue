<template>
  <div class="login-wrapper">
    <h1>로그인</h1>
    <div class="social-login-box">
      <p>간편 로그인</p>
      <button @click="login">카카오 로그인</button>
      <div class="divider">변호사이신가요?</div>
      <router-link to="/login/lawyer">
        <button>변호사로 로그인</button>
      </router-link>
    </div>

    <div class="footer-links">
      <router-link :to="{ name: 'SignUpFirst' }">변호사 회원가입하기</router-link>
    </div>
  </div>
</template>

<script setup>

const login = async () => {

  window.location.href = 'https://i13b204.p.ssafy.io/oauth2/authorization/kakao'
}
</script>


<style scoped>

</style>
