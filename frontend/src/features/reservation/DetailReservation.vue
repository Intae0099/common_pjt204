<template>

  <div class="reservation-wrapper">

    <div class="back-button" @click="$router.back()">
      <span class="arrow-icon">←</span> <span>이전</span>
    </div>

    <div v-if="showApplicationPopup" class="application-popup">
      <div class="popup-content">
        <button class="close-btn" @click="closePopup">
          <span class="icon">×</span>
        </button>
        <p><strong>상담신청서를 작성하셨나요?</strong></p>
        <p>원활한 상담을 위해 예약 전 <strong>상담신청서</strong>를 먼저 작성해주세요. 📄</p>
        <span class="application-link" @click="goToApplicationForm">
          AI 상담신청서 작성하기 ➡️
        </span>
      </div>
    </div>

    <!-- ✅ 2. 두 박스는 같은 선상 수평 정렬 -->
    <div class="reservation-page">
      <!-- 좌측 프로필 박스 -->
      <div class="left-column">
        <div class="profile-box">
          <img v-if="lawyer?.photo" :src="`data:image/jpeg;base64,${lawyer.photo}`" alt="변호사 프로필" />
          <h2>{{ lawyer?.name }} 변호사</h2>
          <p>{{ lawyer?.introduction }}</p>
          <div class="profile-tags">
            <span v-for="tag in lawyer?.tags" :key="tag">#{{ getTagName(tag) }}</span>
          </div>
        </div>
      </div>


      <!-- 우측 스케줄 -->
      <div class="schedule-box">
        <!-- 캘린더 자리 -->
        <h3 class="schedule-title">상담 가능 날짜 및 시간 선택</h3>
        <!-- 여기에 실제 캘린더 컴포넌트 사용 -->
        <input
          type="date"
          v-model="selectedDate"
          :min="today"
          @change="fetchUnavailableSlots"
          class="date-input"
        />

        <!-- 시간 선택 -->
        <div class="time-grid">
          <button
            v-for="time in allTimeSlots"
            :key="time"
            :disabled="!selectedDate || unavailableSlots.includes(time) || isPastTime(time)"
            :class="[
              'btn',
              (!selectedDate || unavailableSlots.includes(time) || isPastTime(time)) ? 'disabled' : '',
              selectedTime === time ? 'selected' : ''
            ]"
            @click="() => {
              if (selectedDate && !unavailableSlots.includes(time) && !isPastTime(time)) selectedTime = time
            }"
          >
            {{ time }}
          </button>
        </div>

        <button
          class="reserve-button"
          :disabled="!selectedDate || !selectedTime"
          @click="openModal"
        >
          상담 예약하기
        </button>

        <div v-if="showModal">
          <ApplicationChoiceModal
            :lawyerId="lawyerId"
            :selectedDate="selectedDate"
            :selectedTime="selectedTime"
            @close="showModal = false"
          />
        </div>
      </div>
    </div>
  </div>
</template>



<script setup>
import { ref, onMounted } from 'vue'
import axios from '@/lib/axios'
import { useRoute, useRouter } from 'vue-router'
import ApplicationChoiceModal from '@/features/reservation/ApplicationChoiceModal.vue'
import { TAG_MAP } from '@/constants/lawyerTags'

const router = useRouter()
const route = useRoute()
const lawyerId = route.params.id
const lawyer = ref(null)
const unavailableSlots = ref([])
const selectedDate = ref('')
const selectedTime = ref('')
const showModal = ref(false)
const today = new Date().toISOString().split('T')[0]
const allTimeSlots = [
  '08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
  '11:00', '11:30', '13:00', '13:30', '14:00', '14:30',
  '15:00', '15:30', '16:00', '16:30'
]

// ✅ 태그 ID ↔ 이름 매핑
const tagMap = TAG_MAP
const showApplicationPopup = ref(true) // 팝업 상태 추가

const getTagName = (id) => {
  const tag = tagMap.find(t => String(t.id) === String(id))  // 문자열 매핑 안전하게
  return tag ? tag.name : '알 수 없음'
}

onMounted(async () => {
  selectedDate.value = today
  await fetchLawyerInfo()
  await fetchUnavailableSlots()
  window.scrollTo(0, 0)   // 페이지 진입 시 최상단 이동
})

const closePopup = () => {
  showApplicationPopup.value = false;
};

const goToApplicationForm = () => {
  // TODO: 실제 AI 상담신청서 페이지 경로로 수정해주세요.
  alert('AI 상담신청서 페이지로 이동합니다.');
  router.push('/consult-form');
};

