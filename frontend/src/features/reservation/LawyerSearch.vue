<template>
  <div class="lawyer-page-container">
    <!-- 태그 필터 UI -->
    <!-- 검색 UI 통합 박스 -->
    <div class="search-row">

      <!-- 태그 필터 -->
      <div class="search-tags">
        <p class="tag-label">상담 분야로 찾기:
          <button class="reset-btn" @click="clearAll">초기화</button>
        </p>

        <button
          v-for="tag in tagMap"
          :key="tag.id"
          @click="toggleTag(tag.id)"
          :class="['tag-filter-btn', { selected: selectedTags.includes(tag.id) }]"
        >
          #{{ tag.name }}
        </button>

      </div>

      <!-- 이름 검색 영역 -->
      <div class="search-bar-full">
        <input
          v-model="searchQuery"
          placeholder="이름으로 검색하세요"
          @keyup.enter="applyFilters"
        />
        <button @click="applyFilters">
          →
        </button>
      </div>
    </div>


    <!-- 정렬 드롭다운 -->
    <div class="sort-dropdown-wrapper">
      <select class="sort-dropdown" v-model="sortOption" @change="applyFilters">
        <option value="name">이름순</option>
        <option value="many">상담많은순</option>
      </select>
    </div>

    <!-- 검색 결과 개수 -->
    <div class="search-summary">
      총 {{ lawyers.length }}명의 변호사가 검색되었습니다.
    </div>

    <!-- 카드 리스트 -->
    <div class="lawyer-card-list">
      <div class="lawyer-card" v-for="lawyer in lawyers" :key="lawyer.id">
        <img
          v-if="lawyer.photo"
          :src="`data:image/jpeg;base64,${lawyer.photo}`"
          alt="변호사 프로필 이미지"
          style="width: 150px; height: 150px; object-fit: cover"
        />
        <div class="lawyer-bottom">
          <p class="lawyer-name">{{ lawyer.name }} 변호사</p>
          <div class="lawyer-tags">
            <span
              class="tag"
              v-for="tag in lawyer.tags.slice(0, 2)"
              :key="tag"
            >
              #{{ getTagName(tag) }}
            </span>
            <button
              v-if="lawyer.tags.length > 2"
              @click="toggleShowTags(lawyer.id)"
              class="more-btn"
            >
              {{ expandedCards.includes(lawyer.id) ? '닫기' : '더보기' }}
            </button>
            <!-- 나머지 태그 (보일 때만 렌더링) -->
            <div v-if="expandedCards.includes(lawyer.id)">
              <span
                class="tag"
                v-for="tag in lawyer.tags.slice(2)"
                :key="tag + '-more'"
              >
                #{{ getTagName(tag) }}
              </span>
            </div>
          </div>
          <button class="reserve-btn" v-if="!isLawyer" @click="goToReservation(lawyer)">상담 예약하기</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/lib/axios'

const router = useRouter()

const lawyers = ref([])
const searchQuery = ref('')
const selectedTags = ref([])

const sortOption = ref('name');  // 기본값 '이름순'

const isLawyer = localStorage.getItem('user_type') === 'LAWYER' // JWT 파싱 or 저장된 사용자 정보 이용

const tagMap = [
  { id: 1, name: '형사 분야' },
  { id: 2, name: '교통·사고·보험' },
  { id: 3, name: '가사·가족' },
  { id: 4, name: '민사·계약·채권' },
  { id: 5, name: '파산·회생·채무조정' },
  { id: 6, name: '상속·증여' },
  { id: 7, name: '지식재산권' },
  { id: 8, name: '노동·고용' },
  { id: 9, name: '행정·조세' },
  { id: 10, name: '환경·공공' },
  { id: 11, name: '의료·생명·개인정보' },
  { id: 12, name: '금융·증권·기업' }
]

const getTagName = (id) => {
  const tag = tagMap.find(t => t.id === Number(id))
  return tag ? tag.name : '알 수 없음'
}
// 태그 선택 토글
const toggleTag = (tagId) => {
  if (selectedTags.value.includes(tagId)) {
    selectedTags.value = selectedTags.value.filter(id => id !== tagId)
  } else {
    selectedTags.value.push(tagId)
  }
  applyFilters()
}

// watch(searchQuery, () => {
//   applyFilters()
// })

const clearAll = () => {
  selectedTags.value = []
  searchQuery.value = ''
  applyFilters()
}

// 필터 적용 후 API 호출
const applyFilters = async () => {
  try {
    const params = new URLSearchParams()
    selectedTags.value.forEach(tagId => params.append('tags', tagId))
    if (searchQuery.value.trim() !== '') {
      params.append('search', searchQuery.value.trim())
    }

    const res = await axios.get(`/api/lawyers/list?${params.toString()}`)

    lawyers.value = res.data.map(l => ({
      ...l,
      id: String(l.lawyerId)
    }))
  } catch (err) {
    console.error('변호사 조회 실패:', err)
  }
}

onMounted(() => {
  applyFilters()
  window.scrollTo(0, 0)   // 페이지 진입 시 최상단 이동
})

const expandedCards = ref([])

const toggleShowTags = (lawyerId) => {
  if (expandedCards.value.includes(lawyerId)) {
    expandedCards.value = expandedCards.value.filter(id => id !== lawyerId)
  } else {
    expandedCards.value.push(lawyerId)
  }
}

const goToReservation = (lawyer) => {
  const userType = localStorage.getItem('user_type')
  if (!userType) {
    alert('로그인이 필요한 기능입니다. 로그인 페이지로 이동합니다.')
    router.push('/login') // 로그인 라우트 이름에 맞게 수정
    return
  }
  router.push({ name: 'DetailReservation', params: { id: lawyer.id } })
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

.search-row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 12px;
  margin-top: 120px;
}


/* 태그 영역 */
.search-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.tag-label {
  width: 100%;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
  display: flex;               /* ✅ Flex로 수평 정렬 */
  align-items: center;
  font-size: 16px;
  outline: none;
  color: #888;
}


.tag-filter-btn.selected {
  background-color: #1d2b50;
  color: white;
  border: none;
}

/* 이름 검색 input */
.search-bar-full {
  display: flex;
  align-items: center;
  border: 1px solid #ccc;
  border-radius: 12px;
  padding: 12px 16px;
  width: 100%;
  max-width: 500px;
  background-color: white;
  transition: border-color 0.2s ease;
}

.search-bar-full:hover {
  border-color: #007bff;  /* 파란색 강조 */
}

.search-bar-full input {
  flex: 1;
  border: none;
  background-color: transparent;
  font-size: 16px;
  outline: none;
  color: #333;
}

.search-bar-full input::placeholder {
  color: #888;
}

.search-bar-full button {
  border: none;
  background: none;
  cursor: pointer;
  font-size: 18px;
  color: #007bff;
  transition: transform 0.2s ease;
}

.search-bar-full button:hover {
  transform: scale(1.1);
}


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
