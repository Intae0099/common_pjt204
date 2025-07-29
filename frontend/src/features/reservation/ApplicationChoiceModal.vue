<template>
  <div class="modal">
    <div class="modal-content">
      <h3>{{ selectedDate }} {{ selectedTime }} 상담 예약</h3>

      <select v-model="selectedApplicationId">
        <option value="">상담신청서 선택</option>
        <option
          v-for="app in applications"
          :value="app.applicationId"
          :key="app.applicationId"
        >
          {{ app.title }}
        </option>
      </select>

      <!-- 기존 신청서가 없는 경우 메시지 -->
      <p v-if="applications.length === 0">
        상담신청서가 없나요?
      </p>

      <!-- 항상 보이는 새 신청서 작성 버튼 -->
      <button class="new-form-btn" @click="goToAiApplication">
        새 상담신청서 작성하기
      </button>

      <div class="btn-group">
        <button
          class="btn"
          :disabled="!selectedApplicationId"
          @click="submitReservation"
        >
          예약하기
        </button>
        <button class="btn cancel" @click="$emit('close')">닫기</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
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

    await axios.post('/api/appointments', {
      lawyerId: props.lawyerId,
      applicationId: selectedApplicationId.value,
      startTime: startTime
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
  router.push('/ai-application')
}

onMounted(fetchApplications)
</script>

<style scoped>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 999;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.4);
  display: flex;
  justify-content: center;
  align-items: center;
}
.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  min-width: 320px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
.btn-group {
  display: flex;
  justify-content: space-between;
  margin-top: 1.5rem;
}
.btn {
  padding: 8px 14px;
  border: none;
  border-radius: 6px;
  background-color: #5A45FF;
  color: white;
  cursor: pointer;
}
.btn.cancel {
  background-color: #888;
}
.btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
