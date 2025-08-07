<template>
  <div class="container">
    <div class="history-container">
      <div class="back-button" @click="goBack">
        <ChevronLeftIcon class="chevron-icon" />
        <span>이전</span>
      </div>
      <div class="header-row">
        <h2>상담내역</h2>
        <div class="sort-wrapper" @click="toggleSortOpen">
          <span>{{ sortOrder === 'desc' ? '최신순' : '오래된순' }}</span>
          <component :is="isSortOpen ? ChevronUpIcon : ChevronDownIcon" class="sort-icon" />
          <select v-model="sortOrder" @change="sortAppointments" class="native-select">
            <option value="desc">최신순</option>
            <option value="asc">오래된순</option>
          </select>
        </div>
      </div>
      <div v-if="consultedAppointments.length === 0" class="empty">
        상담한 내역이 없습니다.
      </div>

      <div v-for="appt in consultedAppointments" :key="appt.appointmentId" class="history-card">
        <div class="card-left">
          <div class="datetime">
            {{ formatDateTime(appt.startTime) }}
          </div>
          <div class="lawyer">
            <span class="lawyer-name">{{ lawyerMap[String(appt.lawyerId)] || '알 수 없음' }}</span> 변호사
          </div>
        </div>
        <button class="view-btn" @click="goToApplication(appt.applicationId)">상담신청서 확인하기</button>
      </div>
    </div>
  </div>

  <ApplicationDetail
  v-if="showModal"
  :data="selectedApplication"
  @close="showModal = false"
  />

</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/lib/axios'
import ApplicationDetail from './ApplicationDetail.vue'
import { ChevronLeftIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/vue/24/solid'

const appointments = ref([])
const lawyerMap = ref({})
const consultedAppointments = ref([])
const router = useRouter()
const showModal = ref(false)
const selectedApplication = ref(null)
const sortOrder = ref('desc')
const isSortOpen = ref(false)

const toggleSortOpen = () => {
  isSortOpen.value = !isSortOpen.value
}
const sortAppointments = () => {
  consultedAppointments.value.sort((a, b) => {
    const timeA = new Date(a.startTime).getTime()
    const timeB = new Date(b.startTime).getTime()
    return sortOrder.value === 'desc' ? timeB - timeA : timeA - timeB
  })
}
const goBack = () => {
  router.push('/user/mypage')
}

const formatDateTime = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const goToApplication = async (applicationId) => {
  showModal.value = true
  const res = await axios.get(`api/applications/${applicationId}`)
  selectedApplication.value = res.data
  showModal.value = true
}

onMounted(async () => {

  try {
    const [appointmentRes, lawyerRes] = await Promise.all([
      axios.get('api/appointments/me'),
      axios.get('api/lawyers/list')
    ])

    appointments.value = appointmentRes.data
    consultedAppointments.value = appointments.value.filter(
      appt => appt.appointmentStatus === 'COMPLETED'
    )

    const map = {}
    lawyerRes.data.forEach(lawyer => {
      map[String(lawyer.lawyerId)] = lawyer.name
    })
    lawyerMap.value = map

  } catch (e) {
    console.error('상담내역 불러오기 실패:', e)
  }

  sortAppointments()
})

</script>

<style scoped>
*{
  font-family: 'Noto Sans KR', sans-serif;
  white-space: nowrap;
}
.history-container{
  margin: 0 10rem;
}
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 2px solid #B9D0DF;
  color: #072D45;
}
.history-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding: 1.5rem 0;
}
.card-left {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 55px;
}
.datetime {
  font-weight: bold;
  font-size: 0.8rem;
  color: #B9D0DF;
}
.lawyer {
  font-size: 1.2rem;
  color: #072D45;
}
.lawyer-name{
  font-weight: bold;
}

.empty {
  color: #aaa;
}

.back-button {
  margin-top: 100px;
  margin-bottom: 50px;
  margin-left: -10px;
  font-size: 1rem;
  color: #B9D0DF;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  width: 80px;
}
.chevron-icon {
  width: 20px;
  height: 20px;
}
.view-btn {
  background: none;
  color: #B9D0DF;
  cursor: pointer;
  font-size: 0.9rem;
  border: none;
  align-self: flex-end;
}

.sort-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid #B9D0DF;
  border-radius: 15px;
  height: 30px;
  padding: 0 1rem;
  font-size: 12px;
  color: #072D45;
  cursor: pointer;
  width: 110px;
  background-color: white;
}

.sort-icon {
  width: 16px;
  height: 16px;
  margin-left: 8px;
}

.native-select {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}


</style>
