<template>
  <section class="recommend-section">
    <h2 class="title">AI추천 변호사</h2>
    <p class="subtitle">AI가 분석한 결과를 바탕으로 변호사를 추천합니다.</p>

    <div v-if="Array.isArray(lawyers) && lawyers.length" class="grid">
      <article
        v-for="lawyer in lawyers"
        :key="lawyer.lawyerId"
        class="card"
        :ref="el => observeCard(el, lawyer.lawyerId)"
      >
        <header class="top-row">
          <div class="name-badges">
            <h3 class="name">
              {{ lawyer.name }} <span class="suffix">변호사</span>
            </h3>
            <span v-if="lawyer.exam" class="pill">{{ lawyer.exam }}</span>
          </div>
          <span class="count">총 상담횟수 {{ lawyer.consultationCnt }}회</span>
        </header>

        <p class="intro">
          {{ lawyer.introduction || '소개가 아직 등록되지 않았습니다.' }}
        </p>

        <div class="field-row">
          <span class="field-label">상담 분야</span>
          <div class="tags">
            <span
              v-for="(tag, i) in visibleTags(lawyer)"
              :key="`${lawyer.lawyerId}-${i}`"
              class="tag"
            >#{{ tag }}</span>

            <button
              v-if="!isWide(lawyer.lawyerId) && hasMoreTags(lawyer)"
              class="more-tags-btn"
              @click="toggleTags(lawyer.lawyerId)"
            >
              <ChevronUp v-if="expanded.has(lawyer.lawyerId)" class="more-tags-icon" />
              <ChevronDown v-else class="more-tags-icon" />
            </button>
          </div>
        </div>

        <div class="actions">
          <button
            v-if="userType !== 'LAWYER'"
            class="cta"
            @click="goToReservation(lawyer.lawyerId)"
          >
            바로 상담하기
          </button>
        </div>
      </article>
    </div>

    <p v-else class="loading">추천 변호사를 불러오는 중입니다...</p>
  </section>
</template>

<script setup>
import { ref, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronDown, ChevronUp } from 'lucide-vue-next'

const userType = localStorage.getItem('userType') // 'LAWYER' | 'USER'

defineProps({
  lawyers: { type: Array, default: () => [] }
})

const router = useRouter()
const expanded = ref(new Set())

// --- 카드 너비 관찰(좁/넓 판정) ---
const WIDE_PX = 560 // 이보다 넓으면 토글 숨기고 태그 모두 노출
const cardWidths = ref(new Map()) // id(string) -> width(px)
let ro /** @type {ResizeObserver | undefined} */

const observeCard = (el, id) => {
  if (!el) return
  if (!ro) {
    ro = new ResizeObserver(entries => {
      for (const e of entries) {
        const key = e.target.dataset.cardId
        if (!key) continue
        cardWidths.value.set(key, e.contentRect.width)
      }
    })
  }
  el.dataset.cardId = String(id)
  ro.observe(el)
}

onBeforeUnmount(() => { ro?.disconnect() })

const isWide = (id) => (cardWidths.value.get(String(id)) || 0) >= WIDE_PX

const toggleTags = (id) => {
  if (expanded.value.has(id)) expanded.value.delete(id)
  else expanded.value.add(id)
}

const hasMoreTags = (lawyer) =>
  Array.isArray(lawyer.tags) && lawyer.tags.length > 2

// 넓으면 전부, 좁으면 2개(+펼치기)
const visibleTags = (lawyer) => {
  const all = lawyer.tags || []
  if (isWide(lawyer.lawyerId)) return all
  return expanded.value.has(lawyer.lawyerId) ? all : all.slice(0, 2)
}

const goToReservation = (lawyerId) => {
  router.push({ name: 'DetailReservation', params: { id: lawyerId } })
}
</script>


<style scoped>
* { font-family: 'Noto Sans KR', sans-serif; }

.recommend-section {
  margin-top: 56px;
}

.title {
  text-align: center;
  color: #072d45;
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.subtitle {
  text-align: center;
  margin-top: 8px;
  margin-bottom: 28px;
  color: #82a0b3;
  font-size: 14px;
}

.grid {
  --gap: 18px;
  display: grid;
  gap: var(--gap);
  max-width: 920px;
  width: 100%;
  margin: 0 auto;
  grid-template-columns: repeat(auto-fit, minmax(calc((920px - 2 * var(--gap)) / 3), 1fr));
  justify-content: center;
  align-content: start;
}

.card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: #ffffffcc;
  border: 1px solid #e5eff7;
  border-radius: 16px;
  padding: 18px;
  box-shadow: 0 6px 20px rgba(15, 44, 89, 0.06);
  transition: transform .15s ease, box-shadow .15s ease;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(15, 44, 89, 0.10);
}

.top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.name-badges {
  display: flex;
  align-items: center;
  gap: 10px;
}

.name {
  margin: 0;
  color: #0b2a47;
  font-size: 15px;
  font-weight: 800;
  word-break: keep-all;
}
.suffix {
  font-weight: 600;
  color: #0b2a47;
}

.pill {
  background: #e6edf5;
  color: #516f90;
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 999px;
  line-height: 1;
}

.count {
  font-size: 12px;
  color: #7e93a7;
}

.intro {
  color: #1d2939;
  font-size: 14px;
  line-height: 1.5;
  min-height: 65px;
}

.field-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-weight: 700;
  color: #0b2a47;
  font-size: 13px;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

/* ▼ PreviewUserView.vue의 태그 스타일과 톤을 맞춤 */
.tag {
  background-color: #e6edf5;
  color: #516f90;
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 8px;
}

.more-tags-btn {
  background: none;
  border: none;
  padding: 0 2px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
}
.more-tags-icon {
  width: 16px;
  height: 16px;
  color: #516f90;
}

.actions {
  margin-top: 8px;
  display: flex;
  justify-content: center;
}
.cta {
  width: 100%;
  padding: 12px 0;
  background: #0F2C59;
  color: #fff;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: background .2s ease;
}
.cta:hover { background: #1c3d78; }

.loading {
  text-align: center;
  color: #82a0b3;
  margin-top: 16px;
}

/* 반응형 그리드 */
@media (max-width: 920px) {
  .grid {
    max-width: 100%;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  }
}
@media (max-width: 560px) {
  .grid { grid-template-columns: 1fr; }
}
</style>
