<template>
  <div class="ai-box-wrapper">
    <div v-if="showBot" class="ai-sticky-header">
      <img class="bot" src="@/assets/ai-bot.png" alt="AI 봇" />
    </div>

    <div v-if="messages && messages.length" class="ai-scroll" :class="{ 'with-bot': showBot }" ref="scrollEl">
      <div v-for="(m, idx) in messages" :key="idx" class="result-box">
        <div class="ai-message-box">
          <template v-if="m.type === 'summary'">
            <h4 style="margin-bottom: 1.2rem;">{{ m.payload.case.title }}</h4>
            <hr style=" margin-bottom: 1.5rem;">
            <h6>요약</h6>
            <div class="summary-box">
              <p style="font-weight: 500; white-space: pre-wrap;">{{ m.payload.case.summary }}</p>
            </div>
            <hr style="border: none; border-top: 1px solid #dbe6ee; margin: 1rem 0;" />
          </template>

          <template v-else-if="m.type === 'verdict'">
            <h4>쟁점 및 AI 소견</h4>
            <ul v-if="m.payload.verdict.issues?.length">
              <li v-for="(issue, i) in m.payload.verdict.issues" :key="`issue-${idx}-${i}`">
                {{ issue }}
              </li>
            </ul>
            <p style="margin-top: 1rem;">{{ m.payload.verdict.opinion }}</p>
            <p><strong>예상 형량:</strong> {{ m.payload.verdict.expected_sentence }}</p>
            <p><strong>신뢰도:</strong> {{ (m.payload.verdict.confidence * 100).toFixed(0) }}%</p>

            <div v-if="m.payload.verdict.tags?.length" class="tags-wrapper">
              <span v-for="tag in m.payload.verdict.tags" :key="tag" class="tag">#{{ tag }}</span>
            </div>

            <div v-if="m.payload.verdict.references?.cases?.length" class="precedent-section">
              <h4>유사 판례</h4>
              <div class="case-list">
                <div
                  v-for="(caseItem, j) in m.payload.verdict.references.cases"
                  :key="`case-${idx}-${j}`"
                  class="case-item"
                >
                  <div class="case-row">
                    <span class="case-label">사건</span>
                    <span class="case-value">{{ caseItem.title }} ({{ caseItem.id }})</span>
                  </div>
                  <div class="case-row">
                    <span class="case-label">분류</span>
                    <span class="case-value">{{ caseItem.category }}</span>
                  </div>
                  <div class="case-row">
                    <span class="case-label">판결일</span>
                    <span class="case-value">{{ caseItem.decision_date }}</span>
                  </div>
                  <div class="case-row">
                    <span class="case-label">요약</span>
                    <span class="case-value">{{ caseItem.chunk_summary }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="m.payload.verdict.statutes?.length" style="margin-top: 1.5rem;">
              <h4>관련 법령</h4>
              <ul style="list-style-type: none; padding-left: 0; margin-top: 0.5rem;">
                <li
                  v-for="(statute, k) in m.payload.verdict.statutes"
                  :key="`stat-${idx}-${k}`"
                  style="margin-bottom: 0.5rem;"
                >
                  <a
                    :href="`http://law.go.kr/법령/${encodeURIComponent(statute.code)}`"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <strong>{{ statute.code }}</strong>
                  </a>
                  <ul
                    v-if="statute.articles && statute.articles.length > 0"
                    style="padding-left: 20px; margin-top: 5px; list-style-type: disc;"
                  >
                    <li v-for="article in statute.articles" :key="article" style="font-size: 0.9rem;">
                      <a
                        :href="`http://law.go.kr/법령/${encodeURIComponent(statute.code)}/제${article}`"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        제{{ article }}
                      </a>
                    </li>
                  </ul>
                </li>
              </ul>
            </div>
          </template>

          <template v-else>
            <p style="white-space: pre-wrap;">{{ m.payload?.text }}</p>
          </template>
        </div>
      </div>

      <div v-if="isFindingVerdict" class="finding-verdict-container">
        <LoadingDots />
        <p class="loading-text">AI가 실제 판례를 찾고 있습니다...</p>
        <img src="@/assets/ai-writing3.png" alt="AI 작성 중" class="loading-image" />
      </div>
    </div>

    <template v-else>
      <div v-if="isLoading" class="loading-container initial-loading">
        <LoadingDots />
        <p class="loading-text">AI가 답변을 생성 중입니다...</p>
        <img src="@/assets/ai-writing3.png" alt="AI 작성 중" class="loading-image" />
      </div>

      <div v-else-if="response" class="result-box">
        <div class="ai-message-box">
          <div v-if="isFindingVerdict" class="finding-verdict-container">
            <LoadingDots />
            <p class="loading-text">AI가 실제 판례를 찾고 있습니다...</p>
            <img src="@/assets/ai-writing3.png" alt="AI 작성 중" class="loading-image" />
          </div>

          <template v-else>
            <template v-if="!verdictResult && response.summary">
              <h4 style="margin-bottom: 1.2rem;">{{ response.title }}</h4>
              <hr style=" margin-bottom: 1.5rem;">
              <h6>요약</h6>
              <div class="summary-box">
                <p style="font-weight: 500; white-space: pre-wrap;">{{ response.summary }}</p>
              </div>
              <hr style="border: none; border-top: 1px solid #dbe6ee; margin: 1rem 0;" />
            </template>

            <template v-else-if="verdictResult">
              <h4>쟁점 및 AI 소견</h4>
              <ul v-if="verdictResult.issues?.length">
                <li v-for="(issue, index) in verdictResult.issues" :key="`issue-${index}`">
                  {{ issue }}
                </li>
              </ul>
              <p style="margin-top: 1rem;">{{ verdictResult.opinion }}</p>
              <p><strong>예상 형량:</strong> {{ verdictResult.expected_sentence }}</p>
              <p><strong>신뢰도:</strong> {{ (verdictResult.confidence * 100).toFixed(0) }}%</p>
              <div v-if="verdictResult.tags?.length" class="tags-wrapper">
                <span v-for="tag in verdictResult.tags" :key="tag" class="tag">#{{ tag }}</span>
              </div>

              <div v-if="verdictResult.references?.cases?.length" class="precedent-section">
                <h4>유사 판례</h4>
                <div class="case-list">
                  <div
                    v-for="(caseItem, index) in verdictResult.references.cases"
                    :key="`case-${index}`"
                    class="case-item"
                  >
                    <div class="case-row">
                      <span class="case-label">사건</span>
                      <span class="case-value">{{ caseItem.title }} ({{ caseItem.id }})</span>
                    </div>
                    <div class="case-row">
                      <span class="case-label">분류</span>
                      <span class="case-value">{{ caseItem.category }}</span>
                    </div>
                    <div class="case-row">
                      <span class="case-label">판결일</span>
                      <span class="case-value">{{ caseItem.decision_date }}</span>
                    </div>
                    <div class="case-row">
                      <span class="case-label">요약</span>
                      <span class="case-value">{{ caseItem.chunk_summary }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="verdictResult.statutes?.length" style="margin-top: 1.5rem;">
                <h4>관련 법령</h4>
                <ul style="list-style-type: none; padding-left: 0; margin-top: 0.5rem;">
                  <li
                    v-for="(statute, index) in verdictResult.statutes"
                    :key="`statute-${index}`"
                    style="margin-bottom: 0.5rem;"
                  >
                    <a
                      :href="`http://law.go.kr/법령/${encodeURIComponent(statute.code)}`"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <strong>{{ statute.code }}</strong>
                    </a>
                    <ul
                      v-if="statute.articles && statute.articles.length > 0"
                      style="padding-left: 20px; margin-top: 5px; list-style-type: disc;"
                    >
                      <li v-for="article in statute.articles" :key="article" style="font-size: 0.9rem;">
                        <a
                          :href="`http://law.go.kr/법령/${encodeURIComponent(statute.code)}/제${article}`"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          제{{ article }}
                        </a>
                      </li>
                    </ul>
                  </li>
                </ul>
              </div>
            </template>
          </template>
        </div>
      </div>

      <div v-else class="empty-state">
        <h1 class="title-ko">로우봇</h1>
        <p class="title-en">Law Bot</p>

        <img class="guide-bot" src="@/assets/ai-consult-bot.png" alt="AI 봇" />

        <p class="lead">
          궁금한 내용을 질문으로 입력하시면, AI가 해당 상황을 분석하여 핵심을 정리해드립니다.
        </p>
        <p class="lead">
          또한 유사 판례를 함께 찾아 제공해드려 보다 깊이 있고 신뢰할 수 있는 정보를 확인하실 수 있습니다.
        </p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue'
import { defineProps, defineEmits, defineExpose } from 'vue'
import instance from '@/lib/axios'
import LoadingDots from './LoadingDots.vue'
const props = defineProps({
  isLoading: Boolean,
  isFindingVerdict: Boolean, // 판례 검색 로딩 상태를 위한 prop 추가
  response: Object,
  verdictResult: Object,
  messages: { type: Array, default: () => [] }
})
const showBot = computed(() => {
  return !!(
    props.isLoading ||
    props.isFindingVerdict ||
    (props.messages && props.messages.length > 0) ||
    props.response ||
    props.verdictResult
  )
})

const scrollEl = ref(null)
const scrollToBottom = async () => {
  await nextTick()
  if (scrollEl.value) scrollEl.value.scrollTop = scrollEl.value.scrollHeight
}
watch(() => props.messages?.length, () => scrollToBottom())

const emit = defineEmits(['open-modal'])

const saveConsultationRecord = async () => {
  // response 객체가 없거나 필요한 데이터가 없으면 실행하지 않음
  if (!props.response || !props.response.title) {
    console.error('저장할 데이터가 없습니다.');
    return;
  }

  // API 요청에 필요한 데이터 구성
  const payload = {
    title: props.response.title,
    summary: props.response.summary,
    content: props.response.fullText,
    outcome: null,
    disadvantage: null,
    recommendedQuestion: null,
    tags: null
  };

  try {
    // isCompleted=false 쿼리 파라미터와 함께 POST 요청
    const response = await instance.post('/api/applications', payload, {
      params: {
        isCompleted: false
      }
    });
    // 성공 시 사용자에게 알림을 띄우는 로직을 추가할 수 있습니다 (예: toast 메시지)
    alert('상담 내용이 임시 저장되었습니다.');

  } catch (error) {
    console.error('상담 경위서 저장 실패:', error);
    // 실패 시 사용자에게 알림
    if (error.response) {
      alert(`저장에 실패했습니다: ${error.response.data.message}`);
    } else {
      alert('저장 중 오류가 발생했습니다.');
    }
  }
};

// ❗️ 부모 컴포넌트에서 이 함수를 호출할 수 있도록 노출시킵니다.
defineExpose({
  saveConsultationRecord,
  scrollToBottom
});


// ❗️ response 데이터가 변경될 때를 감지합니다.
watch(() => props.response, (newResponse) => {
  // ❗️ 조건: verdictResult가 없고(판례 검색 전) response.summary가 있을 때 (AI 요약 완료)
  if (newResponse && newResponse.summary && !props.verdictResult) {
    // 부모 컴포넌트에 모달을 열어달라는 이벤트를 보냅니다.
    emit('open-modal');
  }
}, {
  // 컴포넌트가 처음 마운트될 때도 watch를 실행할 수 있으나,
  // response는 비동기로 받아오므로 깊은 감지가 더 적합할 수 있습니다.
  deep: true
});

</script>

<style scoped>
.ai-box-wrapper {
  width: 100%;
  max-width: 920px;
}
*{
  font-family: 'Noto Sans KR', sans-serif;
}
.ai-scroll {
  max-height: 400px;
  overflow-y: auto;
  padding: 12px 10px;      /* 그림자 공간 */
  margin: -12px -10px;     /* 레이아웃 밀림 방지 */
  box-sizing: border-box;

}
.ai-sticky-header {
  position: sticky;
  top: 0;
  z-index: 5;
  display: flex;
  justify-content: center;
  padding: 0px 0 8px;
  /* 스크롤 시 텍스트와 자연스럽게 분리되도록 페이드 배경 */
  /* background: linear-gradient(to bottom, rgba(255,255,255,0.95), rgba(255,255,255,0)); */
}

.bot{
  width: 70px;
}
.result-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.ai-message-box {
  background-color: #ffffff8f;
  box-shadow: 0px 0px 5px 2px #E4EEF5;
  color: #072D45;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  width: 100%;
  min-height: 120px;
  text-align: left;
  font-size: 0.95rem;
  line-height: 1.5;
  margin-top: 0.35rem;
  margin-bottom: 20px;
}

h4{
  font-size: 1.1rem;
  font-weight: bold;
  text-align: center;
}
h6{
  font-size: 0.85rem;
  font-weight: bold;
}
.summary-box {
  border: 1px solid #e0ecf5;
  border-radius: 10px;
  padding: 15px 10px;
  box-sizing: border-box;
}

.tags-wrapper{
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.tag {
  background-color: #d0e1ef;
  color: #516F90;
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 8px;
}

.precedent-section {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #dbe6ee;
}

.case-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-top: 1rem;
}

.case-item {
  background-color: #f7fafd;
  border: 1px solid #e0ecf5;
  border-radius: 8px;
  overflow: hidden;
}

.case-row {
  display: flex;
  align-items: flex-start;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e0ecf5;
  font-size: 0.9rem;
}

.case-item .case-row:last-child {
  border-bottom: none;
}

.case-label {
  font-weight: 600;
  color: #516F90;
  width: 70px;
  flex-shrink: 0;
}

.case-value {
  flex: 1;
  color: #072D45;
  word-break: keep-all;
}

.empty-state {
  text-align: center;
}


.empty-state p {
  font-size: 1rem;
  font-weight: medium;
  color: #86A3B7;
  line-height: 1.2;
}
/* 타이틀 */
.title-ko {
  margin-top: 8px;
  margin-bottom: 2px;
  font-size: 2.0rem;
  font-weight: 800;
  color: #072D45;
}
.title-en {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: #86A3B7;
}

.guide-bot {
  width: 220px;
  margin: 10px 0 14px;
}

.lead {
  margin: 6px 0;
  font-size: 0.98rem;
  line-height: 1.8;
  color: #82A0B3;
}
.loading-container.initial-loading {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  min-height: 120px;
  color: #82A0B3;
  margin-top: 10px;
}

/* 판례 검색 로딩 컨테이너 스타일 추가 */
.finding-verdict-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  min-height: 200px; /* 채팅창 높이와 비슷하게 설정 */
  text-align: center;
  color: #82A0B3;
}
.loading-text{
  font-size: 1rem;
  color: #516F90;
  font-weight: 500;
}
.loading-image {
  width: 120px; /* 로딩 이미지 크기 조절 */
  margin-top: 1rem;
}

</style>
