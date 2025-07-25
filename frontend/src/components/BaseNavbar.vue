<template>
  <nav class="navbar">
    <!-- 내용만 있음, Navbar 자체를 또 호출하지 않음 -->
    <div class="nav-left">
      <RouterLink to="/" class="logo">LOGO</RouterLink>
    </div>
    <div class="nav-center">
      <RouterLink to="/ai-consult">AI사전상담</RouterLink>
      <RouterLink to="/cases/search">판례 검색</RouterLink>
      <RouterLink to="/lawyers">변호사조회</RouterLink>
      <RouterLink to="/ai-application">AI상담신청서</RouterLink>
      <RouterLink to="/video">화상상담</RouterLink>
    </div>
    <div class="nav-right">
      <RouterLink to="/mypage">마이페이지</RouterLink>
      <button @click="logout" v-if="authStore.isLoggedIn">로그아웃</button>
      <RouterLink to="/login" v-else>로그인</RouterLink>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const logout = () => {
  authStore.clearToken()
  router.push('/login')
}
</script>

<style scoped>

</style>
