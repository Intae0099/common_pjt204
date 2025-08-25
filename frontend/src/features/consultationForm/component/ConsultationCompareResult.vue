<template>
  <div class="compare-container">
    <div class="right-box">
      <div class="character-wrapper">
        <img src="@/assets/ai-writing2.png" alt="AI 캐릭터" class="character-image" />
      </div>
      <div class="ai-result-box">
        <form class="ai-form">
          <div class="form-group">
            <label>사건 제목</label>
            <p>{{ aiData.title }}</p>
          </div>
          <div class="form-group scrollable-group">
            <label>사건 개요</label>
            <p class="scrollable-content">{{ aiData.summary }}</p>
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
            <label for="user-questions">변호사에게 궁금한 점 (직접 수정 가능)</label>
            <textarea id="user-questions" v-model="userQuestionsText" class="scrollable-content editable-textarea"
              placeholder="궁금한 점을 자유롭게 수정, 추가하세요."></textarea>
          </div>
          <div class="label-with-button">
            <label style="display: flex; align-items: center; gap: 0.3rem;">
              AI 추천 질문
              <div class="tooltip-container">
                <InformationCircleIcon class="info-icon" />
                <div class="tooltip-text">
                  AI가 추천하는 질문 목록입니다.<br />오른쪽 버튼을 눌러 위 질문 목록에 추가할 수 있습니다.
                </div>
              </div>
            </label>
            <button
                type="button"
                class="text-copy-btn"
                @click="copyAiQuestions"
                :disabled="isAiQuestionsCopied"
              >
                {{ isAiQuestionsCopied ? '추가 완료' : '궁금한 점에 추가하기 ↑' }}
              </button>
          </div>
          <ul class="scrollable-content">
            <li v-for="(q, idx) in aiData.recommendedQuestions" :key="idx">{{ q }}</li>
          </ul>
          <div class="regenerate-area">
            <button
              type="button"
              class="icon-btn"
              :title="isRegenerating ? '업데이트 중…' : 'AI 추천질문 재생성'"
              :disabled="isRegenerating"
              @click="handleRegenerate"
              aria-label="AI 추천질문 재생성"
            >
              <ArrowPathIcon :class="['icon', { spinning: isRegenerating }]" />
            </button>
            <span class="hint" v-if="!isRegenerating">AI 추천질문 재생성</span>
          </div>
        </form>
      </div>
      <div class="right-buttons">
        <button class="copy-btn" @click="emit('back')">신청서 다시 작성하기</button>
        <button class="submit-btn" @click="handleFinalSubmit">상담신청서 저장하기</button>
      </div>
    </div>
  </div>

</template>

