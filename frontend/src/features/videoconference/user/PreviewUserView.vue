<template>
  <div class="preview-page">
    <!-- 왼쪽: 카메라 미리보기 -->
    <div class="preview-left">
      <h2>화면 미리보기</h2>
      <PreviewCamera />
      <div class="before-consult-msg">
        <p class="title">
          <Smile class="smile-icon" />
          상담 전 궁금한 게 있으신가요?
        </p>
        <p class="desc">
          상담 전에 궁금한 내용을 AI에게 먼저 물어보세요.<br />
          빠르고 간편하게 상담서를 자동으로 작성할 수 있어요!
        </p>
        <router-link to="/ai-consult" class="ai-link">
          AI 상담 받으러 가기
          <MoveRight class="arrow-icon" />
        </router-link>
      </div>
    </div>

    <!-- 오른쪽: 상담 리스트 -->
    <div class="preview-right">
      <h3>오늘 예약된 상담</h3>
      <div class="appointment-wrapper">
        <!-- 예약 존재 -->
        <div v-if="appointments.length">
          <div
            v-for="(appointment, index) in appointments"
            :key="appointment.appointmentId"
            class="appointment-card"
            :class="{ selected: index === 0 }"
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
            <div class="card-body">
              <img :src="appointment.profileImage || defaultImage" class="lawyer-img" />
              <div class="card-info">
                <p class="lawyer-name">
                  <strong class="name-bold">{{ appointment.lawyerName }}</strong>
                  <span class="name-medium"> 변호사</span>
                </p>
                <div class="tags">
                  <span
                    class="tag"
                    v-for="tagId in appointment.tags"
                    :key="tagId"
                  >
                    #{{ tagMap[tagId] || '기타' }}
                  </span>
                </div>
              </div>
              <button class="view-btn" @click="goToApplication(appointment.applicationId)">상담신청서 확인하기</button>
            </div>
          </div>
        </div>

        <!-- 예약 없음 -->
        <div v-else class="no-appointments">
          <img src="@/assets/bot-no-consult.png" class="no-img" />
          <p class="no-msg">앗! 상담 일정이 없어요!</p>
          <div class="links">
            <router-link to="/lawyers">변호사 조회</router-link> |
            <router-link to="/ai-consult">AI 상담받기</router-link>
          </div>
        </div>
      </div>

      <div class="enter-btn-wrapper">
        <button
          class="enter-btn"
          :disabled="!appointments.length || !canEnterMeeting(appointments[0].startTime, appointments[0].endTime)"
          @click="enterMeeting(appointments[0]?.appointmentId)"
        >
          화상상담 입장하기
        </button>
      </div>
    </div>
    <ApplicationDetail
      v-if="showDetailModal"
      :data="selectedApplicationData"
      @close="showDetailModal = false"
    />
  </div>
</template>


<script setup>
import PreviewCamera from '../components/PreviewCamera.vue'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/lib/axios'
import ApplicationDetail from '@/features/profile/user/ApplicationDetail.vue'
import { Smile, MoveRight } from 'lucide-vue-next'
import { TAG_MAP } from '@/constants/lawyerTags'

const appointments = ref([])
const defaultImage = '/default-profile.png'
const router = useRouter()
const showDetailModal = ref(false)
const selectedApplicationData = ref(null)
const tagMap = TAG_MAP

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

  if (isNaN(start)) return '시간 정보 오류'

  const diffMs = start - now
  const diffMinutes = Math.floor(diffMs / (1000 * 60))

  if (diffMinutes < 0) return '이미 시작됨'
  if (diffMinutes < 60) return `${diffMinutes}분 후`

  const hours = Math.floor(diffMinutes / 60)
  const minutes = diffMinutes % 60
  return `${hours}시간 ${minutes}분 후`
}

const canEnterMeeting = (startTime, endTime) => {
  const now = new Date()
  const start = new Date(startTime)
  const end = new Date(endTime)

  return now >= new Date(start.getTime() - 10 * 60 * 1000) && now < end
}



