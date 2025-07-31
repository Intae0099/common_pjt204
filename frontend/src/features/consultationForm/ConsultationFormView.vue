<template>
  <ConsultationFomLayout>
    <LayoutDefault>

      <section class="page-description">
        <h2 class="title">AI 상담 신청서</h2>
        <p class="subtitle">
          상담을 준비하면서 겪은 상황, 원하는 결과, 궁금한 점 등을 자유롭게 작성해 주세요.<br>
          AI가 내용을 정리해 변호사에게 전달할 상담서를 자동으로 생성해 드립니다.
        </p>
      </section>
      <hr class="form-divider" />
      <div v-if="isLoading" class="loading-area">
        <p>Loading...</p>
        <img src="@/assets/ai-writing.png" alt="AI writing" />
      </div>

      <ConsultationForm
        v-else-if="!showCompareView"
        @submitted="handleFormSubmit"
      />

      <ConsultationCompareResult
        v-else
        :userData="userInput"
        :aiData="aiResult"
        @submit="handleFinalSubmit"
        @back="() => (showCompareView.value = false)"
        @regenerate="handleFormSubmit(userInput.value)"
      />
    </LayoutDefault>
  </ConsultationFomLayout>
  <SaveAlertModal v-if="showSaveModal" @close="showSaveModal = false" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

import LayoutDefault from '@/components/layout/LayoutDefault.vue'
import ConsultationFomLayout from '@/components/layout/ConsultationFomLayout.vue'
import ConsultationForm from './component/ConsultationForm.vue'
import ConsultationCompareResult from './component/ConsultationCompareResult.vue'
import SaveAlertModal from './component/SaveAlertModal.vue'

const isLoading = ref(true)
const showCompareView = ref(false)
const userInput = ref(null)
const aiResult = ref(null)
const applicationId = ref(null)
const showSaveModal = ref()

onMounted(() => {
  setTimeout(() => {
    isLoading.value = false
  }, 1000)
})

const handleFormSubmit = async (formData) => {
  isLoading.value = true
  userInput.value = formData

  try {
    // 1단계: application 먼저 생성
    const createRes = await axios.post('https://i13b204.p.ssafy.io/swagger-ui.html/api/applications', {
      title: formData.title,
      summary: formData.summary,
      content: formData.content,
      outcome: null,
      disadvantage: null,
    })
    applicationId.value = createRes.data.applicationId

    // 2단계: outcome + disadvantage 채워서 AI 요청 포함 PATCH
    const patchRes = await axios.patch(`https://i13b204.p.ssafy.io/swagger-ui.html/api/applications/${applicationId.value}`, {
      outcome: formData.outcome,
      disadvantage: formData.disadvantage,
    })

    aiResult.value = {
      fullText: patchRes.data.application.case.fullText,
      recommendedQuestions: JSON.parse(patchRes.data.questions),
    }

    showCompareView.value = true
  } catch (err) {
    console.error('AI 상담서 생성 실패:', err)
  } finally {
    isLoading.value = false
  }
}
const handleFinalSubmit = async (formData) => {
  try {
    await axios.patch(`https://i13b204.p.ssafy.io/swagger-ui.html/api/applications/${applicationId.value}`, {
      ...formData,
    })
    showSaveModal.value = true
  } catch (err) {
    console.error('저장 실패:', err)
    alert('저장에 실패했습니다.')
  }
}
</script>

<style scoped>
*{
  font-family: 'Noto Sans KR', sans-serif;
}
.page-description {
  max-width: 800px;
  margin: 2rem auto 3rem;
  text-align: center;
}

.title {
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 1rem;
  color: #072D45;
}

.subtitle {
  font-size: 1rem;
  color: #82A0B3;
  line-height: 1.6;
}
.form-divider {
  border: none;
  border-top: 1px solid #cfdfe9;
  max-width: 800px;
  margin: 2rem auto;
}
.loading-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 20vh;
  text-align: center;
}

.loading-area p {
  font-size: 1.2rem;
  color: #072D45;
  margin-bottom: 1rem;
}

.loading-area img {
  width: 120px;
  height: auto;
}

</style>
