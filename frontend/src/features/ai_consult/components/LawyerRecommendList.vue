<template>
  <div>
    <h2>당신에게 적합한 변호사 추천</h2>
    <p>AI가 분석한 결과를 바탕으로 변호사를 추천합니다.</p>

    <div v-if="Array.isArray(lawyers) && lawyers.length">
      <div
        v-for="lawyer in lawyers"
        :key="lawyer.lawyerId"
        class="lawyer-card"
      >
        <img
          v-if="lawyer.photo"
          :src="`data:image/jpeg;base64,${lawyer.photo}`"
          alt="변호사 이미지"
          class="lawyer-photo"
        />
        <div class="lawyer-info">
          <h3>{{ lawyer.name }}</h3>
          <p><strong>소개:</strong> {{ lawyer.introduction }}</p>
          <p><strong>시험 유형:</strong> {{ lawyer.exam }}</p>
          <p><strong>상담 횟수:</strong> {{ lawyer.consultationCount }}회</p>
          <p><strong>전문 분야:</strong> {{ lawyer.tags?.join(', ') }}</p>
          <p><strong>AI 적합도:</strong> {{ lawyer.matchScore }}</p>
          <!-- ✅ 바로 상담하기 버튼 -->
          <button
            v-if="userType !== 'LAWYER'"
            @click="goToReservation(lawyer.lawyerId)"
          >
            바로 상담하기
          </button>
        </div>
      </div>
    </div>

    <p v-else>추천 변호사를 불러오는 중입니다...</p>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const userType = localStorage.getItem('userType') // 예: 'LAWYER' 또는 'USER'


defineProps({
  lawyers: {
    type: Array,
    default: () => []
  }
})

const router = useRouter()

const goToReservation = (lawyerId) => {
  router.push({ name: 'DetailReservation', params: { id: lawyerId } })
}
</script>

<style scoped>
.lawyer-card {
  display: flex;
  gap: 1rem;
  border: 1px solid #ccc;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  align-items: flex-start;
}

.lawyer-photo {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
}

.lawyer-info p {
  margin: 0.25rem 0;
}
</style>
