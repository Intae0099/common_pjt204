<template>
  <base-navbar />

  <div class="main-background-container">
    <!-- 왼쪽 장식 패널 -->
    <div
      ref="leftImageEl"
      class="left-image-area"
      :style="{ transform: `translateX(calc(-100% + 40px - ${leftImageOffset}px))` }"
    ></div>

    <!-- 중앙 히어로 -->
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
          <div
            class="pill-track"
            @mousemove="doDrag"
            @mouseup="stopDrag"
            @mouseleave="stopDrag"
            :class="{ dragging: isDragging }"
          >
            <div
              class="drag-container"
              :style="{ transform: `translateX(${dragOffset}px)` }"
            >
              <RouterLink to="/ai-consult" class="btn-primary">
                바로 시작하기
              </RouterLink>
              <div class="pill-round" @mousedown.prevent="startDrag">
                <span class="chev">››</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 그대로, visual에 absolute 배치용 클래스 추가 -->
      <figure class="visual floating-robot">
        <img :src="bot" alt="법률 도우미 로봇" class="bot-img" />
      </figure>

    </div>

    <!-- 오른쪽 라운드 배경 패널 -->
    <div
      ref="rightImageEl"
      class="right-image-area"
      :style="{'--clipOffset': clipOffset + '%'}"
    ></div>
    <div style="height:1000px;"></div>

  </div>
</template>

<script setup>
import BaseNavbar from '@/components/BaseNavbar.vue'
import bot from '@/assets/main-bot.png'
import { onMounted, onUnmounted, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter()
const isDragging = ref(false)
const startX = ref(0)
const dragOffset = ref(0)
const threshold = 130 // 드래그 완료 임계값 (pill-track 너비에 맞게 조정)
const pillTrackWidth = 360 // .pill-track의 최대 너비
const clipOffset = ref(60);           // 첫 화면: 오른쪽 40%만 보이게
const rightImageEl = ref(null);
const leftImageOffset = ref(0); // translateX(0)에서 시작
const leftImageEl = ref(null);

const handleScroll = () => {
  const newOffset = 60 - window.scrollY * 0.1;   // 감도 조절
  clipOffset.value = Math.max(newOffset, 0);
  rightImageEl.value?.style.setProperty('--clipOffset', clipOffset.value + '%');

  // left-image-area 스크롤 로직 추가
  // 스크롤 Y 값에 비례하여 왼쪽으로 이동 (사라지게)
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

const startDrag = (e) => {
  isDragging.value = true
  startX.value = e.clientX
}

const doDrag = (e) => {
  if (!isDragging.value) return

  e.preventDefault()
  const currentX = e.clientX
  const newOffset = currentX - startX.value

  // 드래그 거리가 0 이상이고, 최대 드래그 가능한 거리(pillTrackWidth - 버튼 너비)를 넘지 않도록 제한
  const maxOffset = pillTrackWidth - e.currentTarget.querySelector('.btn-primary').offsetWidth;
  if (newOffset > 0 && newOffset < maxOffset) {
    dragOffset.value = newOffset
  }
}

const stopDrag = () => {
  if (!isDragging.value) return
  isDragging.value = false

  // 드래그 거리가 임계값을 넘으면 페이지 이동
  if (dragOffset.value > threshold) {
    router.push('/ai-consult')
  }

  // 드래그 상태 초기화 (원래 위치로 부드럽게 복귀)
  dragOffset.value = 0
}
</script>

<style scoped>
/* ===== 기본 레이아웃 ===== */
.main-background-container {
  --nav-h: 72px;
  font-family: 'Noto Sans KR', sans-serif;
  background: #fff;
  width: 100vw;
  height: auto; /* 높이를 자동으로 변경 */
  min-height: calc(100vh - var(--nav-h)); /* 최소 높이 지정 */
  margin-top: var(--nav-h);
  position: relative;
  overflow: clip;
  color: #1d2b50;
}

/* ===== 배경 패널 ===== */
.right-image-area {
  position: absolute;
  top: 0; right: 0;
  width: 100%; height: 100%;
  background: url('@/assets/main-right.png') center / cover no-repeat;

  /* 펼쳐지는 효과 */
  clip-path: inset(0 0 0 var(--clipOffset, 60%));  /* 처음엔 오른쪽 40%만 보임 */
  transition: clip-path .3s ease-out;
  will-change: clip-path;
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
  mask-image:j linear-gradient(to left, transparent, black 10%, black 100%);
  transition: transform 0.3s ease-out; /* 부드러운 애니메이션 효과 추가 */
}

/* ===== 히어로 그리드 (웹사이트 기본) ===== */
.hero {
  position: relative;
  z-index: 2;
  height: 100%;
  max-width: min(92vw, 1440px);
  margin: 0 auto;
  margin-left: 100px;
  padding: clamp(8px, 2.2vw, 28px);
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  align-items: center;
  gap: clamp(20px, 3vw, 40px);
}

/* 유리 카드 */
.glass-card {
  position: absolute;
  z-index: 0;
  margin-left: -20px;
  left: clamp(0px, 1vw, 12px);
  right: clamp(4px, 1vw, 7px);
  top: clamp(42vh, 46vh, 52vh);
  transform: translateY(-50%);
  height: clamp(460px, 58vh, 660px);
  width: 70%;
  border-radius: clamp(22px, 3.4vw, 38px);
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(40px) brightness(1.02);
  -webkit-backdrop-filter: blur(26px) brightness(1.02);
  box-shadow: 0 20px 40px rgba(146, 147, 150, 0.08), 0 6px 18px rgba(165, 167, 171, 0.06) inset;
}


/* ===== 텍스트 카피 ===== */
.copy {
  align-self: center;
  padding-left: clamp(4px, 1.6vw, 28px);
  margin-top: clamp(0px, -2vh, -20px);
  position: relative;
  z-index: 2;
}

.headline {
  margin: 0 0 clamp(8px, 1.4vw, 16px);
  line-height: 1.04;
  letter-spacing: -0.6px;
  font-weight: 800;
  font-size: clamp(38px, 6vw, 72px);
}
.headline .thin {
  font-weight: 700;
  color: #2d3a55;
}
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
  line-height: clamp(24px, 3.1vw, 34px);
  opacity: .92;
  max-width: clamp(440px, 46vw, 640px);
}

/* ===== CTA 버튼 ===== */
.cta-wrap {
  margin-top: clamp(18px, 1.9vw, 26px);
  display: flex;
  gap: clamp(8px, 1.1vw, 14px);
  align-items: center;
}

.pill-track {
  position: relative;
  width: clamp(200px, 28vw, 360px);
  height: clamp(40px, 5.2vh, 46px);
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(202, 212, 254, 0.9) 20%, rgba(255,255,255,1) 100%);
  cursor: grab;
}

