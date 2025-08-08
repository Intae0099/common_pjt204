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

      <div class="appointment-wrapper">
        <!-- 상담 있음 -->
        <div v-if="appointments.length">
          <div
            class="appointment-card"
            v-for="appointment in appointments"
            :key="appointment.appointmentId"
            :class="{ selected: selectedAppointmentId === appointment.appointmentId }"
            @click="selectAppointment(appointment.appointmentId)"
          >
            <div class="card-header">
              <span class="card-time">
                {{ formatFullDateTime(appointment.startTime) }} ~
                {{ formatTime(appointment.endTime) }}
              </span>
              <span class="time-diff">
                {{ getTimeDifference(appointment.startTime) }}
              </span>
            </div>
            <div class="client-row">
              <p class="client">
                <span class="client-name">{{ appointment.clientName }}</span>
                <span class="client-label"> 의뢰인</span>
              </p>
              <button class="check-btn" @click.stop="goToApplication(appointment.applicationId)">
                상담신청서 확인하기
              </button>
            </div>
          </div>
        </div>

        <!-- 상담 없음 -->
        <div v-else class="no-appointment">
          <img src="@/assets/bot-no-consult.png" />
          <p>앗! 상담 일정이 없어요</p>
        </div>
      </div>

      <!-- 입장 버튼 -->
      <div class="enter-btn-wrapper">
        <button
          class="enter-btn"
          :disabled="!selectedAppointmentId"
          @click="enterMeeting(selectedAppointmentId)"
        >
          화상상담 입장하기
        </button>
      </div>
    </div>
  </div>

  <ApplicationDetail
  v-if="showDetailModal"
  :data="selectedApplicationData"
  @close="showDetailModal = false"
  />

</template>

<script setup>
import PreviewCamera from '../components/PreviewCamera.vue'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/lib/axios'
import ApplicationDetail from '@/features/profile/user/ApplicationDetail.vue'


const appointments = ref([])
const selectedAppointmentId = ref(null)
const router = useRouter()
const showDetailModal = ref(false)
const selectedApplicationData = ref(null)

const formatFullDateTime = (datetimeStr) => {
  const date = new Date(datetimeStr)
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatTime = (datetimeStr) => {
  const date = new Date(datetimeStr)
  return date.toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
}

const getTimeDifference = (startTime) => {
  const start = new Date(startTime)
  const now = new Date()

  // 날짜 변환 실패 시
  if (isNaN(start)) return '시간 정보 오류'

  const diffMs = start - now
  const diffMinutes = Math.floor(diffMs / (1000 * 60))

  if (diffMinutes < 0) return '이미 시작됨'
  if (diffMinutes < 60) return `${diffMinutes}분 전`

  const hours = Math.floor(diffMinutes / 60)
  const minutes = diffMinutes % 60
  return `${hours}시간 ${minutes}분 전`
}


const selectAppointment = (id) => {
  if (selectedAppointmentId.value === id) {
    // 이미 선택된 항목이면 해제
    selectedAppointmentId.value = null
  } else {
    // 새로운 항목 선택
    selectedAppointmentId.value = id
  }
}


const goToApplication = async (applicationId) => {

  try {
    const { data } = await axios.get(`/api/applications/${applicationId}`)
    const app = data.data.application
    const questions = Object.values(app.recommendedQuestion || {})

    selectedApplicationData.value = {
      ...app,
      recommendedQuestions: questions
    }
    showDetailModal.value = true
  } catch (err) {
    console.error('신청서 조회 실패:', err)
    alert('상담신청서 불러오기 실패')
  }
}


const enterMeeting = async (appointmentId) => {
  if (!appointmentId) {
    alert('입장할 상담을 선택해주세요.');
    return;
  }
  // --- 메인 로직 시작 (try-catch로 에러 관리) ---
  try {
    // 1. 방 생성을 먼저 시도합니다. (상담의 첫 입장자일 경우)
    // 서버에 '이 상담 ID로 화상상담 방을 만들어달라'고 요청합니다.
    await axios.post(`/api/rooms/${appointmentId}`);

    // 성공적으로 방이 생성되었으므로, 이제 참가자로서 토큰을 발급받습니다.
    const res = await axios.post(`/api/rooms/${appointmentId}/participants`);
    const token = res.data.data.openviduToken;

    // 받은 토큰과 상담 ID를 가지고 실제 화상상담 페이지(MeetingRoom)로 이동합니다.
    router.push({ name: 'MeetingRoom', query: { token, appointmentId } });

  } catch (err) {
    // 2. 위 try 블록(방 생성)에서 409 에러가 발생했을 경우의 처리입니다.
    // 만약 발생한 에러가 '409 Conflict'라면, 이는 방이 이미 존재한다는 의미입니다.
    if (err.response?.status === 409) {
      try {
        // 2-1. 이미 방이 존재하므로, 이번엔 '참가자'로서 입장을 시도합니다.
        // 서버에 '이미 있는 이 방에 참가자로 들어갈게요'라고 요청합니다.
        const res = await axios.post(`/api/rooms/${appointmentId}/participants`);

        // 참가자용 토큰을 성공적으로 받아옵니다.
        const token = res.data.data.openviduToken;

        // 화상상담 페이지로 이동합니다.
        router.push({ name: 'MeetingRoom', query: { token, appointmentId } });

      } catch (err2) {
        // 방이 이미 있는데도 참가에 실패한 경우입니다.
        console.error('방 참가 실패:', err2);
        alert('화상상담 입장에 실패했습니다.');
      }
    } else {
      // 2-2. 409가 아닌 다른 모든 에러(예: 500 서버 에러, 네트워크 문제 등)를 처리합니다.
      // 개발자를 위해 콘솔에 상세 에러를 출력하고,
      console.error('방 생성 또는 입장 실패:', err);
      // 사용자에게는 실패했다는 알림을 표시합니다.
      alert('화상상담 방 입장에 실패했습니다.');
    }
  }
};

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/appointments/me')
    appointments.value = data
  } catch (e) {
    console.error('상담 일정 불러오기 실패:', e)
  }
})
</script>

