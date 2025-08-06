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
        @application-selected="(id) => applicationId.value = id"
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
import { useRouter, useRoute } from 'vue-router'
import axios from '@/lib/axios'

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
const route = useRoute()
const router = useRouter()

onMounted(() => {
  setTimeout(() => {
    isLoading.value = false

    // 로그인 필요한 상태인지 query 확인 후 alert
    if (route.query.needLogin === 'true') {
      alert('로그인이 필요한 페이지입니다.')
      router.replace('/login')  // 히스토리에 남기지 않음
    }
  }, 1000)  // 1초 로딩 후 처리
})

const handleFormSubmit = async (formData) => {
  isLoading.value = true
  userInput.value = formData

  try {
    const res = await axios.post('api/consult/application', {
      case: {
        title: formData.title,
        summary: formData.summary,
        fullText: formData.content,
      },
      desiredOutcome: formData.outcome,
      weakPoints: formData.disadvantage,
    })

    const app = res.data.data.application
    aiResult.value = {
      title: app.data.case.title,
      summary: app.data.case.summary,
      fullText: app.data.case.fullText,
      outcome: app.desiredOutcome,
      disadvantage: app.weakPoints,
      recommendedQuestions: JSON.parse(res.data.data.questions),
      tags: res.data.data.tags, // 실제 저장용에 사용
    }

    showCompareView.value = true
  } catch (err) {
    console.error('AI 상담서 생성 실패:', err)
  } finally {
    isLoading.value = false
  }
}

const handleFinalSubmit = async (formData) => {
  const hasPreviousApplication = applicationId.value !== null

  try {
    if (hasPreviousApplication) {
      await axios.patch(`api/applications/${applicationId.value}`, {
        ...formData,
        recommendedQuestion: {
          question1: formData.recommendedQuestions[0] || '',
          question2: formData.recommendedQuestions[1] || '',
        },
        tags: aiResult.value.tags,
      })
    } else {
      const res = await axios.post('api/applications?isCompleted=true', {
        title: formData.title,
        summary: formData.summary,
        content: formData.content,
        outcome: formData.outcome,
        disadvantage: formData.disadvantage,
        recommendedQuestion: {
          question1: formData.recommendedQuestions[0] || '',
          question2: formData.recommendedQuestions[1] || '',
        },
        tags: aiResult.value.tags,
      })
      applicationId.value = res.data.applicationId
    }

    showSaveModal.value = true
  } catch (err) {
    console.error('상담서 저장 실패:', err)
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
