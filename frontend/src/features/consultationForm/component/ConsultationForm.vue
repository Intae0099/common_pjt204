<template>
  <!-- 폼과 버튼 전체를 감싸는 래퍼 (temp.vue의 구조) -->
  <div class="consult-page-wrapper">
    <form @submit.prevent="submit" class="consult-form">
      <!-- 사건 제목 (form.vue의 '불러오기' 기능 추가) -->
      <div class="form-group">
        <div class="label-row">
          <label for="title">사건 제목</label>
          <div class="fetch-wrapper">
            <!-- <button type="button" @click="showModal = true" class="fetch-btn">불러오기</button> -->
            <!-- <div class="tooltip-container">
              <InformationCircleIcon class="info-icon" />
              <div class="tooltip-text">
                AI상담을 기반으로 작성된<br />사건 경위서를 불러오실 수 있습니다.
              </div>
            </div> -->
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
        <label for="summary">사건개요</label>
        <textarea
          id="summary"
          v-model="form.summary"
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

      <!-- 사건에서 불리한 점 -->
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

      <!-- AI 생성 추천 질문 (초기에는 비활성화 상태로 표시) -->
      <div class="form-group">
         <!-- 새로운 클래스 ai-label-row를 추가하고, 아이콘을 레이블 앞으로 이동 -->
         <div class="label-row ai-label-row">
          <label for="ai-questions">AI 생성 추천 질문</label>
            <div class="tooltip-container">
              <InformationCircleIcon class="info-icon" />
              <!-- 아이콘에 대한 툴팁 텍스트도 추가해주는 것이 좋습니다. -->
              <div class="tooltip-text">
                입력하신 내용을 바탕으로<br/>AI가 변호사에게 할 만한<br/>질문을 추천해 드립니다.
              </div>
            </div>
         </div>
         <textarea
            id="ai-questions"
            placeholder="사건 내용을 작성하고 'AI 상담서 작성하기'를 누르면 AI가 추천 질문을 생성합니다."
            readonly
            class="ai-placeholder"
         />
      </div>

      <!-- 'AI 상담서 작성하기' 버튼은 하단으로 이동 -->
    </form>

    <!-- 버튼 컨테이너 (temp.vue의 구조) -->
    <div v-if="!props.hideSubmitButton" class="button-container">
      <button type="button" @click="resetForm" class="btn-secondary">신청서 다시 작성하기</button>
      <button type="button" @click="submit" class="btn-primary">AI 상담서 작성하기</button>
    </div>
  </div>

  <!-- 불러오기 모달 -->
  <IncidentSelect v-if="showModal" @select="handleSelect" @close="showModal = false" />
</template>

<script setup>
import { ref, watch } from 'vue'
import IncidentSelect from './IncidentSelect.vue' // 경로는 실제 위치에 맞게 조정해주세요.
import { InformationCircleIcon } from '@heroicons/vue/24/outline'

// 부모 컴포넌트로 이벤트를 보내기 위한 설정
const emit = defineEmits(['submitted', 'application-selected', 'reset'])

// 부모로부터 받는 props 정의
const props = defineProps({
  form: Object,
  questionsInput: String,
  hideSubmitButton: {
    type: Boolean,
    default: false
  }
})

// ★★★ 핵심: 초기 폼 상태를 정의합니다.
const getInitialFormState = () => ({
  title: '',
  summary: '',
  outcome: '',
  disadvantage: '',
  recommendedQuestions: [],
});

const showModal = ref(false) // '불러오기' 모달 표시 여부
const form = ref(props.form ? { ...props.form } : getInitialFormState())
const questionsInput = ref(props.questionsInput || '')

// props.form이 변경될 때 내부 form 데이터를 동기화
watch(() => props.form, (newForm) => {
  form.value = { ...newForm }
}, { deep: true })

// props.questionsInput이 변경될 때 내부 questionsInput 데이터를 동기화
watch(() => props.questionsInput, (newQuestions) => {
  questionsInput.value = newQuestions
})

