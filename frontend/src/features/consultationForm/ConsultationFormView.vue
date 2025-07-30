<template>
  <ConsultationFomLayout>
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
      v-else
      @submitted="handleFormSubmit"
    />
  </ConsultationFomLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

import ConsultationFomLayout from '@/components/layout/ConsultationFomLayout.vue'
import ConsultationForm from './component/ConsultationForm.vue'

const isLoading = ref(true)

onMounted(() => {
  setTimeout(() => {
    isLoading.value = false
  }, 1000)
})

const handleFormSubmit = async (formData) => {
  const payload = {
    title: formData.title,
    summary: formData.recommendedQuestions.join(', ') || '', // summary 역할
    content: formData.content,
    outcome: formData.outcome || null,
    disadvantage: formData.disadvantage || null,
  }

  try {
    const res = await axios.post('/api/applications', payload)
    console.log('상담서 생성됨!', res.data.applicationId)
  } catch (err) {
    console.error('에러 발생:', err)
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
