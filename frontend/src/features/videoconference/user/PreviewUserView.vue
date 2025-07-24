<template>
    <div class="preview-page">
      <!-- 좌측: 미리보기 영상 -->
      <div class="preview-left">
        <h2>화면 미리보기</h2>
        <PreviewCamera />
        <p>상담 전 궁금한 점 있으신가요?</p>
        <router-link to="/ai-consult">
          <button>AI 상담 받으러 가기 →</button>
        </router-link>
      </div>

      <!-- 우측: 예약된 상담 -->
      <div class="preview-right">
        <h3>오늘 예약된 상담</h3>
        <div v-if="appointments.length">
          <div v-for="(appointment, index) in appointments" :key="index">
            <p>{{ appointment.date }} {{ appointment.time }}</p>
            <p>{{ appointment.lawyerName }} 변호사</p>
            <button>상담신청서 확인하기</button>
          </div>
          <button>화상상담 입장하기</button>
        </div>
        <div v-else>
          <p>앗! 상담 일정이 없어요</p>
          <router-link to="/lawyers">변호사 조회</router-link> |
          <router-link to="/ai-consult">AI 상담받기</router-link>
          <button disabled>화상상담 입장하기</button>
        </div>
      </div>
    </div>
</template>

<script setup>
import PreviewCamera from '../PreviewCamera.vue'
import { ref, onMounted } from 'vue'
// import axios from '@/lib/axios'

const appointments = ref([])

onMounted(async () => {

  // 백엔드 연결 전 임시 데이터
  appointments.value = [
    {
      date: '2025.07.22(화)',
      time: '15:00 ~ 15:15',
      lawyerName: '홍길동',
    },
    {
      date: '2025.07.22(화)',
      time: '17:00 ~ 17:15',
      lawyerName: '김영희',
    },
  ]
  // try {
  //   const { data } = await axios.get('/api/appointments/me')
  //   appointments.value = data
  // } catch (e) {
  //   console.error('상담 일정 불러오기 실패:', e)
  // }
})
</script>

<style scoped>

</style>
