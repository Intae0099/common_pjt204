<template>
  <div v-if="user && appointments.length !== null" class="mypage-container">
    <div class="text-wrapper-4">마이페이지</div>

    <!-- 프로필 카드 -->
    <div class="element">
      <div class="div">
        <div class="overlap">
          <div class="text-wrapper">{{ user.oauthname }}</div>
          <div class="ellipse"></div>
          <div class="text-wrapper">{{ user.email }}</div>
        </div>

        <hr />

        <!-- 예약 일정 -->
        <div class="text-wrapper-5">예약일정</div>
        <div v-if="filteredAppointments.length === 0" class="no-reservations">
          예약된 일정이 없습니다.
        </div>
        <div v-else>
          <div
            v-for="appt in filteredAppointments"
            :key="appt.appointmentId"
            class="overlap-group"
          >
            <div class="text-wrapper-6">
              {{ lawyerMap[String(appt.lawyerId)] || '알 수 없음' }} 변호사
            </div>
            <div class="text-wrapper-7">{{ formatDateTime(appt.startTime) }}</div>
            <div class="east">
              <!-- <img class="vector" alt="Vector" src="@/assets/images/vector5.svg" /> -->
            </div>
          </div>
          <hr />
        </div>

        <!-- 상담신청서 보관함 -->
        <div class="text-wrapper-8">상담신청서 보관함</div>
        <div v-for="form in applications" :key="form.applicationId" class="overlap-group">
          <div class="text-wrapper-6">{{ form.title }}</div>
          <div class="text-wrapper-7">{{ form.createdAt }}</div>
          <div class="east">
            <!-- <img class="vector" alt="Vector" src="@/assets/images/vector5.svg" /> -->
          </div>
        </div>
        <hr />

        <!-- 상담내역 -->
        <div class="text-wrapper-9" @click="$router.push('/consult-history')">상담내역</div>
        <hr />

        <!-- 회원탈퇴 -->
        <div class="text-wrapper-10">회원탈퇴</div>
      </div>
    </div>
  </div>

  <div v-else>
    마이페이지 정보를 불러오는 중입니다...
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from '@/lib/axios'

// 사용자 정보
const user = ref(null)

// 예약 정보
const appointments = ref([])
const lawyerMap = ref({})

// 상담신청서 목록
const applications = ref([])

// 필터링된 예약 정보 (오늘 이후)
const filteredAppointments = computed(() => {
  const now = new Date()
  return appointments.value.filter(appt => new Date(appt.startTime) > now)
})

// 날짜 형식 함수
const formatDateTime = dateStr => {
  const date = new Date(dateStr)
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}


// API 호출
onMounted(async () => {
  try {
    const [userRes, appointmentRes, formRes, lawyerListRes] = await Promise.all([
      axios.get('/api/clients/me'),
      axios.get('/api/appointments/me'),
      axios.get('/api/applications/me'),
      axios.get('/api/lawyers/list'),
    ])

    user.value = userRes.data
    appointments.value = appointmentRes.data
    applications.value = formRes.data

    const map = {}
    lawyerListRes.data.forEach(lawyer => {
      map[String(lawyer.lawyerId)] = lawyer.name
    })
    lawyerMap.value = map

  } catch (err) {
    console.error('마이페이지 데이터 로딩 실패:', err)
  }
  console.log('lawyerMap:', JSON.stringify(lawyerMap.value, null, 2))
  console.log('appointments:', JSON.stringify(appointments.value, null, 2))


})
</script>

<style scoped>
.mypage-container {
  padding: 1rem;
}

.no-reservations {
  padding: 20px;
  text-align: center;
  color: #888;
}

/* 예시: 필요한 스타일은 추가로 보완하세요 */
.text-wrapper-4 {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
}
.overlap {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.text-wrapper-6 {
  font-weight: bold;
}
.text-wrapper-7 {
  color: gray;
}
</style>
