<template>
  <nav class="navbar fixed-top py-2"
     :class="[isMenuOpen ? 'navbar--default-text' : navbarTextColorClass, { 'navbar--scrolled': isScrolled }]">


    <div v-if="isMenuOpen" class="menu-backdrop" @click="isMenuOpen = false"></div>

    <div class="container d-flex justify-content-between align-items-center">

      <RouterLink to="/" class="fw-bold text-dark text-decoration-none">
        <img :src="logoSrc" alt="로고" style="height: 25px;" />
      </RouterLink>

      <button class="btn d-lg-none" @click="isMenuOpen = !isMenuOpen">
        <Bars2Icon class="hamburger-icon" />
      </button>

      <ul class="nav gap-4 d-none d-lg-flex">
        <li class="nav-item">
          <RouterLink to="/ai-consult" class="nav-link" @click="refreshData">AI사전상담</RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/cases/search" class="nav-link" :class="{ active: isActive('/cases/search') }" @click="refreshData">판례 검색</RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/lawyers" class="nav-link" @click="refreshData">변호사 찾기</RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/consult-form" class="nav-link" :class="{ active: isActive('/consult-form') }" @click="refreshData" @click.prevent="goToConsultForm">AI상담신청서</RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink :to="videoCallPath" class="nav-link" @click="refreshData">화상상담</RouterLink>
        </li>
      </ul>

      <div class="d-none d-lg-block">
        <template v-if="isLoggedIn">
          <RouterLink :to="mypagePath" class="me-3 fw-medium text-decoration-none nav-link" @click="refreshData">
            마이페이지
          </RouterLink>
          <a href="#" class="fw-medium text-decoration-none nav-link" @click.prevent="logout">
            로그아웃
          </a>
        </template>

        <template v-else>
          <RouterLink to="/login" class="fw-medium text-decoration-none nav-link">
            로그인
          </RouterLink>
        </template>
      </div>

    </div>

    <div
      :class="['mobile-menu', { open: isMenuOpen }]"
      class="d-lg-none"
      @click.stop
    >
      <button class="close-button" @click="isMenuOpen = false">
        <XMarkIcon class="close-icon" />
      </button>

      <div class="mobile-menu-inner d-flex flex-column h-100">
        <ul class="nav flex-column p-3 pt-5 text-start">
          <li class="nav-item"><RouterLink to="/ai-consult" class="nav-link" @click="refreshData">AI사전상담</RouterLink></li>
          <li class="nav-item"><RouterLink to="/cases/search" class="nav-link" @click="refreshData">판례 검색</RouterLink></li>
          <li class="nav-item"><RouterLink to="/lawyers" class="nav-link" @click="refreshData">변호사 조회</RouterLink></li>
          <li class="nav-item"><RouterLink to="/consult-form" class="nav-link" @click.prevent="handleMobileConsultFormClick" @click="refreshData">AI상담신청서</RouterLink></li>
          <li class="nav-item"><RouterLink :to="videoCallPath" class="nav-link" @click="refreshData">화상상담</RouterLink></li>
        </ul>

        <ul class="nav flex-column px-3 pb-4 text-start menu-footer">
          <template v-if="isLoggedIn">
            <li class="nav-item">
              <RouterLink :to="mypagePath" class="nav-link text-dark fw-medium text-decoration-none" @click="refreshData">
                마이페이지
              </RouterLink>
            </li>
            <li class="nav-item">
              <a href="#" class="nav-link text-dark fw-medium text-decoration-none" @click.prevent="logout">
                로그아웃
              </a>
            </li>
          </template>

          <template v-else>
            <li class="nav-item">
              <RouterLink to="/login" class="nav-link text-dark fw-medium text-decoration-none">
                로그인
              </RouterLink>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
</template>


<script setup>
import { Bars2Icon, XMarkIcon  } from '@heroicons/vue/24/solid'
import { useAuthStore } from '@/stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { onMounted, onUnmounted, ref, computed } from 'vue'
import defaultLogo from '@/assets/logo.png'
import whiteLogo from '@/assets/logo-white.png'
import axios from '@/lib/axios';

