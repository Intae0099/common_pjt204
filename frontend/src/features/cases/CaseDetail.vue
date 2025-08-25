<template>
  <CaseLayout>
    <LayoutDefault>
    <div class="back-button" @click="goBack">
        <ChevronLeftIcon class="chevron-icon" />
        <span>이전</span>
    </div>


    <div v-if="isLoading" class="status-message"><p>판례 정보를 불러오는 중입니다...</p></div>
    <div v-else-if="error" class="status-message error"><p>{{ error }}</p></div>

    <section v-else-if="caseData" class="detail-container">
      <header class="title-block">
        <h1 class="title">{{ caseData.title }}</h1>
      </header>

      <section class="meta-card">
        <div class="meta-grid">
          <div class="meta-item">
            <span class="meta-label">사건번호</span>
            <span class="meta-value">{{ caseData.caseId || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">사건종류</span>
            <span class="meta-value badge">{{ caseData.category || '-' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">선고일자</span>
            <time class="meta-value">{{ caseData.decisionDate || '-' }}</time>
          </div>
        </div>
      </section>

      <section class="content-card" v-if="caseData.statutes">
        <h2 class="section-title">참조 법령 · 조문</h2>
        <div class="richtext" v-html="caseData.statutes"></div>
      </section>

      <section class="content-card" v-if="caseData.issue">
        <h2 class="section-title">판시사항</h2>
        <div class="richtext" v-html="caseData.issue"></div>
      </section>

      <section class="content-card" v-if="caseData.summary">
        <h2 class="section-title">판결요지</h2>
        <div class="richtext" v-html="caseData.summary"></div>
      </section>

      <section class="content-card" v-if="caseData.fullText">
        <h2 class="section-title">판례전문</h2>
        <div class="richtext" v-html="caseData.fullText"></div>
      </section>

      <div class="bottom-actions">
        <button class="to-list" @click="goBack">목록으로</button>
        <button class="to-top" @click="scrollToTop">맨 위로 ↑</button>

      </div>
    </section>

    <div v-else class="status-message"><p>판례 정보를 불러오는 중입니다...</p></div>
    </LayoutDefault>
  </CaseLayout>
</template>

<script setup>
import CaseLayout from '@/components/layout/CaseLayout.vue'
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fastapiApiClient } from '@/lib/axios'
import LayoutDefault from '@/components/layout/LayoutDefault.vue'
import { ChevronLeftIcon } from '@heroicons/vue/24/solid'

const route = useRoute()
const router = useRouter()

const caseData = ref(null)
const isLoading = ref(true)
const error = ref(null)

const goBack = () => router.go(-1)

/* ✅ 맨 위로 스크롤 함수 */
const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(async () => {
  const precId = route.params.id
  if (!precId) {
    error.value = '잘못된 접근입니다. 판례 ID가 없습니다.'
    isLoading.value = false
    return
  }
  try {
    isLoading.value = true
    const { data } = await fastapiApiClient.get(`/cases/${precId}`)
    if (data.success) {
      caseData.value = data.data
    } else {
      throw new Error(data.error?.message || '오류')
    }
  } catch (err) {
    console.error(err)
    error.value = err.response?.data?.error?.message || '정보를 불러오는 데 실패했습니다.'
  } finally {
    isLoading.value = false
  }
})
</script>


<style scoped>
.back-button {
  margin-top: 10px;
  margin-bottom: 20px;
  margin-left: -10px;
  font-size: 1rem;
  color: #6c9bcf;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  width: 80px;
  transition: color 0.2s ease-in-out;
}

.back-button:hover {
  color: #cfcfcf;
}
.chevron-icon {
  width: 20px;
  height: 20px;
}



/* 상단 바 */
.detail-topbar{
  max-width: 980px; margin: 24px auto 10px; display:flex; align-items:center; gap:10px;
}

/* 컨테이너 */
.detail-container{ max-width:980px; margin: 0 auto 60px; }
.title-block{
  position:relative; padding:18px 22px 10px 22px; margin-bottom:12px; border-left:4px solid #6c9bcf;
}
.title{ margin-bottom:10px; font-size:24px; line-height:1.5; font-weight:800; color:#333333; word-break: keep-all; }

/* 메타 카드 */
.meta-card{
  border:1px solid #cfcfcf; border-radius:15px; background:#fff; padding:16px 18px; margin-bottom:16px;
}
.meta-grid{
  display:grid; grid-template-columns: 1fr 1fr 1fr; gap:20px;
}
.meta-item{ display:flex; flex-direction:column; gap:6px; }
.meta-label{ font-size:12px; color:#888; }
.meta-value{ font-size:14px; color:#333333; }
.badge{
  width: 200px; display:inline-block; padding:4px 30px; border:1px solid #e7eef7; background:#f4f7fb; border-radius:10px; color:#355a88;
}

/* 콘텐츠 카드 공통 */
.content-card{
  border:1px solid #cfcfcf; border-radius:16px; background:#fff; padding:20px 22px; margin-bottom:16px;
}
.section-title{
  margin:0 16px 10px 0; font-size:16px; font-weight:700; color:#333333; position:relative;
}
.section-title::after{
  content:''; display:block; width:28px; height:3px; border-radius:2px; background:#6c9bcf; margin-top:6px;
}

/* 본문 리치텍스트 가독성 */
.richtext{
  color:#333333; font-size:15px; line-height:1.85;white-space: pre-line;
}
.richtext :is(p, li){ margin: 8px 0; }
.richtext br{ content:''; display:block; margin-bottom:6px; }
.richtext b, .richtext strong{ font-weight:700; }
.richtext u{ text-underline-offset:2px; }
.richtext a{ color:#2b6cb0; text-decoration:underline; }

/* 하단 동작 */
.bottom-actions{ display:flex; justify-content:flex-end; gap:8px; margin-top:10px; }
.to-list{
  appearance: none;
  height: 30px;
  padding: 0 1rem;
  border: 1px solid #cfcfcf;
  border-radius: 15px;
  font-size: 15px;
  color:  #888;
  background-color: #fff;
}

.to-top{
  border:none; background:#fff; color: #6c9bcf; padding: 0 2.5rem 0 1rem; cursor:pointer;
}
.to-top:hover{ color:#cfcfcf; }

/* 상태 */
.status-message{ text-align:center; margin:40px 0; color:#888 }
.error{ color:#d33 }

/* 반응형 */
@media (max-width: 1024px){
  .meta-grid{ grid-template-columns: 1fr 1fr; }
}
@media (max-width: 640px){
  .detail-topbar{ margin-top: 12px; }
  .title{ font-size:20px; }
  .meta-grid{ grid-template-columns: 1fr; }
  .content-card{ padding:16px; }
}
</style>
