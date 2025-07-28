<template>
  <div class="chat-input-box">
    <!-- 프로필 이미지 -->
    <img class="avatar" :src="userAvatarUrl" alt="user" />

    <!-- 입력창 -->
    <textarea
      v-model="text"
      class="textarea"
      :placeholder="placeholder"
      :disabled="disabled"
      @keydown.enter.prevent="submit"
    />

    <!-- 제출 버튼 (아이콘 대체 가능) -->
    <button @click="submit" :disabled="!text.trim() || disabled">
      ⬇️
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const { placeholder, disabled, userAvatarUrl } = defineProps({
  placeholder: {
    type: String,
    default: '질문을 입력해주세요...'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  userAvatarUrl: {
    type: String,
    default: 'test.png' // 👉 사용자 이미지 URL (ex: 로그인된 유저 프로필)
  }
})

const emit = defineEmits(['submit'])

const text = ref('')

const submit = () => {
  if (text.value.trim()) {
    emit('submit', text.value.trim())
    text.value = ''
  }
}
</script>

<style scoped>
.chat-input-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.avatar {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 50%;
  margin-bottom: 12px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.input-wrapper {
  position: relative;
  width: 100%;
  max-width: 500px;
}

.textarea {
  width: 100%;
  min-width: 400px;
  min-height: 120px;
  border: 1px solid #e0ecf5;
  border-radius: 12px;
  padding: 16px;
  font-size: 16px;
  resize: none;
  box-shadow: 0 0 6px rgba(0, 132, 255, 0.1);
  outline: none;
  background: white;
}

.textarea:disabled {
  background-color: #f5f5f5;
  color: #aaa;
}

.submit-button {
  position: absolute;
  bottom: 8px;
  right: 12px;
  border: none;
  background: none;
  font-size: 18px;
  cursor: pointer;
  color: #007bff;
}

.submit-button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
</style>
