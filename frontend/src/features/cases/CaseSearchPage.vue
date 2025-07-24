<!-- src/pages/case/CaseSearchPage.vue -->
<template>
  <CaseLayout>
    <!-- 여기부터 빨간 박스 내부 콘텐츠 -->
    <div class="search-bar">
      <input v-model="query" placeholder="궁금한 판례를 검색해보세요" />
      <button @click="search">→</button>
    </div>
    <div class="text-wrapper-10">정확도 순</div>
    <div class="case-list">
      <CaseCard
        v-for="item in caseList"
        :key="item.id"
        :data="item"
      />
    </div>
  </CaseLayout>
</template>

<script setup>
import CaseLayout from '@/components/layout/CaseLayout.vue'
import CaseCard from '@/features/cases/CaseCard.vue'
import { ref } from 'vue'

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
