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

      <div v-if="appointments.length">
        <div
          class="appointment-card"
          v-for="appointment in appointments"
          :key="appointment.appointmentId"
          :class="{ selected: selectedAppointmentId === appointment.appointmentId }"
          @click="selectAppointment(appointment.appointmentId)"
        >
          <p>{{ formatDateTime(appointment.startTime) }}</p>
          <p>의뢰인 ID: {{ appointment.clientId }}</p>
          <button @click.stop="goToApplication(appointment.applicationId)">
            상담신청서 확인하기
          </button>
        </div>

        <!-- 선택된 예약이 있을 때만 입장 가능 -->
        <button
          class="enter-button"
          :disabled="!selectedAppointmentId"
          @click="enterMeeting(selectedAppointmentId)"
        >
          화상상담 입장하기
        </button>
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
import PreviewCamera from '../components/PreviewCamera.vue'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/lib/axios'

const appointments = ref([])
const selectedAppointmentId = ref(null)
const router = useRouter()

const formatDateTime = (startTime) => {
  const date = new Date(startTime)
  const dateStr = date.toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' })
  const timeStr = date.toTimeString().slice(0, 5)
  return `${dateStr} ${timeStr}`
}

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/appointments/me')
    appointments.value = data
  } catch (e) {
    console.error('상담 일정 불러오기 실패:', e)
  }
})

const selectAppointment = (id) => {
  selectedAppointmentId.value = id
}

const goToApplication = (applicationId) => {
  router.push({ name: 'ApplicationDetail', params: { applicationId } })
}

const enterMeeting = async (appointmentId) => {
  try {
    await axios.post(`/api/rooms/${appointmentId}`).catch((err) => {
      console.log('방 생성 실패 또는 이미 존재함', err.response?.data || err)
    })
    const res = await axios.post(`/api/rooms/${appointmentId}/participants`)
    const token = res.data.data.openviduToken

    router.push({
      name: 'MeetingRoom',
      query: {
        token,
        appointmentId
      }
    })
  } catch (err) {
    console.error('화상상담 입장 실패:', err)
    alert('화상상담 방 입장에 실패했습니다.')
  }
}
</script>
