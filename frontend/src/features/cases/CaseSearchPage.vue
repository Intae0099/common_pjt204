<template>
  <CaseLayout>
    <LayoutDefault>
    <div class="search-container">
      <div class="search-bar">
        <input
          type="text"
          v-model="query"
          placeholder="궁금한 판례를 검색해보세요"
          @keyup.enter="performSearch"
        />
        <button @click="performSearch">→</button>
      </div>
      <select v-model="sortOption" @change="handleSortChange" class="sort-select">
        <option value="accuracy">정확도 순</option>
        <option value="recent">최신 순</option>
      </select>
    </div>

    <div v-if="isLoading" class="status-message">
      <p>판례를 검색 중입니다...</p>
    </div>
    <div v-else-if="error" class="status-message error">
      <p>{{ error }}</p>
    </div>

    <div v-else-if="hasResults">
      <div class="case-list">
        <CaseCard
          v-for="item in paginatedCaseList"
          :key="item.caseId"
          :data="item"
          :highlight="query"
        />
      </div>

      <div v-if="totalPages > 1" class="pagination-container">
        <button
          @click="setPage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="page-btn"
        >
          이전
        </button>
        <button
          v-for="page in totalPages"
          :key="page"
          @click="setPage(page)"
          :class="{ active: page === currentPage }"
          class="page-btn"
        >
          {{ page }}
        </button>
        <button
          @click="setPage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="page-btn"
        >
          다음
        </button>
      </div>
    </div>

    <div v-else class="status-message">
      <p>{{ searchPerformed ? '검색 결과가 없습니다.' : '판례를 검색해 보세요.' }}</p>
    </div>
    </LayoutDefault>
  </CaseLayout>
</template>

<script setup>
import CaseLayout from '@/components/layout/CaseLayout.vue';
import CaseCard from '@/features/cases/CaseCard.vue';
import LayoutDefault from '@/components/layout/LayoutDefault.vue'
import { useCasesStore } from '@/stores/cases';
import { storeToRefs } from 'pinia';
import { onMounted } from 'vue'

onMounted(()=>{
  window.scrollTo(0, 0);
})

// 1. 스토어 인스턴스 생성
const casesStore = useCasesStore();

// 2. ✨ storeToRefs로 필요한 상태와 getter 가져오기 (paginatedCaseList 추가)
const {
  query,
  sortOption,
  isLoading,
  error,
  searchPerformed,
  hasResults,
  // --- 페이지네이션을 위한 getter와 state ---
  paginatedCaseList,
  totalPages,
  currentPage,
  // ------------------------------------------
} = storeToRefs(casesStore);

// 3. ✨ 액션 가져오기
const { searchCases, setPage } = casesStore;

const performSearch = () => {
  searchCases();
};

const handleSortChange = () => {
  // `v-model`이 이미 `sortOption` 상태를 변경했습니다.
  // 우리는 페이지만 1로 리셋하여 사용자 경험을 향상시킵니다.
  setPage(1);
};
</script>

<style scoped>
/* 기존 스타일은 그대로 유지 */
.search-container {
  display: flex;
  justify-content: center;
  align-items: end;
  gap: 1rem;
  margin: 2rem 0;
}
.search-bar {
  display: flex;
  align-items: center;
  width: 600px;
  border: 1px solid #cfcfcf;
  border-radius: 15px;
  padding: 0.75rem 1rem;
  transition: border 0.3s ease;
}
.search-bar:hover {
  border: 1px solid #6c9bcf
}
.search-bar input {
  flex: 1;
  border: none;
  background-color: transparent;
  font-size: 16px;
  padding: 0;
  outline: none;
}
.search-bar button {
  border: none;
  background: none;
  cursor: pointer;
  font-size: 18px;
  color: #888;
  transition: transform 0.2s ease;
}
.search-bar button:hover {
  transform: scale(1.1);
}
.sort-select {
  appearance: none;
  height: 30px;
  padding: 0 2.5rem 0 1rem;
  border: 1px solid #cfcfcf;
  border-radius: 15px;
  font-size: 12px;
  color:  #888;
  background-image: url("data:image/svg+xml,%3Csvg fill='gray' height='16' viewBox='0 0 24 24' width='16' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 12px;
}

.status-message {
  text-align: center;
  margin-top: 2rem;
  color: #888;
}
.error {
  color: red;
}

/* 결과 카드 리스트 레이아웃 */
.case-list{
  max-width: 980px;            /* 배너/검색과 균형 */
  margin: 24px auto 0;
  display: grid;
  gap: 12px;                   /* 카드 간격 */
  grid-template-columns: 3fr;  /* 기본 1열 */
}

/* 넓은 화면에서는 2열로 (검색바 폭 600px과도 균형) */
@media (min-width: 1200px){
  .case-list{
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
}


/* ✨ 페이지네이션 UI 스타일 추가 */
.pagination-container {
  font-family: 'Noto Sans KR', sans-serif;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 2rem;
  gap: 0.5rem;
}
.page-btn {
  border: none;
  background-color: #fff;
  color: #6c9bcf;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.page-btn:hover:not(:disabled) {
  background-color: #eee;
}
.page-btn.active {
  background-color: #6c9bcf;
  color: white;
  border-color: #6c9bcf;
  cursor: default;
}
.page-btn:disabled {
  color: #cfcfcf;
  cursor: not-allowed;
}
</style>
