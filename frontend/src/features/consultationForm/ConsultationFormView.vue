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
        @application-selected="handleApplicationSelect"
      />

      <ConsultationCompareResult
        v-else
        :userData="userInput"
        :aiData="aiResult"
        @submit="handleFinalSubmit"
        @back="showCompareView = false"
        @regenerate="handleFormSubmit"
      />
    </LayoutDefault>
  </ConsultationFomLayout>
  <SaveAlertModal v-if="showSaveModal" @close="showSaveModal = false" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios, { fastapiApiClient }  from '@/lib/axios'

import LayoutDefault from '@/components/layout/LayoutDefault.vue'
import ConsultationFomLayout from '@/components/layout/ConsultationFomLayout.vue'
import ConsultationForm from './component/ConsultationForm.vue'
import ConsultationCompareResult from './component/ConsultationCompareResult.vue'
import SaveAlertModal from './component/SaveAlertModal.vue'
import { TAG_MAP } from '@/constants/lawyerTags'

const isLoading = ref(true)
const showCompareView = ref(false)
const userInput = ref(null)
const aiResult = ref(null)
const applicationId = ref(null)
const showSaveModal = ref()
const route = useRoute()
const router = useRouter()

onMounted(() => {
  window.scrollTo(0, 0);
  setTimeout(() => {
    isLoading.value = false

    // 로그인 필요한 상태인지 query 확인 후 alert
    if (route.query.needLogin === 'true') {
      alert('로그인이 필요한 페이지입니다.')
      router.replace('/login')  // 히스토리에 남기지 않음
    }
  }, 1000)  // 1초 로딩 후 처리
})

const handleApplicationSelect = (id) => {
  applicationId.value = id;
};

const handleFormSubmit = async (formData) => {
  isLoading.value = true
  window.scrollTo(0, 0);
  if (formData.recommendedQuestions) {
    userInput.value = {
      ...userInput.value, // 기존 사용자 입력(불러오기 ID 등) 유지
      ...formData, // AI 수정 화면에서 넘어온 데이터(제목, 개요, 질문 등)
    };
  } else {
    // 처음 'AI 상담서 작성하기'를 눌렀을 때의 로직은 그대로 유지
    userInput.value = formData;
  }

  try {
    const contentForApi = formData.content || formData.fullText;
    const summaryForApi = formData.summary || contentForApi;
    const res = await fastapiApiClient.post('/consult', {
      case: {
        title: formData.title,
        summary: summaryForApi,
        fullText: contentForApi,
      },
      desiredOutcome: formData.outcome,
      weakPoints: formData.disadvantage,
    })

     if (res.data.success) {
      const responseData = res.data.data;
      const applicationData = responseData.application;

      aiResult.value = {
        title: applicationData.case.title,
        summary: applicationData.case.summary,
        fullText: applicationData.case.fullText,
        outcome: applicationData.desiredOutcome,
        disadvantage: applicationData.weakPoints,
        recommendedQuestions: responseData.questions,
        tags: responseData.tags,
      }
      showCompareView.value = true
    } else {
      // API 응답이 success: false 일 경우 에러 처리
      throw new Error(res.data.error.message || 'AI 상담서 생성에 실패했습니다.')
    }

    showCompareView.value = true
  } catch (err) {
    console.error('AI 상담서 생성 실패:', err)
    alert(err.message || 'AI 상담서 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.')
  } finally {
    isLoading.value = false
  }
}
const handleFinalSubmit = async (finalQuestions) => {
  window.scrollTo(0, 0);
  const tagNamesFromAI = aiResult.value.tags || [];

  // ★★★ 핵심 변환 로직 ★★★
  const tagIds = tagNamesFromAI
    .map(tagName => {
      // 각 태그 이름(tagName)에 해당하는 객체를 TAG_MAP에서 찾습니다.
      return TAG_MAP.find(tagObject => tagObject.name === tagName);
    })
    .filter(foundTag => foundTag) // TAG_MAP에 없어서 못 찾은 경우(undefined)를 배열에서 제거합니다.
    .map(foundTag => foundTag.id); // 찾아낸 객체에서 id 값만 추출하여 새로운 배열을 만듭니다.
                                    // 결과: [7, 9]
  // 서버로 보낼 데이터를 payload 변수로 먼저 만듭니다.

  const summaryForPayload = aiResult.value.summary || aiResult.value.fullText.substring(0, 100);

   const payload = {
    title: aiResult.value.title,
    summary: summaryForPayload,
    content: aiResult.value.fullText, // Spring Boot에서 content를 받으므로 aiResult의 fullText를 매핑
    outcome: aiResult.value.outcome,
    disadvantage: aiResult.value.disadvantage,
    recommendedQuestion: {
      question1: finalQuestions[0] || '',
      question2: finalQuestions[1] || '',
      question3: finalQuestions[2] || '',
    },
    tags: tagIds,
  };

  try {
    if (applicationId.value) {
      // ID가 있으면 기존 상담서를 수정(PATCH)합니다.
      await axios.patch(`api/applications/${applicationId.value}?isCompleted=true`, payload);
    } else {
      // ID가 없으면 새로운 상담서를 생성(POST)합니다.
      const res = await axios.post('api/applications?isCompleted=true', payload);
      // 새로 생성된 ID를 저장하여 다음 저장 시에는 PATCH를 사용하도록 합니다.
      applicationId.value = res.data.applicationId;
    }

    showSaveModal.value = true;
  } catch (err) {
    console.error('상담서 저장 실패:', err);
    console.error('Error response:', err.response?.data); // 서버 응답을 자세히 로깅
    const serverErrorMessage = err.response?.data?.message || err.response?.data?.error || '저장에 실패했습니다.';
    alert(serverErrorMessage);
  }
};
/*
const handleFinalSubmit = async (formData) => {
  const hasPreviousApplication = applicationId.value !== null

  try {
    if (hasPreviousApplication) {
      await axios.post(`api/applications`, {
        title: formData.title,
        summary: formData.summary,
        content: formData.content, // Spring Boot는 content를 받습니다.
        outcome: formData.outcome,
        disadvantage: formData.disadvantage,
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
*/
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
  color: #333333;
}

.subtitle {
  font-size: 1rem;
  color: #888;
  line-height: 1.6;
}
.form-divider {
  border: none;
  border-top: 1px solid #cfcfcf;
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
