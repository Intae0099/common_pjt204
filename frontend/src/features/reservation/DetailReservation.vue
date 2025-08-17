<template>
  <div class="reservation-wrapper">
    <div class="back-button" @click="goBack">
        <ChevronLeftIcon class="chevron-icon" />
        <span>이전</span>
    </div>


    <div v-if="showApplicationPopup" class="application-banner">
      <div class="banner-inner">
        <div class="banner-text">
          <strong>상담신청서를 작성하셨나요?</strong>
          <span>원활한 상담을 위해 예약 전 <strong>상담신청서</strong>를 먼저 작성해주세요.</span>
        </div>
        <button class="banner-cta" @click="goToApplicationForm">
          AI 상담신청서 작성하기
        </button>
        <button class="banner-close" @click="closePopup">×</button>
      </div>
    </div>

    <div class="reservation-page">
      <div class="left-column">
        <div class="card profile-card">
          <img class="profile-card-img" v-if="lawyer?.photo" :src="`data:image/jpeg;base64,${lawyer.photo}`" alt="변호사 프로필" />
          <h2 class="name">{{ lawyer?.name }} 변호사 <img :src="checkbadge" alt="인증 배지" class="check-badge-icon" /></h2>
          <p class="intro">{{ lawyer?.introduction }}</p>
          <div class="profile-tags">
            <span v-for="tag in lawyer?.tags" :key="tag">#{{ getTagName(tag) }}</span>
          </div>
        </div>
      </div>

      <div class="card schedule-card">
        <h3 class="schedule-title">1:1 화상상담 예약</h3>

        <div class="date-row">
          <ol class="stepper" aria-label="예약 단계1">
            <li :class="{ selectedDate }">
              <span class="step-index">1</span> 날짜 선택
            </li>
          </ol>
          <input
            id="dateInput"
            type="date"
            v-model="selectedDate"
            :min="today"
            @change="onDateChange"
            class="date-input"
            :aria-invalid="dateError ? 'true' : 'false'"
            aria-describedby="dateHelp"
          />
          <p id="dateHelp" class="field-help">
            * 날짜를 먼저 선택하세요. (오늘 이전 선택 불가)
          </p>
          <p v-if="dateError" class="field-error">{{ dateError }}</p>

        </div>

        <div class="time-section">
          <div class="time-header">
            <ol class="stepper" aria-label="예약 단계2">
              <li :class="{ selectedDate }">
                <span class="step-index">2</span> 시간 선택
              </li>
            </ol>
            <div class="legend">
              <span class="legend-item"><i class="dot available"></i>가능</span>
              <span class="legend-item"><i class="dot disabled"></i>예약불가/지난시간</span>
              <span class="legend-item"><i class="dot selected"></i>선택됨</span>
            </div>
          </div>

          <div v-if="selectedDate" class="pill-row">
            <span class="pill">선택한 날짜: {{ selectedDate }}</span>
          </div>

          <div class="time-grid-wrapper" :class="{ locked: !selectedDate }" aria-live="polite">
            <div v-if="!selectedDate" class="locked-overlay">
              <div class="locked-text">먼저 날짜를 선택하세요</div>
            </div>

            <div v-if="loadingSlots" class="slots-loading">가능한 시간을 불러오는 중…</div>

            <div v-else class="time-grid">
              <button
                v-for="time in allTimeSlots"
                :key="time"
                :disabled="isTimeDisabled(time)"
                :class="['slot-btn',
                  isTimeDisabled(time) ? 'is-disabled' : '',
                  selectedTime === time ? 'is-selected' : ''
                ]"
                @click="selectTime(time)"
                :aria-pressed="selectedTime === time ? 'true' : 'false'"
              >
                {{ time }}
              </button>
            </div>
          </div>
        </div>

        <div class="reserve-row">
          <button
            class="reserve-button"
            :disabled="!selectedDate || !selectedTime"
            @click="openModal"
          >
            상담 예약하기
          </button>
        </div>

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
import { ChevronLeftIcon } from '@heroicons/vue/24/solid'
import checkbadge from '@/assets/check-badge.png'

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
const loadingSlots = ref(false)
const dateError = ref('')

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

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/lawyers')
  }
}

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


