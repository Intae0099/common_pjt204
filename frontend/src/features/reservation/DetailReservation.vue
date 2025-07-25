<template>
  <div>
    <button @click="$router.back()">← 이전</button>
    <h2>{{ lawyer?.name }} 변호사</h2>
    <p>{{ lawyer?.introduction }}</p>
    <div>
      <span v-for="tag in lawyer?.tags" :key="tag">#{{ tag }}</span>
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

    <ApplicationChoiceModal
      v-if="showModal"
      :lawyerId="lawyerId"
      :selectedDate="selectedDate"
      :selectedTime="selectedTime"
      @close="showModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'
import ApplicationChoiceModal from './ApplicationChoiceModal.vue'

const route = useRoute()
const lawyerId = route.params.id
const lawyer = ref(null)
const unavailableSlots = ref([])
const selectedDate = ref('')
const selectedTime = ref('')
const showModal = ref(false)
const today = new Date().toISOString().split('T')[0]  // YYYY-MM-DD 형식
const allTimeSlots = [
  '08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
  '11:00', '11:30', '13:00', '13:30', '14:00', '14:30',
  '15:00', '15:30', '16:00', '16:30'
]

onMounted(async () => {
  selectedDate.value = today
  await fetchLawyerInfo()
  await fetchUnavailableSlots()
})


const fetchLawyerInfo = async () => {
  const res = await axios.get(`/api/admin/lawyers/list`)
  lawyer.value = res.data.find(l => l.id == lawyerId)
}

const fetchUnavailableSlots = async () => {
  if (!selectedDate.value) return
  selectedTime.value = ''
  const res = await axios.get(`/api/lawyers/${lawyerId}/unavailable-slot`, {
    params: { date: selectedDate.value }
  })
  unavailableSlots.value = res.data
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
