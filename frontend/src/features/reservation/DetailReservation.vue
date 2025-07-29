<template>
  <div>
    <button @click="$router.back()">← 이전</button>
    <!-- 프로필 사진 -->
    <img
      v-if="lawyer?.photo"
      :src="`data:image/jpeg;base64,${lawyer.photo}`"
      alt="변호사 프로필"
      style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover; margin-bottom: 1rem"
    />
    <h2>{{ lawyer?.name }} 변호사</h2>
    <p>{{ lawyer?.introduction }}</p>
    <!-- 태그 이름 표시 -->
    <div>
      <span v-for="tag in lawyer?.tags" :key="tag">#{{ getTagName(tag) }}</span>
    </div>


    <!-- 날짜 선택 -->
    <input
      type="date"
      v-model="selectedDate"
      :min="today"
      @change="fetchUnavailableSlots"
    />

    <!-- 시간 선택 -->
    <div class="time-grid">
      <button
        v-for="time in allTimeSlots"
        :key="time"
        :disabled="!selectedDate || unavailableSlots.includes(time)"
        :class="[
          'btn',
          !selectedDate || unavailableSlots.includes(time) ? 'disabled' : '',
          selectedTime === time ? 'selected' : ''
        ]"
        @click="() => {
          if (selectedDate && !unavailableSlots.includes(time)) selectedTime = time
        }"
      >
        {{ time }}
      </button>
    </div>

    <button :disabled="!selectedDate || !selectedTime" @click="openModal">상담 예약하기</button>

    <div v-if="showModal">
      <ApplicationChoiceModal
        :lawyerId="lawyerId"
        :selectedDate="selectedDate"
        :selectedTime="selectedTime"
        @close="showModal = false"
      />
    </div>

    <p v-if="!lawyer">변호사 정보를 불러오는 중...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'
import ApplicationChoiceModal from '@/features/reservation/ApplicationChoiceModal.vue'

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
const tagMap = [
  { id: 1, name: '형사 분야' },
  { id: 2, name: '교통·사고·보험' },
  { id: 3, name: '가사·가족' },
  { id: 4, name: '민사·계약·채권' },
  { id: 5, name: '파산·회생·채무조정' },
  { id: 6, name: '상속·증여' },
  { id: 7, name: '지식재산권' },
  { id: 8, name: '노동·고용' },
  { id: 9, name: '행정·조세' },
  { id: 10, name: '환경·공공' },
  { id: 11, name: '의료·생명·개인정보' },
  { id: 12, name: '금융·증권·기업' }
]

const getTagName = (id) => {
  const tag = tagMap.find(t => t.id === Number(id))
  return tag ? tag.name : '알 수 없음'
}

onMounted(async () => {
  selectedDate.value = today
  await fetchLawyerInfo()
  await fetchUnavailableSlots()
})

const fetchLawyerInfo = async () => {
  const res = await axios.get(`/api/admin/lawyers/list`)
  lawyer.value = res.data.find(l => l.lawyerId == lawyerId)
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

const openModal = () => {
  console.log('✅ 모달 열림 시도', selectedDate.value, selectedTime.value)
  showModal.value = true
}
</script>


<style>
.btn {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
  margin: 4px;
  transition: all 0.2s ease-in-out;
}

.btn.disabled {
  background-color: #f5f5f5;
  color: #bbb;
  border-color: #e0e0e0;
  cursor: not-allowed;
  text-decoration: line-through;
}

.btn.selected {
  background-color: #5A45FF;  /* 브랜드 보라색 */
  color: white;
  font-weight: bold;
  border-color: #5A45FF;
}

</style>
