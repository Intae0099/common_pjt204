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
  response: Object,
})

defineEmits(['open-modal'])
</script>

<style scoped>

</style>
