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
// import { useAuthStore } from '@/stores/auth'
// import { useRouter } from 'vue-router'
// import axios from '@/lib/axios'

// const authStore = useAuthStore()
// const router = useRouter()

const login = async () => {

  window.location.href = 'https://i13b204.p.ssafy.io/oauth2/authorization/kakao'

//   try {
//     const res = await axios.get('/oauth2/authorization/kakao')

//     const token = res.data.access_token
//     authStore.setToken(token)

//     // ✅ 사용자 타입 설정 (소셜 로그인은 일반회원)
//     authStore.setUserType('USER')

//     // ✅ 로그인 후 경로 이동
//     router.push('/user/mypage')
//   } catch (err) {
//     console.error('로그인 실패:', err)
//     alert('로그인 실패')
//   }
}
</script>


<style scoped>

</style>
