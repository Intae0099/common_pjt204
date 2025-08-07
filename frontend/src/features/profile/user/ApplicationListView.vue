<!-- src/views/ApplicationListView.vue -->
<template>
  <div v-if="loading" class="page-container loading-container">
    <p>상담 내역을 불러오는 중입니다...</p>
  </div>

  <div v-else-if="items.length === 0" class="page-container loading-container">
     <p>표시할 상담 내역이 없습니다.</p>
     <button @click="$router.back()" class="back-btn">돌아가기</button>
  </div>

  <div v-else class="page-container">
    <!-- 이전 항목으로 가는 버튼 -->
    <button @click="prevItem" class="nav-arrow left">
      <ChevronLeftIcon class="nav-icon" />
    </button>

    <!-- 컨텐츠 영역 (애니메이션 적용) -->
    <div class="content-window">
      <transition :name="transitionName" mode="out-in">
        <div class="content-wrapper" :key="currentIndex">
          <button @click="$router.back()" class="close-btn">
            <XMarkIcon class="x-icon" />
          </button>
          <div class="scroll-area">
            <form class="consult-form">
              <!-- 사건 제목 -->
              <input
                type="text"
                :value="currentItem.title"
                readonly
                class="readonly-input-title"
              />
              <!-- 한 줄 요약 -->
              <div v-if="currentItem.summary" class="form-group">
                <label>한 줄 요약</label>
                <input
                  type="text"
                  :value="currentItem.summary"
                  readonly
                  class="readonly-input"
                />
              </div>

              <!-- 사건 개요 -->
              <div v-if="currentItem.content" class="form-group scrollable-group">
                <label>사건 개요</label>
                <textarea
                  class="scrollable-content"
                  :value="currentItem.content"
                  readonly
                ></textarea>
              </div>

              <!-- 원하는 결과 -->
              <div v-if="currentItem.outcome" class="form-group scrollable-group">
                <label>원하는 결과</label>
                <textarea
                  class="scrollable-content"
                  :value="currentItem.outcome"
                  readonly
                ></textarea>
              </div>

              <!-- 불리한 점 -->
              <div v-if="currentItem.disadvantage" class="form-group scrollable-group">
                <label>사건에서 불리한 점</label>
                <textarea
                  class="scrollable-content"
                  :value="currentItem.disadvantage"
                  readonly
                ></textarea>
              </div>

              <!-- 궁금한 점 (API 데이터 구조에 맞게 수정) -->
              <div v-if="currentItem.recommendedQuestions?.length" class="form-group scrollable-group">
                <label>변호사에게 궁금한 점</label>
                <textarea
                  class="scrollable-content"
                  :value="currentItem.recommendedQuestions.join('\n')"
                  readonly
                ></textarea>
              </div>
            </form>
          </div>
        </div>
      </transition>
    </div>

    <!-- 다음 항목으로 가는 버튼 -->
    <button @click="nextItem" class="nav-arrow right">
      <ChevronRightIcon class="nav-icon" />
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/lib/axios'
import { ChevronLeftIcon, ChevronRightIcon, XMarkIcon } from '@heroicons/vue/24/solid'

const route = useRoute()
const router = useRouter()

const items = ref([])
const loading = ref(true)
const currentIndex = ref(0)
const transitionName = ref('slide-next')

// API 응답 데이터를 프론트엔드 모델에 맞게 변환하는 함수
const transformApiData = (apiList) => {
  return apiList.map(item => ({
    ...item,
    // API의 recommendedQuestion 객체를 recommendedQuestions 배열로 변환
    recommendedQuestions: Object.values(item.recommendedQuestions || {})
  }))
}

onMounted(async () => {
  try {
    const res = await axios.get('/api/applications/me')
    if (res.data.success) {
      const apiList = res.data.data.applicationList;
      // API 데이터를 프론트엔드 모델에 맞게 변환하여 저장
      items.value = transformApiData(apiList);

      // URL 파라미터에서 초기 ID를 가져옴
      const initialId = Number(route.params.id)

      // 해당 ID를 가진 항목의 인덱스를 찾음
      const initialIndex = items.value.findIndex(item => item.applicationId === initialId)

      // 찾았으면 해당 인덱스로, 못찾았으면 0번 인덱스로 설정
      currentIndex.value = initialIndex !== -1 ? initialIndex : 0
    } else {
      throw new Error(res.data.message)
    }
  } catch (error) {
    console.error('상담신청서 목록 로딩 실패:', error)
    items.value = [] // 에러 발생 시 빈 배열로 설정
  } finally {
    loading.value = false
  }
})

