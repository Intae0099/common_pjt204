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
            <div v-if="item.summary" class="form-group">
              <label>한 줄 요약</label>
              <input
                type="text"
                :value="item.summary"
                readonly
                class="readonly-input"
              />
            </div>
            <div v-if="item.content" class="form-group scrollable-group">
              <label>사건 개요</label>
              <textarea
                class="scrollable-content"
                :value="item.content"
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
    const res = await axios.get('/api/applications/me')
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
/* ✅ 전체 페이지 스타일 */
.page-container, .wide-container {
  font-family: 'Noto Sans KR', sans-serif;
}
.page-container {
  padding: 100px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
}
.wide-container {
  padding-top: 100px;
}
.loading-container {
  flex-direction: column;
  color: #555;
  font-size: 1.2rem;
}
.back-btn {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  cursor: pointer;
  background-color: white;
}
.history-container {
  margin: 0 10rem;
  width: 100%;
}
.back-button {
  margin-top: 10px;
  margin-bottom: 25px;
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
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 2px solid #B9D0DF;
  color: #072D45;
  margin-bottom: 2rem;
}

/* ✅ 상담 신청서 카드 스타일 */
.history-card {
  border: 1px solid #e0e0e0;
  background: #f9f9f9;
  border-radius: 10px;
  margin-bottom: 1rem;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  cursor: pointer;
}
.card-header:hover {
  background-color: #f0f0f0;
}
.card-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.datetime {
  font-weight: bold;
  font-size: 0.8rem;
  color: #B9D0DF;
}
.title-text {
  font-size: 1.1rem;
  font-weight: bold;
  color: #072D45;
}
.expand-icon {
  width: 24px;
  height: 24px;
  color: #B9D0DF;
  transition: transform 0.2s ease;
}

/* ✅ 카드 상세 내용 스타일 */
.card-detail {
  padding: 1.5rem;
  border-top: 1px solid #e0e0e0;
  background-color: #fff;
  border-bottom-left-radius: 10px;
  border-bottom-right-radius: 10px;
}

/* 폼 스타일 재사용 */
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
input, textarea {
  padding: 0.75rem;
  border: 1px solid #B9D0DF;
  border-radius: 8px;
  font-size: 1rem;
  resize: none;
  background-color: #f7fcff;
  color: #555;
}
.readonly-input {
  background-color: #fff;
  color: #82A0B3;
}
.readonly-input-title{
  border: none;
  padding: 0;
  font-size: 1.5rem;
  font-weight: bold;
  background-color: transparent;
}
.scrollable-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.scrollable-content {
  min-height: 100px;
  max-height: 150px;
  overflow-y: auto;
  background-color: #fff;
  border: 1px solid #B9D0DF;
  color: #82A0B3;
  border-radius: 8px;
  padding: 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
}
.scroll-area::-webkit-scrollbar,
.scrollable-content::-webkit-scrollbar {
  width: 6px;
}
.scroll-area::-webkit-scrollbar-thumb,
.scrollable-content::-webkit-scrollbar-thumb {
  background-color: #d4e1ed;
  border-radius: 3px;
}
.scroll-area::-webkit-scrollbar-track,
.scrollable-content::-webkit-scrollbar-track {
  background-color: transparent;
}
</style>
