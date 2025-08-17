<template>
  <footer class="base-footer">
    <div class="container py-5">
      <div class="row gy-4">
        <div class="col-12 col-md-6">
          <div class="d-flex align-items-center gap-2 mb-2">
            <strong class="footer-title">ALaw</strong>
          </div>
          <p class="footer-slogan">법률상담은 어디로? <span class="text-accent">에이로!</span></p>
          <p class="team small text-muted-light mb-0">
            <strong>팀장</strong> 김태인 &nbsp; <strong>팀원</strong> 권자은, 방승철, 윤규성, 이정연, 전해지
          </p>
        </div>
        <div class="col-6 col-md-6">
          <h6 class="section-title">바로가기</h6>
          <ul class="nav flex-row gap-3 flex-wrap">
            <li class="nav-item"><RouterLink to="/ai-consult" class="footer-link">AI사전상담</RouterLink></li>
            <li class="nav-item"><RouterLink to="/cases/search" class="footer-link">판례검색</RouterLink></li>
            <li class="nav-item"><RouterLink to="/lawyers" class="footer-link">변호사찾기</RouterLink></li>
            <li class="nav-item">
              <a href="#" class="footer-link" @click.prevent="goToConsultForm">AI상담신청서</a>
            </li>
            <li class="nav-item"><RouterLink :to="videoCallPath" class="footer-link">화상상담</RouterLink></li>
          </ul>
        </div>
      </div>

      <hr class="my-4 hr-light" />

      <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-2">
        <p class="small text-muted-light mb-0">© {{ year }} ALaw. All rights reserved.</p>

        <div class="d-flex align-items-center gap-3">
          <RouterLink v-if="isLoggedIn" :to="mypagePath" class="footer-link small">마이페이지</RouterLink>
          <RouterLink v-else to="/login" class="footer-link small">로그인</RouterLink>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isLoggedIn = computed(() => !!authStore.accessToken)
const mypagePath = computed(() =>
  authStore.userType === 'LAWYER' ? '/lawyer/mypage' : '/user/mypage'
)
const videoCallPath = computed(() =>
  authStore.userType === 'LAWYER' ? '/videocall/preview/lawyer' : '/videocall/preview/client'
)

const goToConsultForm = () => {
  if (!isLoggedIn.value) {
    router.push({ path: '/consult-form', query: { needLogin: 'true' } })
  } else {
    router.push('/consult-form')
  }
}

const year = new Date().getFullYear()
</script>

<style scoped>
.base-footer {
  font-family: 'Noto Sans KR', sans-serif;
  background: #1d2b50; /* 네이비 */
  color: #f4f7fb; /* 거의 흰색 */
}
.footer-title {
  font-size: 1rem;
  letter-spacing: .2px;
}
.footer-slogan {
  margin-bottom: .25rem;
}
.section-title {
  font-size: .875rem;
  font-weight: 700;
  color: #f4f7fb;
  margin-bottom: .75rem;
}
.footer-link {
  text-decoration: none;
  color: #cfcfcf; /* 라이트 그레이 */
  white-space: nowrap;
}
.footer-link:hover {
  color: #6c9bcf; /* 밝은 파랑 */
  text-decoration: none;
}
.text-accent {
  color: #6c9bcf;
}
.text-muted-light {
  color: #cfcfcf;
}
.hr-light {
  border-color: #888; /* 그레이 */
}
</style>