// 'AI 상담서 작성하기' 버튼 클릭 시 실행될 함수
const submit = () => {
  // 사용자가 입력한 질문을 쉼표로 구분하여 배열로 변환
  form.value.recommendedQuestions = questionsInput.value
    .split(',')
    .map(q => q.trim())
    .filter(q => q.length > 0)

  // 부모 컴포넌트(ConsultationFormView)에 'submitted' 이벤트와 함께 폼 데이터를 전달
  emit('submitted', form.value)
}

// '신청서 다시 작성하기' 버튼 클릭 시 실행될 함수 (★★★ 수정된 부분)
const resetForm = () => {
  // 1. 컴포넌트 내부의 form 데이터를 직접 초기화합니다.
  form.value = getInitialFormState();
  questionsInput.value = '';

  // 2. 부모에게도 reset 이벤트를 보내 상태를 동기화할 기회를 줍니다.
  console.log('Form has been reset.');
  emit('reset');
}

// '불러오기' 모달에서 사건을 선택했을 때 실행될 함수
const handleSelect = (data) => {
  form.value.title = data.title;
  form.value.summary = data.summary; // API 응답에 맞게 필드명 조정
  
  // 부모에게 선택된 사건의 ID를 전달
  emit('application-selected', data.applicationId);
  showModal.value = false;
}

</script>

<style scoped>
/* ConsultationFormtemp.vue의 스타일과 form.vue의 스타일을 결합 */

/* 전체 페이지 래퍼 */
.consult-page-wrapper {
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem; /* 폼과 버튼 사이 간격 */
}

.consult-form {
  color: #333333;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 2.5rem;
  background-color: #fafdff;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-group > label {
    font-weight: 600;
    font-size: 1.1rem;
}

input, textarea {
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  background-color: #fff;
  font-family: 'Noto Sans KR', sans-serif;
}

textarea {
  min-height: 120px;
  resize: vertical; /* 세로 크기 조절 허용 */
  line-height: 1.6;
}

input::placeholder,
textarea::placeholder {
  color: #888;
  opacity: 1;
}

/* AI 추천 질문 readonly 스타일 */
.ai-placeholder {
    background-color: #f5f5f5;
    color: #777;
}


/* === '불러오기' 관련 스타일 (form.vue에서 가져옴) === */
.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fetch-wrapper {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.ai-label-row {
  justify-content: flex-start; /* 왼쪽부터 정렬하도록 변경 */
  gap: 0.5rem; /* 아이콘과 텍스트 사이의 간격 추가 */
}


.fetch-btn {
  font-size: 0.9rem;
  background: none;
  border: none;
  color: #555;
  cursor: pointer;
  padding: 0;
  font-weight: 500;
}
.fetch-btn:hover {
  color: #072d45;
  text-decoration: underline;
}

.tooltip-container {
  position: relative;
  display: flex;
  align-items: center;
}

.info-icon {
  width: 20px;
  height: 20px;
  color: #aaa;
  cursor: pointer;
}

.tooltip-text {
  display: none;
  position: absolute;
  top: 130%;
  right: 0;
  transform: translateX(0);
  background-color: #333;
  color: #fff;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  white-space: nowrap;
  font-size: 0.85rem;
  z-index: 10;
  line-height: 1.4;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  text-align: center;
}

.tooltip-container:hover .tooltip-text {
  display: block;
}


/* === 버튼 컨테이너 및 버튼 스타일 (temp.vue에서 가져옴) === */
.button-container {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.button-container button {
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  border: 1px solid transparent;
  transition: background-color 0.2s;
}

.btn-secondary {
  background-color: #fff;
  color: #333;
  border-color: #ccc;
}
.btn-secondary:hover {
  background-color: #f5f5f5;
}

.btn-primary {
  background-color: #072d45;
  color: white;
  border: none;
}
.btn-primary:hover {
  background-color: #1d4a68;
}
</style>