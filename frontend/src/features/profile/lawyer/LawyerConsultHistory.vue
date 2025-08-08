<template>
  <div class="container">
    <div class="history-container">
      <div class="back-button" @click="goBack">
        <ChevronLeftIcon class="chevron-icon" />
        <span>이전</span>
      </div>
      <div class="header-row">
        <h2>상담내역</h2>
        <div class="filter-sort-group">
          <div class="sort-wrapper" @click="toggleFilterOpen">
            <span>{{ filterText(selectedStatus) }}</span>
            <component :is="isFilterOpen ? ChevronUpIcon : ChevronDownIcon" class="sort-icon" />
            <select v-model="selectedStatus" @change="filterAndSortAppointments" class="native-select">
              <option value="all">전체</option>
              <option value="PENDING">대기중</option>
              <option value="CONFIRMED">상담확정</option>
              <option value="REJECTED">거절됨</option>
              <option value="CANCELLED">취소됨</option>
              <option value="ENDED">상담종료</option>
            </select>
          </div>
          <div class="sort-wrapper" @click="toggleSortOpen">
            <span>{{ sortOrder === 'desc' ? '최신순' : '오래된순' }}</span>
            <component :is="isSortOpen ? ChevronUpIcon : ChevronDownIcon" class="sort-icon" />
            <select v-model="sortOrder" @change="filterAndSortAppointments" class="native-select">
              <option value="desc">최신순</option>
              <option value="asc">오래된순</option>
            </select>
          </div>
        </div>
      </div>

      <div v-if="appointments.length === 0" class="empty">
        상담한 내역이 없습니다.
      </div>

      <div v-else>
        <div v-for="(group, month) in groupedAppointments" :key="month">
          <h3 class="month-header">{{ month }}</h3>
          <div v-for="appt in group" :key="appt.appointmentId" class="history-card">
            <div class="card-left">
              <div class="datetime">
                {{ formatDateTime(appt.startTime) }}
              </div>
              <div class="client">
                <span class="client-name">{{ appt.counterpartName }}</span> 의뢰인
              </div>
              <div :class="statusClass(appt.appointmentStatus)">
                {{ filterText(appt.appointmentStatus) }}
              </div>
            </div>
            <button class="view-btn" @click="goToApplication(appt.applicationId)">상담신청서 확인하기</button>
          </div>
        </div>
      </div>

      <div class="pagination">
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="page-btn"
        >
          이전
        </button>
        <button
          v-for="page in totalPages"
          :key="page"
          @click="goToPage(page)"
          :class="{ 'page-btn': true, 'active': currentPage === page }"
        >
          {{ page }}
        </button>
        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="page-btn"
        >
          다음
        </button>
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
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/lib/axios'
// ✅ 모달 및 아이콘 컴포넌트 임포트
import ApplicationDetail from '@/features/profile/user/ApplicationDetail.vue'
import { ChevronLeftIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/vue/24/solid'

const appointments = ref([])
const router = useRouter()
const showModal = ref(false)
const selectedApplication = ref(null)
const sortOrder = ref('desc')
const selectedStatus = ref('all') // ✅ 필터링 상태값
const isSortOpen = ref(false)
const isFilterOpen = ref(false)
const allAppointments = ref([]);

// ✅ 페이지네이션 관련 상태 변수
const currentPage = ref(1);
const itemsPerPage = ref(10); // 페이지당 10개 항목

// ✅ 전체 페이지 수 계산
const totalPages = computed(() => {
  return Math.ceil(allAppointments.value.length / itemsPerPage.value);
});

// ✅ 현재 페이지에 보여줄 데이터를 계산
const paginatedAppointments = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return appointments.value.slice(start, end);
});

// ✅ 월별로 상담 내역을 그룹화하는 계산 속성
const groupedAppointments = computed(() => {
  const groups = {};
  if (paginatedAppointments.value) {
    paginatedAppointments.value.forEach(appt => {
      const date = new Date(appt.startTime);
      const year = date.getFullYear();
      const month = date.getMonth() + 1;
      const monthKey = `${year}년 ${month}월`;
      if (!groups[monthKey]) {
        groups[monthKey] = [];
      }
      groups[monthKey].push(appt);
    });
  }
  return groups;
});

const toggleSortOpen = () => {
  isSortOpen.value = !isSortOpen.value
}
const toggleFilterOpen = () => {
  isFilterOpen.value = !isFilterOpen.value
}

const filterText = (status) => {
  switch (status) {
    case 'all': return '전체';
    case 'PENDING': return '대기중';
    case 'CONFIRMED': return '상담확정';
    case 'REJECTED': return '거절됨';
    case 'CANCELLED': return '취소됨';
    case 'ENDED': return '상담종료';
    default: return '기타';
  }
}

const statusClass = (status) => {
  return `status-${status.toLowerCase()}`;
};



// ✅ 모든 데이터를 불러온 후 필터링/정렬을 수행하는 함수
const fetchAppointments = async () => {
  try {
    const res = await axios.get('/api/appointments/me');
    allAppointments.value = res.data;
    filterAndSortAppointments();
  } catch (e) {
    console.error('상담내역 불러오기 실패:', e);
  }
}

// ✅ 필터링과 정렬을 수행하는 함수
const filterAndSortAppointments = () => {
  let filtered = allAppointments.value;
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(appt => appt.appointmentStatus === selectedStatus.value);
  }

  filtered.sort((a, b) => {
    const timeA = new Date(a.startTime).getTime();
    const timeB = new Date(b.startTime).getTime();
    return sortOrder.value === 'desc' ? timeB - timeA : timeA - timeB;
  });

  appointments.value = filtered;
  currentPage.value = 1; // 필터링/정렬 시 첫 페이지로 이동
}


// ✅ 페이지 이동 함수
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  }
}

const goBack = () => {
  // ✅ 변호사 마이페이지로 이동
  router.push('/lawyer/mypage');
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
  if (!applicationId) {
    alert('상담 신청서가 존재하지 않습니다.');
    return;
  }
  try {
    const res = await axios.get(`api/applications/${applicationId}`);
    selectedApplication.value = res.data.data.application;
    showModal.value = true;
  } catch (err) {
    console.error('상담 신청서 조회 실패:', err);
    alert('상담 신청서를 불러오는 데 실패했습니다.');
  }
};

onMounted(() => {
  fetchAppointments();
});
</script>

<style scoped>
/* UserConsultHistory.vue와 동일한 스타일 적용 */
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
.client {
  font-size: 1.2rem;
  color: #072D45;
}
.client-name{
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
.filter-sort-group {
    display: flex;
    gap: 1rem;
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
/* 상태별 스타일 */
.status-confirmed {
  color: #3478ff;
  font-weight: bold;
}
.status-pending {
  color: #f5a623;
  font-weight: bold;
}
.status-rejected {
  color: #f44336;
  font-weight: bold;
}
.status-cancelled {
  color: #f44336;
  font-weight: bold;
}
.status-ended {
  color: #888;
  font-weight: bold;
}

/* ✅ 페이지네이션 스타일 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 2rem;
}

.page-btn {
  padding: 8px 12px;
  border: 1px solid #B9D0DF;
  background-color: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  color: #072D45;
}

.page-btn:disabled {
  color: #ccc;
  cursor: not-allowed;
}

.page-btn.active {
  background-color: #072D45;
  color: white;
  border-color: #072D45;
}
/* ✅ 월별 헤더 스타일 */
.month-header {
  font-size: 1.2rem;
  font-weight: bold;
  color: #072D45;
  margin-top: 2rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}
</style>
