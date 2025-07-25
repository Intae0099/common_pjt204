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
  }
}
</script>

<style scoped>

</style>
