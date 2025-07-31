<!-- src/pages/case/CaseSearchPage.vue -->
<template>
  <CaseLayout>
    <LayoutDefault>
      <!-- 여기부터 빨간 박스 내부 콘텐츠 -->
        <div class="search-container">
          <div class="search-bar">
            <input
            type="text"
            v-model="query"
            placeholder="궁금한 판례를 검색해보세요"
            @keyup.enter="search"/>
            <button @click="search">→</button>
          </div>
          <select v-model="sortOption" class="sort-select">
            <option value="accuracy">정확도 순</option>
            <option value="recent">최신 순</option>
          </select>
        </div>
      <div class="case-list">
        <CaseCard
          v-for="item in caseList"
          :key="item.id"
          :data="item"
        />
      </div>
    </LayoutDefault>
  </CaseLayout>
</template>

<script setup>
import CaseLayout from '@/components/layout/CaseLayout.vue'
import CaseCard from '@/features/cases/CaseCard.vue'
import LayoutDefault from '@/components/layout/LayoutDefault.vue'
import { ref } from 'vue'

const sortOption = ref('accuracy')
const query = ref('')
const caseList = ref([
  // 더미 데이터들, 페이징 없다 가정
  { id: 1, title: '유언효력 확인 사건', summary: '유언 녹음 관련 사건 요약...' },
  { id: 2, title: '손해배상 청구 사건', summary: '교통사고로 인한 손해배상 요약...' },
  { id: 3, title: '부동산 소유권 이전등기', summary: '매매 계약 후 소유권 이전 관련 요약...' },
  { id: 1, title: '유언효력 확인 사건', summary: '유언 녹음 관련 사건 요약...' },
  { id: 2, title: '손해배상 청구 사건', summary: '교통사고로 인한 손해배상 요약...' },
  { id: 3, title: '부동산 소유권 이전등기', summary: '매매 계약 후 소유권 이전 관련 요약...' },
  { id: 1, title: '유언효력 확인 사건', summary: '유언 녹음 관련 사건 요약...' },
  { id: 2, title: '손해배상 청구 사건', summary: '교통사고로 인한 손해배상 요약...' },
  { id: 3, title: '부동산 소유권 이전등기', summary: '매매 계약 후 소유권 이전 관련 요약...' },
])
</script>

<style scoped>
/* 검색창 */
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
  border: 1px solid #b4c3d1;
  border-radius: 10px;
  padding: 0.75rem 1rem;
  transition: border 0.3s ease;
}
.search-bar:hover {
  border: 1px solid #007bff;
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
  color: #007bff;
  transition: transform 0.2s ease;
}

.search-bar button:hover {
  transform: scale(1.1);
}

.sort-select {
  appearance: none;
  height: 30px;
  padding: 0 2.5rem 0 1rem;
  border: 1px solid #b4c3d1;
  border-radius: 15px;
  font-size: 12px;
  color: #333;
  background-image: url("data:image/svg+xml,%3Csvg fill='black' height='16' viewBox='0 0 24 24' width='16' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 12px;
}
</style>
