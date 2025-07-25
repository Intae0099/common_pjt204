<template>
  <div>
    <input v-model="searchQuery" placeholder="이름 or 상담 분야" />
    <div v-for="lawyer in filteredLawyers" :key="lawyer.id">
      <div>
        <img :src="lawyer.profile_image" />
        <p>{{ lawyer.name }} 변호사</p>
        <div>
          <span v-for="tag in lawyer.tags" :key="tag">#{{ tag }}</span>
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

const isLawyer = localStorage.getItem('user_type') === 'lawyer' // JWT 파싱 or 저장된 사용자 정보 이용

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
  router.push({ name: 'DetailReservation', params: { id: lawyer.id } })
}
</script>