const onDateChange = async () => {
  dateError.value = ''
  selectedTime.value = ''
  // 브라우저 min 속성 이슈 대비: 수동 검증
  if (selectedDate.value && selectedDate.value < today) {
    dateError.value = '오늘 이전 날짜는 선택할 수 없습니다.'
    selectedDate.value = ''
    return
  }
  await fetchUnavailableSlots()
}


const fetchUnavailableSlots = async () => {
  if (!selectedDate.value) return
  loadingSlots.value = true
  try {
    selectedTime.value = ''
    const res = await axios.get(`/api/lawyers/${lawyerId}/unavailable-slot`, {
      params: { date: selectedDate.value }
    })
    const selectedDateStr = selectedDate.value
    const unavailableTimes = res.data
      .filter(slot => slot.startTime.startsWith(selectedDateStr))
      .map(slot => slot.startTime.split(' ')[1].slice(0, 5))
    unavailableSlots.value = unavailableTimes
  } finally {
    loadingSlots.value = false
  }
}

const isPastTime = (time) => {
  if (selectedDate.value !== today) return false  // 오늘만 비교

  const [hour, minute] = time.split(':').map(Number)
  const now = new Date()
  const selectedTimeDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hour, minute)

  return selectedTimeDate < now  // 과거 시간이면 true 반환
}

const isTimeDisabled = (time) => {
  // 날짜 미선택 시 전부 잠금
  if (!selectedDate.value) return true
  // 서버에서 불가 슬롯
  if (unavailableSlots.value.includes(time)) return true
  // 오늘의 과거 시간
  if (isPastTime(time)) return true
  return false
}

const selectTime = (time) => {
  if (isTimeDisabled(time)) return
  // 같은 버튼을 한 번 더 누르면 해제
  selectedTime.value = (selectedTime.value === time) ? '' : time
}



const openModal = () => {
  showModal.value = true
}
</script>


<style>
/* 컨테이너 여백 */
.reservation-wrapper {
  font-family: 'Noto Sans KR', sans-serif;
  padding: 120px 20px 0px;
  max-width: 1200px;
  margin: 0 auto 60px;
}
@media (min-width:1024px) {
  .reservation-wrapper { padding: 120px 80px 0; }
}

