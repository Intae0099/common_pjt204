<template>
  <div v-if="user && appointments !== null" class="mypage-container">
    <!-- ✅ 프로필 영역 -->
    <section class="profile-section">
      <div class="profile-box">
        <div class="profile-left">
          <img
            src="C:\Users\SSAFY\Desktop\S13P11B204\frontend\src\assets\kakakoprofile.png"
            alt="프로필 이미지"
            class="profile-img"
          />
          <div class="profile-info">
            <h3>{{ user.oauthName }}</h3>
            <p class="email">이메일: {{ user.email || '등록된 이메일이 없습니다.' }}</p>
          </div>
        </div>
        <button class="setting-btn" @click="$router.push('/user/update')">계정설정</button>
      </div>
    </section>

    <!-- ✅ 예약 일정 -->
    <section class="appointment-section">
      <h4>예약된 상담</h4>
      <ul v-if="filteredAppointments.length > 0" class="appointment-list">
        <li
          v-for="appt in filteredAppointments"
          :key="appt.appointmentId"
          class="appointment-item"
        >
          <div class="appt-info">
            <div>
              <p class="lawyer-name">{{ lawyerMap[String(appt.lawyerId)] || '알 수 없음' }} 변호사</p>
              <p class="appt-time">{{ formatDateTime(appt.startTime) }}</p>
            </div>
          </div>
        </li>
      </ul>
      <p v-else class="no-appt">예약된 일정이 없습니다.</p>
    </section>

    <!-- ✅ 상담신청서 보관함 -->
    <section class="application-section">
      <h4>상담신청서 보관함</h4>
      <ul v-if="applications.length > 0" class="application-list">
        <li
          v-for="form in applications"
          :key="form.applicationId"
          class="appointment-item"
        >
          <div class="appt-info">
            <div>
              <p class="form-title">{{ form.title }}</p>
              <p class="appt-time">{{ formatDateTime(form.createdAt) }}</p>
            </div>
          </div>
        </li>
      </ul>
      <p v-else class="no-appt">상담신청서가 없습니다.</p>
    </section>

    <!-- ✅ 기타 메뉴 -->
    <section class="menu-section">
      <div class="menu-item" @click="$router.push('/consult-history')">
        상담내역 보기
        <span class="arrow">›</span>
      </div>
      <div class="menu-item" @click="handleWithdraw">
        회원탈퇴
        <span class="arrow">›</span>
      </div>
    </section>
  </div>

  <div v-else class="loading">마이페이지 정보를 불러오는 중입니다...</div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from '@/lib/axios'

const user = ref(null)
const appointments = ref([])
const lawyerMap = ref({})
const applications = ref([])

const filteredAppointments = computed(() => {
  const now = new Date()
  return appointments.value.filter(appt => new Date(appt.startTime) > now)
})

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

    console.log('user.value.email:', user.value?.email)
  } catch (err) {
    console.error('마이페이지 데이터 로딩 실패:', err)
  }
})

const handleWithdraw = async () => {
  if (!confirm('정말로 회원탈퇴하시겠습니까? 탈퇴 후 복구할 수 없습니다.')) return

  try {
    await axios.delete('/api/clients/me')  // ✅ 탈퇴 API 호출
    alert('회원탈퇴가 완료되었습니다.')

    // JWT 토큰 및 사용자 타입 제거
    localStorage.removeItem('accessToken')
    localStorage.removeItem('userType')

    // 홈으로 이동
    window.location.href = '/'
  } catch (error) {
    console.error('회원탈퇴 실패:', error)
    alert('탈퇴 중 오류가 발생했습니다. 다시 시도해주세요.')
  }
}

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
  margin-bottom: 40px;
}
.profile-box {
  position: relative;
  display: flex;
  align-items: center;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  width: 100%;
  max-width: 100%;
  margin-top: 40px;
}
.profile-left {
  display: flex;
  align-items: center;
  margin-left: 20px; /* ✅ 왼쪽 여백 추가 */
  margin-top: 20px;
}
.profile-img {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 20px;
}
.profile-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.profile-info h3 {
  font-size: 1.4rem;
  font-weight: bold;
  margin-bottom: 4px;
}
.email {
  color: #999;
  font-size: 0.9rem;
}
.setting-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: 0.85rem;
  color: #888;
  background: none;
  border: none;
  cursor: pointer;
}

/* 예약/신청서 공통 */
.appointment-section,
.application-section {
  margin-bottom: 40px;
}
h4 {
  font-size: 1.2rem;
  margin-bottom: 16px;
  font-weight: bold;
}
.appointment-list,
.application-list {
  list-style: none;
  padding: 0;
  margin: 0;
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
.lawyer-name,
.form-title {
  font-size: 1rem;
  font-weight: bold;
}
.appt-time {
  font-size: 0.95rem;
  color: #333;
  margin-top: 4px;
}
.no-appt {
  margin-top: 20px;
  color: #888;
  text-align: center;
}

/* 메뉴 */
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
.loading {
  text-align: center;
  margin-top: 40px;
}
</style>
