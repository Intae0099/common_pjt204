<template>
  <div class="preview-page">
    <!-- 왼쪽: 카메라 미리보기 -->
    <div class="preview-left">
      <h2>화면 미리보기</h2>
      <PreviewCamera />
      <div class="before-consult-msg">
        <p class="title">🙂 상담 전 궁금한 게 있으신가요?</p>
        <p class="desc">
          상담 전에 궁금한 내용을 AI에게 먼저 물어보세요.<br />
          빠르고 간편하게 상담서를 자동으로 작성할 수 있어요!
        </p>
        <router-link to="/ai-consult" class="ai-link">AI 상담 받으러 가기 →</router-link>
      </div>
    </div>

    <!-- 오른쪽: 상담 리스트 -->
    <div class="preview-right">
      <h3>오늘 예약된 상담</h3>
      <div class="appointment-wrapper">
        <!-- 예약 존재 -->
        <div v-if="appointments.length">
          <div
            v-for="appointment in appointments"
            :key="appointment.appointmentId"
            class="appointment-card"
          >
            <div class="info">
              <img :src="defaultImage" class="lawyer-img" />
              <div class="meta">
                <p class="time">{{ formatDateTime(appointment.startTime) }}</p>
                <p class="name">예약된 상담</p>
              </div>
            </div>
            <button @click="goToApplication(appointment.applicationId)">상담신청서 확인하기</button>
          </div>
          <button
            class="enter-btn"
            @click="enterMeeting(appointments[0].appointmentId)"
          >
            화상상담 입장하기
          </button>
        </div>

        <!-- 예약 없음 -->
        <div v-else class="no-appointments">
          <img src="@/assets/bot-no-consult.png" class="no-img" />
          <p class="no-msg">앗! 상담 일정이 없어요!</p>
          <div class="links">
            <router-link to="/lawyers">변호사 조회</router-link> |
            <router-link to="/ai-consult">AI 상담받기</router-link>
          </div>
          <button class="enter-btn" disabled>화상상담 입장하기</button>
        </div>
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
const defaultImage = '/default-profile.png'
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

const goToApplication = (applicationId) => {
  router.push({ name: 'ApplicationDetail', params: { applicationId } })
}

const enterMeeting = async (appointmentId) => {
  try {
    // 1. 방 생성 요청
    const res = await axios.post(`/api/rooms/${appointmentId}`)
    const token = res.data.openviduToken
    router.push({
      name: 'MeetingRoom',
      query: { token, appointmentId }
    })
  } catch (err) {
    // 2. 방이 이미 존재하면 참가 요청
    if (err.response?.status === 409) {
      try {
        const res = await axios.post(`/api/rooms/${appointmentId}/participants`)
        const token = res.data.openviduToken
        router.push({
          name: 'MeetingRoom',
          query: { token, appointmentId }
        })
      } catch (err2) {
        console.error('방 참가 실패:', err2)
        alert('화상상담 입장에 실패했습니다.')
      }
    } else {
      console.error('방 생성 실패:', err)
      alert('화상상담 방 생성에 실패했습니다.')
    }
  }
}

</script>

<style scoped>
*{
  font-family: 'Noto Sans KR', sans-serif;
}
.preview-page {
  margin-top: 100px;
  display: flex;
  justify-content: space-between;
  padding: 2rem;
}

.preview-left {
  width: 60%;
  h2 {
    text-align: center;
    margin-bottom: 1rem;
    color: #82A0B3;
    font-size: 1rem;
    font-weight: bold;
  }
  .before-consult-msg {
    margin-top: 2rem;
    .title {
      font-weight: bold;
    }
    .desc {
      margin: 0.5rem 0;
      color: gray;
    }
    .ai-link {
      font-weight: bold;
      color: #007aff;
    }
  }
}

.preview-right {
  width: 35%;
  h3 {
    margin-left: 5px;
    margin-bottom: 1rem;
    color: #072D45;
    font-size: 1rem;
    font-weight: bold;
  }

  .appointment-wrapper {
    border: 1px solid #B9D0DF;
    border-radius: 12px;
    padding: 1.5rem;
    height: 500px;
  }
  .appointment-card {
    border: 1px solid #ccc;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    background-color: #f9fbff;
    &.selected {
      border-color: #007aff;
      box-shadow: 0 0 0 2px #007aff33;
    }
    .info {
      display: flex;
      gap: 1rem;
    }
    .lawyer-img {
      width: 60px;
      height: 60px;
      border-radius: 50%;
    }
    .meta {
      .time {
        font-weight: bold;
        margin-bottom: 0.3rem;
      }
      .tags {
        .tag {
          font-size: 0.8rem;
          margin-right: 0.3rem;
          background: #eee;
          border-radius: 8px;
          padding: 0.2rem 0.5rem;
        }
      }
    }
  }

  .no-appointments {
    text-align: center;
    .no-img {
      width: 100px;
      margin-bottom: 1rem;
    }
    .no-msg {
      font-weight: bold;
      color: #82A0B3;
    }
    .links {
      margin: 0.5rem 0;
      color: #2A5976;
      font-weight: bold;
      a {
        color: inherit;
        text-decoration: none;
      }
    }
  }

  .enter-btn {
    margin-top: 1rem;
    width: 100%;
    background-color: #007aff;
    color: white;
    padding: 0.8rem;
    border-radius: 10px;
    &:disabled {
      background-color: #ddd;
    }
  }
}

</style>