/* 뒤로가기 */
.back-button {
  margin: 10px 0 40px -10px;
  font-size: 1rem;
  color: #6c9bcf;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  width: 80px;
  transition: color 0.2s ease-in-out;
}
.back-button:hover { color: #cfcfcf; }
.chevron-icon { width: 20px; height: 20px; }

/* 공통 카드 */
.card {
  background: #fff;
  border: 1px solid #f1f1f1;
  border-radius: 15px;
  box-shadow: 0 6px 16px rgba(0,0,0,.04);
  padding: 20px;
}

/* 2열 레이아웃 */
.reservation-page {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 32px;
  align-items: start;
}
@media (max-width: 960px) {
  .reservation-page { grid-template-columns: 1fr; gap: 16px; }
}

/* 배너 */
.application-banner { margin-bottom: 16px; }
.banner-inner {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  background: #f4f7fb;
  border-radius: 8px;
  padding: 14px 16px;
  gap: 16px;
}
.banner-text { color: #333; display: flex; gap: 10px; flex-wrap: wrap; }
.banner-text strong { font-weight: 700; }
.banner-cta {
  height: 30px;
  padding: 0 1rem;
  border: 1px solid #cfcfcf;
  border-radius: 15px;
  font-size: 12px;
  color: #888;
  background-color: transparent;
}
.banner-cta:hover { border-color: #6c9bcf; color: #6c9bcf; }
.banner-close {
  position: absolute; top: 8px; right: 10px;
  border: none; background: transparent;
  font-size: 20px; color: #8aa; cursor: pointer;
}

/* 프로필 카드 */
.profile-card { text-align: center; }
.profile-card-img {
  width: 240px; height: 300px; object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,.08);
  margin: 4px auto 14px;
}
.check-badge-icon { width: 22px; height: 22px; margin-left: 4px; margin-bottom: 4px; }
.profile-card .name { font-size: 22px; font-weight: 800; color: #192C56; margin: 0 0 8px; }
.profile-card .intro {
  font-size: 13px; color: #333;
  background: #f4f7fb; border: 1px solid #EEF2F7;
  padding: 10px; border-radius: 8px; margin: 0 auto 12px;
}
.profile-tags { display: flex; justify-content: center; flex-wrap: wrap; gap: 8px; }
.profile-tags span {
  background-color: #f1f1f1;
  color: #333;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}

/* 스케줄 카드 */
.schedule-card { padding: 22px; }
.schedule-title {
  font-size: 16px; font-weight: 700; color: #1d2b50;
  margin: 0 0 12px; padding-bottom: 8px;
  border-bottom: 1px solid #cfcfcf;
}
.date-row { margin-bottom: 16px; }
.date-input {
  padding: 8px 10px; font-size: 14px;
  border: 1px solid #CBD5E1; border-radius: 8px; outline: none;
}
.date-input:focus {
  border-color: #6c9bcf;
  box-shadow: 0 0 0 3px rgba(51,165,235,.15);
}

/* 시간 슬롯 */
.time-grid {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 10px; margin-bottom: 24px;
}
@media (max-width: 520px) {
  .time-grid { grid-template-columns: repeat(3, 1fr); }
}
.slot-btn {
  border: 1px solid #cfcfcf; background: #fff; color: #334155;
  padding: 10px 0; border-radius: 8px; font-size: 13px; cursor: pointer;
  transition: all .15s ease;
}
.slot-btn:hover { border-color: #6c9bcf; }
.slot-btn.is-selected {
  background: #6c9bcf; color: #fff; font-weight: 700; border-color: #33A5EB;
  box-shadow: 0 4px 10px rgba(51,165,235,.25);
}
.slot-btn.is-disabled {
  background: #f1f1f1; color: #888; border-color: #EBEFF5; cursor: not-allowed;
  text-decoration: line-through;
}

/* 스텝퍼 */
.stepper {
  display: flex; gap: 16px; list-style: none; padding: 0; margin: 0 0 16px 0;
  align-items: center;
}
.stepper li {
  display: flex; align-items: center; gap: 8px; color: #1d2b50; font-weight: 600;
}
.step-index {
  display: inline-flex; align-items: center; justify-content: center;
  width: 22px; height: 22px; border-radius: 50%;
  border: 1px solid #C8CFD9; font-size: 12px; font-weight: 700;
}

/* 필드 도움말/에러 */
.field-help { margin-top: 6px; font-size: 12px; color: #888; }
.field-error { margin-top: 6px; font-size: 12px; color: #d92d20; }

/* 선택 배지 */
.pill-row { margin-top: 8px; margin-bottom:12px; }
.pill {
  display: inline-block; background: #f4f7fb; color: #1d2b50; border: 1px solid #6c9bcf;
  padding: 6px 10px; border-radius: 999px; font-size: 12px; font-weight: 600;
}

/* 시간 영역 */
.time-section { margin-top: 12px; }
.time-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;
}
.legend { display: flex; gap: 12px; font-size: 12px; color: #64748b; }
.legend-item { display: inline-flex; align-items: center; gap: 6px; }
.dot {
  display: inline-block; width: 10px; height: 10px; border-radius: 50%;
  border: 1px solid #CBD5E1; background: #fff;
}
.dot.disabled { background: #f1f1f1; }
.dot.selected { background: #6c9bcf; border-color: #33A5EB; }

/* 시간 그리드 잠금 */
.time-grid-wrapper { position: relative; }
.time-grid-wrapper.locked {
  pointer-events: none; filter: grayscale(0.3) opacity(0.7);
}
.locked-overlay {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(to bottom, rgba(255,255,255,.8), rgba(255,255,255,.9));
  border-radius: 8px; z-index: 1;
}
.locked-text {
  font-size: 14px; color: #64748b; background: #fff; border: 1px dashed #CBD5E1;
  padding: 8px 12px; border-radius: 8px;
}

/* 시간 로딩 */
.slots-loading { font-size: 13px; color: #64748b; padding: 12px 0; }

/* 예약 버튼 */
.reserve-row { display: flex; justify-content: center; }
.reserve-button {
  background: #192C56; color: #fff; font-weight: 400; border: none;
  padding: 8px 24px; border-radius: 8px; cursor: pointer; letter-spacing: .2px;
}
.reserve-button:hover { filter: brightness(1.05); }
.reserve-button:disabled { background: #C8CFD9; cursor: not-allowed; }

</style>
