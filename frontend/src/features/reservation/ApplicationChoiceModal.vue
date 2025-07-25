<template>
  <div class="modal">
    <div class="modal-content">
      <h3>{{ selectedDate }} {{ selectedTime }} 예약</h3>

      <select v-model="selectedApplicationId">
        <option value="">상담신청서 선택</option>
        <option v-for="app in applications" :value="app.id" :key="app.id">
          {{ app.title }}
        </option>
      </select>

      <p v-if="applications.length === 0">
        상담신청서가 없나요?
        <button @click="goToAiApplication">작성하러가기</button>
      </p>

      <button :disabled="!selectedApplicationId" @click="submitReservation">예약하기</button>
      <button @click="$emit('close')">닫기</button>
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
  const res = await axios.get('/api/applications/me')
  applications.value = res.data
}

const submitReservation = async () => {
  await axios.post('/api/appointments', {
    lawyer_id: props.lawyerId,
    date: props.selectedDate,
    time: props.selectedTime,
    application_id: selectedApplicationId.value
  })
  alert('예약이 완료되었습니다!')
  emit('close')
  router.push('/user/mypage')
}

const goToAiApplication = () => {
  emit('close')  // 모달 닫기
  router.push('/ai-application')  // 경로 이동
}

onMounted(fetchApplications)
</script>

<style>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 999;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.4); /* 반투명 배경 */
  display: flex;
  justify-content: center;
  align-items: center;
}
.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  min-width: 300px;
}
</style>
