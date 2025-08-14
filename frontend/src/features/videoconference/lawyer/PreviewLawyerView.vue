<template>
  <div class="preview-page">
    <div class="preview-left">
      <h2>화면 미리보기</h2>
      <PreviewCamera />
    </div>

    <div class="preview-right">
      <h3>오늘 예약된 상담</h3>

      <div class="appointment-wrapper">
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
                <span class="client-name">{{ appointment.counterpartName }}</span>
                <span class="client-label"> 의뢰인</span>
              </p>
              <button class="check-btn" @click.stop="goToApplication(appointment.applicationId)">
                상담신청서 확인하기
              </button>
            </div>
          </div>
        </div>

        <div v-else class="no-appointment">
          <img src="@/assets/bot-no-consult.png" />
          <p>앗! 상담 일정이 없어요</p>
        </div>
      </div>

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

  // "진행중" 또는 "N분 후"로 표시되도록 수정
  if (diffMinutes < 0) return '진행중'
  if (diffMinutes < 60) return `${diffMinutes}분 후`

  const hours = Math.floor(diffMinutes / 60)
  const minutes = diffMinutes % 60
  return `${hours}시간 ${minutes}분 후`
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
  try {
    // 방 생성을 먼저 시도
    const res = await axios.post(`/api/rooms/${appointmentId}`);
    const token = res.data.data.openviduToken;
    router.push({ name: 'MeetingRoom', query: { token, appointmentId } });
  } catch (err) {
    // 방이 이미 존재할 경우(409 Conflict) 참가자로 입장
    if (err.response?.status === 409) {
      try {
        const res = await axios.post(`/api/rooms/${appointmentId}/participants`);
        const token = res.data.data.openviduToken;
        router.push({ name: 'MeetingRoom', query: { token, appointmentId } });
      } catch (err2) {
        // 서버가 보내준 구체적인 에러 메시지를 확인합니다.
        const serverMessage = err2.response?.data?.message || '서버로부터 상세 메시지를 받지 못했습니다.';
        console.error('방 참가 실패! 서버 응답:', serverMessage, err2);

        alert(`화상상담 입장에 실패했습니다.\n서버 메시지: ${serverMessage}`);
      }
    } else {
      // 그 외 다른 에러
      console.error('방 생성 실패:', err);
      alert('화상상담 방 생성에 실패했습니다.');
    }
  }
};

onMounted(async () => {
  try {
    // API 호출 시 params를 추가하여 승인된('CONFIRMED') 상담만 가져오도록 변경
    // const { data: allAppointments } = await axios.get('/api/appointments/me', {
    //   params: { status: 'CONFIRMED' },
    // });
    /* 실제코드. 추후 주석 해제
    // 오늘 날짜의, 아직 끝나지 않은 예약만 필터링합니다.
    const now = new Date();
    const todaysAppointments = allAppointments.filter(
      (appointment) => {
        const startTime = new Date(appointment.startTime);
        const endTime = new Date(appointment.endTime);

        // 조건 1: 상담 시작일이 오늘인지 확인 (연, 월, 일 비교)
        const isToday =
          startTime.getFullYear() === now.getFullYear() &&
          startTime.getMonth() === now.getMonth() &&
          startTime.getDate() === now.getDate();

        // 조건 2: 상담 종료 시간이 현재 시간 이후인지 확인
        const hasNotEnded = endTime > now;

        return isToday && hasNotEnded;
      }
    );
    appointments.value = todaysAppointments;
    */
    // 1. 'CONFIRMED' 상태와 'IN_PROGRESS' 상태에 대한 API 요청을 각각 생성합니다.
    const confirmedPromise = axios.get('/api/appointments/me', {
      params: { status: 'CONFIRMED' },
    });
    const inProgressPromise = axios.get('/api/appointments/me', {
      params: { status: 'IN_PROGRESS' }, // '진행중' 상태명이 다르다면 수정 필요
    });

    // 2. Promise.all을 사용해 두 요청을 동시에 보냅니다.
    const [confirmedResponse, inProgressResponse] = await Promise.all([
      confirmedPromise,
      inProgressPromise,
    ]);

    // 3. 각 응답에서 데이터 배열을 추출합니다. (데이터가 없을 경우 빈 배열로 처리)
    const confirmedAppointments = confirmedResponse.data || [];
    const inProgressAppointments = inProgressResponse.data || [];
    const allAppointments = [...confirmedAppointments, ...inProgressAppointments];

    // [개발용. 추후 삭제예정] 모든 확정된 상담 목록을 불러옵니다.
    appointments.value = allAppointments;
    //여기까지 개발용

  } catch (e) {
    console.error('상담 일정 불러오기 실패:', e);
  }
});
</script>

<style scoped>
.preview-left :deep(video) {
  transform: scaleX(-1);
}

* {
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
