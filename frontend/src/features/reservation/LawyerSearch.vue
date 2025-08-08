<template>
  <LawyerSearchLayout>
    <LayoutDefault>
      <div class="lawyer-page-container">

        <div class="filter-wrapper">
          <div class="filter-header">
            <span class="header-title">태그를 선택해주세요.</span>
            <button class="toggle-btn" @click="showFilters = !showFilters">
              <ChevronDownIcon :class="{ rotated: showFilters }" class="chevron-icon" />
            </button>
          </div>

          <div class="search-box">
            <MagnifyingGlassIcon class="search-icon" />
            <input
              v-model="searchQuery"
              placeholder="변호사 이름을 검색해주세요."
              @keyup.enter="applyFilters"
            />
            <button class="search-btn" @click="applyFilters">검색</button>
          </div>

          <transition name="fade">
            <div v-if="showFilters" class="filter-content">
              <div class="filter-table">
                <div class="filter-col big-col">
                  <ul class="list">
                    <li
                      v-for="c in CATEGORY_MAP"
                      :key="c.catId"
                      @click="selectCategory(c.catId)"
                      :class="['list-item', { active: activeCatId === c.catId }]"
                    >{{ c.title }}
                    <ChevronRightIcon class="arrow-icon" /></li>

                  </ul>
                </div>

                <div class="filter-col sub-col">
                  <ul class="list">
                    <li
                      v-for="tag in tagsOfActiveCategory"
                      :key="tag.id"
                      @click="toggleTag(tag.id)"
                      :class="['list-item', { selected: selectedTags.includes(tag.id) }]"
                    >{{ tag.name }}</li>
                  </ul>
                </div>
              </div>

              <div v-if="selectedTags.length" class="selected-tags">
                <span
                  v-for="id in selectedTags"
                  :key="id"
                  class="tag selected-tag"
                  @click="toggleTag(id)"
                >#{{ getTagName(id) }} <XMarkIcon class="remove-icon" /></span>
                <button class="reset-btn" @click="clearAll">모두 해제</button>
              </div>
            </div>
          </transition>
        </div>

        <div class="sort-dropdown-wrapper">
          <select class="sort-dropdown" v-model="sortOption" @change="applyFilters">
            <option value="name">이름순</option>
            <option value="many">상담많은순</option>
          </select>
        </div>

        <div class="search-summary">총 {{ lawyers.length }}명의 변호사가 검색되었습니다.</div>

        <div class="lawyer-card-list" id="lawyer-results">
          <div class="lawyer-card" v-for="lawyer in lawyers" :key="lawyer.id">
            <img v-if="lawyer.photo" :src="`data:image/jpeg;base64,${lawyer.photo}`" alt="프로필" />
            <div class="lawyer-bottom">
              <p class="lawyer-name">{{ lawyer.name }} 변호사</p>
              <div class="lawyer-tags">
                <span class="tag" v-for="tag in lawyer.tags.slice(0,2)" :key="tag">#{{ getTagName(tag) }}</span>
                <button v-if="lawyer.tags.length>2" @click="toggleShowTags(lawyer.id)" class="more-btn">
                  {{ expandedCards.includes(lawyer.id) ? '닫기' : '더보기' }}
                </button>
                <div v-if="expandedCards.includes(lawyer.id)">
                  <span class="tag" v-for="tag in lawyer.tags.slice(2)" :key="tag+'-m'">#{{ getTagName(tag) }}</span>
                </div>
              </div>
              <button class="reserve-btn" v-if="!isLawyer" @click="goToReservation(lawyer)">상담 예약하기</button>
            </div>
          </div>
        </div>
      </div>
    </LayoutDefault>
  </LawyerSearchLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/lib/axios'
import { TAG_MAP } from '@/constants/lawyerTags'
import { MagnifyingGlassIcon, ChevronDownIcon, XMarkIcon, ChevronRightIcon } from '@heroicons/vue/24/solid'
import LawyerSearchLayout from '@/components/layout/LawyerSearchLayout.vue';
import LayoutDefault from '@/components/layout/LayoutDefault.vue'

/* ----- 상태 ----- */
const router       = useRouter()
const showFilters  = ref(false)
const lawyers      = ref([])
const searchQuery  = ref('')
const sortOption   = ref('name')
const selectedTags = ref([])