<style scoped>
*{
  font-family: 'Noto Sans KR', sans-serif;
}
.preview-page {
  margin-top: 100px;
  display: flex;
  justify-content: space-between;
  padding: 1rem;
}

.preview-left {
  width: 60%;
}
.preview-left h2 {
  text-align: center;
  margin-bottom: 1rem;
  color: #82A0B3;
  font-size: 1rem;
  font-weight: bold;
}

.preview-right {
  width: 37%;
}
.preview-right h3 {
  color: #072D45;
  font-size: 1rem;
  font-weight: bold;
  margin-bottom: 1rem;
  margin-left: 10px;
}

.appointment-wrapper {
  border: 1px solid #B9D0DF;
  border-radius: 12px;
  padding: 1.5rem;
  height: 400px;
  overflow-y: auto;
  background-color: #fff;
}

.appointment-card {
  border: 1px solid #B9D0DF;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
  background-color: #f9fbff;
  cursor: pointer;
  transition: all 0.2s;
}

.appointment-card.selected {
  border-color: #2E90FA;
  box-shadow: 0 0 0 2px #2E90FA33;
}

.appointment-card p {
  margin: 0.3rem 0;
}

.appointment-card .time {
  font-weight: bold;
  color: #072D45;
}

.appointment-card .client {
  font-weight: bold;
  color: #1D2939;
}

.appointment-card .time-diff {
  font-size: 0.85rem;
  color: #94A3B8;
}

.appointment-card .check-btn {
  font-size: 0.8rem;
  background-color: transparent;
  color: #B9D0DF;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  padding: 0.3rem 0;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  color: #072D45;
}

.client-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
  color: #072D45;
}
.client-name {
  font-weight: bold;
}

.client-label {
  font-weight: 500; /* medium */
}

.no-appointment {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
}
.no-appointment img {
  width: 200px;
  margin-bottom: 1rem;
}
.no-appointment p {
    font-weight: bold;
    color: #82A0B3;
}

.enter-button,
.enter-btn {
  background-color: #2E90FA;
  color: white;
  padding: 0.6rem 1.5rem;
  font-size: 0.95rem;
  font-weight: bold;
  border-radius: 8px;
  border: none;
  transition: background-color 0.3s;
}

.enter-button:disabled,
.enter-btn:disabled {
  background-color: #E4EEF5;
  color: #B9D0DF;
  cursor: not-allowed;
}

.enter-button {
  margin-top: 1rem;
  float: right;
}

.enter-btn-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}
</style>

