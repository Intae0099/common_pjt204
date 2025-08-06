<template>
  <div class="mypage-container">
    <!-- ✅ 프로필 영역 -->
    <section class="profile-section">
      <div class="profile-box">
        <div class="profile-left">
          <img
            :src="lawyer?.photo || 'https://via.placeholder.com/150'"
            alt="변호사 프로필"
            class="profile-img"
          />
          <div class="profile-info">
            <h3>
              {{ lawyer?.name || 'Username' }} 변호사
              <span class="verified">✔</span>
            </h3>
            <!-- ✅ 소개글 -->
            <p class="intro">{{ lawyer?.introduction || '소개글이 없습니다.' }}</p>
            <!-- ✅ 태그 -->
            <div class="tags">
              <span
                v-for="tagId in lawyer?.tags"
                :key="tagId"
                class="tag-badge"
              >
                #{{ getTagName(tagId) }}
              </span>
            </div>
          </div>
        </div>
        <button class="setting-btn" @click="goToProfileUpdate">계정설정</button>
      </div>
    </section>

    <!-- ✅ 예약 일정 영역 -->
    <section class="calendar-appointment-section">
      <div class="calendar-box">
        <Datepicker
          v-model="selectedDate"
          :inline="true"
          :format="'yyyy.MM.dd'"
          :min-date="new Date()"
          :highlighted="[{ date: new Date(), class: 'highlight-today' }]"
        />
      </div>

      <div class="appointment-box">
        <h4>{{ formatSelectedDate(selectedDate) }}</h4>

        <ul v-if="filteredAppointments.length > 0" class="appointment-list">
          <li v-for="appt in filteredAppointments" :key="appt.appointmentId" class="appointment-item">
            <div class="appt-info">
              <div>
                <p class="client-name">{{ appt.client.name }} 의뢰인</p>
                <p class="appt-time">{{ formatTime(appt.startTime) }}</p>
              </div>
              <span class="status-badge" :class="appt.appointmentStatus">
                {{ statusText(appt.appointmentStatus) }}
              </span>
            </div>
          </li>
        </ul>
        <p v-else class="no-appt">선택한 날짜에 예약이 없습니다.</p>
      </div>
    </section>

    <!-- ✅ 메뉴 섹션 -->
    <section class="menu-section">
      <div class="menu-item" @click="goToHistory">
        상담내역
        <span class="arrow">›</span>
      </div>
      <div class="menu-item" @click="handleWithdraw">
        회원탈퇴
        <span class="arrow">›</span>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/lib/axios'
import Datepicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import { useTagStore } from '@/stores/tags'

const lawyer = ref(null)
const appointments = ref([])
const clients = ref([])
const selectedDate = ref(new Date())

const router = useRouter()
const tagStore = useTagStore()

const getTagName = (id) => {
  const tag = tagStore.tagMap.find(t => t.id === id)
  return tag ? tag.name : '알 수 없음'
}

const formatSelectedDate = (dateObj) => {
  return dateObj.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'short' })
}

const formatTime = (datetime) => {
  const d = new Date(datetime)
  return d.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
}

const statusText = (status) => {
  if (status === 'APPROVED') return '상담확정'
  if (status === 'PENDING') return '대기중'
  return '기타'
}

const filteredAppointments = computed(() => {
  return appointments.value.filter(appt => {
    const apptDate = new Date(appt.startTime)
    return apptDate.toDateString() === selectedDate.value.toDateString()
  }).map(appt => ({
    ...appt,
    client: clients.value.find(c => c.clientId === appt.clientId)
  }))
})

const fetchLawyerProfile = async () => {
  try {
    const res = await axios.get('/api/lawyers/me')
    lawyer.value = res.data
  } catch (err) {
    console.error('변호사 정보 실패:', err)
  }
}

const fetchAppointments = async () => {
  try {
    const res = await axios.get('/api/appointments/me')
    appointments.value = res.data
  } catch (err) {
    console.error('예약 실패:', err)
  }
}

const clientCache = new Map()

