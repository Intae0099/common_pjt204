<template>
  <div class="verdict-finding-box">
    <p class="loading-text">AI가 실제 판례를 찾고 있습니다...</p>
    <div class="typing-indicator">
      <span></span><span></span><span></span>
    </div>
  </div>
</template>

<script setup>
// props나 emits 필요 없음
</script>

<style scoped>
.verdict-finding-box {
  width: 500px;
  min-height: 200px;
  margin-top: 24px;
  border-radius: 16px;
  padding: 24px;
  background-color: #f4f7ff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-text {
  font-size: 16px;
  color: #5a45ff;
  font-weight: bold;
  margin-bottom: 16px;
}

.typing-indicator {
  display: flex;
  gap: 6px;
  justify-content: center;
}

.typing-indicator span {
  width: 10px;
  height: 10px;
  background-color: #5a45ff;
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
</style>
