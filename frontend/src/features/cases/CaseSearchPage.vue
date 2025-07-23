<!-- src/pages/case/CaseSearchPage.vue -->
<template>
  <CaseLayout>
    <!-- 여기부터 빨간 박스 내부 콘텐츠 -->
    <div class="search-bar">
      <input v-model="query" placeholder="궁금한 판례를 검색해보세요" />
      <button @click="search">→</button>
    </div>

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
import { ref } from 'vue'

const query = ref('')
const caseList = ref([
  { id: 1, title: '유언효력 확인 사건', summary: '유언 녹음 관련 사건 요약...' },
  // 더미 데이터들
])
</script>
