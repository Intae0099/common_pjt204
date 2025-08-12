<template>
  <div class="reservation-wrapper">
    <div class="back-button" @click="goBack">
        <ChevronLeftIcon class="chevron-icon" />
        <span>이전</span>
    </div>


    <!-- ▲ 안내 배너 -->
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

    <!-- 본문 2열 -->
    <div class="reservation-page">
      <!-- 좌측: 변호사 카드 -->
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

      <!-- 우측: 스케줄 카드 -->
      <div class="card schedule-card">
        <h3 class="schedule-title">상담 가능 날짜 및 시간 선택</h3>

        <div class="date-row">
          <input
            type="date"
            v-model="selectedDate"
            :min="today"
            @change="fetchUnavailableSlots"
            class="date-input"
          />
        </div>

        <div class="time-grid">
          <button
            v-for="time in allTimeSlots"
            :key="time"
            :disabled="!selectedDate || unavailableSlots.includes(time) || isPastTime(time)"
            :class="[
              'slot-btn',
              (!selectedDate || unavailableSlots.includes(time) || isPastTime(time)) ? 'is-disabled' : '',
              selectedTime === time ? 'is-selected' : ''
            ]"
            @click="() => {
              if (selectedDate && !unavailableSlots.includes(time) && !isPastTime(time)) selectedTime = time
            }"
          >
            {{ time }}
          </button>
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
/* 컨테이너 여백 */
.reservation-wrapper{
  font-family: 'Noto Sans KR', sans-serif;
  padding: 120px 20px 0px;
  max-width: 1200px;
  margin: 0 auto;
  margin-bottom: 60px;
}
@media (min-width:1024px){
  .reservation-wrapper{ padding:120px 80px 0; }
}

/* 뒤로가기 */
.back-button {
  margin-top: 10px;
  margin-bottom: 40px;
  margin-left: -10px;
  font-size: 1rem;
  color: #6c9bcf;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  width: 80px;
  transition: color 0.2s ease-in-out;
}

.back-button:hover {
  color: #cfcfcf;
}
.chevron-icon {
  width: 20px;
  height: 20px;
}

/* 공통 카드 */
.card{
  background:#fff;
  border:1px solid #f1f1f1;
  border-radius:15px;
  box-shadow: 0 6px 16px rgba(0,0,0,.04);
  padding: 20px;
}

/* 2열 레이아웃 */
.reservation-page{
  display:grid;
  grid-template-columns: 320px 1fr;
  gap: 32px;
  align-items: start;
}
@media (max-width: 960px){
  .reservation-page{ grid-template-columns: 1fr; gap:16px; }
}

/* ── 배너 (상단 안내) ─────────────────────────── */
.application-banner{
  margin-bottom: 16px;
}
.banner-inner{
  position: relative;
  display: flex;
  align-items: center;     /* 가로 가운데 */
  justify-content: center; /* 세로 가운데 */
  text-align: center;      /* 텍스트 가운데 */
  background:#f4f7fb;
  border-radius:8px;
  padding:14px 16px;
  gap: 16px;
}
.banner-text{ color:#333333; display:flex; gap:10px; flex-wrap:wrap; }
.banner-text strong{ font-weight:700; }
.banner-cta{
  appearance: none;
  height: 30px;
  padding: 0 1rem;
  border: 1px solid #cfcfcf;
  border-radius: 15px;
  font-size: 12px;
  color:  #888;
  background-color: transparent;

}
.banner-cta:hover{ border: 1px solid #6c9bcf; color: #6c9bcf }

.banner-close{
  position:absolute; top:8px; right:10px; border:none; background:transparent; font-size:20px; color:#8aa; cursor:pointer;
}

/* ── 프로필 카드 ──────────────────────────────── */
.profile-card{ text-align:center; }
.profile-card-img{
  width: 240px; height: 300px; object-fit: cover; border-radius:12px;
  box-shadow:0 4px 12px rgba(0,0,0,.08); margin: 4px auto 14px;
}
.check-badge-icon {
  width: 22px; /* 아이콘 크기 조절 */
  height: 22px;
  margin-left: 4px;
  margin-bottom: 4px;
  /* 필요에 따라 추가적인 스타일을 지정할 수 있습니다. */
}
.profile-card .name{ font-size:22px; font-weight:800; color:#192C56; margin: 0 0 8px; }
.profile-card .intro{
  font-size:13px; color:#333333; background:#f4f7fb; border:1px solid #EEF2F7;
  padding:10px; border-radius:8px; margin: 0 auto 12px;
}
.profile-tags{ display:flex; justify-content:center; flex-wrap:wrap; gap:8px; }
.profile-tags span{
  background-color: #f1f1f1;
  color: #333;
  padding: 4px 8px;
  border-radius: 12px;
  font-size:12px;
}

/* ── 스케줄 카드 ──────────────────────────────── */
.schedule-card{ padding:22px; }
.schedule-title{
  font-size:16px; font-weight:700; color:#1d2b50;; margin:0 0 12px; padding-bottom:8px;
  border-bottom:1px solid #cfcfcf;
}
.date-row{ margin-bottom:16px; }
.date-input{
  padding:8px 10px; font-size:14px; border:1px solid #CBD5E1; border-radius:8px;
  outline:none;
}
.date-input:focus{ border-color:#6c9bcf; box-shadow:0 0 0 3px rgba(51,165,235,.15); }

/* 시간 슬롯 */
.time-grid{
  display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; margin-bottom:24px;
}
@media (max-width:520px){
  .time-grid{ grid-template-columns: repeat(3, 1fr); }
}
.slot-btn{
  border:1px solid #cfcfcf; background:#fff; color:#334155;
  padding:10px 0; border-radius:8px; font-size:13px; cursor:pointer;
  transition: all .15s ease;
}
.slot-btn:hover{ border-color:#6c9bcf; }
.slot-btn.is-selected{
  background:#33A5EB; color:#fff; font-weight:700; border-color:#33A5EB;
  box-shadow: 0 4px 10px rgba(51,165,235,.25);
}
.slot-btn.is-disabled{
  background:#f1f1f1; color:#888; border-color:#EBEFF5; cursor:not-allowed;
  text-decoration: line-through;
}

/* 예약 버튼 */
.reserve-row{ display:flex; justify-content:center; }
.reserve-button{
  background:#192C56; color:#fff; font-weight:400; border:none;
  padding:12px 24px; border-radius:8px; cursor:pointer; letter-spacing:.2px;
}
.reserve-button:hover{ filter: brightness(1.05); }
.reserve-button:disabled{ background:#C8CFD9; cursor:not-allowed; }

</style>
