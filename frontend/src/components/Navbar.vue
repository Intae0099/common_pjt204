<template>
  <nav class="navbar">
    <!-- 왼쪽: 로고 -->
    <div class="nav-left">
      <RouterLink to="/" class="logo">LOGO</RouterLink>
    </div>

    <!-- 가운데: 메뉴 -->
    <div class="nav-center">
      <RouterLink to="/ai-preconsult">AI사전상담</RouterLink>
      <RouterLink to="/cases">판례 검색</RouterLink>
      <RouterLink to="/lawyers">변호사조회</RouterLink>
      <RouterLink to="/ai-application">AI상담신청서</RouterLink>
      <RouterLink to="/video">화상상담</RouterLink>
    </div>

    <!-- 오른쪽: 마이페이지 / 로그인 / 로그아웃 -->
    <div class="nav-right">
      <RouterLink to="/mypage">마이페이지</RouterLink>
      <button @click="logout" v-if="authStore.isLoggedIn">Logout</button>
      <RouterLink to="/login" v-else>Login</RouterLink>
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
