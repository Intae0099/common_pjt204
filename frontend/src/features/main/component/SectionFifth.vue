<template>
  <section class="fifth-section" ref="sectionRef">
    <div class="container">
      <article class="card card-1" :style="{ '--bg': `url(${card1})` }">
        <div class="overlay"></div>
        <div class="copy">
          <p class="eyebrow"><strong>네번째,</strong> AI로 상담신청서 작성하기</p>
          <h3 class="title">
            사건 내용을 바탕으로<br />
            <strong>맞춤형 상담 질문</strong>을 생성
          </h3>
        </div>
      </article>

      <article class="card card-2" :style="{ '--bg': `url(${card2})` }">
        <div class="overlay"></div>
        <div class="copy">
          <p class="eyebrow"><strong>다섯번째,</strong> 상담예약하고 화상상담 진행하기</p>
          <h3 class="title">
            상담 예약부터 <strong>화상 진행</strong>까지<br />
            한 번에 간편하게
          </h3>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import card1 from '@/assets/section5-card1.png'
import card2 from '@/assets/section5-card2.png'

const sectionRef = ref(null)
let observer

onMounted(() => {
  const root = sectionRef.value
  if (!root) return

  const cards = Array.from(root.querySelectorAll('.card'))

  // 뷰포트에 들어오면 in 추가, 나가면 제거 ⇒ 재진입 시 매번 재생
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        const el = entry.target
        if (entry.isIntersecting) {
          el.classList.add('in')
        } else {
          // 충분히 벗어나면 제거(스크롤 살짝 흔들려도 깜빡임 방지)
          if (entry.intersectionRatio === 0) {
            el.classList.remove('in')
          }
        }
      })
    },
    {
      threshold: [0, 0.2],
      rootMargin: '0px 0px -10% 0px', // 약간 더 들어왔을 때 트리거
    }
  )

  cards.forEach((el) => observer.observe(el))
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<style scoped>
.fifth-section {
  padding: clamp(56px, 7vw, 96px) 0;
  background: #fff;
}

.container {
  max-width: 1120px;
  margin: 20px auto 200px;
  padding: 0 20px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: clamp(16px, 2vw, 24px);
  align-items: start;
}

/* 카드 */
.card {
  position: relative;
  height: clamp(340px, 38vw, 765px);
  border-radius: 28px;
  overflow: hidden;
  background: var(--bg) center / cover no-repeat;
  box-shadow: 0 16px 40px rgba(23,36,64,.16);
  isolation: isolate;

  /* 애니메이션 초기 상태 */
  --offset: 0px;
  --delay: 0ms;            /* 각 카드별 지연 시간 */
  opacity: 0;
  transform: translateY(calc(var(--offset, 0px) + 120px));
  will-change: transform, opacity;
  transition:
    transform .7s cubic-bezier(.2,.8,.2,1) var(--delay),
    opacity .7s ease var(--delay);
}

/* 두 번째 카드의 레이아웃 오프셋 유지 */
.card:last-child {
  --offset: 100px;
}

/* 스태거: CSS 변수로 지연 부여 (재진입에도 유지) */
.card-1 { --delay: 0ms; }
.card-2 { --delay: 140ms; }

/* 보여질 때 */
.card.in {
  opacity: 1;
  transform: translateY(var(--offset, 0px));
}

/* 텍스트 */
.copy { position: relative; z-index: 2; color: #eaf2ff; padding: clamp(22px, 3vw, 32px); text-shadow: 0 1px 2px rgba(0,0,0,.18); }
.eyebrow { font-size: clamp(14px, 1.2vw, 18px); opacity: .95; margin: 0 0 10px; }
.title { margin: 0 0 16px; font-weight: 400; letter-spacing: -0.3px; line-height: 1.28; font-size: clamp(20px, 2.4vw, 28px); color: #fff; }

/* 반응형 */
@media (max-width: 960px) {
  .container { grid-template-columns: 1fr; }
  .card { height: clamp(240px, 50vw, 320px); }
  .card:last-child { --offset: 0px; } /* 모바일 겹침 제거 */
}

/* 모션 최소화 */
@media (prefers-reduced-motion: reduce) {
  .card {
    transition: none !important;
    opacity: 1 !important;
    transform: translateY(var(--offset, 0px)) !important;
  }
}
</style>
