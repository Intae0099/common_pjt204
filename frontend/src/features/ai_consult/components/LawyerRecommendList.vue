<template>
  <div class="recommend-list-wrapper">
    <h2 class="title">당신에게 적합한 변호사 추천</h2>
    <p class="desc">AI가 분석한 결과를 바탕으로 변호사를 추천합니다.</p>

    <div class="lawyer-cards">
      <div class="lawyer-card" v-for="lawyer in lawyers" :key="lawyer.id">
        <img class="profile-img" :src="lawyer.image" alt="변호사 이미지" />
        <h3 class="name">{{ lawyer.name }}</h3>
        <p class="specialty">전문 분야: {{ lawyer.specialty }}</p>
        <p class="intro">{{ lawyer.intro }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 실제 API 연동 전 임시 데이터
const lawyers = ref([
  {
    id: 1,
    name: '김지훈 변호사',
    specialty: '형사 사건',
    intro: '피해자와 피의자 모두의 입장을 이해하며 조력하는 변호사입니다.',
    image: 'https://via.placeholder.com/80x80'
  },
])
</script>

<style scoped>
.recommend-list-wrapper {
  margin-top: 40px;
  text-align: center;
}

.title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.desc {
  font-size: 14px;
  color: #777;
  margin-bottom: 24px;
}

.lawyer-cards {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
}

.lawyer-card {
  width: 220px;
}

/* 모바일: 카드 전체 너비 */
@media (max-width: 767px) {
  .lawyer-card {
    width: 100%;
    max-width: 90%;
  }
}


.profile-img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 12px;
}

.name {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 6px;
}

.specialty {
  font-size: 13px;
  color: #5a45ff;
  margin-bottom: 6px;
}

.intro {
  font-size: 13px;
  color: #555;
}
</style>
