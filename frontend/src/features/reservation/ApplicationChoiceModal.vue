<template>
  <div class="modal-overlay">
    <div class="modal-box">
      <h3 class="modal-title">
        {{ selectedDate }} {{ selectedTime }} 상담 예약
      </h3>

      <select v-model="selectedApplicationId" class="application-select">
        <option value="">상담신청서 선택</option>
        <option
          v-for="app in applications"
          :value="app.applicationId"
          :key="app.applicationId"
        >
          {{ app.title }}
        </option>
      </select>

      <p v-if="applications.length === 0" class="no-app-message">
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
import { ref, onMounted } from 'vue'
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

const fetchApplications = async () => {
  const res = await axios.get('/api/applications/me?isCompleted=true')
  applications.value = res.data
}

const submitReservation = async () => {
  try {
    const startTime = `${props.selectedDate}T${props.selectedTime}:00`  // ISO 형식 조합

    const end = new Date(`${props.selectedDate}T${props.selectedTime}:00`)
    end.setMinutes(end.getMinutes() + 30)
    const endTime = end.toISOString().split('.')[0].replace('T', ' ')  // "YYYY-MM-DD HH:MM:SS"

    await axios.post('/api/appointments', {
      lawyerId: props.lawyerId,
      applicationId: selectedApplicationId.value,
      startTime: startTime.replace('T', ' '),  // 백엔드가 공백 포맷 기대 시
      endTime: endTime
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

.application-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  margin-bottom: 12px;
  font-size: 14px;
  color: #333;
}

.no-app-message {
  font-size: 13px;
  color: #777;
  margin-bottom: 12px;
  text-align: left;
}

.new-app-btn {
  background: none;
  border: none;
  color: #007bff;
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
