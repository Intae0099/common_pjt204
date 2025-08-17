<template>
  <base-navbar />

  <div class="main-background-container">
    <div
      ref="leftImageEl"
      class="left-image-area"
      :style="{ transform: `translateX(calc(-100% + 40px - ${leftImageOffset}px))` }"
    ></div>

    <div class="hero">
      <div class="glass-card"></div>

      <section class="copy">
        <h1 class="headline">
          <span class="thin">법률 상담,</span><br />
          <span class="brand">어디로? 에이로!</span>
        </h1>

        <p class="subcopy">
          AI와 함께 상담하고, 변호사가 이어받는 스마트 법률 서비스<br />
          간편한 사전상담부터 1:1 화상상담까지 한 번에 해결하세요
        </p>

      <div class="cta-wrap">
        <RouterLink to="/ai-consult" class="ai-cta">바로 시작하기</RouterLink>
      </div>

      </section>
      <figure class="visual floating-robot">
        <img :src="bot" alt="법률 도우미 로봇" class="bot-img" />
      </figure>
    </div>

    <div class="scroll-hint" @click="scrollToOverview">
      <span class="label">아래로 스크롤</span>
      <ChevronsDown class="chevrons" aria-hidden="true" />
    </div>
    <section class="ai-overview">
      <div class="ai-container">
        <p class="ai-eyebrow"><strong>첫번째,</strong> AI에게 물어보기</p>

        <h2 class="ai-title">
          법률 상담을 위한<br />
          <strong>AI 기반 사건 분석 · 관련 판례 찾기</strong>
        </h2>

        <ul class="ai-cards">
          <li class="ai-card">
            <img class="ai-icon" src="@/assets/section2-1.png" alt="사건요약 아이콘" />
            <h3>사건요약</h3>
            <span class="ai-divider" aria-hidden="true"></span>
            <p>복잡한 사건 내용을 핵심만 간결하게 AI가 정리해드립니다.</p>
          </li>

          <li class="ai-card">
            <img class="ai-icon" src="@/assets/section2-2.png" alt="쟁점 및 AI 소견 아이콘" />
            <h3>쟁점 및 AI 소견</h3>
            <span class="ai-divider" aria-hidden="true"></span>
            <p>주요 쟁점을 분석하고, 전략적 시각에서 의견을 제시합니다.</p>
          </li>

          <li class="ai-card">
            <img class="ai-icon" src="@/assets/section2-3.png" alt="유사판례 아이콘" />
            <h3>유사판례</h3>
            <span class="ai-divider" aria-hidden="true"></span>
            <p>관련성이 높은 판례를 찾아 근거 기반의 판단을 돕습니다.</p>
          </li>
        </ul>


        <router-link to="/ai-consult" class="ai-cta">바로가기</router-link>
      </div>
    </section>

    <div
      ref="rightImageEl"
      class="right-image-area"
      :style="{'--clipOffset': clipOffset + '%'}"
    ></div>

  </div>
  <SectionThird/>
  <SectionFourth/>
  <SectionFifth/>
</template>


<script setup>
import BaseNavbar from '@/components/BaseNavbar.vue'
import bot from '@/assets/main-bot.png'
import { onMounted, onUnmounted, ref } from 'vue';
import SectionThird from './component/SectionThird.vue';
import SectionFourth from './component/SectionFourth.vue';
import SectionFifth from './component/SectionFifth.vue';
import { ChevronsDown } from 'lucide-vue-next'
const clipOffset = ref(60);           // 첫 화면: 오른쪽 40%만 보이게
const rightImageEl = ref(null);
const leftImageOffset = ref(0); // translateX(0)에서 시작
const leftImageEl = ref(null);

const handleScroll = () => {
  const newOffset = 60 - window.scrollY * 0.1;   // 감도 조절
  clipOffset.value = Math.max(newOffset, 0);
  rightImageEl.value?.style.setProperty('--clipOffset', clipOffset.value + '%');

  // left-image-area 스크롤 로직: 스크롤 Y에 비례하여 왼쪽으로 이동
  const leftOffset = window.scrollY * 0.2; // 사라지는 속도 조절
  leftImageOffset.value = Math.min(leftOffset, 100); // 최대 100%까지 이동
};

onMounted(() => {
  // 초기값 반영 + 스크롤 이벤트
  rightImageEl.value?.style.setProperty('--clipOffset', clipOffset.value + '%');
  window.addEventListener('scroll', handleScroll, { passive: true });
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});

