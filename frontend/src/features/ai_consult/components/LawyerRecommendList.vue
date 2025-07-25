<template>
  <div>
    <h2>당신에게 적합한 변호사 추천</h2>
    <p>AI가 분석한 결과를 바탕으로 변호사를 추천합니다.</p>

    <div>
      <div v-for="lawyer in lawyers" :key="lawyer.id">
        <img :src="lawyer.image" alt="변호사 이미지" />
        <h3>{{ lawyer.name }}</h3>
        <p>전문 분야: {{ lawyer.specialty }}</p>
        <p>{{ lawyer.intro }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const lawyers = ref([])

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/lawyers/recommend')
    lawyers.value = data
  } catch (error) {
    console.error('변호사 추천 요청 실패:', error)
  }
})
</script>

<style scoped>

</style>
