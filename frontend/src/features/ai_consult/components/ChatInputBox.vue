<template>
  <div class="chat-input-box">
    <!-- 입력창 -->
    <div class="input-area">
      <textarea
        ref="textareaRef" v-model="text"
        class="textarea"
        :placeholder="placeholder"
        :disabled="disabled"
        @keydown.enter.prevent="submit"
        @input="handleInput"
      ></textarea>


      <!-- 제출 버튼 (아이콘 대체 가능) -->
      <button
        @click="submit"
        :disabled="!text.trim() || disabled"
        class="submit-button"
      >
        <ArrowRightIcon class="arrow-icon"/>
      </button>

    </div>
    <p v-if="showWarning" class="warning-text">
      50자 이상으로 내용을 더 정확하게 입력해 주세요.
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ArrowRightIcon } from '@heroicons/vue/24/solid'
const { placeholder, disabled} = defineProps({
  placeholder: {
    type: String,
    default: '질문을 입력해주세요...'
  },
  disabled: {
    type: Boolean,
    default: false
  },
})

const emit = defineEmits(['submit'])

const text = ref('')
const showWarning = ref(false)
const textareaRef = ref(null)

const handleInput = (e) => {
  const textarea = e.target
  textarea.style.height = 'auto'
  textarea.style.height = `${textarea.scrollHeight}px`
}

const submit = () => {
  if (disabled) return
  const inputLength = text.value.trim().length

  if (inputLength < 50) {
    showWarning.value = true
    return
  }

  showWarning.value = false
  emit('submit', text.value.trim())
  text.value = ''

  if (textareaRef.value) {
    textareaRef.value.style.height = '120px' // 기존 CSS에 설정된 min-height 값
  }
}
</script>

<style scoped>
*{
  font-family: 'Noto Sans KR', sans-serif;
}
.chat-input-box {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  position: relative;
  flex: 1; /* 왼쪽 컬럼의 공간을 차지하도록 flex 속성 추가 */
  max-width: 500px;
  min-width: 350px;
  margin-top: 81px;
}

.input-area {
  position: relative;
  width: 100%;
}

.input-wrapper {
  position: relative;
  width: 100%;
  max-width: 500px;
}

.textarea {
  box-sizing: border-box;
  width: 100%;
  min-height: 120px;
  border: 1px solid #e0ecf5;
  border-radius: 12px;
  padding: 16px 16px 40px 16px;
  font-size: 16px;
  resize: none;
  box-shadow: 0 0 6px rgba(0, 132, 255, 0.1);
  outline: none;
  background: white;
  overflow-y: hidden;
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}
.textarea::placeholder {
  color: #d1dee8;
}
.textarea:disabled {
  background-color: #f5f5f5;
  color: #aaa;
}
/* Webkit 브라우저(크롬, 사파리 등)용 스크롤바 숨기기 */
.textarea::-webkit-scrollbar {
  display: none;
}

.submit-button {
  position: absolute;
  bottom: 12px;
  right: 12px;
  border: none;
  background: none;
  font-size: 18px;
  cursor: pointer;
  color: #C7E5F7;
}

.submit-button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.arrow-icon {
  width: 24px;
  height: 24px;
}

.warning-text {
  color: red;
  font-size: 14px;
  margin-left: 6px;
}
</style>
