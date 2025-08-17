<template>
  <div v-if="user && appointments !== null" class="mypage-container">
    <h1 class="mypage-title">마이페이지</h1>
    <section class="profile-section">
      <div class="profile-box">
        <div class="profile-left">
          <img
            src="@/assets/kakakoprofile.png"
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

    <section class="appointment-section">
      <h4>예약된 상담</h4>
      <ul v-if="confirmedAppointments.length > 0" class="appointment-list">
        <li
          v-for="appt in confirmedAppointments"
          :key="appt.appointmentId"
          class="appointment-item"
        >
          <div class="appt-info">
            <div>
              <p class="lawyer-name">{{ lawyerMap[String(appt.lawyerId)] || '알 수 없음' }} 변호사</p>
              <p class="appt-time">{{ formatDateTime(appt.startTime) }}</p>
              <span
                @click="openDetailModal(appt.applicationId)"
                class="view-application-link"
              >
                상담신청서 보기
              </span>
            </div>
            <div class="status-group">
              <p :class="statusClass(appt.appointmentStatus)" class="appointment-status">
                {{ statusText(appt.appointmentStatus) }}
              </p>
              <button
                v-if="isVideocallEnabled(appt.startTime) && appt.appointmentStatus === 'CONFIRMED'"
                @click="goToVideocall(appt.appointmentId)"
                class="videocall-btn"
              >
                화상 상담 입장
              </button>
            </div>
          </div>
        </li>
      </ul>
      <p v-else class="no-appt">예약된 일정이 없습니다.</p>
    </section>

    <section class="appointment-section">
      <h4>예약 요청한 상담</h4>
      <ul v-if="requestedAppointments.length > 0" class="appointment-list">
        <li
          v-for="appt in requestedAppointments"
          :key="appt.appointmentId"
          class="appointment-item"
        >
          <button
            class="cancel-x-btn"
            @click.stop="cancelAppointment(appt)"
          >×</button>

          <div class="appt-info">
            <div>
              <p class="lawyer-name">{{ lawyerMap[String(appt.lawyerId)] || '알 수 없음' }} 변호사</p>
              <p class="appt-time">{{ formatDateTime(appt.startTime) }}</p>
              <span
                @click="openDetailModal(appt.applicationId)"
                class="view-application-link"
              >
                상담신청서 보기
              </span>
            </div>
            <div class="status-group">
              <p :class="statusClass(appt.appointmentStatus)" class="appointment-status">
                {{ statusText(appt.appointmentStatus) }}
              </p>
            </div>
          </div>
        </li>
      </ul>
      <p v-else class="no-appt">예약 요청한 상담이 없습니다.</p>
    </section>

    <section class="application-section">
      <h4 @click="goToAllApplications" class="section-title-link">
        상담신청서 보관함
        <span class="arrow">›</span>
      </h4>
      <ul v-if="recentApplications.length > 0" class="application-list">
        <li
          v-for="form in recentApplications"
          :key="form.applicationId"
          class="appointment-item"
          @click="openDetailModal(form.applicationId)"
          style="cursor: pointer;"
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
    <section class="menu-section">
      <div class="menu-item" @click="$router.push('/user/consult-history')">
        상담내역
        <span class="arrow">›</span>
      </div>
      <div class="menu-item" @click="handleWithdraw">
        회원탈퇴
        <span class="arrow">›</span>
      </div>
    </section>
  </div>

  <div v-else class="loading">마이페이지 정보를 불러오는 중입니다...</div>

  <ApplicationDetail
    v-if="isDetailModalOpen"
    :data="selectedApplication"
    @close="isDetailModalOpen = false"
  />

</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from '@/lib/axios'
import ApplicationDetail from './ApplicationDetail.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = ref(null)
const appointments = ref([])
const lawyerMap = ref({})
const applications = ref([])

const isDetailModalOpen = ref(false)
const selectedApplication = ref(null)

const confirmedAppointments = computed(() => {
  return appointments.value
    .filter(a => a.appointmentStatus === 'CONFIRMED')
    // 필요하면 ‘다가올 일정만’으로 제한하려면 아래 줄 주석 해제
    // .filter(a => new Date(a.startTime) > new Date())
})

const requestedAppointments = computed(() => {
  return appointments.value.filter(a =>
    ['PENDING', 'REJECTED', 'CANCELLED'].includes(a.appointmentStatus)
  )
})

