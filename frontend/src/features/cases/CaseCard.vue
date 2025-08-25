<template>
  <router-link
    :to="{ name: 'CaseDetail', params: { id: data.caseId } }"
    class="card-link"
  >
    <article class="case-card">
      <span class="accent" aria-hidden="true"></span>

      <header class="case-header">
        <h3 class="case-title" v-html="highlightedTitle"></h3>
        <time class="case-date" :datetime="data.decisionDate">
          {{ formatDate(data.decisionDate) }}
        </time>
      </header>

      <p class="case-excerpt" v-html="highlightedExcerpt"></p>
    </article>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    required: true,
    // 기대 필드: caseId, title, judgmentDate(YYYY-MM-DD), summary 또는 content
  },
  highlight: { type: String, default: '' }
})

/** YYYY.MM.DD 포맷 */
const formatDate = (d) => {
  if (!d) return ''
  const [y, m = '', dd = ''] = String(d).split(/-|\/|\./)
  return `${y}.${m.padStart(2,'0')}.${dd.padStart(2,'0')}`
}


/* 원문 200자 요약 */
const rawExcerpt = computed(() => {
  const raw = String(props.data.summary || props.data.content || '')
    .replace(/<[^>]+>/g, '')
    .replace(/\s+/g, ' ')
    .trim()
  return raw.length > 150 ? raw.slice(0, 150) + '…' : raw
})

/* 안전 이스케이프 + 키워드 하이라이트 */
const escapeHtml = (s) =>
  String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

const escapeRegex = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

const highlightText = (text, query) => {
  const base = escapeHtml(text ?? '')
  const q = String(query || '').trim()
  if (!q) return base
  const terms = [...new Set(q.split(/\s+/).filter(t => t.length > 1))]
  if (!terms.length) return base
  const pattern = new RegExp(`(${terms.map(escapeRegex).join('|')})`, 'gi')
  return base.replace(pattern, '<mark>$1</mark>')
}

const highlightedTitle   = computed(() => highlightText(props.data.title || '', props.highlight))
const highlightedExcerpt = computed(() => highlightText(rawExcerpt.value || '', props.highlight))

</script>

<style scoped>
/* 링크 기본 스타일 유지 */
.card-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

/* 카드 */
.case-card{
  font-family: 'Noto Sans KR', sans-serif;
  color: #333333;
  position: relative;
  /* display: grid;
  gap: .75rem; */
  padding: 20px 22px 16px 22px;
  border: 1px solid #cfcfcf;
  border-radius: 15px;
  background: #fff;
  transition: box-shadow .2s ease, border-color .2s ease, transform .2s ease;
   height: 100%;                  /* 1. 부모(.card-link)의 높이를 꽉 채웁니다. */
  display: flex;                  /* 2. 내부 정렬을 위해 Flexbox를 사용합니다. */
  flex-direction: column;
}
.case-card:hover{
  box-shadow: 0 6px 16px rgba(0,0,0,.06);
  border-color: #6c9bcf;
  transform: translateY(-1px);
}

/* 좌측 포인트 라인 */
.accent{
  position: absolute;
  left: 0; top: 6px; bottom: 6px;
  width: 4px;
  border-radius: 4px 0 0 4px;
  background: linear-gradient(180deg, #6c9bcf 0%, #a7c5eb 100%);
}

/* 헤더 */
.case-header{
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 12px;
}
.case-title{
  flex: 1;
  font-size: 18px;
  line-height: 1.4;
  font-weight: 700;
  color: #222;
  margin: 0;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2; /* 3줄로 제한. 2줄로 바꿔도 좋습니다. */
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: break-all; /* 긴 영문/숫자 단어가 있을 경우 줄바꿈을 위함 */
}
.case-date{
  flex-shrink: 0;
  font-size: 12px;
  color: #888;
  background: #f4f7fb;
  border: 1px solid #e7eef7;
  padding: 4px 8px;
  border-radius: 8px;
}

/* 본문 3줄 클램프 */
.case-excerpt{
  margin: 2px 0 4px;
  color: #444;
  font-size: 14px;
  line-height: 1.7;
  flex-grow: 1;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ✅ 하이라이트 스타일 */
:deep(mark){
  background: #fff2a8;       /* 은은한 노란색 */
  padding: 0 2px;
  border-radius: 3px;
}

@media (max-width: 640px){
  .case-title{ font-size: 16px }
}
</style>
