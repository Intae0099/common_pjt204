<template>
  <div class="mypage-container">
    <section class="profile-section">
      <div class="profile-box">
        <div class="profile-left">
          <img
              :src="lawyerPhotoSrc"
              alt="변호사 프로필"
              class="profile-img"
            />
          <div class="profile-info">
            <h3>
              {{ lawyer?.name || 'Username' }} 변호사
              <span class="verified">✔</span>
            </h3>
            <p class="intro">{{ lawyer?.introduction || '소개글이 없습니다.' }}</p>
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

    <section class="pending-appointments-section" v-if="pendingAppointments.length > 0">
      <h4>대기중인 상담 요청 ({{ pendingAppointments.length }}건)</h4>
      <ul class="appointment-list">
        <li v-for="appt in pendingAppointments" :key="appt.appointmentId" class="appointment-item">
          <div class="appt-info">
            <div>
              <p class="client-name">{{ appt.client?.name }} 의뢰인</p>
              <p class="appt-time">{{ formatAppointmentDateTime(appt.startTime) }}</p>
              <p v-if="appt.isTimeConflict" class="conflict-warning">
                ❗ 같은 시간에 다른 대기 중인 요청이 있습니다.
              </p>
              <p v-if="appt.isSlotUnavailable" class="conflict-warning">
                🚫 이미 확정된 예약과 시간이 겹칩니다.
              </p>
              <p v-if="appt.isTimeExpired" class="conflict-warning">
                ⏰ 상담 수락 가능 시간이 지났습니다.
              </p>
              <span @click="viewApplication(appt.applicationId)" class="view-application-link">
                상담신청서 보기
              </span>
            </div>
            <div class="action-buttons">
              <button
                @click="updateAppointmentStatus(appt.appointmentId, 'CONFIRMED')"
                class="accept-btn"
                :disabled="appt.isSlotUnavailable || appt.isTimeExpired"
              >
                수락
              </button>
              <button @click="updateAppointmentStatus(appt.appointmentId, 'REJECTED')" class="reject-btn" :disabled="appt.isTimeExpired">거절</button>
            </div>
          </div>
        </li>
      </ul>
    </section>
    <ApplicationDetail
      v-if="isModalOpen"
      :data="modalApplicationData"
      @close="isModalOpen = false"
    />

    <h4>내 상담 스케줄 확인</h4>
    <section class="calendar-appointment-section">

      <div class="calendar-box">
        <Datepicker
          v-model="selectedDate"
          :inline="true"
          :format="'yyyy.MM.dd'"
          :min-date="new Date()"
          :highlighted="highlightedDates"
        />
      </div>

      <div class="appointment-box">
        <h4>{{ formatSelectedDate(selectedDate) }}</h4>

        <ul v-if="filteredAppointments.length > 0" class="appointment-list">
          <li v-for="appt in filteredAppointments" :key="appt.appointmentId" class="appointment-item">
            <div class="appt-info">
              <div>
                <p class="client-name">{{ appt.client?.name }} 의뢰인 ({{ appt.client?.loginEmail }})</p>
                <p class="appt-time">{{ formatTime(appt.startTime) }}</p>
                <span @click="viewApplication(appt.applicationId)" class="view-application-link">
                  상담신청서 보기
                </span>
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
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from '@/lib/axios';
import Datepicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import { useTagStore } from '@/stores/tags';
import ApplicationDetail from '@/features/profile/user/ApplicationDetail.vue';

const lawyer = ref(null);
const appointments = ref([]);
const unavailableSlots = ref([]);
const selectedDate = ref(new Date());

const isModalOpen = ref(false);
const modalApplicationData = ref({});

const router = useRouter();
const tagStore = useTagStore();

const lawyerPhotoSrc = computed(() => {
  // lawyer 객체와 photoBase64 데이터가 있는지 확인
  if (lawyer.value?.photoBase64) {
    // 'data:image/jpeg;base64,' 접두사를 붙여 완전한 데이터 URI를 반환
    return `data:image/jpeg;base64,${lawyer.value.photoBase64}`;
  }
  // 데이터가 없으면 기본 플레이스홀더 이미지 반환
  return 'https://via.placeholder.com/150';
});