/* 대분류 데이터 */
const CATEGORY_MAP = [
  { catId: 1, title: '형사 분야',          tagIds: [1,2,3,4,5,6] },
  { catId: 2, title: '교통·사고·보험',      tagIds: [7,8,9] },
  { catId: 3, title: '가사·가족',          tagIds: [10,11,12,13,14] },
  { catId: 4, title: '민사·계약·채권',      tagIds: [15,16,17,18] },
  { catId: 5, title: '파산·회생·채무조정',    tagIds: [19,20,21] },
  { catId: 6, title: '상속·증여',          tagIds: [22,23,24] },
  { catId: 7, title: '지식재산권',          tagIds: [25,26,27,28] },
  { catId: 8, title: '노동·고용',          tagIds: [29,30,31,32] },
  { catId: 9, title: '행정·조세',          tagIds: [33,34,35,36] },
  { catId:10, title: '의료·생명·개인정보',    tagIds: [37,38,39,40] },
  { catId:11, title: '환경·공공',          tagIds: [41,42,43] },
  { catId:12, title: '금융·증권·기업',      tagIds: [44,45,46,47,48] },
]

const activeCatId = ref(CATEGORY_MAP[0].catId)

/* 계산된 소분류 */
const tagsOfActiveCategory = computed(()=>{
  const ids=CATEGORY_MAP.find(c=>c.catId===activeCatId.value)?.tagIds||[]
  return TAG_MAP.filter(t=>ids.includes(t.id))
})

/* ───── 함수들 ───── */
const getTagName = (id)=>TAG_MAP.find(t=>t.id===id)?.name||''

const selectCategory = (id)=>{ activeCatId.value=id }

const toggleTag = (id)=>{
  selectedTags.value.includes(id)
    ?selectedTags.value=selectedTags.value.filter(t=>t!==id)
    :selectedTags.value.push(id)
  applyFilters(false)
}

const clearAll = ()=>{ selectedTags.value=[]; searchQuery.value=''; applyFilters(false) }

const applyFilters = async (shouldScroll = true) =>{
  try{
    const params=new URLSearchParams()
    selectedTags.value.forEach(id=>params.append('tags',id))
    if(searchQuery.value.trim()) params.append('search',searchQuery.value.trim())
    if(sortOption.value) params.append('sort',sortOption.value)

    const { data } = await axios.get(`/api/lawyers/list?${params.toString()}`)
    lawyers.value=data.map(l=>({...l,id:String(l.lawyerId)}))

    if (shouldScroll) {
      const resultsElement = document.getElementById('lawyer-results')
      if (resultsElement) {
        resultsElement.scrollIntoView({ behavior: 'smooth' })
      }
    }
  }catch(e){ console.error('변호사 조회 실패',e) }
}

onMounted(()=>{ applyFilters(false);
  window.scrollTo(0, 0);})

/* 카드 관련 */
const expandedCards = ref([])
const isLawyer = localStorage.getItem('userType')==='LAWYER'
const toggleShowTags = id => expandedCards.value.includes(id)
  ? expandedCards.value=expandedCards.value.filter(i=>i!==id)
  : expandedCards.value.push(id)
const goToReservation = lawyer =>{
  if(!localStorage.getItem('userType')){
    alert('로그인이 필요한 기능입니다.');
    router.push('/login')
    return
  }
  router.push({ name:'DetailReservation', params:{ id: lawyer.id } })
}
</script>

<style scoped>
/* ── Universal Layout ─────────────────────────── */
.lawyer-page-container {
  padding: 0px 0px 20px;
  max-width: 1200px;
  margin: 60px auto;
}

/* ── Filter & Search Section ─────────────────────────── */
.filter-wrapper {
  border: 1px solid #e5e5e5;
  font-size: 15px;
  margin-top: -100px;
  padding-top: -100px;
  /* 반응형 레이아웃을 위한 Grid 설정 */
  display: grid;
  grid-template-columns: 2fr 1fr; /* 2열: 남은공간 | 자동너비 */
  grid-template-areas:
    "header search"
    "content content";
  align-items: center;
}