const cancelAppointment = async (appt) => {
  if (!confirm('상담 예약을 취소하시겠습니까?')) return
  try {
    // 백엔드 명세에 맞춰 cancel 엔드포인트 호출 (POST가 일반적)
    await axios.post(`/api/appointments/${appt.appointmentId}/cancel`)
    // 낙관적 업데이트: 상태를 CANCELLED로 갱신하여 목록에서 즉시 반영
    appt.appointmentStatus = 'CANCELLED'
    alert('예약이 취소되었습니다.')
  } catch (err) {
    console.error('예약 취소 실패:', err)
    alert('취소 중 오류가 발생했습니다. 다시 시도해주세요.')
  }
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

// ✅ 상담 상태 텍스트를 반환하는 함수 추가
const statusText = (status) => {
  switch (status) {
    case 'PENDING': return '대기중';
    case 'CONFIRMED': return '상담확정';
    case 'REJECTED': return '거절됨';
    case 'CANCELLED': return '취소됨';
    case 'ENDED': return '상담종료';
    default: return '알 수 없음';
  }
}

// ✅ 상담 상태별 스타일 클래스를 반환하는 함수 추가
const statusClass = (status) => {
  return `status-${status.toLowerCase()}`;
};

// ✅ 화상 상담 버튼 활성화 조건을 확인하는 함수 추가
const isVideocallEnabled = (startTime) => {
  const now = new Date();
  const appointmentTime = new Date(startTime);
  const timeDifferenceInMinutes = (appointmentTime - now) / (1000 * 60);

  // 상담 시작 30분 전부터 시작 시간까지 활성화
  return timeDifferenceInMinutes <= 30 && timeDifferenceInMinutes >= 0;
};

// ✅ 화상 상담 페이지로 이동하는 함수 추가
const goToVideocall = (appointmentId) => {
  router.push(`/videocall/${appointmentId}`);
};



const openDetailModal = async (applicationId) => {
  try {
    const res = await axios.get(`/api/applications/${applicationId}`)
    if (res.data.success) {
      // API 응답 데이터 구조에 맞게 selectedApplication에 할당
      selectedApplication.value = res.data.data.application
      isDetailModalOpen.value = true // 데이터 로딩 성공 시 모달 열기
    } else {
      throw new Error(res.data.message)
    }
  } catch (error) {
    console.error('상세 정보 로딩 실패:', error)
    alert(error.message || '상세 정보를 불러오는 데 실패했습니다.')
  }
}

// ✅ 최근 상담신청서 2개를 반환하는 계산 속성
const recentApplications = computed(() => {
  if (!applications.value) return [];
  // 최신순으로 정렬 (가장 최근에 생성된 순)
  const sorted = [...applications.value].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  // 상위 2개만 잘라내기
  return sorted.slice(0, 2);
})

const goToAllApplications = () => {
  // ✅ ID 파라미터 없이 목록 페이지 라우트('ApplicationList')로 이동합니다.
  router.push({ name: 'ApplicationList' });
}

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

onMounted(async () => {
  try {
    const [userRes, appointmentRes, formRes, lawyerListRes] = await Promise.all([
      axios.get('/api/clients/me'),
      axios.get('/api/appointments/me'),
       axios.get('/api/applications/me', { params: { isCompleted: true } }),
      axios.get('/api/lawyers/list'),
    ])
    user.value = userRes.data
    appointments.value = appointmentRes.data
    applications.value = formRes.data.data.applicationList


    const map = {}
    lawyerListRes.data.forEach(lawyer => {
      map[String(lawyer.lawyerId)] = lawyer.name
    })
    lawyerMap.value = map

  } catch (err) {
    console.error('마이페이지 데이터 로딩 실패:', err)
    user.value = {} // 로딩 상태를 해제하기 위해 빈 객체 할당
    appointments.value = []
    applications.value = []
  }
})

</script>

<style scoped>
.section-title-link {
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.section-title-link:hover {
  color: #6c9bcf; /* 호버 시 색상 변경 (예시) */
}
.mypage-container {
  max-width: 700px;
  margin: 0 auto;
  padding: 100px 20px;
  font-family: 'Noto Sans KR', sans-serif;
  color: #333333
}
.mypage-container h1 {
  text-align: center;
  margin-top: 15px;
  margin-bottom: 5px;
}
.mypage-title {
  font-size: 24px;
  margin-bottom: 40px;
  font-weight: bold;
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
  border: 1px solid #cfcfcf;
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
  margin-bottom: 15px;
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
  color: #888;
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
  color: #333;
  border: 1px solid #cfcfcf;
  background: #ffffff;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 12px;
  position: relative;
}
.appointment-item:hover {
  background: #f4f7fb;
  border-color: #6c9bcf;
  transform: translateY(-1px);;
}


/* X 버튼 */
.cancel-x-btn {
  position: absolute;
  top: 8px;
  right: 10px;
  z-index: 2;                    /* appt-info 위로 */
  background: transparent;              /* 카드 배경과 동일 */
  border-radius: 6px;
  border: none;
  padding: 1px 8px;
  height: auto;
  width: auto;                   /* "취소" 글자 안 잘리게 */
  line-height: normal;
  font-size: 0.85rem;
  color: #888;
  /* transition: transform 0.12s ease, border-color 0.15s ease; */
}
.cancel-x-btn:hover {
  color: #6c9bcf; /* 밝은 파랑(사용 중인 포커스 컬러) */
}


.appt-info {
  display: flex;
  flex-grow: 1; /* ✅ 추가 */
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
.lawyer-name,
.form-title {
  font-size: 1rem;
  font-weight: bold;
  margin-bottom: 4px;
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
.view-application-link {
  font-size: 0.85rem;
  color: #888;
  cursor: pointer;
  margin-top: 4px;
}
.view-application-link:hover {
  text-decoration: underline;
}

.status-group {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px; /* 상태와 버튼 사이 간격 */
}

/* ✅ 상담 상태 스타일 추가 */
.appointment-status {
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 0.8rem;
  white-space: nowrap;
}
.status-pending {
  background: #FFBF66;
  color: white;
}
.status-confirmed {
  background: #6c9bcf;
  color: white;
}
.status-rejected, .status-cancelled {
  background: #B3261E;
  color: white;
}
.status-ended {
  color: #888;
}

/* 메뉴 */
.menu-section {
  border-top: 1px solid #cfcfcf;
}
.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #cfcfcf;
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