const fetchLawyerInfo = async () => {
  const res = await axios.get(`/api/lawyers/list`)
  const found = res.data.find(l => String(l.lawyerId) === lawyerId)

  if (found) {
    lawyer.value = {
      ...found,
      lawyerId: String(found.lawyerId),
      tags: found.tags.map(tagId => String(tagId)) // 숫자 → 문자열 변환
    }
  }
}

const fetchUnavailableSlots = async () => {
  if (!selectedDate.value) return
  selectedTime.value = ''
  const res = await axios.get(`/api/lawyers/${lawyerId}/unavailable-slot`, {
    params: { date: selectedDate.value }
  })
  const selectedDateStr = selectedDate.value
  const unavailableTimes = res.data
    .filter(slot => slot.startTime.startsWith(selectedDateStr))
    .map(slot => {
      const timePart = slot.startTime.split(' ')[1].slice(0, 5) // "HH:MM"
      return timePart
    })

  unavailableSlots.value = unavailableTimes
}

const isPastTime = (time) => {
  if (selectedDate.value !== today) return false  // 오늘만 비교

  const [hour, minute] = time.split(':').map(Number)
  const now = new Date()
  const selectedTimeDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hour, minute)

  return selectedTimeDate < now  // 과거 시간이면 true 반환
}

const openModal = () => {
  console.log('✅ 모달 열림 시도', selectedDate.value, selectedTime.value)
  showModal.value = true
}
</script>


<style>
/* 최상위 여백 적용 */
.reservation-wrapper {
  padding: 120px 20px 0 20px;  /* 위쪽 패딩 추가 + 좌우 20px 유지 */
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

/* 웹 기준 좌우 여백 확장 */
@media (min-width: 1024px) {
  .reservation-wrapper {
    padding: 120px 80px 0 80px;  /* ← 넉넉하게 여백 줌 */
  }
}

/* ── 상담신청서 팝업 스타일 추가 ──────────────────── */
.application-popup {
  background-color: #f0f8ff; /* 연한 하늘색 배경 */
  border: 1px solid #cce5ff;
  border-radius: 8px;
  padding: 15px 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.popup-content {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.popup-content p {
  margin: 0;
  font-size: 15px;
  color: #333;
}

.application-link {
  font-weight: bold;
  color: #1d2b50;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.2s ease;
  white-space: nowrap;
}

.application-link:hover {
  color: #0056b3;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 0;
  font-size: 20px;
  color: #888;
}

/* 모바일 화면에서 팝업 레이아웃 조정 */
@media (max-width: 768px) {
  .popup-content {
    flex-direction: column;
    align-items: flex-start;
  }
  .popup-content p {
    font-size: 14px;
  }
}

/* 레이아웃 */
.reservation-page {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  gap: 80px;
}

/* 왼쪽 열: 이전 버튼 + 프로필 */
.left-column {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

/* '이전' 버튼 디자인 */
.back-button {
  margin-bottom: 32px;
  color: #506176;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  margin-left: 0;
}

/* ✅ 웹 기준 강력 이동 */
@media (min-width: 1024px) {
  .back-button {
    margin-left: 160px; /* 프로필 시작선 딱 맞춤 */
  }
}

.arrow-icon {
  font-size: 16px;
}



/* 프로필 영역 */
.profile-box {
  text-align: center;
  max-width: 280px;
}

.profile-box img {
  width: 240px;
  height: 300px;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  margin-bottom: 1rem;
}

.profile-box h2 {
  font-size: 22px;
  font-weight: 700;
  margin: 0.5rem 0;
  color: #192C56;
}

.profile-box p {
  font-size: 13px;
  color: #555;
  background-color: #f3f6f9;
  padding: 10px;
  border-radius: 10px;
  margin-bottom: 1rem;
}

.profile-tags {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}

.profile-tags span {
  background-color: #e8ebf0;
  color: #333;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}

/* 스케줄 영역 */
.schedule-box {
  max-width: 500px;
}

.schedule-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #192C56;
  border-bottom: 1px solid #ddd;
  padding-bottom: 8px;
}

/* date input (임시 캘린더 대체용) */
.date-input {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 14px;
}

/* 시간 선택 */
.time-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 30px;
}

.btn {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  font-size: 13px;
}

.btn.disabled {
  background-color: #f5f5f5;
  color: #bbb;
  border-color: #e0e0e0;
  cursor: not-allowed;
  text-decoration: line-through;
}

.btn.selected {
  background-color: #33A5EB;
  color: white;
  font-weight: bold;
  border-color: #33A5EB;
}

/* 예약 버튼 */
.reserve-button {
  background-color: #192C56;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: bold;
  cursor: pointer;
}

.reserve-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}


</style>
