<template>
  <div>
    <input v-model="searchQuery" placeholder="이름 or 상담 분야" />
    <div v-for="lawyer in filteredLawyers" :key="lawyer.id">
      <div>
        <img :src="lawyer.profile_image" />
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const lawyers = ref([])
const searchQuery = ref('')
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

const fetchLawyers = async () => {
  const res = await axios.get('/api/admin/lawyers/list')
  lawyers.value = res.data
}

onMounted(fetchLawyers)

const filteredLawyers = computed(() =>
  lawyers.value.filter(l =>
    l.name.includes(searchQuery.value) || l.tags.some(tag => tag.includes(searchQuery.value))
  )
)

const goToReservation = (lawyer) => {
  const userType = localStorage.getItem('user_type')
  if (!userType) {
    alert('로그인이 필요한 기능입니다. 로그인 페이지로 이동합니다.')
    router.push({ name: 'UserLogin' }) // 로그인 라우트 이름에 맞게 수정
    return
  }
  router.push({ name: 'DetailReservation', params: { id: lawyer.id } })
}
</script>
