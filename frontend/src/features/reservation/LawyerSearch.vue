<template>
  <div>
    <!-- 태그 필터 UI -->
    <div class="tag-filter-wrapper">
      <button
        v-for="tag in tagMap"
        :key="tag.id"
        @click="toggleTag(tag.id)"
        :class="{ selected: selectedTags.includes(tag.id) }"
      >
        #{{ tag.name }}
      </button>
    </div>

    <!-- 이름 검색창 -->
    <input
      v-model="searchQuery"
      placeholder="이름을 검색해주세요"
      @keyup.enter="applyFilters"
    />
    <!-- <button @click="applyFilters">
      🔍 검색
    </button> -->


    <div v-for="lawyer in lawyers" :key="lawyer.id">
      <div>
        <img
          v-if="lawyer.photo"
          :src="`data:image/jpeg;base64,${lawyer.photo}`"
          alt="변호사 프로필 이미지"
          style="width: 150px; height: 150px; object-fit: cover"
        />
        <p>{{ lawyer.name }} 변호사</p>
        <div>
          <span v-for="tag in lawyer.tags" :key="tag">#{{ getTagName(tag) }}</span>
        </div>
        <button v-if="!isLawyer" @click="goToReservation(lawyer)">상담 예약하기</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/lib/axios'

const lawyers = ref([])
const searchQuery = ref('')
const selectedTags = ref([])

const router = useRouter()

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

watch(searchQuery, () => {
  applyFilters()
})

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

onMounted(applyFilters)


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
.selected {
  background-color: #5A45FF;
  color: white;
  border-radius: 20px;
  padding: 5px 10px;
}

.tag-filter-wrapper {
  margin-top: 60px; /* NavBar 높이만큼 여백 확보 */
  position: relative;
  z-index: 10;  /* NavBar 아래로 내려왔기 때문에 클릭 OK */
}
</style>
