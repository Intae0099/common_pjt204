<template>
  <div class="ai-box">
    <!-- 작성 중 -->
    <div v-if="isLoading" class="ai-writing">
      <p class="status-text">AI가 작성 중입니다...</p>
      <div class="typing-indicator">
        <span></span><span></span><span></span>
      </div>
    </div>

    <!-- 결과 도착 -->
    <div v-else-if="response" class="ai-result">
      <h2 class="title">AI 상담 결과</h2>
      <p class="response-text">{{ response.result }}</p>

      <button class="link-button" @click="$emit('open-modal')">
        바로 상담하기
      </button>
    </div>

    <!-- 아무 입력도 없을 때 -->
    <div v-else class="ai-idle">
      <p class="idle-text">왼쪽에 질문을 입력해주세요.</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  isLoading: Boolean,
  response: Object
})

defineEmits(['open-modal'])
</script>

<style scoped>
.ai-box {
  width: 500px;
  min-height: 300px;
  border-radius: 16px;
  padding: 24px;
  background-color: #ffffff;
  box-shadow: 0 0 10px rgba(90, 69, 255, 0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.ai-writing {
  text-align: center;
  color: #999;
}

.typing-indicator {
  display: flex;
  gap: 6px;
  justify-content: center;
  margin-top: 10px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background-color: #aaa;
  border-radius: 50%;
  animation: blink 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}
.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes blink {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.ai-result {
  text-align: center;
}

.title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 12px;
  color: #333;
}

.response-text {
  font-size: 14px;
  color: #444;
  line-height: 1.6;
  margin-bottom: 20px;
  white-space: pre-wrap;
}

.link-button {
  padding: 10px 20px;
  background-color: #5a45ff;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.link-button:hover {
  background-color: #4331e0;
}

.ai-idle {
  text-align: center;
  color: #ccc;
}
</style>
