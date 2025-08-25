<template>
  <div v-if="loading" class="page-container loading-container">
    <p>상담 신청서를 불러오는 중입니다...</p>
  </div>

  <div v-else-if="items.length === 0" class="page-container loading-container">
    <p>표시할 상담 신청서가 없습니다.</p>
    <button @click="$router.back()" class="back-btn">돌아가기</button>
  </div>

  <div v-else class="page-container">
    <div class="history-container">
      <div class="back-button" @click="$router.back()">
        <ChevronLeftIcon class="chevron-icon" />
        <span>이전</span>
      </div>
      <div class="header-row">
        <h2>상담신청서 보관함</h2>
      </div>

      <div v-for="item in items" :key="item.applicationId" class="history-card">
        <div class="card-header" @click="toggleExpand(item.applicationId)">
          <div class="card-left">
            <div class="datetime">
              {{ formatDateTime(item.createdAt) }}
            </div>
            <div class="title-text">
              {{ item.title }}
            </div>
          </div>
          <component :is="expandedItemId === item.applicationId ? ChevronUpIcon : ChevronDownIcon" class="expand-icon" />
        </div>

        <div v-if="expandedItemId === item.applicationId" class="card-detail">
          <form class="consult-form">
            <div v-if="item.summary" class="form-group scrollable-group">
              <label>사건 개요</label>
              <textarea
                class="scrollable-content"
                :value="item.summary"
                readonly
              ></textarea>
            </div>
            <div v-if="item.outcome" class="form-group scrollable-group">
              <label>원하는 결과</label>
              <textarea
                class="scrollable-content"
                :value="item.outcome"
                readonly
              ></textarea>
            </div>
            <div v-if="item.disadvantage" class="form-group scrollable-group">
              <label>사건에서 불리한 점</label>
              <textarea
                class="scrollable-content"
                :value="item.disadvantage"
                readonly
              ></textarea>
            </div>
            <div v-if="item.recommendedQuestions?.length" class="form-group scrollable-group">
              <label>변호사에게 궁금한 점</label>
              <textarea
                class="scrollable-content"
                :value="item.recommendedQuestions.join('\n')"
                readonly
              ></textarea>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '@/lib/axios'
import { ChevronLeftIcon, ChevronDownIcon, ChevronUpIcon } from '@heroicons/vue/24/solid'


const items = ref([])
const loading = ref(true)
const expandedItemId = ref(null) // ✅ 펼쳐진 카드의 ID를 저장

const transformApiData = (apiList) => {
  return apiList.map(item => ({
    ...item,
    recommendedQuestions: Object.values(item.recommendedQuestions || {})
  }))
}

onMounted(async () => {
  try {
    const res = await axios.get('/api/applications/me', { params: { isCompleted: true } })
    if (res.data.success) {
      const apiList = res.data.data.applicationList;
      items.value = transformApiData(apiList);
      // ✅ 최신순으로 정렬
      items.value.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    } else {
      throw new Error(res.data.message)
    }
  } catch (error) {
    console.error('상담신청서 목록 로딩 실패:', error)
    items.value = []
  } finally {
    loading.value = false
  }
})

// ✅ 카드 펼치기/접기 함수
const toggleExpand = (id) => {
  expandedItemId.value = expandedItemId.value === id ? null : id;
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
</script>

<style scoped>
/* ===== 공통 레이아웃 / 타이포 ===== */
.page-container {
  max-width: 700px;         /* 두 번째 페이지와 동일한 폭 */
  margin: 0 auto;           /* 가운데 정렬 */
  padding: 20px 20px;       /* 동일 여백 */
  font-family: 'Noto Sans KR', sans-serif;
  color: #333333;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  color: #888;
  font-size: 1rem;
}

/* ===== 헤더 영역 ===== */
.back-button {
  margin-top: 100px;        /* 동일 위치감 */
  margin-bottom: 20px;
  margin-left: -10px;
  font-size: 1rem;
  color: #6c9bcf;           /* 포인트 컬러 통일 */
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  width: 80px;
  transition: color 0.2s ease-in-out;
}
.back-button:hover { color: #cfcfcf; }

.chevron-icon { width: 20px; height: 20px; }

.header-row {
  display: flex;
  flex-direction: column;   /* 세로 정렬 (제목 중앙) */
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid #888; /* 상담내역 페이지와 동일한 구분선 */
  margin-bottom: 1rem;
}
.header-row h2 {
  text-align: center;
  margin: 15px 0 10px;
  font-size: 24px;
  font-weight: 700;
  color: #333333;
}

/* ===== 리스트/빈 상태 ===== */
.history-container { width: 100%; }

.empty,
.page-container.loading-container p {
  margin-top: 10px;
  color: #cfcfcf;
  text-align: center;
}

/* ===== 카드 리스트 ===== */
.history-card {
  border: 1px solid #cfcfcf;     /* 동일 테두리 */
  border-radius: 8px;            /* 동일 라운드 */
  background: #fff;
  padding: 0;                    /* 헤더/디테일에서 패딩 관리 */
  margin-bottom: 16px;
  transition: background-color 0.15s ease;
}
.history-card:hover { background-color: #fafafa; }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;               /* 상담내역 카드 패딩 값 */
  cursor: pointer;
}
.card-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.datetime {
  font-size: 0.8rem;
  color: #B9D0DF;                /* 날짜 색 통일 */
  font-weight: 500;
}
.title-text {
  font-size: 1.05rem;
  color: #333333;                /* 제목 색 통일 */
  font-weight: 700;
  line-height: 1.3;
}
.expand-icon {
  width: 20px;
  height: 20px;
  color: #6c9bcf;                /* 포인트 컬러 통일 */
  transition: transform 0.2s ease;
}

/* ===== 카드 디테일 (폼) ===== */
.card-detail {
  padding: 1.5rem;
  border-top: 1px solid #eaeaea;
  background-color: #fff;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
}

.consult-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
label {
  font-size: 0.9rem;
  color: #666;
}
input,
textarea {
  padding: 0.75rem;
  border: 1px solid #cfcfcf;     /* 테두리 색 통일 */
  border-radius: 8px;
  font-size: 1rem;
  background-color: #fff;        /* 기본 흰색 (상담내역과 톤 맞춤) */
  color: #333;
}
.readonly-input { color: #666; }
.scrollable-group {}
.scrollable-content {
  min-height: 100px;
  max-height: 150px;
  overflow-y: auto;
  border: 1px solid #cfcfcf;
  border-radius: 8px;
  padding: 0.75rem;
  line-height: 1.5;
  color: #333;
}

/* 스크롤바 톤 맞춤 */
.scrollable-content::-webkit-scrollbar { width: 6px; }
.scrollable-content::-webkit-scrollbar-thumb {
  background-color: #e0e0e0;
  border-radius: 3px;
}
.scrollable-content::-webkit-scrollbar-track { background-color: transparent; }

/* ===== 버튼(빈 상태의 돌아가기 등) ===== */
.back-btn {
  margin-top: 1rem;
  padding: 8px 12px;
  border: 1px solid #cfcfcf;
  border-radius: 8px;
  background-color: #fff;
  color: #6c9bcf;
  cursor: pointer;
  transition: background-color 0.2s;
}
.back-btn:hover { background-color: #eee; }

/* ===== 반응형 ===== */
@media (max-width: 640px) {
  .page-container { padding: 16px; }
  .card-header, .card-detail { padding: 1.1rem; }
  .title-text { font-size: 1rem; }
}

</style>
