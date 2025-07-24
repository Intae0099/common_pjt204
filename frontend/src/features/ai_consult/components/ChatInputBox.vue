<template>
  <div class="chat-input-box">
    <!-- 프로필 이미지 -->
    <img class="avatar" :src="userAvatarUrl" alt="user" />

    <!-- 입력창 -->
    <textarea
      v-model="text"
      class="input"
      :placeholder="placeholder"
      :disabled="disabled"
      @keydown.enter.prevent="submit"
    />

    <!-- 제출 버튼 (아이콘 대체 가능) -->
    <button class="submit-button" @click="submit" :disabled="!text.trim() || disabled">
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
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 16px;
}

.input {
  width: 100%;
  height: 120px;
  padding: 12px;
  font-size: 14px;
  color: #333;
  border: 2px solid #d9e3ec;
  border-radius: 10px;
  resize: none;
  margin-bottom: 12px;
  font-family: inherit;
}

.submit-button {
  font-size: 24px;
  background: none;
  border: none;
  color: #aaa;
  cursor: pointer;
  transition: 0.2s ease;
}

.submit-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
