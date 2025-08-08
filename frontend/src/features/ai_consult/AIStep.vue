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

          <div v-if="isLoading || isFindingVerdict" class="loading-dots-wrapper">
            <LoadingDots />
          </div>

          <AiBox
            ref="aiBoxRef"
            :isLoading="isLoading"
            :isFindingVerdict="isFindingVerdict"
            :response="aiResponse"
            :userText="userInput"
            :showPredictButton="!verdictResult"
            :verdictResult="verdictResult"
            @open-modal="handleOpenSaveModal"
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

        <SaveModal
          v-if="showSaveModal"
          @confirm-save="handleConfirmSave"
          @close="showSaveModal = false"
        />

        <div v-if="verdictResult && canShowRecommendBtn && !showRecommendList" class="recommend-button-wrapper">
          <button class="recommend-button" @click="showLawyers">
            변호사 추천받기
            <span class="arrow">→</span>
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
import SaveModal from './components/SaveModal.vue'
import LawyerRecommendList from './components/LawyerRecommendList.vue'
// import axios from 'axios'
import { fastapiApiClient } from '@/lib/axios';
import LoadingDots from './components/LoadingDots.vue'

const aiBoxRef = ref(null)
const showSaveModal = ref(false)

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
  verdictResult.value = null
  isLoading.value = true

  try {
    const { data } = await fastapiApiClient.post('/cases/structuring', {
      freeText: text,
    })

    if (data.success) {
      aiResponse.value = data.data.case // aiResponse에는 case 객체가 할당됩니다.
    } else {
      console.error('API 응답 오류:', data.error.message)
      alert(data.error.message)
    }
  } catch (error) {
    console.error('AI 응답 실패:', error)
  } finally {
    isLoading.value = false
  }
}

const handleOpenSaveModal = () => {
  showSaveModal.value = true;
}

// ❗️ handleConfirmSave 함수는 이제 모달을 닫는 로직도 포함합니다.
const handleConfirmSave = () => {
  if (aiBoxRef.value) {
    aiBoxRef.value.saveConsultationRecord();
  }
  showSaveModal.value = false; // 저장 후 모달 닫기
}

const handlePredictVerdict = async () => {
  // const token = localStorage.getItem('access_token') // 또는 적절한 로그인 상태 체크 방식
  // if (!token) {
  //   alert('로그인이 필요합니다. 로그인 페이지로 이동합니다.')
  //   router.push('/login') // 실제 로그인 경로에 맞게 수정
  //   return
  // }

  if (!aiResponse.value) {
    alert('먼저 사건 내용을 입력하고 분석을 받아야 합니다.')
    return
  }

  isFindingVerdict.value = true
  try {
    const { data } = await fastapiApiClient.post('/analysis', {
      case: aiResponse.value // 첫 번째 API의 결과를 요청 본문에 담아 보냄
    })

    if (data.success) {
      // API 응답에 맞춰 state 업데이트
      verdictResult.value = data.data.report
      lawyers.value = data.data.report.recommendedLawyers
      canShowRecommendBtn.value = true
    } else {
      console.error('판례 분석 API 오류:', data.error.message)
      alert(data.error.message)
    }

  } catch (err) {
    console.error('판례 분석 실패:', err)
    alert('판례를 분석하는 중 오류가 발생했습니다.')
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
*{
  font-family: 'Noto Sans KR', sans-serif;
}
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
  padding: 100px 16px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh; /* 화면 전체 가운데 정렬을 위한 높이 */
}
.wrapper {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  gap: 50px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding-top: 40px;
}
.loading-dots-wrapper {
  position: absolute;
  /* 상단에서부터의 위치. 필요시 px 값을 조정하세요. */
  top: 150px;
  /* 수평 중앙 정렬 */
  left: 50%;
  transform: translateX(-50%);
  z-index: 10; /* 다른 요소들 위에 오도록 설정 */
}
/* 화면이 768px보다 좁아질 때 세로로 배치되도록 수정합니다. */
@media (max-width: 768px) {
  .wrapper {
    flex-direction: column;
    align-items: center;
  }
}
.recommend-button-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 100px;
}

.recommend-button {
  background-color: #F7FCFF;
  color: #82A0B3;
  font-weight: 500;
  border: 1.8px solid #e4ebf0;
  border-radius: 12px;
  padding: 10px 20px;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease-in-out;
  box-shadow: 0px 2px 4px rgba(77, 130, 200, 0.081);
}

.recommend-button:hover {
  background-color: #f3f9fd;
  cursor: pointer;
}

.arrow {
  font-size: 1.1rem;
  font-weight: bold;
}

</style>