</script>


<style scoped>
/* ===== 공통 토큰 ===== */
:root {
  --navy: #1d2b50;
  --text-sub: #5a6b84;
  --text-mute: #6b7a90;
  --shadow-card: 0 6px 24px rgba(20,40,80,.06);
}

/* ===== 기본 레이아웃 ===== */
.main-background-container {
  --nav-h: 80px;
  font-family: 'Noto Sans KR', sans-serif;
  background: #fff;
  height: auto;
  min-height: calc(100vh - var(--nav-h));
  margin-top: var(--nav-h);
  position: relative;
  overflow: clip;
  color: var(--navy);
}

/* ===== 배경 패널 ===== */
.right-image-area {
  position: absolute;
  top: 0; right: 0;
  width: 100%; height: 100%;
  background: url('@/assets/main-right.png') center / cover no-repeat;

  /* 펼쳐지는 효과 */
  clip-path: inset(0 0 0 var(--clipOffset, 60%));
  transition: clip-path .3s ease-out;
  will-change: clip-path;
  z-index: 0;
}

/* 완전히 펼쳐졌을 땐 경계선만 사라지게(선택) */
.right-image-area.fully-opened::after{
  opacity:0;
}

.left-image-area {
  background-image: url('@/assets/main-right.png');
  background-size: cover;
  background-position: center;
  position: absolute;
  bottom: 20vh;
  left: 0;
  width: clamp(200px, 60vw, 1000px);
  height: clamp(180px, 50vh, 1000px);
  transform: translateX(-70%);
  border-top-right-radius: clamp(18px, 3vw, 40px);
  border-bottom-right-radius: clamp(18px, 3vw, 40px);
  z-index: 1;
  mask-image: linear-gradient(to left, transparent, black 10%, black 100%);
  transition: transform 0.3s ease-out;
}

/* ===== 히어로 그리드 ===== */
.hero {
  position: relative;
  z-index: 2;
  height: 100%;
  max-width: min(92vw, 1440px);
  margin: 0 auto;
  padding: 80px 100px;
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  grid-template-areas: "copy visual";
  align-items: center;
  gap: clamp(20px, 3vw, 40px);
}

/* 유리 카드 */
.glass-card {
  position: absolute;
  z-index: 0;
  left: clamp(0px, 1vw, 12px);
  right: clamp(4px, 1vw, 7px);
  top: 50%;                   /* ⬅️ vh 대신 percentage */
  transform: translateY(-50%);
  height: 450px;
  width: 70%;
  border-radius: clamp(22px, 3.4vw, 38px);
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(26px) brightness(1.02);
  box-shadow: 0 15px 50px rgba(203, 213, 240, 0.5);
}

/* 텍스트 카피 */
.copy {
  grid-area: copy;
  align-self: center;
  z-index: 5;
}