const currentItem = computed(() => {
  // items 배열이 비어있지 않을 때만 현재 아이템 반환
  return items.value.length > 0 ? items.value[currentIndex.value] : null
})

const nextItem = () => {
  if (items.value.length === 0) return;
  transitionName.value = 'slide-next'
  currentIndex.value = (currentIndex.value + 1) % items.value.length
}

const prevItem = () => {
    if (items.value.length === 0) return;
  transitionName.value = 'slide-prev'
  currentIndex.value = (currentIndex.value - 1 + items.value.length) % items.value.length
}
</script>

<style scoped>
/* 페이지 및 로딩 컨테이너 */
.page-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 100vh;
  background-color: #e9f5ff;
  padding: 2rem;
  box-sizing: border-box;
}
.loading-container {
  flex-direction: column;
  color: #555;
  font-size: 1.2rem;
}
.back-btn {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  cursor: pointer;
  background-color: white;
}

/* 컨텐츠 창 */
.content-window {
  width: 800px;
  max-width: 100%;
  position: relative;
  overflow: hidden;
}
.content-wrapper {
  position: relative;
  background: #F7FCFF;
  border-radius: 12px;
  padding: 3rem 0;
  max-height: 90vh;
  width: 100%;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

/* 닫기 버튼 */
.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  cursor: pointer;
  z-index: 10;
}
.x-icon {
  width: 24px;
  height: 24px;
  color: #B9D0DF;
  transition: transform 0.2s ease, color 0.2s ease;
}
.close-btn:hover .x-icon {
  transform: scale(1.2);
  color: #7ca0c3;
}


/* 스크롤 영역 */
.scroll-area {
  overflow-y: auto;
  max-height: calc(90vh - 6rem);
  padding: 0 1rem 0 2rem;
}

/* 폼 스타일 */
.consult-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding-right: 1.5rem;
}

/* ... (나머지 스타일은 이전 답변과 동일하게 유지) ... */
.scroll-area::-webkit-scrollbar, .scrollable-content::-webkit-scrollbar { width: 6px; }
.scroll-area::-webkit-scrollbar-thumb, .scrollable-content::-webkit-scrollbar-thumb { background-color: #d4e1ed; border-radius: 3px; }
.scroll-area::-webkit-scrollbar-track, .scrollable-content::-webkit-scrollbar-track { background-color: transparent; }
.form-group { display: flex; flex-direction: column; gap: 0.5rem; }
input, textarea { padding: 0.75rem; border: 1px solid #B9D0DF; border-radius: 8px; font-size: 1rem; resize: none; color: #334155; }
.readonly-input { background-color: #fff; }
.readonly-input-title{ border: none; padding: 0; font-size: 1.5rem; font-weight: bold; background-color: transparent; }
.scrollable-group { display: flex; flex-direction: column; gap: 0.5rem; }
.scrollable-content { min-height: 100px; max-height: 150px; overflow-y: auto; background-color: #fff; border: 1px solid #B9D0DF; border-radius: 8px; padding: 0.75rem; font-size: 1rem; line-height: 1.5; }
input:focus, textarea:focus { outline: none; border-color: #B9D0DF; box-shadow: none; }
.nav-arrow { background: none; border: none; cursor: pointer; padding: 1rem; margin: 0 1rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: background-color 0.2s ease, transform 0.2s ease; }
.nav-arrow:hover { background-color: rgba(255, 255, 255, 0.5); transform: scale(1.1); }
.nav-icon { width: 32px; height: 32px; color: #7ca0c3; }
.slide-next-enter-active, .slide-next-leave-active, .slide-prev-enter-active, .slide-prev-leave-active { transition: transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1); }
.slide-next-enter-from { transform: translateX(100%); }
.slide-next-leave-to { transform: translateX(-100%); }
.slide-prev-enter-from { transform: translateX(-100%); }
.slide-prev-leave-to { transform: translateX(100%); }
</style>
