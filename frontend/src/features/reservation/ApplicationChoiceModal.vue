<template>
  <div class="modal-overlay" @click.self="closeDropdown">
    <div class="modal-box">
      <h3 class="modal-title">
        {{ selectedDate }} {{ selectedTime }} 상담 예약
      </h3>

      <div class="custom-select-wrapper">
        <div class="custom-select" @click="toggleDropdown">
          <div class="custom-select-trigger">
            <span>{{ selectedApplicationTitle || '상담신청서 선택' }}</span>
            <div class="arrow" :class="{ 'open': isDropdownOpen }"></div>
          </div>
        </div>
        <div class="custom-options" v-if="isDropdownOpen">
          <div class="custom-option" @click="selectDefaultOption">
            상담신청서 선택
          </div>
          <div
            class="custom-option"
            v-for="app in applications"
            :key="app.applicationId"
            :title="app.title"
            @click="selectApplication(app)"
          >
            {{ app.title }}
          </div>
        </div>
      </div>

      <p class="no-app-message">
        상담신청서가 없나요?
        <button class="new-app-btn" @click="goToAiApplication">
        새 상담신청서 작성하기
        </button>
      </p>

      <div class="modal-buttons">
        <button
          class="modal-btn"
          :disabled="!selectedApplicationId"
          @click="submitReservation"
        >
          예약하기
        </button>
        <button class="modal-btn cancel" @click="$emit('close')">닫기</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue' // ✅ computed 추가
import axios from '@/lib/axios'
import { useRouter } from 'vue-router'

const props = defineProps({
  lawyerId: [String, Number],
  selectedDate: String,
  selectedTime: String
})

const emit = defineEmits(['close'])

const applications = ref([])
const selectedApplicationId = ref('')
const router = useRouter()

// ✅ [추가] 커스텀 드롭다운 상태 관리를 위한 ref
const isDropdownOpen = ref(false)

// ✅ [추가] 선택된 신청서의 제목을 표시하기 위한 computed 속성
const selectedApplicationTitle = computed(() => {
  const selectedApp = applications.value.find(
    app => app.applicationId === selectedApplicationId.value
  )
  return selectedApp ? selectedApp.title : ''
})

const fetchApplications = async () => {
  try {
    const res = await axios.get('/api/applications/me?isCompleted=true')
    if (res.data && res.data.data && res.data.data.applicationList) {
      applications.value = res.data.data.applicationList
    } else {
      applications.value = []
    }
  } catch (error) {
    console.error('상담신청서 조회 중 오류가 발생했습니다:', error)
    applications.value = []
  }
}

// ✅ [추가] 커스텀 드롭다운 제어 함수들
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

const closeDropdown = () => {
  isDropdownOpen.value = false
}

const selectApplication = (app) => {
  selectedApplicationId.value = app.applicationId
  closeDropdown()
}

const selectDefaultOption = () => {
  closeDropdown()
}

const submitReservation = async () => {
  try {
    // 1. startTime을 "yyyy-mm-dd hh:mm:ss" 형식으로 조합
    const startTimeStr = `${props.selectedDate} ${props.selectedTime}:00`

    // 2. endTime을 계산하기 위해 Date 객체 생성
    const startDate = new Date(`${props.selectedDate}T${props.selectedTime}:00`)
    startDate.setMinutes(startDate.getMinutes() + 30)

    // 3. endTime을 "yyyy-mm-dd hh:mm:ss" 형식으로 포맷팅
    const pad = (num) => num.toString().padStart(2, '0')
    const year = startDate.getFullYear()
    const month = pad(startDate.getMonth() + 1)
    const day = pad(startDate.getDate())
    const hours = pad(startDate.getHours())
    const minutes = pad(startDate.getMinutes())
    const seconds = pad(startDate.getSeconds())
    const endTimeStr = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`

    await axios.post('/api/appointments', {
      lawyerId: props.lawyerId,
      applicationId: selectedApplicationId.value,
      startTime: startTimeStr,
      endTime: endTimeStr
    })

    alert('예약이 완료되었습니다!')
    emit('close')
    router.push('/user/mypage')
  } catch (err) {
    alert('예약 중 오류가 발생했습니다.')
    console.error(err)
  }
}

const goToAiApplication = () => {
  emit('close')
  router.push('/consult-form')
}

onMounted(fetchApplications)
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-box {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 360px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  position: relative;
}

.modal-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 16px;
  text-align: left;
  color: #333;
}

/* --- ✅ [수정/추가] 커스텀 드롭다운 스타일 --- */
.custom-select-wrapper {
  position: relative;
  width: 100%;
  margin-bottom: 12px;
}

.custom-select {
  position: relative;
  cursor: pointer;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
  padding: 10px;
  font-size: 14px;
  color: #333;
}

.custom-select-trigger {
  display: flex;
  justify-content: space-between;
  align-items: center;
  /* 말줄임표 스타일 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.arrow {
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 5px solid #333;
  transition: transform 0.2s ease;
}

.arrow.open {
  transform: rotate(180deg);
}

.custom-options {
  color: #888;
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #ddd;
  border-top: 0;
  border-radius: 0 0 6px 6px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1001; /* 모달 위로 올라오도록 설정 */
  margin-top: -4px; /* select 박스와 경계선 겹치게 */
}

.custom-option {
  color: #888;
  padding: 10px;
  padding-top: 5px;
  cursor: pointer;
  font-size: 14px;
  /* 말줄임표 스타일 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.custom-option:hover {
  background-color: #f0f0f0;
}
/* --- 여기까지 커스텀 드롭다운 스타일 --- */


.no-app-message {
  font-size: 13px;
  color: #888;
  margin-bottom: 12px;
  text-align: left;
}

.new-app-btn {
  background: none;
  border: none;
  color: #6c9bcf;
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 20px;
  padding: 0;
  text-align: left;
}

.new-app-btn:hover {
  text-decoration: underline;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.modal-btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  background-color: #33A5EB;
  color: white;
}

.modal-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.modal-btn.cancel {
  background-color: #f0f0f0;
  color: #333;
}
</style>
