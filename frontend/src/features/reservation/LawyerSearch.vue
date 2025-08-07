<template>
  <div class="lawyer-page-container">
    <!-- ▾ 필터 WRAPPER -------------------------------------------------- -->
    <div class="filter-wrapper">

      <!-- 헤더 : 대분류 / 소분류 / 검색창 + 토글 -->
      <div class="filter-header-row">
        <div class="filter-header-cells">
          <span class="header-cell">대분류</span>
          <span class="header-cell">소분류</span>
        </div>

        <!-- 검색창 (폭을 줄여 배치) -->
        <div class="search-box">
          <MagnifyingGlassIcon class="search-icon" />
          <input
            v-model="searchQuery"
            placeholder="변호사 이름을 검색해주세요."
            @keyup.enter="applyFilters"
          />
        </div>

        <button class="toggle-btn" @click="showFilters = !showFilters">
          <ChevronDownIcon
            :class="{ rotated: showFilters }"
            class="chevron-icon"
          />
        </button>
      </div>

      <!-- 펼쳐지는 상세 필터 (대분류 | 소분류 | 여백) -->
      <transition name="fade">
        <div v-if="showFilters" class="filter-table">
          <!-- 대분류 -->
          <div class="filter-col big-col">
            <ul class="list">
              <li
                v-for="c in CATEGORY_MAP"
                :key="c.catId"
                @click="selectCategory(c.catId)"
                :class="['list-item', { active: activeCatId === c.catId }]"
              >{{ c.title }}</li>
            </ul>
          </div>

          <!-- 소분류 -->
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

          <!-- 남은 공간(검색창 우측) -->
          <div class="filter-col filler"></div>
        </div>
      </transition>

      <!-- 선택된 태그 칩 -->
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

    <!-- ▼ 결과 / 정렬 / 카드 리스트 -------------------------------------------------- -->
    <div class="sort-dropdown-wrapper">
      <select class="sort-dropdown" v-model="sortOption" @change="applyFilters">
        <option value="name">이름순</option>
        <option value="many">상담많은순</option>
      </select>
    </div>

    <div class="search-summary">총 {{ lawyers.length }}명의 변호사가 검색되었습니다.</div>

    <div class="lawyer-card-list">
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/lib/axios'
import { TAG_MAP } from '@/constants/lawyerTags'
import { MagnifyingGlassIcon, ChevronDownIcon, XMarkIcon } from '@heroicons/vue/24/solid'

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
  applyFilters()
}

const clearAll = ()=>{ selectedTags.value=[]; searchQuery.value=''; applyFilters() }

const applyFilters = async()=>{
  try{
    const params=new URLSearchParams()
    selectedTags.value.forEach(id=>params.append('tags',id))
    if(searchQuery.value.trim()) params.append('search',searchQuery.value.trim())
    if(sortOption.value) params.append('sort',sortOption.value)

    const { data } = await axios.get(`/api/lawyers/list?${params.toString()}`)
    lawyers.value=data.map(l=>({...l,id:String(l.lawyerId)}))
  }catch(e){ console.error('변호사 조회 실패',e) }
}

onMounted(()=>{ applyFilters(); window.scrollTo(0,0) })

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
.lawyer-page-container {
  padding-top: 60px; /* navbar 높이 + 여유 공간 */
  /* 기존 padding 유지 */
  padding-left: 20px;
  padding-right: 20px;
  max-width: 1200px;
  margin: 0 auto;
}