const highlightedDates = computed(() => {
  const dates = appointments.value
    .filter(appt => appt.appointmentStatus === 'CONFIRMED' || appt.appointmentStatus === 'PENDING')
    .map(appt => new Date(appt.startTime));
  return [{ dates: dates, class: 'highlight-appointment' }];
});

const getTagName = (id) => {
  const tag = tagStore.tagMap.find(t => t.id === id);
  return tag ? tag.name : '알 수 없음';
};

const formatSelectedDate = (dateObj) => {
  return dateObj.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'short' });
};

const formatTime = (datetime) => {
  const d = new Date(datetime);
  return d.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
};

const statusText = (status) => {
  switch (status) {
    case 'PENDING': return '대기중';
    case 'CONFIRMED': return '상담확정';
    case 'REJECTED': return '거절됨';
    case 'IN_PROGRESS': return '상담중';
    case 'CANCELLED': return '취소됨';
    case 'ENDED': return '상담종료';
    default: return '기타';
  }
};

const filteredAppointments = computed(() => {
  return appointments.value.filter(appt => {
    const apptDate = new Date(appt.startTime);
    return (apptDate.toDateString() === selectedDate.value.toDateString()) &&
           (appt.appointmentStatus === 'CONFIRMED' || appt.appointmentStatus === 'PENDING');
  });
});

const pendingAppointments = computed(() => {
  // ✅ PENDING 상태이면서, 예약 날짜가 오늘 이후인 예약만 필터링
  const now = new Date();
  now.setHours(0, 0, 0, 0); // 오늘 날짜의 자정으로 설정하여 시간은 무시

  const pending = appointments.value.filter(appt => {
    const apptDate = new Date(appt.startTime);
    apptDate.setHours(0, 0, 0, 0); // 예약 날짜의 자정으로 설정하여 시간은 무시
    return appt.appointmentStatus === 'PENDING' && apptDate >= now;
  });

  const checkConflicts = (currentAppt) => {
    return pending.some(otherAppt => {
      if (currentAppt.appointmentId === otherAppt.appointmentId) {
        return false;
      }
      return new Date(currentAppt.startTime).getTime() === new Date(otherAppt.startTime).getTime();
    });
  };

  return pending.map(appt => {
    const isSlotUnavailable = appointments.value.some(confirmedAppt => {
      return confirmedAppt.appointmentStatus === 'CONFIRMED' &&
             new Date(appt.startTime).getTime() === new Date(confirmedAppt.startTime).getTime();
    });

    const startTime = new Date(appt.startTime);
    const timeDifference = startTime.getTime() - new Date().getTime();
    const oneHourInMillis = 60 * 60 * 1000;
    const isTimeExpired = timeDifference < oneHourInMillis;

    return {
      ...appt,
      isTimeConflict: checkConflicts(appt),
      isSlotUnavailable: isSlotUnavailable,
      isTimeExpired: isTimeExpired
    };
  });
});