.headline {
  margin: 0 0 20px;
  line-height: 1.2;
  letter-spacing: -0.6px;
  font-weight: 800;
  font-size: clamp(38px, 6vw, 72px);
}
.headline .thin { font-weight: 700; color: #2d3a55; }
.headline .brand {
  background: linear-gradient(135deg, #8fb0ff 0%, #adc6ff 55%, #6f83b5 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subcopy {
  margin-top: clamp(10px, 1.4vw, 16px);
  color: #2a3650;
  font-size: clamp(15px, 1.55vw, 20px);
  line-height: clamp(20px, 3vw, 34px);
  opacity: .92;
  max-width: clamp(440px, 46vw, 640px);
}
.copy .ai-cta {
  margin: 12px 0 0 -5px;
}
/* CTA 버튼 (히어로) */
.cta-wrap {
  margin-top: clamp(18px, 2vw, 26px);
  display: flex;
  gap: clamp(8px, 1.1vw, 14px);
  align-items: center;
}

/* 로봇 이미지 */
.visual {
  z-index: 2;
  grid-area: visual;
  justify-self: end;
  align-self: center;
  width: clamp(360px, 30vw, 900px);
  transform: none;
    /* ⬇️ 위치/크기 조정용 변수 */
  --robot-x: -450px;           /* 오른쪽(+) 왼쪽(-)으로 이동 */
  --robot-y: -110px;           /* 아래(+) 위(-)로 이동 */
  --robot-scale: 1;         /* 크기 */

  transform: translate(var(--robot-x), var(--robot-y)) scale(var(--robot-scale));
  transition: transform .25s ease; /* 미세 조정 시 부드럽게 */
}
.bot-img { width: 100%; height: auto; pointer-events: none; }


/* 히어로 아래 스크롤 힌트 */
.scroll-hint {
  position: relative;
  z-index: 3;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  margin: -50px 0 28px;      /* 히어로와 2섹션 사이 간격 */
  color: #6b7a90;          /* --text-mute 톤 */
  cursor: pointer;
  user-select: none;
  opacity: .85;
  transition: opacity .2s ease, transform .2s ease;
}
.scroll-hint:hover { opacity: 1; transform: translateY(-2px); }

.scroll-hint .label {
  font-size: 14px;
  letter-spacing: .2px;
}

.scroll-hint .chevrons {
  width: 26px;
  height: 26px;
  animation: hint-bounce 1.4s infinite ease-in-out;
}

/* 아래로 살짝 점프하는 느낌 */
@keyframes hint-bounce {
  0%, 100% { transform: translateY(0); opacity: .9; }
  50%      { transform: translateY(6px); opacity: 1; }
}

/* 모션 최소화 환경 */
@media (prefers-reduced-motion: reduce) {
  .scroll-hint .chevrons { animation: none; }
}


/* =========================
   2섹션 스타일 (AI Overview)
   ========================= */
.ai-overview {

  padding: 110px 0 84px;
  position: relative;
  z-index: 2;
}

.ai-container {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 20px;
}

.ai-eyebrow {
  text-align: center;
  font-size: 20px;
  color: var(--text-mute);
  margin-bottom: 15px;
}

.ai-title {
  text-align: center;
  font-weight: 400;
  font-size: 50px;
  line-height: 1.25;
  color: var(--navy);
  margin: 0 0 90px;
}

.ai-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
  margin: 0 0 100px;
  list-style: none;
  padding-left: 0;
}
/* 큰 화면에서 로봇만 살짝 키우고 오른쪽으로 밀기 */
@media (min-width: 1600px) {
  .visual { width: clamp(600px, 36vw, 920px); margin-right: clamp(0px, 1vw, 24px); }
}
/* 태블릿 이하에선 단일 컬럼로 안전하게 */
@media (max-width: 1024px) {
  .hero {
    grid-template-columns: 1fr;
    grid-template-areas:
      "copy"
      "visual";
  }
  .visual { justify-self: center; margin-right: 0; }
}
@media (max-width: 960px) {
  .ai-cards { grid-template-columns: 1fr; }
}

/* 2섹션 카드 그리드: 아이콘 좌, 텍스트 컬럼 우 */
.ai-card {
  background: #ffffffa9;
  border-radius: 18px;
  padding: 30px;
  box-shadow: var(--shadow-card);
  list-style: none;
  display: grid;
  grid-template-columns: auto 1fr; /* 아이콘 + 텍스트 한 줄 */
  grid-template-rows: auto auto auto; /* h3 | divider | p */
  column-gap: 12px;
  align-items: center;
  box-shadow: 0px 0px 5px #E0F2FF;
}

.ai-card::marker { content: ""; } /* 혹시 남는 브라우저 마커 제거 */

.ai-icon {
  width: 40px;
  height: 40px;
  grid-column: 1;
  grid-row: 1; /* 제목과 같은 줄 */
}

.ai-card h3 {
  grid-column: 2;
  grid-row: 1;
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  color: var(--navy);
}

/* ⬇️ 제목 아래 얇은 구분선 */
.ai-divider {
  grid-column: 1 / -1; /* 카드 전체 너비 차지 */
  grid-row: 2;
  height: 1px;
  background: #cfd8e6;
  border-radius: 1px;
  margin: 8px 0;
}

.ai-card p {
  grid-column: 1 / -1; /* 전체 너비 */
  grid-row: 3;
  margin: 0;
  color: var(--text-sub);
  line-height: 1.6;
}


/* 중앙 정렬 + 색상 + 그림자 제거는 유지 */
.ai-cta {
  display: block;
  width: max-content;
  margin: 16px auto 0;
  padding: 12px 22px;
  min-width: 200px;
  text-decoration: none;
  border-radius: 999px;
  background: #1d2b50;
  color: #fff;
  font-weight: 500;
  box-shadow: none;
  text-align: center;
}

</style>

