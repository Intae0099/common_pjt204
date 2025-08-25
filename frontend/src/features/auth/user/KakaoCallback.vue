<template>
  <div>로그인 처리 중…</div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

onMounted(() => {
  const params      = new URLSearchParams(window.location.search)
  const accessToken = params.get('accessToken')   // 여기서도 accessToken

  if (accessToken) {
    auth.setToken(accessToken)
    auth.setUserType('USER')
    localStorage.setItem('hasRefresh', 'true');
    router.replace({ name: 'UserMyPage' })

  } else {
    alert('로그인에 실패했습니다.')
    router.replace({ name: 'SocialLogin' })
  }
})
</script>