const formatAppointmentDateTime = (datetime) => {
  const d = new Date(datetime);
  return d.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const fetchLawyerProfile = async () => {
  try {
    const res = await axios.get('/api/lawyers/me');
    lawyer.value = res.data;
  } catch (err) {
    console.error('변호사 정보 실패:', err);
  }
};

const fetchAppointments = async () => {
  try {
    const res = await axios.get('/api/appointments/me');
    const appointmentsWithClients = await Promise.all(
      res.data.map(async (appt) => {
        const clientRes = await axios.get(`/api/clients/${appt.clientId}`);
        return { ...appt, client: clientRes.data };
      })
    );
    appointments.value = appointmentsWithClients;
  } catch (err) {
    console.error('예약 실패:', err);
  }
};

const fetchUnavailableSlots = async () => {
  if (!lawyer.value || !lawyer.value.lawyerId) return;
  try {
    const res = await axios.get(`/api/lawyers/${lawyer.value.lawyerId}/unavailable-slot`);
    unavailableSlots.value = res.data;
  } catch (err) {
    console.error('사용 불가능한 슬롯 정보 실패:', err);
    unavailableSlots.value = [];
  }
};

// ✅ 상담 신청서 조회 함수 추가
const viewApplication = async (applicationId) => {
  if (!applicationId) {
    alert('상담 신청서가 존재하지 않습니다.');
    return;
  }
  try {
    const res = await axios.get(`/api/applications/${applicationId}`);
    modalApplicationData.value = res.data.data.application;
    isModalOpen.value = true;
  } catch (err) {
    console.error('상담 신청서 조회 실패:', err);
    alert('상담 신청서를 불러오는 데 실패했습니다.');
  }
};

const updateAppointmentStatus = async (appointmentId, status) => {
  const statusText = status === 'REJECTED' ? '거절' : '수락';
  if (!confirm(`정말로 이 상담 요청을 ${statusText}하시겠습니까?`)) {
    return;
  }

  try {
    const res = await axios.patch(`/api/appointments/${appointmentId}/status`, {
      "appointmentStatus": status
    });

    if (res.status === 200) {
      alert(`상담이 ${statusText}되었습니다.`);
      // ✅ 상태 변경 후 예약 목록을 다시 가져와 UI를 즉시 갱신
      await fetchAppointments();
    }
  } catch (error) {
    console.error(`상담 ${statusText} 실패:`, error);
    alert(`상담 ${statusText}에 실패했습니다. 다시 시도해주세요.`);
  }
};

const goToProfileUpdate = () => {
  router.push({ name: 'LawyerProfileUpdate' });
};

const goToHistory = () => {
  router.push({ name: 'LawyerConsultHistory' });
};

const handleWithdraw = async () => {
  if (!confirm('정말로 회원탈퇴하시겠습니까?')) return;

  try {
    await axios.delete('/api/lawyers/me');
    alert('회원탈퇴가 완료되었습니다.');
    localStorage.removeItem('accessToken');
    localStorage.removeItem('userType');
    window.location.href = '/';
  } catch (error) {
    console.error('회원탈퇴 실패:', error);
    alert('회원탈퇴에 실패했습니다. 다시 시도해주세요.');
  }
};

onMounted(async () => {
  await fetchLawyerProfile();
  await Promise.all([
    fetchAppointments(),
    fetchUnavailableSlots()
  ]);
  console.log('API에서 받은 변호사 데이터:', lawyer.value?.certificationStatus);
});
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
  width: 100%; /* ✅ 부모 영역(mypage-container)에 꽉 차게 */
  max-width: 100%;
  margin-top: 30px; /* ✅ 위에 여백 추가 */
}
.profile-left {
  display: flex;
  align-items: center;
}

.profile-info {
  display: flex;
  flex-direction: column; /* 수직 정렬 */
  align-items: flex-start; /* 왼쪽 정렬 */
  font-size: 0.8rem;
  margin-left: 1rem;
}
.profile-img {
  width: 160px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 20px;
}
.verified {
  color: #1d2b50;
  margin-left: 8px;
}
.unverified {
  color: #ccc;
  margin-left: 8px;
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


/* 대기중인 예약 목록 */
.pending-appointments-section {
  margin-bottom: 40px;
}
.pending-appointments-section h4 {
  margin-bottom: 20px;
}
.action-buttons {
  display: flex;
  gap: 8px;
}
.action-buttons button {
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: bold;
  cursor: pointer;
  border: none;
}
.accept-btn {
  background-color: #3478ff;
  color: white;
}
.reject-btn {
  background-color: #f44336;
  color: white;
}

.conflict-warning {
  color: #d32f2f;
  font-size: 0.8rem;
  margin-top: 4px;
}

.accept-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
.action-buttons button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  color: #666;
}
.accept-btn:disabled {
    background-color: #ccc;
}
.reject-btn:disabled {
    background-color: #ccc;
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
  padding: 0px 8px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: bold;
  white-space: nowrap;
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