const isMenuOpen = ref(false)
const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const isLoggedIn = computed(() => !!authStore.accessToken)

const mypagePath = computed(() =>
  authStore.userType === 'LAWYER' ? '/lawyer/mypage' : '/user/mypage'
)

const videoCallPath = computed(() =>
  authStore.userType === 'LAWYER' ? '/videocall/preview/lawyer' : '/videocall/preview/client'
)

const logoSrc = computed(() => {
  const whitePages = ['/cases/search', '/consult-form']
  const isWhitePage = whitePages.includes(route.path)  || route.path.startsWith('/cases/detail');

  if (isWhitePage && !isScrolled.value) {
    return whiteLogo
  } else {
    return defaultLogo
  }
})

const logout = () => {
  authStore.clearAuth()
  localStorage.removeItem('hasRefresh');
  router.push('/login')
}

const navbarTextColorClass = computed(() => {
  const whitePages = ['/cases/search', '/cases/detail/:id', '/consult-form',]
  const isWhitePage = whitePages.includes(route.path)  || route.path.startsWith('/cases/detail');
  if (isWhitePage && !isScrolled.value) {
    return 'navbar--white-text'
  } else {
    return 'navbar--default-text'
  }
})

const goToConsultForm = () => {
  if (!isLoggedIn.value) {
    router.push({ path: '/consult-form', query: { needLogin: 'true' } })
  } else {
    router.push('/consult-form')
  }
}

const handleMobileConsultFormClick = () => {
  isMenuOpen.value = false  // 모바일 메뉴 닫기
  goToConsultForm()
}

const isActive = (path) => route.path === path

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

/* access 토큰 갱신 */
const refreshData = async () => {
  const hasRefresh = localStorage.getItem('hasRefresh') === 'true';

  if (!hasRefresh) {
    return; // 리프레시 토큰 없다고 판단
  }
  try {
    const res = await axios.post('/api/auth/refresh', null, { withCredentials: true });
    const { accessToken } = res.data;
    if (accessToken) {
      authStore.accessToken = accessToken;
      localStorage.setItem('accessToken', accessToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
    }
  } catch (e) {
    console.error('토큰 갱신 실패:', e);
  }
};


</script>

<style scoped>

.navbar {
  position: fixed;
  z-index: 1000;
  transition: background-color 0.1s ease, color 0.1s ease;
  width: 100%;
}

.hamburger-icon {
  width: 24px;
  height: 24px;
  color: #333;
}
::v-deep(a.nav-link) {
  color: #6c9bcf;
  transition: color 0.2s ease;
  padding: 10px 0;
  text-decoration: none;
  display: inline-block;
}

::v-deep(a.nav-link:hover) {
  color: #1f3f75;
  font-weight: 500;
}

::v-deep(a.nav-link.router-link-active) {
  color: #1f3f75;
  font-weight: 600;
}


/* 모바일 메뉴 영역 */
.mobile-menu {
  position: fixed;
  top: 0;
  right: 0;
  width: 220px;
  height: 100vh;
  background-color: white;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
  transform: translateX(100%);
  transition: transform 0.3s ease-in-out;
  z-index: 999;
}

.mobile-menu.open {
  transform: translateX(0);
}

.mobile-menu-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  justify-content: start;
}

.menu-footer {
  margin-top: 30px;
}

.menu-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.3); /* 어두운 배경 */
  z-index: 998; /* mobile-menu (999) 보다 낮고, navbar 보다 높게 */
}



/* 닫기 버튼 */
.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  cursor: pointer;
}
.close-icon {
  width: 24px;
  height: 24px;
  color: #333;
}


/* 기본 텍스트 스타일 */
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
  color: #6c9bcf;
}
.navbar--default-text .nav-link.active {
  color: #1f3f75;
}

</style>
