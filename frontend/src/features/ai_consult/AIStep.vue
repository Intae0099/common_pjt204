<template>
  <div class="layout-background">
    <div class="container">
      <div>
        <div class="wrapper">
          <!-- 왼쪽: 사용자 입력창 -->
          <ChatInputBox
            :disabled="isLoading || isFindingVerdict"
            @submit="handleUserInput"
          />

          <!-- 오른쪽: AiBox는 작성중 / 결과 표시 -->
          <AiBox
            :isLoading="isLoading"
            :response="aiResponse"
            :userText="userInput"
            :showPredictButton="!verdictResult"
            @open-modal="showModal = true"
            @predict="handlePredictVerdict"
          />
        </div>

        <!-- 하단 버튼 영역 -->
        <BottomActionBar
          v-if="aiResponse && !isFindingVerdict && !verdictResult && !showRecommendList"
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
        <div v-if="verdictResult">
          <p>{{ verdictResult }}</p>
          <button
            v-if="canShowRecommendBtn && !showRecommendList"
            @click="showLawyers"
          >
            변호사 추천받기
          </button>
        </div>
        <!-- 변호사 추천 리스트 -->
        <LawyerRecommendList v-if="showRecommendList" :lawyers="lawyers" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

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
const verdictResult = ref(null)            // 판례 예측 결과
const canShowRecommendBtn = ref(false)     // 버튼 활성화 조건
const lawyers = ref([])                    // 추천 변호사 목록
const showRecommendList = ref(false)       // 변호사 추천 리스트 보여줄지 여부


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
  try {
    const { data } = await axios.post('/api/verdict/predict', {
      content: userInput.value,
    })

    // ✅ 전체 데이터를 받아놓고 필요한 부분만 시점에 맞게 표시
    verdictResult.value = data.verdictSummary
    lawyers.value = data.lawyers
    canShowRecommendBtn.value = true
  } catch (err) {
    console.error('판례 예측 실패', err)
  } finally {
    isFindingVerdict.value = false
  }
}

const showLawyers = () => {
  showRecommendList.value = true
}


const router = useRouter()

const handleModalRoute = (target) => {
  showModal.value = false
  if (target === 'lawyer') {
    router.push({ name: 'LawyerSearch' }) // ✅ SPA 방식 라우팅
  }
}
</script>

<style scoped>
.layout-background {
  position: relative;
  width: 100vw;
  left: 50%;
  right: 50%;
  margin-left: -50vw;
  margin-right: -50vw;
  background-image: url('@/assets/ai-consult-bg.png');
  background-size: cover;
  background-repeat: no-repeat;
  background-position: center;
  min-height: 100vh;
  background-color: #F7FCFF;
}
.container{
  padding: 40px 16px;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh; /* 화면 전체 가운데 정렬을 위한 높이 */
}
.wrapper {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  gap: 60px;
  flex-wrap: wrap;
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 40px;
}
</style>
