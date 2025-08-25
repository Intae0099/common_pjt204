<template>
  <div class="layout-background">
    <div class="container">
      <div>
        <div class="wrapper">

          <AiBox
            ref="aiBoxRef"
            :messages="messages"
            :isLoading="isLoading"
            :isFindingVerdict="isFindingVerdict"
            :response="aiResponse"
            :userText="userInput"
            :showPredictButton="!verdictResult"
            :verdictResult="verdictResult"
            @open-modal="handleOpenSaveModal"
            @predict="handlePredictVerdict"
          />

          <ChatInputBox
            :disabled="isInputLocked"
            @submit="handleUserInput"
          />
        </div>

        <BottomActionBar
          v-if="aiResponse && !isFindingVerdict && !verdictResult && !showRecommendList"
          @predict="handlePredictVerdict"
          @quick-consult="showModal = true"
        />

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
          <button class="action-button" @click="showLawyers">
            변호사 추천받기
          </button>
        </div>
        <LawyerRecommendList v-if="showRecommendList" :lawyers="lawyers" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'

import ChatInputBox from './components/ChatInputBox.vue'
import AiBox from './components/AiBox.vue'
import BottomActionBar from './components/BottomActionBar.vue'
import SuggestModal from './components/SuggestModal.vue'
import SaveModal from './components/SaveModal.vue'
import LawyerRecommendList from './components/LawyerRecommendList.vue'
// import axios from 'axios'
import { fastapiApiClient } from '@/lib/axios';
import { TAG_MAP } from '@/constants/lawyerTags'

const aiBoxRef = ref(null)
const showSaveModal = ref(false)

const userInput = ref('')
const aiResponse = ref(null)
const messages = ref([])
const isLoading = ref(false)
const isInputLocked = ref(false)
const showModal = ref(false)
const isFindingVerdict = ref(false)
const verdictResult = ref(null)            // 판례 예측 결과
const canShowRecommendBtn = ref(false)     // 버튼 활성화 조건
const lawyers = ref([])                    // 추천 변호사 목록
const showRecommendList = ref(false)       // 변호사 추천 리스트 보여줄지 여부


const pushAndScroll = async (msg) => {
  messages.value.push(msg)
  await nextTick()
  aiBoxRef.value?.scrollToBottom?.()
}

const handleUserInput = async (text) => {
  userInput.value = text
  aiResponse.value = null
  verdictResult.value = null
  isInputLocked.value = true
  isLoading.value = true

  try {
    const { data } = await fastapiApiClient.post('/cases/structuring', {
      freeText: text,
    })

    if (data.success) {
      aiResponse.value = data.data.case // aiResponse에는 case 객체가 할당됩니다.
      await pushAndScroll({ role: 'assistant', type: 'summary', payload: { case: data.data.case } })
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
  const token = localStorage.getItem('access_token');
  if (!token) {
    return; // 함수 실행 중단
  }
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
  const token = localStorage.getItem('access_token') // 또는 적절한 로그인 상태 체크 방식
  if (!token) {
    alert('로그인이 필요합니다. 로그인 페이지로 이동합니다.')
    router.push('/login') // 실제 로그인 경로에 맞게 수정
    return
  }

  if (!aiResponse.value) {
    alert('먼저 사건 내용을 입력하고 분석을 받아야 합니다.')
    return
  }

  isFindingVerdict.value = true
  try {
    const { data } = await fastapiApiClient.post('/analysis', {
      case: aiResponse.value
    })

    if (data.success) {
      verdictResult.value = data.data.report

      // --- 2. 태그 ID를 이름으로 변환하는 로직 ---
      // 성능 향상을 위해 TAG_MAP을 Map 객체로 변환 (ID로 이름을 바로 찾기 위함)
      const tagIdToNameMap = new Map(TAG_MAP.map(tag => [tag.id, tag.name]));

      // 추천 변호사 목록을 순회하며 태그를 변환
      const processedLawyers = data.data.report.recommendedLawyers.map(lawyer => {
        // 각 변호사의 tags 배열(ID 목록)을 이름 목록으로 변환
        const tagNames = lawyer.tags
          .map(tagId => tagIdToNameMap.get(tagId)) // Map에서 ID에 해당하는 이름을 찾음
          .filter(Boolean); // 혹시 모를 null이나 undefined 값을 제거

        // 기존 변호사 정보에 변환된 태그(이름 배열)를 포함하여 새로운 객체 반환
        return {
          ...lawyer,
          tags: tagNames
        };
      });

      // 변환된 변호사 목록을 state에 저장
      lawyers.value = processedLawyers;
      // --- 로직 종료 ---

      canShowRecommendBtn.value = true
      await pushAndScroll({ role: 'assistant', type: 'verdict', payload: { verdict: data.data.report } })
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
  width: 99vw;
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
  z-index: 0;
}
.container{
  padding: 100px 16px;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh; /* 화면 전체 가운데 정렬을 위한 높이 */
}
.wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 28px;
  max-width: 920px;
  width: 100%;
  margin: 0 auto;
}
.loading-dots-wrapper {
  position: static;         /* ⬅︎ absolute → static */
  margin-top: -6px;        /* ⬅︎ 살짝 붙여줌(취향) */
  display: flex;
  justify-content: center;
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
  margin-top: 50px;
}

.action-button {
  background-color: #0F2C59;
  color: white;
  font-size: 14px;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: medium;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.action-button:hover {
  background-color: #1c3d78;
}

.arrow {
  font-size: 1.1rem;
  font-weight: bold;
}

</style>