.filter-header { grid-area: header; display: flex; align-items: center; padding: 20px 20px; }
.search-box { grid-area: search; display: flex; align-items: center; padding: 10 30px; gap:10px; }
.filter-content { grid-area: content; border-top: 1px solid #e5e5e5;}

.header-title { font-weight: 400; color:#888}

.toggle-btn {
  background: transparent; /* 배경을 투명하게 변경 */
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 14px;
}

.chevron-icon {
  width: 22px;
  height: 22px;
  color: #5d5d5d;
  transition: transform 0.25s;
}
.chevron-icon.rotated { transform: rotate(180deg); }

.search-icon { width: 21px; color: #888; }
.search-box input {
  border: none;
  border-bottom: 1px solid #ccc;
  outline: none;
  width: 100%;
  min-width: 200px;
  font-size: 15px;
  padding: 8px 4px;
  margin: 0 12px;
  writing-mode: initial;
}
.search-box input:focus { border-bottom-color: #1d2b50; }
.search-btn {
  background: #1d2b50;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-weight: 400;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  writing-mode: horizontal-tb;
  white-space: nowrap;
  margin-right: 10px;
}
.search-btn:hover { background-color: #394b85; }

/* ── Filter Content (Table & Tags) ──────────────────────── */
.fade-enter-active, .fade-leave-active { transition: all 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-8px); }

.filter-table { display: flex; }
.filter-col { flex: 1; }
.big-col {
  flex: 0 0 300px; /* 컬럼이 늘어나거나 줄어들지 않고, 기본 너비를 220px로 고정 */
  border-right: 1px solid #e5e5e5;
}
.sub-col {
  flex: 0 0 350px; /* 소분류는 조금 더 넓게 260px로 고정 */
}

.list {
  margin: 0;
  padding: 0;
  list-style: none;
  max-height: 300px;
  overflow-y: auto;
}
.list-item {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e5e5;
  cursor: pointer;
  transition: background 0.15s;
  color: #333;
  position: relative; /* 화살표를 이 요소 기준으로 위치시키기 위해 추가 */
  display: flex;
  justify-content: space-between; /* 텍스트와 화살표를 양쪽으로 분리 */
  align-items: center;
}

.arrow-icon {
  width: 18px; /* 아이콘 크기 */
  height: 18px;
  color: #ccc; /* 기본 회색 */
  transition: transform 0.25s, color 0.25s; /* 부드러운 전환 효과 */
}

/* hover 상태일 때 스타일 */
.list-item:hover .arrow-icon {
  color: #fff; /* 호버 시 흰색으로 변경 */
  transform: rotate(0); /* (선택사항) 호버 시에도 오른쪽을 가리키도록 원래대로 */
}



.list-item:hover { background: #f1f1f1; }
.list-item:last-child { border-bottom: none; }
.list-item.active { background: #1d2b50; color: #fff; font-weight: 600; }
.list-item.selected { background: #33416c; color: #fff; font-weight: 600; }

.list::-webkit-scrollbar { width: 6px; }
.list::-webkit-scrollbar-thumb { background: #9a9a9a; border-radius: 3px; }

/* 선택된 태그 칩 */
.selected-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding: 14px 18px;
  border-top: 1px solid #e5e5e5;
}
.selected-tag {
  background: #1d2b50;
  color: #fff;
  border-radius: 16px;
  padding: 4px 10px;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  font-size: 14px;
}
.remove-icon { width: 12px; }
.reset-btn {
  margin-left: auto;
  background-color: transparent;
  border: 1px solid #b4c3d1;
  border-radius: 15px;
  padding: 6px 12px;
  font-size: 13px;
  color: #333;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.reset-btn:hover { background-color: #e9e9e9; }


/* ── Result & Sort Section ─────────────────────────── */
.sort-dropdown-wrapper {
  display: flex;
  justify-content: flex-end;
  margin: 20px 0 10px;
}
.sort-dropdown {
  appearance: none;
  height: 30px;
  padding: 0 2.5rem 0 1rem;
  border: 1px solid #b4c3d1;
  border-radius: 15px;
  font-size: 12px;
  color: #333;
  background-image: url("data:image/svg+xml,%3Csvg fill='black' height='16' viewBox='0 0 24 24' width='16' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 12px;
}

.search-summary {
  text-align: right;
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
  padding-right: 10px;
}

/* ── Lawyer Card List ─────────────────────────────── */
.lawyer-card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 30px;
  margin-top: 20px;
}
.lawyer-card {
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 360px;
}
.lawyer-bottom {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.lawyer-name { font-weight: bold; font-size: 16px; margin-bottom: 10px; }
.lawyer-tags { margin-bottom: 15px; }
.tag {
  background-color: #f1f1f1;
  color: #333;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin: 2px;
  display: inline-block;
}
.more-btn {
  background: none;
  border: none;
  color: #007bff;
  font-size: 12px;
  cursor: pointer;
  margin-left: 4px;
  padding: 0;
  text-decoration: underline;
}
.reserve-btn {
  background-color: #1d2b50;
  color: white;
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  width: 100%;
  transition: background-color 0.2s ease;
}
.reserve-btn:hover { background-color: #394b85; }

/* ── Responsive Layout (Mobile) ─────────────────── */
@media (max-width: 768px) {
  .filter-wrapper {
    /* Grid 레이아웃을 1열로 변경하고, search를 맨 아래로 보냅니다. */
    grid-template-columns: 1fr;
    grid-template-areas:
      "header"
      "content"
      "search";
  }

  .filter-header {
    border-bottom: 1px solid #e5e5e5;
  }

  .filter-content {
    border-top: none; /* 모바일에서는 헤더의 border-bottom으로 대체 */
  }

  .filter-table {
    flex-direction: column;
  }
  .big-col {
    border-right: none;
  }
}

</style>