<script setup>
import { ref } from 'vue'
import { InformationCircleIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'

const isRegenerating = ref(false)

const props = defineProps({
  userData: Object,
  aiData: Object
})

const emit = defineEmits(['submit', 'back', 'regenerate'])

// ▼▼▼▼▼ [수정 4] '변호사에게 궁금한 점' textarea를 위한 ref 생성 ▼▼▼▼▼
// userData의 질문 배열을 줄바꿈 문자로 합쳐서 초기값으로 설정합니다.
const userQuestionsText = ref(
  props.userData.recommendedQuestions?.join('\n') || ''
);

const isAiQuestionsCopied = ref(false);

// 'AI 추천질문 복사하기' 버튼 클릭 시 실행될 함수
const copyAiQuestions = () => {
  if (isAiQuestionsCopied.value) return;

  if (props.aiData.recommendedQuestions.length === 0) {
    alert('추가할 AI 추천 질문이 없습니다.');
    return;
  }

  const aiQuestionsString = props.aiData.recommendedQuestions.join('\n');

  // 기존 텍스트가 있으면 줄바꿈 후 추가, 없으면 그냥 추가
  if (userQuestionsText.value.trim().length > 0) {
    userQuestionsText.value += '\n' + aiQuestionsString;
  } else {
    userQuestionsText.value = aiQuestionsString;
  }
  isAiQuestionsCopied.value = true;
};

// '상담신청서 저장하기' 버튼 클릭 시 실행될 함수
const handleFinalSubmit = () => {
  // textarea의 내용을 줄바꿈 기준으로 다시 배열로 변환합니다.
  // 비어있는 줄은 제거합니다.
  const finalQuestions = userQuestionsText.value
    .split('\n')
    .map(q => q.trim())
    .filter(q => q.length > 0);

  // 'submit' 이벤트를 발생시키면서 수정된 질문 배열을 부모에게 전달합니다.
  emit('submit', finalQuestions);
};

const handleRegenerate = () => {
  // 1. 현재 '변호사에게 궁금한 점' textarea의 내용을 배열로 변환합니다.
  const currentQuestions = userQuestionsText.value
    .split('\n')
    .map(q => q.trim())
    .filter(q => q.length > 0);

  // 2. 부모에게 전달할 데이터를 만듭니다.
  // AI가 다시 생성해야 할 데이터(aiData)와 사용자가 수정한 질문(currentQuestions)을 함께 보냅니다.
  const payload = {
    ...props.aiData, // 기존 AI 데이터 (제목, 개요 등)
    // fullText가 없는 경우를 대비하여 summary로 대체
    fullText: props.aiData.fullText || props.aiData.summary,
    // 사용자가 수정한 질문 내용을 'recommendedQuestions' 키로 덮어씁니다.
    recommendedQuestions: currentQuestions,
  };

  isAiQuestionsCopied.value = false;

  // 3. 'regenerate' 이벤트를 발생시킵니다.
  isRegenerating.value = true
  emit('regenerate', payload);

  setTimeout(() => { isRegenerating.value = false }, 1200)
};
</script>

<style scoped>
.editable-textarea {
  font-family: 'Noto Sans KR', sans-serif;
  color: #333; /* 수정 가능하므로 사용자 입력처럼 보이게 색상 변경 */
  background-color: #fff;
}
.label-with-button {
  display: flex;
  /* justify-content: space-between; */
  align-items: center;
  gap: 0.5rem;
}
.text-copy-btn {
  background: none;
  border: 1px solid #888;
  color: #888;
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
  border-radius: 6px;
  cursor: pointer;
  text-align: start;
}
.text-copy-btn:hover {
  background-color: #f0f6fa;
}
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
  justify-content: flex-end;
  align-items: center;
  gap: 1rem;
}

.ai-result-box {
  flex: 1;
  width: 100%;
  max-width: 900px;
  border: 1px solid #6c9bcf;
  border-radius: 12px;
  padding: 2rem 1rem;
  background-color: #f4f7fb ;
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
.form-group p {
  color: #333333;
  background-color: #f6f6f6;
  cursor: block;
}
.form-group textarea {
  color: #333333;
}


label {
  font-weight: medium;
  color: #333333;
}

p,
ul {
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
  max-height: 20cqb;
  overflow-y: auto;
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
  resize: none;
  list-style-type: none;
}

.refresh-btn {
  background-color: #fff;
  color: #cfcfcf;
  width: 80%;
  border: 1px solid #cfcfcf;
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
.submit-btn:hover {
  background-color: #6c9bcf;
}

.copy-btn {
  /* font-size: 0.8rem; */
  padding: 0.5rem 1.2rem;
  background-color: #fff;
  color: #1d2b50;
  border: 1px solid #1d2b50;;
}

.copy-btn:hover {
  color: #6c9bcf;
  border-color: #6c9bcf;
}

.regenerate-area {
  display: flex;
  align-items: center;
  gap: .5rem;
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid #6c9bcf;
  background: #fff;
  cursor: pointer;
  transition: background-color .15s ease, border-color .15s ease, transform .05s ease;
}
.icon-btn:hover { background-color: #f4f9fc; border-color: #82A0B3; }
.icon-btn:active { transform: scale(0.98); }
.icon-btn:disabled { opacity: .5; cursor: not-allowed; }

.icon {
  width: 20px;
  height: 20px;
  color: #6c9bcf;
}
.spinning { animation: spin 0.9s linear infinite; }

@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

/* (선택) 보조 텍스트 */
.hint {
  font-size: .85rem;
  color: #6c9bcf;
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
  color: #888;
  /* cursor: pointer; */
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
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  opacity: 0.9;
}

.tooltip-container:hover .tooltip-text {
  display: block;
}
</style>
