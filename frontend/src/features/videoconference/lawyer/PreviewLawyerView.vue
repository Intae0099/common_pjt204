<template>
    <div class="preview-page">
      <!-- 왼쪽: 카메라 미리보기 -->
      <div class="preview-left">
        <h2>화면 미리보기</h2>
        <PreviewCamera />
      </div>

      <!-- 오른쪽: 오늘 예약된 상담 -->
      <div class="preview-right">
        <h3>오늘 예약된 상담</h3>

        <!-- 예약이 있을 때 -->
        <div v-if="appointments.length">
          <div
            class="appointment-card"
            v-for="(appointment, index) in appointments"
            :key="index"
            :class="{ selected: index === 0 }"
          >
            <p>{{ appointment.date }} {{ appointment.time }}</p>
            <p>{{ appointment.clientName }} 의뢰인</p>
            <button>상담신청서 확인하기</button>
          </div>
          <button class="enter-button">화상상담 입장하기</button>
        </div>

        <!-- 예약이 없을 때 -->
        <div v-else class="no-appointment">
          <p>앗! 상담 일정이 없어요</p>
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

onMounted(() => {

  // try {
  //   const { data } = await axios.get('/api/appointments/me')
  //   appointments.value = data
  // } catch (err) {
  //   console.error('API 호출 실패:', err)

  appointments.value = [
    {
      date: '2025.07.22(화)',
      time: '15:00 ~ 15:15',
      clientName: '전혜지',
    },
    {
      date: '2025.07.22(화)',
      time: '15:30 ~ 16:00',
      clientName: '이정연',
    },
    {
      date: '2025.07.22(화)',
      time: '16:00 ~ 16:15',
      clientName: '윤규성',
    },
    {
      date: '2025.07.22(화)',
      time: '16:30 ~ 17:00',
      clientName: '전혜지',
    },
  ]
})

</script>

<style scoped>

</style>