/* 드래그할 버튼과 화살표를 감싸는 컨테이너 */
.drag-container {
  display: flex;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  transition: transform .3s ease-out; /* 드래그 후 복귀 애니메이션 */
  /* background-color: rgba(240, 243, 255, 0.8); */
  /* mask-image: linear-gradient(to left, transparent, black 10%, black 110%); */
}
.pill-track.dragging .drag-container {
  transition: none; /* 드래그 중에는 애니메이션 제거 */
}

.btn-primary {
  width: clamp(180px, 18vw, 220px);
  height: clamp(40px, 5.2vh, 46px);
  border-radius: 999px;
  background:#1d2b50;
  color:#fff;
  font-weight:700;
  font-size: clamp(14px,1.3vw,16px);
  padding: 0 18px;
  box-shadow: 0 10px 28px rgba(29,43,80,.18);
  display: grid;
  place-items: center;
  pointer-events: none; /* 드래그 대상이 아니므로 이벤트 방해 방지 */
  text-decoration: none;
}

/* ===== 새롭게 추가된 클래스 ===== */
.pill-round {
  position: relative; /* pill-track 내부에서 상대적 위치 */
  width: clamp(40px, 5.2vh, 46px);
  height: clamp(40px, 5.2vh, 46px);
  border-radius: 50%;
  border: 1.5px solid #1d2b50;
  background: #fff;
  display: grid;
  place-items: center;
  margin-left: -35px; /* 버튼과 겹치도록 음수 마진 사용 */
}
.chev {
  font-size: clamp(18px,2.2vw,22px);
  color:#1d2b50;
}


/* ===== 로봇 이미지 (웹사이트 기본) ===== */
.visual {
  position: relative;
  z-index: 3;
  width: clamp(360px, 40vw, 900px);
  filter: drop-shadow(0 20px 40px rgba(29, 43, 80, .18));
  transform: translate(-16vw, -10vh);
}
.bot-img {
  width: 100%;
  height: auto;
  pointer-events: none;
}




</style>
