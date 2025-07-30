<template>
  <form @submit.prevent="submit" class="consult-form">
    <!-- 사건 제목 -->
    <div class="form-group">
      <div class="label-row">
        <label for="title">사건 제목</label>
        <div class="fetch-wrapper">
          <button type="button" @click="showModal = true" class="fetch-btn">불러오기</button>
          <div class="tooltip-container">
            <InformationCircleIcon class="info-icon" />
            <div class="tooltip-text">
              AI상담을 기반으로 작성된<br />사건 경위서를 불러오실 수 있습니다.
            </div>
          </div>
        </div>
      </div>
      <input
        id="title"
        v-model="form.title"
        type="text"
        placeholder="사건 제목을 입력해주세요"
        required
      />
    </div>

    <!-- 사건 개요 -->
     <div class="form-group">
       <label for="content">사건 개요</label>
       <textarea
         id="content"
         v-model="form.content"
         placeholder="사건 개요를 입력해주세요"
         required
       />
     </div>

    <!-- 원하는 결과 -->
    <div class="form-group">
      <label for="outcome">원하는 결과</label>
      <textarea
        id="outcome"
        v-model="form.outcome"
        placeholder="원하시는 결과를 적어주세요"
      />
    </div>

    <!-- 불리한 점 -->
    <div class="form-group">
      <label for="disadvantage">사건에서 불리한 점</label>
      <textarea
        id="disadvantage"
        v-model="form.disadvantage"
        placeholder="불리한 점을 적어주세요"
      />
    </div>

    <!-- 변호사에게 궁금한 점 -->
    <div class="form-group">
      <label for="questions">변호사에게 궁금한 점 (쉼표로 구분)</label>
      <textarea
        id="questions"
        v-model="questionsInput"
        placeholder="예: 무죄 가능할까요?, 운전자 바꿔치기 괜찮을까요?"
      />
    </div>

    <!-- 제출 버튼 -->
    <button type="submit">AI 상담서 작성하기</button>
  </form>
  <IncidentSelect v-if="showModal" @select="handleSelect" @close="showModal = false" />
</template>

<script setup>
import { ref } from 'vue'
import IncidentSelect from './IncidentSelect.vue'
import { InformationCircleIcon } from '@heroicons/vue/24/outline'

const emit = defineEmits(['submitted'])
const showModal = ref(false)

const form = ref({
  title: '',
  content: '',
  outcome: '',
  disadvantage: '',
  recommendedQuestions: [],
})

const questionsInput = ref('') // 쉼표로 입력받기

const submit = () => {
  // 쉼표 기준으로 분리
  form.value.recommendedQuestions = questionsInput.value
    .split(',')
    .map(q => q.trim())
    .filter(q => q.length > 0)

  emit('submitted', form.value)
}
const handleSelect = (data) => {
  form.value.title = data.title
  form.value.content = data.content
}
</script>

<style scoped>
.consult-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  border: 1px solid #cfdfe9;
  border-radius: 12px;
  padding: 2rem;
  background-color: #fff;
  max-width: 800px;
  margin: 2rem auto;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
input, textarea {
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 1rem;
  resize: vertical;
}
button {
  background: #072D45;
  color: white;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 20px;
}
button:hover {
  background: #032133;
}
input::placeholder,
textarea::placeholder {
  color: #a0aec0;
  opacity: 1;
}
.fetch-btn {
  font-size: 0.9rem;
  background: none;
  border: none;
  color: #a0aec0;
  cursor: pointer;
  padding: 0;
  margin-top: 0px;
}
.fetch-btn:hover {
  background: none;
}
.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fetch-wrapper {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  line-height: 1.1;
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
  opacity: 50%;
}

.tooltip-container:hover .tooltip-text {
  display: block;
}


</style>
