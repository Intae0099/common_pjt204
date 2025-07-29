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
  console.log('window.location.search:', window.location.search)
  const params      = new URLSearchParams(window.location.search)
  const accessToken = params.get('accessToken')   // 여기서도 accessToken
  console.log('parsed accessToken:', accessToken)

  if (accessToken) {
    auth.setToken(accessToken)
    auth.setUserType('USER')
    router.replace({ name: 'UserMyPage' })
  } else {
    alert('로그인에 실패했습니다.')
    router.replace({ name: 'SocialLogin' })
  }
})
</script>
