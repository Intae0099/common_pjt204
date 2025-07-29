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
    <div v-else-if="response" class="result-box">
      <img class="bot" src="@/assets/ai-bot.png" alt="AI 봇" />
      <div class="ai-message-box">
        <p>{{ response.result }}</p>
        <p v-if="verdictResult" style="margin-top: 8px; color: #072D45;">
        {{ verdictResult }}
        </p>
      </div>
    </div>

    <!-- 아무 입력도 없을 때 -->
    <div v-else class="empty-state">
      <h1>AI 사전 상담</h1>
      <p>질문만 입력하면 상황을 정리해드리고,<br/>
        유사한 판례까지 AI가 찾아드립니다.</p>
      <img class="guide-bot" src="@/assets/ai-consult-bot.png" alt="AI 봇" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  isLoading: Boolean,
  response: Object,
  verdictResult: String,
})

defineEmits(['open-modal'])
</script>

<style scoped>
*{
  font-family: 'Noto Sans KR', sans-serif;
}
.bot{
  width: 70px;
  margin-top: 0.3rem;
}
.result-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.ai-message-box {
  background-color: #eaf2f8;
  color: #072D45;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  width: 100%;
  min-width: 350px;
  min-height: 120px;
  text-align: left;
  font-size: 0.95rem;
  line-height: 1.5;
  margin-top: 0.35rem;
}

.empty-state {
  text-align: center;
}

.empty-state h1 {
  margin-top: 10px;
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
  color: #072D45;
}

.empty-state p {
  font-size: 1rem;
  font-weight: medium;
  color: #82A0B3;
  line-height: 1.5;
}

.guide-bot {
  width: 250px;
  margin-top: 15px;
}

</style>