const fetchClient = async (clientId) => {
  if (clientCache.has(clientId)) return clientCache.get(clientId)
  const res = await axios.get(`/api/clients/${clientId}`)
  clientCache.set(clientId, res.data)
  return res.data
}

const fetchClients = async () => {
  const uniqueIds = [...new Set(appointments.value.map(a => a.clientId))]
  const fetchedClients = await Promise.all(uniqueIds.map(id => fetchClient(id)))
  clients.value = fetchedClients
}

const goToProfileUpdate = () => {
  router.push({ name: 'LawyerProfileUpdate' })
}

const goToHistory = () => {
  alert('상담내역 페이지로 이동 예정')
}

const handleWithdraw = async () => {
  if (!confirm('정말로 회원탈퇴하시겠습니까?')) return

  try {
    await axios.delete('/api/lawyers/me')  // ✅ API 경로 수정 필요
    alert('회원탈퇴가 완료되었습니다.')
    // 로그아웃 처리 및 홈 이동
    localStorage.removeItem('accessToken')  // JWT 토큰 삭제
    localStorage.removeItem('user_type')     // 사용자 타입 등도 삭제
    window.location.href = '/'  // 홈으로 이동
  } catch (error) {
    console.error('회원탈퇴 실패:', error)
    alert('회원탈퇴에 실패했습니다. 다시 시도해주세요.')
  }
}

onMounted(async () => {
  await fetchLawyerProfile()
  await fetchAppointments()
  await fetchClients()
})
</script>

<style scoped>
.mypage-container {
  max-width: 700px;
  margin: 0 auto;
  padding: 100px 20px;
  font-family: 'Noto Sans KR', sans-serif;
}

/* 프로필 */
.profile-section {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-bottom: 60px;
  font-size: 0.8rem;
}
.profile-box {
  position: relative;
  display: flex;
  align-items: center; /* 세로 중앙정렬 */
  justify-content: flex-start; /* 좌측 정렬 */
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  width: 100%;         /* ✅ 부모 영역(mypage-container)에 꽉 차게 */
  max-width: 100%;
  margin-top: 30px; /* ✅ 위에 여백 추가 */
}
.profile-left {
  display: flex;
  align-items: center;
}
.profile-img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 16px;
}
.profile-info {
  display: flex;
  flex-direction: column; /* 수직 정렬 */
  align-items: flex-start; /* 왼쪽 정렬 */
  font-size: 0.8rem;
}
.verified {
  color: #1d2b50;
  margin-left: 8px;
}
.birth {
  color: #888;
  font-size: 0.95rem;
  margin-bottom: 10px;
}
.intro {
  font-size: 0.85rem;
  color: #333;
  margin: 8px 0;
  padding: 6px 10px;
  background: #f5f7fa;
  border-radius: 8px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-badge {
  background-color: #1d2b50;
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.7rem;
}

.setting-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: 0.85rem;
  color: #aaa;
  background: none;
  border: none;
  cursor: pointer;
}

/* 캘린더 + 예약 */
.calendar-appointment-section {
  display: flex;
  gap: 40px;
  margin-bottom: 40px;
}
.calendar-box {
  flex: 1;
}
.appointment-box {
  flex: 2;
}
.appointment-list {
  list-style: none;
  padding: 0;
  margin-top: 20px;
}
.appointment-item {
  border: 1px solid #e0e0e0;
  background: #f9f9f9;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 12px;
}
.appt-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.client-name {
  font-size: 1rem;
  font-weight: bold;
}
.appt-time {
  font-size: 0.95rem;
  color: #333;
  margin-top: 4px;
}
.status-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: bold;
}
.status-badge.APPROVED {
  background: #3478ff;
  color: white;
}
.status-badge.PENDING {
  background: #f5a623;
  color: white;
}
.no-appt {
  margin-top: 20px;
  color: #888;
}

/* 메뉴 섹션 */
.menu-section {
  border-top: 1px solid #e0e0e0;
}
.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 1rem;
  cursor: pointer;
}
.arrow {
  font-size: 1.2rem;
  color: #888;
}
</style>
