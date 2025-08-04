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

        <!-- 🔹 판례 예측 전: 사건 요약만 -->
        <template v-if="!verdictResult && response.summary">
          <!-- 사건 제목 -->
          <h4 style="margin-bottom: 0.8rem;">{{ response.title }}</h4>
          <!-- 한 줄 요약 -->
          <p style="font-weight: 500; white-space: pre-wrap;">{{ response.summary }}</p>
          <hr style="border: none; border-top: 1px solid #dbe6ee; margin: 1rem 0;" />
          <!-- 정리된 본문 -->
          <p style="font-size: 0.9rem; color: #333; white-space: pre-wrap;">{{ response.fullText }}</p>
        </template>

        <!-- 🔸 판례 예측 후: opinion 등 -->
        <template v-else-if="verdictResult">
          <h4>쟁점 및 AI 소견</h4>
          <ul v-if="verdictResult.issues?.length">
            <li v-for="(issue, index) in verdictResult.issues" :key="`issue-${index}`">
              {{ issue }}
            </li>
          </ul>
          <p style="margin-top: 1rem;">{{ verdictResult.opinion }}</p>
          <p><strong>예상 형량:</strong> {{ verdictResult.sentencePrediction }}</p>
          <p><strong>신뢰도:</strong> {{ (verdictResult.confidence * 100).toFixed(0) }}%</p>

          <!-- ✅ 유사 판례 정보 -->
          <div v-if="verdictResult.references?.cases?.length" style="margin-top: 1rem;">
            <h4>📚 유사 판례</h4>
            <ul>
              <li v-for="(caseItem, index) in verdictResult.references.cases" :key="`case-${index}`" style="margin-bottom: 0.5rem;">
                <p><strong>사건명:</strong> {{ caseItem.name }}</p>
                <p><strong>법원:</strong> {{ caseItem.court }}</p>
                <p><strong>년도:</strong> {{ caseItem.year }}</p>
              </li>
            </ul>
          </div>
          <div v-if="verdictResult.references?.statutes?.length" style="margin-top: 1rem;">
            <h4>⚖️ 관련 법령</h4>
            <ul>
              <li v-for="(statute, index) in verdictResult.references.statutes" :key="`statute-${index}`">
                <p>{{ statute.code }} 제{{ statute.article }}</p>
              </li>
            </ul>
          </div>
        </template>

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
  verdictResult: Object,
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
