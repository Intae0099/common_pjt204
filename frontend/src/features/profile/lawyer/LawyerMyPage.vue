<template>
  <div v-if="userInfo" class="element">
    <div class="div">
      <!-- 사용자 정보 -->
      <div class="overlap">
        <img class="img" :src="userInfo.profileImage" alt="Profile" />
        <div class="text-wrapper">{{ userInfo.name }}</div>
        <div class="overlap-group" />
        <div class="text-wrapper-2">{{ userInfo.birthdate }}</div>
        <div class="text-wrapper-3">계정설정</div>
      </div>
      <div class="text-wrapper-4">마이페이지</div>

      <!-- 예약일정 -->
      <div class="text-wrapper-5">예약일정</div>

      <!-- v-calendar 컴포넌트 -->
      <v-calendar
        class="custom-calendar"
        :attributes="calendarAttributes"
        @dayclick="handleDateSelect"
        is-expanded
      />
      <div class="text-wrapper-client-requests">상담 요청 현황</div>
      <div class="client-request-list">
        <div v-if="clientRequests.length === 0" class="no-requests">
          새로운 상담 요청이 없습니다.
        </div>
        <div v-for="request in clientRequests" :key="request.id" class="client-request-item">
          <p>
            <span class="span">{{ request.clientName }} </span>
            <span class="text-wrapper-14">의뢰인</span>
            <span class="status-badge" :class="`status-${request.status.code}`">{{ request.status.text }}</span>
            <button class="text-wrapper-9">상담신청서 확인</button>
          </p>
        </div>
      </div>
      <!-- 선택된 날짜 표시 -->
      <div class="selected-date-display">{{ formattedSelectedDate }}</div>

      <!-- 시간표 (로딩 상태에 따라 표시) -->
      <div v-if="isLoadingTimeSlots" class="loading-spinner">
        시간표를 불러오는 중...
      </div>
      <div v-else>
        <!-- 오전 시간표 -->
        <div class="text-wrapper-10">오전</div>
        <div class="time-grid">
          <button v-for="slot in morningSlots" :key="slot.time" class="time-slot-button" :class="{ 'has-appointment': slot.details }" :disabled="!slot.details" @click="openAppointmentModal(slot.details)">
            {{ slot.time }}
          </button>
        </div>
        <!-- 오후 시간표 -->
        <div class="text-wrapper-12">오후</div>
        <div class="time-grid">
          <button v-for="slot in afternoonSlots" :key="slot.time" class="time-slot-button" :class="{ 'has-appointment': slot.details }" :disabled="!slot.details" @click="openAppointmentModal(slot.details)">
            {{ slot.time }}
          </button>
        </div>
      </div>
      <hr class="section-divider">
      <div class="text-wrapper-15">상담내역</div>
      <hr class="section-divider">
      <div class="text-wrapper-16">프로필 수정</div>
      <hr class="section-divider">
      <div class="text-wrapper-16">회원탈퇴</div>
    </div>
  </div>

  <div v-else class="initial-loading">
    마이페이지 정보를 불러오는 중입니다...
  </div>

  <!-- 예약 정보 모달 -->
  <div v-if="isModalVisible" class="modal-backdrop" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>예약 상세 정보</h3>
        <button class="close-button" @click="closeModal">×</button>
      </div>
      <div class="modal-body" v-if="selectedAppointment">
        <p><strong>시간:</strong> {{ selectedAppointment.time }}</p>
        <p><strong>의뢰인:</strong> {{ selectedAppointment.clientName }}</p>
        <p><strong>상담 주제:</strong> {{ selectedAppointment.topic }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { Calendar as VCalendar } from 'v-calendar';
import 'v-calendar/style.css';

// --- 반응형 데이터 정의 ---
const userInfo = ref(null);
const timeSlots = ref([]);
const selectedDate = ref(new Date());
const appointmentDates = ref([]);
const isLoadingTimeSlots = ref(false);
const isModalVisible = ref(false);
const selectedAppointment = ref(null);
// 새로 추가된 상담 요청 목록 데이터
const clientRequests = ref([]);

// --- Computed 속성 ---
const morningSlots = computed(() => timeSlots.value.filter(slot => parseInt(slot.time.split(':')[0]) < 12));
const afternoonSlots = computed(() => timeSlots.value.filter(slot => parseInt(slot.time.split(':')[0]) >= 12));
const formattedSelectedDate = computed(() => {
  if (!selectedDate.value) return '날짜를 선택해주세요.';
  const year = selectedDate.value.getFullYear();
  const month = String(selectedDate.value.getMonth() + 1).padStart(2, '0');
  const day = String(selectedDate.value.getDate()).padStart(2, '0');
  const dayOfWeek = ['일', '월', '화', '수', '목', '금', '토'][selectedDate.value.getDay()];
  return `${year}.${month}.${day} (${dayOfWeek})`;
});
const calendarAttributes = computed(() => [
  { highlight: { color: 'blue', fillMode: 'solid' }, dates: appointmentDates.value },
  { key: 'today', dot: true, dates: new Date() }
]);

// --- 메서드 ---
const handleDateSelect = async (day) => {
  if (!appointmentDates.value.includes(day.id)) { return; }
  selectedDate.value = day.date;
  await fetchAppointmentsForDate(day.id);
};

const fetchAppointmentsForDate = async (dateString) => {
  isLoadingTimeSlots.value = true;
  timeSlots.value = [];
  const allAppointmentsByDate = {
    '2025-07-16': [ { time: '10:00', clientName: '전해지', topic: '부동산 계약 분쟁' }, { time: '17:30', clientName: '박의뢰', topic: '손해배상 청구 소송' } ],
    '2025-07-18': [ { time: '14:00', clientName: '최고객', topic: '이혼 소송 자문' } ]
  };
  await new Promise(resolve => setTimeout(resolve, 500));
  const backendAppointments = allAppointmentsByDate[dateString] || [];
  const allPossibleTimes = [];
  for (let h = 8; h <= 20; h++) {
    for (let m = 0; m < 60; m += 30) {
      if(h === 12) continue;
      allPossibleTimes.push(`${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`);
    }
  }
  timeSlots.value = allPossibleTimes.map(timeStr => ({
    time: timeStr,
    details: backendAppointments.find(appt => appt.time === timeStr) || null
  }));
  isLoadingTimeSlots.value = false;
};

const openAppointmentModal = (details) => {
  if (!details) return;
  selectedAppointment.value = details;
  isModalVisible.value = true;
};

const closeModal = () => {
  isModalVisible.value = false;
  selectedAppointment.value = null;
};

// --- 생명주기 훅 ---
onMounted(async () => {
  userInfo.value = {
    name: '김변호',
    birthdate: '1985.01.10',
    profileImage: 'https://via.placeholder.com/100'
  };

  appointmentDates.value = ['2025-07-16', '2025-07-18'];

  // 새로 추가된 상담 요청 목록 데이터 로딩 (시뮬레이션)
  clientRequests.value = [
    { id: 1, clientName: '윤규성', status: { code: 'accepted', text: '요청수락' } },
    { id: 2, clientName: '전해지', status: { code: 'pending', text: '요청대기' } },
    { id: 3, clientName: '강상담', status: { code: 'completed', text: '상담완료' } }
  ];

  if (appointmentDates.value.length > 0) {
    const initialDateStr = appointmentDates.value[0];
    selectedDate.value = new Date(initialDateStr);
    await fetchAppointmentsForDate(initialDateStr);
  } else {
    const todayStr = new Date().toISOString().split('T')[0];
    await fetchAppointmentsForDate(todayStr);
  }
});
</script>

<style>
</style>
