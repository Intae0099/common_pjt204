<template>
<div>
  <div>로그인 처리중</div>
</div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/lib/axios'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  const provider = route.params.provider
  try {
    const res = await axios.get(`/api/auth/users/oauth2/social/${provider}/callback`, {
    })
    const token = res.data.access_token
    authStore.setToken(token)
    router.push('/')
  } catch (err) {
    console.error('로그인 실패:', err)
    alert('로그인 실패')
    router.push('/login')
  }
})
</script>

<style scoped>

</style>
