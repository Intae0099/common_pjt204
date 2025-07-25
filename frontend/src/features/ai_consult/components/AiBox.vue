<template>
  <div>
    <!-- 작성 중 -->
    <div v-if="isLoading">
      <p>AI가 작성 중입니다...</p>
      <div>
        <span></span><span></span><span></span>
      </div>
    </div>

    <!-- 결과 도착 -->
    <div v-else-if="response">
      <h2>AI 상담 결과</h2>
      <p>{{ response.result }}</p>
    </div>

    <!-- 아무 입력도 없을 때 -->
    <div v-else>
      <p>왼쪽에 질문을 입력해주세요.</p>
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