onMounted(async () => {

  try {
    const { data: appointmentData } = await axios.get('/api/appointments/me')

    const appointmentsWithLawyerInfo = await Promise.all(
      appointmentData.map(async (appointment) => {
        try {
          const { data: lawyer } = await axios.get(`/api/lawyers/${appointment.lawyerId}`)
          return {
            ...appointment,
            lawyerName: lawyer.name,
            profileImage: lawyer.photo,
            tags: lawyer.tags
          }
        } catch (e) {
          console.error('변호사 정보 불러오기 실패:', e)
          return appointment
        }
      })
    )

    appointments.value = appointmentsWithLawyerInfo.length
  } catch (e) {
    console.error('상담 일정 불러오기 실패:', e)

  }
})


const goToApplication = async (applicationId) => {
  try {
    const { data } = await axios.get(`/api/applications/${applicationId}`)
    const questions = Object.values(data.recommendedQuestion || {})

    selectedApplicationData.value = {
      ...data,
      recommendedQuestions: questions
    }
    showDetailModal.value = true
  } catch (err) {
    console.error('상담신청서 상세 조회 실패:', err)
    alert('상담신청서를 불러오는 데 실패했습니다.')
  }
}

const enterMeeting = async (appointmentId) => {
  try {
    const res = await axios.post(`/api/rooms/${appointmentId}`)
    const token = res.data.data.openviduToken
    router.push({ name: 'MeetingRoom', query: { token, appointmentId } })
  } catch (err) {
    if (err.response?.status === 409) {
      try {
        const res = await axios.post(`/api/rooms/${appointmentId}/participants`)
        const token = res.data.data.openviduToken
        router.push({ name: 'MeetingRoom', query: { token, appointmentId } })
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
  padding: 1rem;
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
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: #072D45;
    }
    .smile-icon {
      width: 20px;
      height: 20px;
      color: #82A0B3;
    }
    .desc {
      margin: 0.5rem 0;
      color: #82A0B3;
      font-size: 0.9rem;
    }
    .ai-link {
      font-weight: medium;
      color: #2A5976;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    .arrow-icon {
      width: 16px;
      height: 16px;
      stroke-width: 2;
    }

  }
}

/* 최종 스타일 */
.preview-right {
  width: 37%;
}
.preview-right h3{
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
  height: 480px;
  overflow-y: auto;
}

.appointment-card {
  border: 1px solid #ccc;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
  background-color: #f9fbff;
  transition: all 0.3s;
}

.appointment-card.selected {
  border-color: #2E90FA;
  box-shadow: 0 0 0 2px #2E90FA33;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
}

.card-time {
  color: #1D2939;
  font-weight: bold;
  font-size: 0.95rem;
}

.time-diff {
  font-size: 0.85rem;
  color: #94A3B8;
}

.card-body {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.lawyer-img {
  width: 90px;
  height: 100px;
  border-radius: 12px;
  object-fit: cover;
  border: 1px solid #E0E7ED;
}

.card-info {
  flex-grow: 1;
}
.card-time{
  color: #072D45;
}
.lawyer-name {
  margin-bottom: 10px;
  .name-bold {
    font-weight: 700; /* 또는 bold */
  }

  .name-medium {
    font-weight: 500; /* medium (보통 500 정도) */
  }

}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.tag {
  background-color: #E6EDF5;
  color: #516F90;
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 8px;
}

.view-btn {
  margin-top: 75px;
  font-size: 0.8rem;
  background-color: transparent;
  color: #B9D0DF;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
  border: none;
}
.no-appointments {
  text-align: center;
  .no-img {
    width: 200px;
    margin-top: 40px;
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
.enter-btn-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}

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

.enter-btn:disabled {
  background-color: #E4EEF5;
  color: #B9D0DF;
  cursor: not-allowed;
}

</style>