/* wrapper + 헤더 행 */
.filter-wrapper{border:1px solid #e5e5e5;font-size:15px}
.filter-header-row{display:flex;align-items:center;border-bottom:1px solid #e5e5e5}
.filter-header-cells{display:flex;gap:1px;flex:1}
.header-cell{flex:1;padding:18px;font-weight:600;text-align:center;border-right:1px solid #e5e5e5}

/* 검색창 + 토글 버튼 */
.search-box{flex:1.5;display:flex;align-items:center;gap:8px;padding:0 16px}
.search-box{max-width:300px}

.search-icon{width:21px}
.search-box input{border:none;outline:none;width:100%;font-size:15px}
.toggle-btn{width:68px;background:#1d2b50;color:#fff;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center}
.chevron-icon{width:22px;height:22px;transition:transform .25s}
.chevron-icon.rotated{transform:rotate(180deg)}
.toggle-btn:hover{background:#33416c}

/* 선택 태그 칩 영역 */
.selected-tags{display:flex;align-items:center;flex-wrap:wrap;gap:8px;padding:14px 18px;border-top:1px solid #e5e5e5}
.selected-tag{background:#1d2b50;color:#fff;cursor:pointer;display:flex;align-items:center;gap:4px}
.remove-icon{width:12px}

.fade-enter-active,.fade-leave-active{transition:all .25s ease}
.fade-enter-from,.fade-leave-to{opacity:0;transform:translateY(-8px)}


/* 3열 비율 고정: 220px | 260px | 나머지 */
.filter-table{
  display:flex;
}

.filter-col.big-col{flex:0 0 220px}   /* 대분류 */
.filter-col.sub-col{flex:0 0 260px}   /* 소분류 */
.search-dummy{flex:1}

/* 여기까지가 태그 관련 */
/* 대분류소분류 스크롤 줄이기 */
.big-list,.sub-list{
  max-height:280px;        /* 헤더·패딩 감안해서 */
  overflow-y:auto;
}


/* radio 커스텀 – 체크박스와 동일한 비주얼 */
.check-label input[type="radio"],
.check-label input[type="checkbox"]{
  appearance:none;width:20px;height:20px;border:1px solid #bbb;border-radius:3px;
  position:relative;cursor:pointer
}
.check-label input:checked{background:#1d2b50;border-color:#1d2b50}
.check-label input:checked::after{
  content:"";position:absolute;left:5px;top:2px;width:6px;height:11px;
  border:2px solid #fff;border-top:none;border-left:none;transform:rotate(45deg)
}

/* ── 리스트 공통 ─────────────────────────── */
.list{margin:0;padding:0;list-style:none;max-height:300px;overflow-y:auto}
.list-item{
  padding:12px 16px;border-bottom:1px solid #e5e5e5;cursor:pointer;
  transition:background .15s;color:#333
}
.list-item:hover{background:#f1f1f1}

/* 대분류 선택 시 */
.list-item.active{
  background:#1d2b50;color:#fff;font-weight:600
}

/* 소분류 다중 선택 시 */
.list-item.selected{
  background:#33416c;color:#fff;font-weight:600
}

/* 선택 태그 칩 영역 */
.selected-tags{
  display:flex;flex-wrap:wrap;gap:8px;padding:14px 18px;border-top:1px solid #e5e5e5
}
.selected-tag{
  background:#1d2b50;color:#fff;border-radius:16px;padding:4px 10px;
  display:flex;align-items:center;gap:4px;cursor:pointer
}
.remove-icon{width:12px}

.big-list::-webkit-scrollbar,
.sub-list::-webkit-scrollbar{width:6px}
.big-list::-webkit-scrollbar-thumb,
.sub-list::-webkit-scrollbar-thumb{background:#9a9a9a;border-radius:3px}

/* 기존 toggle·header·search-box·fade 애니메이션 클래스는 그대로 사용 */


.reset-btn {
  margin-left: auto;           /* ✅ 오른쪽으로 밀기 */
  background-color: transparent;
  border: 1px solid #b4c3d1;
  border-radius: 15px;
  padding: 6px 10px;
  font-size: 12px;
  color: #333;
  cursor: pointer;
  height: 30px;
  transition: background-color 0.2s ease;
}

.reset-btn:hover {
  background-color: #e0e0e0;
}

.search-summary {
  text-align: right;
  font-size: 14px;
  color: #666;
  margin-top: 20px;
  margin-bottom: 10px;
  padding-right: 10px;
}

.lawyer-card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 30px;
  margin-top: 40px;
}

/* 개별 카드 */
.lawyer-card {
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 360px; /* 필요시 높이 조절 */
}

.lawyer-img {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 15px;
  margin-left: auto;
  margin-right: auto;
}

.lawyer-bottom {
  margin-top: auto;  /* 가장 하단으로 밀어냄 */
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 이름 */
.lawyer-name {
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 10px;
}

/* 태그 리스트 */
.lawyer-tags {
  margin-bottom: 15px;
}

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

/* 상담 예약 버튼 */
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

.reserve-btn:hover {
  background-color: #394b85;
}

.tag-filter-btn {
  background-color: #f3f3f3;
  border: 1px solid #d0d0d0;
  border-radius: 20px;
  padding: 6px 12px;
  margin: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tag-filter-btn:hover {
  background-color: #e0e0e0;
}

.tag-filter-btn.selected {
  background-color: #1d2b50;
  color: white;
  border: none;
}

/* 정렬 드롭다운 */
/* 드롭다운 wrapper: 오른쪽 정렬 */
.sort-dropdown-wrapper {
  display: flex;
  justify-content: flex-end;
  margin: 10px 0;
}

/* 드롭다운 select 스타일 */
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
</style>
