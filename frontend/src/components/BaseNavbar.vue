<template>
  <nav class="navbar fixed-top py-2" :class="[navbarTextColorClass, { 'navbar--scrolled': isScrolled }]">
    <!-- ✨ 여기에 container 추가 -->
    <div class="container d-flex justify-content-between align-items-center">
    <!-- 왼쪽: 로고 -->
    <RouterLink to="/" class="fw-bold text-dark text-decoration-none">LOGO</RouterLink>

    <!-- 가운데: 메뉴 목록 -->
    <ul class="nav gap-4">
      <li class="nav-item">
        <RouterLink to="/ai-consult" class="nav-link">AI사전상담</RouterLink>
      </li>
      <li class="nav-item">
        <RouterLink to="/cases/search" class="nav-link" :class="{ active: isActive('/cases/search') }">판례 검색</RouterLink>
      </li>
      <li class="nav-item">
        <RouterLink to="/lawyers" class="nav-link">변호사 조회</RouterLink>
      </li>
      <li class="nav-item">
        <RouterLink to="/consult-form" class="nav-link" :class="{ active: isActive('/consult-form') }">AI상담신청서</RouterLink>
      </li>
      <li class="nav-item">
        <RouterLink to="/videocall/preview/client" class="nav-link">화상상담</RouterLink>
      </li>
    </ul>

    <!-- 오른쪽: 마이페이지 & 로그아웃 -->
    <div>
      <RouterLink to="/lawyer/mypage" class="me-3 text-dark fw-medium text-decoration-none">마이페이지</RouterLink>
      <a href="#" class="text-dark fw-medium text-decoration-none" @click.prevent="logout">Logout</a>
    </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter,useRoute } from 'vue-router'
import { onMounted, onUnmounted, ref, computed } from 'vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const logout = () => {
  authStore.clearToken()
  router.push('/login')
}

//경로별 텍스트 컬러변경
const navbarTextColorClass = computed(() => {
  const whitePages = ['/cases/search', '/consult-form']
  const isWhitePage = whitePages.includes(route.path)
  if (isWhitePage && !isScrolled.value) {
    return 'navbar--white-text'
  } else {
    return 'navbar--default-text'
  }
})
const isActive = (path) => route.path === path

//스크롤 감지
const isScrolled = ref(false)
const handleScroll = () => {
  isScrolled.value = window.scrollY > 10
}
onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})
onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.navbar {
  position: fixed;
  z-index: 1000;
  transition: background-color 0.1s ease, color 0.1s ease;
}
.navbar--scrolled {
  background-color: rgba(255, 255, 255);
  backdrop-filter: saturate(180%) blur(10px);
}
.navbar--white-text .nav-link {
  color: rgba(255, 255, 255, 0.7);
}
.navbar--white-text .nav-link.active {
  color: rgba(255, 255, 255, 1);
}
.navbar--default-text .nav-link {
  color: #333;
}
.navbar--default-text .nav-link.active {
  color: #000;
}
</style>
