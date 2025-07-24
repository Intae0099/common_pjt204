<template>
  <div class="ai-step-wrapper">
    <div class="main-content">
      <!-- 왼쪽: 사용자 입력창 -->
      <ChatInputBox
        :disabled="isLoading || isFindingVerdict"
        @submit="handleUserInput"
      />

      <!-- 오른쪽: AiBox는 작성중 / 결과 표시 -->
      <AiBox
        :isLoading="isLoading"
        :response="aiResponse"
        @open-modal="showModal = true"
      />
    </div>

    <!-- 하단 버튼 영역 -->
    <BottomActionBar
      v-if="aiResponse && !isFindingVerdict && !lawyerListVisible"
      @predict="handlePredictVerdict"
      @quick-consult="showModal = true"
    />

    <!-- '바로 상담하기' 모달 -->
    <SuggestModal
      v-if="showModal"
      @close="showModal = false"
      @route="handleModalRoute"
    />

    <!-- 판례 찾는 중 표시 -->
    <VerdictFindingBox v-if="isFindingVerdict" />

    <!-- 변호사 추천 리스트 -->
    <LawyerRecommendList v-if="lawyerListVisible" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ChatInputBox from './components/ChatInputBox.vue'
import AiBox from './components/AiBox.vue'
import BottomActionBar from './components/BottomActionBar.vue'
import SuggestModal from './components/SuggestModal.vue'
import VerdictFindingBox from './components/VerdictFindingBox.vue'
import LawyerRecommendList from './components/LawyerRecommendList.vue'
import axios from 'axios'

const userInput = ref('')
const aiResponse = ref(null)
const isLoading = ref(false)
const showModal = ref(false)
const isFindingVerdict = ref(false)
const lawyerListVisible = ref(false)

const handleUserInput = async (text) => {
  userInput.value = text
  aiResponse.value = null
  isLoading.value = true

  try {
    const { data } = await axios.post('/api/ai-consult', { content: text })
    aiResponse.value = data
  } catch (error) {
    console.error('AI 응답 실패:', error)
  } finally {
    isLoading.value = false
  }
}

const handlePredictVerdict = async () => {
  isFindingVerdict.value = true
  await new Promise((resolve) => setTimeout(resolve, 2000)) // 실제 API 대체
  isFindingVerdict.value = false
  lawyerListVisible.value = true
}

const handleModalRoute = (target) => {
  showModal.value = false
  if (target === 'lawyer') {
    // 예: 라우팅 이동
    window.location.href = '/lawyers'
  }
}
</script>

<style scoped>
.ai-step-wrapper {
  width: 100%;
  min-height: 100vh;
  background-color: #f9fcff;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 40px;
}

.main-content {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  gap: 80px;
  margin-bottom: 40px;
  /* 기본: 가로 배치 (데스크탑) */
  flex-direction: row;
}

/* 태블릿 이하: 세로 배치 */
@media (max-width: 1023px) {
  .main-content {
    flex-direction: column;
    align-items: center;
    gap: 40px;
  }
}
</style>
