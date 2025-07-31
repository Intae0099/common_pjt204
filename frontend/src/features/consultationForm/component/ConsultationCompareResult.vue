<template>
  <div class="compare-container">
    <!-- 왼쪽: 사용자 입력 폼 -->

       <ConsultationForm
         :form="localUserData"
         :questions-input="questionsInput"
         @submitted="handleSubmit"
         :hide-submit-button="true"
       />

    <!-- 오른쪽: AI 결과 -->
    <div class="ai-result-box">
      <form class="ai-form">
        <div class="form-group">
          <label>사건 제목</label>
          <p>{{ aiData.title }}</p>
        </div>
        <div class="form-group">
          <label>사건 한 줄 요약</label>
          <p>{{ aiData.summary }}</p>
        </div>
        <div class="form-group scrollable-group">
          <label>사건 개요</label>
          <p class="scrollable-content">{{ aiData.fullText }}</p>
        </div>
        <div class="form-group scrollable-group">
          <label>원하는 결과</label>
          <p class="scrollable-content">{{ aiData.outcome }}</p>
        </div>
        <div class="form-group scrollable-group">
          <label>사건에서 불리한 점</label>
          <p class="scrollable-content">{{ aiData.disadvantage }}</p>
        </div>
        <div class="form-group scrollable-group">
          <label>AI 추천 질문</label>
          <ul class="scrollable-content">
            <li v-for="(q, idx) in aiData.recommendedQuestions" :key="idx">{{ q }}</li>
          </ul>
        </div>
      </form>
    </div>
  </div>
  <button class="refresh-btn" @click="emit('regenerate')">AI로 정보 수정하기</button>
  <div class="compare-buttons">
    <button class="copy-btn" @click="copyToUserForm">복사해서 수정하기</button>
    <button class="submit-btn" @click="emit('submit')">상담서 저장하기</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import ConsultationForm from './ConsultationForm.vue'

const props = defineProps({
  userData: Object,
  aiData: Object
})
const route = useRoute()
const router = useRouter()
const localUserData = ref({ ...props.userData })

const emit = defineEmits(['submit', 'back'])
const questionsInput = ref(props.userData.recommendedQuestions?.join(', ') || '')

const copyToUserForm = () => {
  if (!confirm('AI 상담서 내용을 사용자 입력 폼에 복사하시겠습니까?')) return

  localUserData.value.title = props.aiData.title
  localUserData.value.summary = props.aiData.summary
  localUserData.value.content = props.aiData.fullText
  localUserData.value.outcome = props.aiData.outcome
  localUserData.value.disadvantage = props.aiData.disadvantage
  localUserData.value.recommendedQuestions = [...props.aiData.recommendedQuestions]
  questionsInput.value = props.aiData.recommendedQuestions.join(', ')
}

const handleSubmit = async (formData) => {
  const applicationId = route.params.id // 또는 props 등에서 ID 받기

  try {
    await axios.patch(`https://i13b204.p.ssafy.io/swagger-ui.html/api/applications/${applicationId}`, {
      ...formData,
    })
    alert('상담서가 저장되었습니다!')
    router.push('/success') // 저장 후 이동
  } catch (err) {
    console.error(err)
    alert('저장 실패')
  }
}

</script>

<style scoped>
.compare-container {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}

.ai-result-box {
  flex: 1;
  max-width: 900px;
  border: 1px solid #B9D0DF;
  border-radius: 12px;
  padding: 2rem 1rem;
  background-color: #F7FCFF;
}

.ai-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: medium;
  color: #000;
}

p, ul {
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
}
.form-group ul {
  list-style: none;
}

/* 각 항목별 스크롤 영역 */
.scrollable-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}


/* 공통 스크롤 스타일 (ex. 최대 높이 150px) */
.scrollable-content {
  min-height: 100px;
  max-height: 150px;
  overflow-y: auto;
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
  resize: none; /* textarea에만 필요 */
}


.compare-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin: 2rem 0;
}
.refresh-btn {
  background-color: #E2E8F0;
  color: #072D45;
}
.refresh-btn:hover {
  background-color: #CBD5E0;
}

.copy-btn,
.submit-btn {
  padding: 0.5rem 1.2rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  border: none;
}

.copy-btn {
  background-color: #072D45;
  color: white;
}
.copy-btn:hover {
  background-color: #032133;
}

.submit-btn {
  background: #072D45;
  color: white;
}
</style>
