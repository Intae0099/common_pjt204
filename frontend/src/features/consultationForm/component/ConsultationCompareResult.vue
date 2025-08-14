<template>
  <div class="compare-container">
    <!-- 왼쪽: 사용자 입력 폼 -->
    <!-- <div class="left-box">
      <ConsultationForm
        :form="localUserData"
        :questions-input="questionsInput"
        @submitted="handleSubmit"
        :hide-submit-button="true"
      />
      <div class="left-button"> -->
        <!-- <button class="refresh-btn" @click="emit('regenerate')">AI로 정보 수정하기</button> -->
        <!-- <button class="refresh-btn" @click="handleRegenerate">AI로 정보 수정하기</button>
      </div>
    </div> -->

    <div class="right-box">
      <div class="character-wrapper">
        <img src="@/assets/ai-writing2.png" alt="AI 캐릭터" class="character-image" />
      </div>
      <!-- 오른쪽: AI 결과 -->
      <div class="ai-result-box">
        <form class="ai-form">
          <div class="form-group">
            <label>사건 제목</label>
            <p>{{ aiData.title }}</p>
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
            <label>변호사에게 궁금한점</label>
            <p class="scrollable-content">{{ aiData.disadvantage }}</p>
          </div>
          <div class="form-group scrollable-group">
            <label style="display: flex; align-items: center; gap: 0.3rem;">
              AI 추천 질문
              <div class="tooltip-container">
                <InformationCircleIcon class="info-icon" />
                <div class="tooltip-text">
                  AI상담을 기반으로 작성된<br />사건 경위서를 불러오실 수 있습니다.
                </div>
              </div>
            </label>
            <ul class="scrollable-content">
              <li v-for="(q, idx) in aiData.recommendedQuestions" :key="idx">{{ q }}</li>
            </ul>
          </div>
          <div>
            <button type="button" @click="emit('regenerate', aiData)">AI로 다시 수정하기</button>
          </div>
        </form>
      </div>
      <div class="right-buttons">
        <button class="copy-btn" @click="emit('back')">신청서 다시 작성하기</button>
        <button class="submit-btn" @click="emit('submit')">상담신청서 저장하기</button>
      </div>
    </div>
  </div>

</template>

<script setup>
import { ref } from 'vue'

import ConsultationForm from './ConsultationForm.vue'
import { InformationCircleIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  userData: Object,
  aiData: Object
})

const localUserData = ref({ ...props.userData })
const emit = defineEmits(['submit', 'back', 'regenerate'])
const questionsInput = ref(props.userData.recommendedQuestions?.join(', ') || '')

const handleRegenerate = () => {
  // 1. ConsultationForm의 submit 로직과 동일하게 questionsInput을 배열로 변환합니다.
  localUserData.value.recommendedQuestions = questionsInput.value
    .split(',')
    .map(q => q.trim())
    .filter(q => q.length > 0)

  // 2. 가공된 최신 데이터를 담아 'regenerate' 이벤트를 발생시킵니다.
  emit('regenerate', localUserData.value)
}

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
/*
const handleSubmit = async (formData) => {
  const applicationId = route.params.id

  try {
    await axios.patch(`api/applications/${applicationId}`, {
      ...formData,
    })
    alert('상담서가 저장되었습니다!')
    router.push('/success')
  } catch (err) {
    console.error(err)
    alert('저장 실패')
  }
}
*/

</script>

<style scoped>
.compare-container {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}
.left-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.left-button {
  margin-top: 1rem;
  width: 100%;
  max-width: 900px;
  display: flex;
  justify-content: center;
}
.right-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.right-buttons {
  margin-top: 1rem;
  width: 100%;
  max-width: 900px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.ai-result-box {
  flex: 1;
  width: 100%;
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
  color: #82A0B3;
}

.form-group ul {
  list-style: none;
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
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
  resize: none;
}

.refresh-btn {
  background-color: #fff;
  color: #82A0B3;
  width: 80%;
  border: 1px solid #B9D0DF;
  border-radius: 8px;
  padding: 0.5rem;
}
.refresh-btn:hover {
  background-color: #f4f9fc;
}

.copy-btn,
.submit-btn {
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  border: none;
}

.copy-btn {
  font-size: 0.8rem;
  background-color: #fff;
  color: #B9D0DF;
}
.copy-btn:hover {
  color: #82A0B3;
}

.submit-btn {
  background: #072D45;
  color: white;
  padding: 0.5rem 1.2rem;
}

.character-wrapper {
  position: relative;
  width: 100%;
  max-width: 900px;
  height: 0;
}

.character-image {
  position: absolute;
  top: -70px;
  right: -10px;
  width: 120px;
  z-index: 10;
}

.tooltip-container {
  position: relative;
  display: inline-block;
}

.info-icon {
  width: 20px;
  height: 20px;
  color: #a0aec0;
  cursor: pointer;
}

.tooltip-text {
  display: none;
  position: absolute;
  top: 130%;
  left: 50%;
  transform: translateX(-50%);
  background-color: #fff;
  color: #072D45;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  white-space: nowrap;
  font-size: 0.85rem;
  z-index: 10;
  line-height: 1.4;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
  opacity: 0.9;
}

.tooltip-container:hover .tooltip-text {
  display: block;
}


</style>
