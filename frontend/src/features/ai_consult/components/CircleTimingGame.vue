<template>
  <div class="circle-game" role="group" aria-label="로딩 미니게임: 타이밍 스톱">
    <!-- 타겟 영역 (윗부분 반달) -->
    <div class="target-arc"></div>

    <!-- 바늘 -->
    <div
      class="needle"
      :style="{
        transform: `translate(-50%, -100%) rotate(${angle}deg)`,
        height: props.radius + 'px'
      }"
    />


    <!-- 중앙 점 -->
    <div class="hub"></div>

    <!-- 결과 오버레이 -->
    <div
      v-if="result"
      class="result-overlay"
      :class="result === '성공!' ? 'success' : 'fail'"
    >
      {{ result }}
    </div>

    <!-- 하단 UI -->
    <div class="ui">
      <!-- spinning일 때만 STOP 보이기 -->
      <button class="btn" v-if="spinning" @click="shoot">STOP</button>

      <!-- 멈춘 상태에서만 다시하기 보이기 -->
      <button class="btn ghost" v-else @click="restart">다시하기</button>
      <span class="hint">상단 영역에 맞춰 정지하면 성공!</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

/**
 * Props
 * - active: 부모에서 로딩 중(true)일 때 자동으로 회전 시작/종료 제어
 * - speedDeg: 1틱(60ms)마다 증가하는 각도(도)
 * - targetHalfWidth: 성공 판정 각도 반폭(도). 0°(정상단)을 기준 ±값
 */
const props = defineProps({
  active: { type: Boolean, default: true },
  speedDeg: { type: Number, default: 8 },

  // --- 성공 판정 모드/치수 ---
  mode: { type: String, default: 'band' }, // 'band' | 'wedge'
  targetHalfWidth: { type: Number, default: 18 }, // wedge 모드에서만 사용 (±도)
  radius: { type: Number, default: 70 },          // 바늘 길이(px)
  targetBandHeight: { type: Number, default: 42 } // band 모드에서 띠 높이(px)
})


const emit = defineEmits(['played']) // { success: boolean, angle: number }

const angle = ref(0)        // 0° = 위쪽(12시 방향)
const spinning = ref(false)
const result = ref('')
let timer = null

function tick() {
  angle.value = (angle.value + props.speedDeg) % 360
}

function start() {
  clearTimer()
  spinning.value = true
  result.value = ''
  timer = setInterval(tick, 60)
}

function clearTimer() {
  if (timer) { clearInterval(timer); timer = null }
}

function stop() {
  spinning.value = false
  clearTimer()
}

function shoot() {
  stop()
  const norm = ((angle.value % 360) + 360) % 360
  let success = false

  if (props.mode === 'wedge') {
    // 12시 기준 부채꼴
    success = norm <= props.targetHalfWidth || norm >= (360 - props.targetHalfWidth)
  } else {
    // band: 윗 띠 안이면 성공
    // 0°가 12시. 바늘 끝의 세로 오프셋: R(1 - cosθ)
    const rad = (norm * Math.PI) / 180
    const distanceFromTop = props.radius * (1 - Math.cos(rad)) // 0 ~ 2R
    success = distanceFromTop <= props.targetBandHeight
  }

  result.value = success ? '성공!' : '실패'
  emit('played', { success, angle: norm })
}

function restart() {
  angle.value = 0
  start()
}

watch(() => props.active, (on) => {
  if (on) start()
  else stop()
}, { immediate: true })

onMounted(() => { if (props.active) start() })
onUnmounted(() => clearTimer())
</script>

<style scoped>
.circle-game{
  --border:#6c9bcf;
  --bg:#f7fafd;
  --target:#d0e1ef;
  --text:#516F90;

  position: relative;
  width: 180px;
  height: 180px;
  margin: 10px auto 0;
  border-radius: 50%;
  border: 3px solid var(--border);
  background: #fff;
  box-shadow: 0 0 5px 2px #E4EEF5;
}

/* 상단 타겟 영역(원 위쪽 60~70px 높이 띠) */
.target-arc{
  position:absolute;
  top: 8px;
  left: 8px;
  right: 8px;
  height: 42px;
  border-top-left-radius: 999px;
  border-top-right-radius: 999px;
  background: var(--target);
  opacity: .9;
  z-index: 1;
}

/* 바늘 */
.needle{
  position:absolute;
  top: 50%;
  left: 50%;
  width: 2px;
  height: 70px;                 /* 반지름에 맞게 조절 */
  background: var(--border);
  transform-origin: 50% 100%;   /* '바늘의 바닥' = 원의 중심 */
  z-index: 2;                   /* 타겟 영역보다 위에 */
}

/* 중앙 허브 */
.hub{
  position:absolute;
  top:50%;
  left:50%;
  width: 10px;
  height: 10px;
  transform: translate(-50%,-50%);
  background: var(--border);
  border-radius: 50%;
  z-index: 3;
}

/* 하단 UI */
.ui{
  position:absolute;
  bottom: -70px;
  left: 50%;
  transform: translateX(-50%);
  display:flex;
  align-items:center;
  gap: 8px;
  flex-wrap: wrap;
  width: 220px;
  justify-content: center;
}

.btn{
  border: 1px solid #6c9bcf;
  background: transparent;          /* ← 배경 제거 */
  color: #516F90;                   /* ← 텍스트 고정 색 */
  padding: .36rem .7rem;
  border-radius: 10px;
  font-size: .88rem;
  cursor: pointer;
  transition: none;                 /* ← 호버 때 색 변화 없음 */
}

/* 다시하기(ghost)도 동일하게 배경 없음 */
.btn.ghost{
  background: transparent;          /* ← 배경 제거 */
  color: #516F90;                   /* ← 텍스트 고정 색 */
  border: 1px solid #cfe0eb;
}

/* 호버/포커스/액티브 때도 색상과 배경 변화 없도록 고정 */
.btn:hover,
.btn:focus,
.btn:active,
.btn.ghost:hover,
.btn.ghost:focus,
.btn.ghost:active{
  background: transparent;          /* ← 계속 투명 */
  color: #516F90;                   /* ← 계속 동일 */
  border-color: inherit;            /* ← 테두리도 그대로 */
  box-shadow: none;
  outline: none;
}

/* 화면 리더만 읽도록 */
.sr-only{
  position:absolute !important;
  width:1px; height:1px;
  padding:0; margin:-1px;
  overflow:hidden; clip:rect(0,0,0,0);
  white-space:nowrap; border:0;
}

/* 가운데 결과 박스 */
.result-overlay{
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%,-50%) scale(0.9);
  min-width: 84px;
  text-align: center;
  padding: 10px 14px;
  border-radius: 12px;
  font-weight: 700;
  font-size: .95rem;
  color: #072D45;
  background: rgba(255,255,255,.95);
  border: 1px solid #e0ecf5;
  box-shadow: 0 6px 16px rgba(12, 42, 70, .10);
  z-index: 4; /* 바늘/허브 위 */
  opacity: 0;
  animation: popIn .18s ease-out forwards;
}

.result-overlay.success{
  border-color: #6C9BCF;
  box-shadow: 0 6px 16px rgba(46, 85, 125, 0.12);
}
.result-overlay.fail{
  border-color: #e6b8b8;
  box-shadow: 0 6px 16px rgba(183, 28, 28, .12);
}

@keyframes popIn{
  to { opacity: 1; transform: translate(-50%,-50%) scale(1); }
}


.hint{
  flex-basis: 100%;
  text-align: center;
  font-size: .78rem;
  color: #86A3B7;
}
</style>
