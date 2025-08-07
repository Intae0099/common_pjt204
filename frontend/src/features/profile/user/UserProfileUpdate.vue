<template>
  <div class="profile-edit-container">
    <!-- ⬅️ 뒤로가기 -->
    <div class="header-row">
      <button class="back-btn" @click="goBack">← 마이페이지</button>
    </div>

    <h2>프로필 수정</h2>

    <!-- 이름 입력 -->
    <div class="section">
      <h3>이름</h3>
      <input type="text" v-model="name" placeholder="이름을 입력하세요" />
    </div>

    <!-- 이메일 입력 -->
    <div class="section">
      <h3>이메일 (선택사항)</h3>
      <input type="text" v-model="email" placeholder="이메일을 입력하세요" />
    </div>

    <!-- 저장 버튼 -->
    <div class="footer">
      <button @click="saveChanges">변경사항 저장</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/lib/axios'

const router = useRouter()
const name = ref('')
const email = ref('')

const goBack = () => {
  router.push('/mypage')
}

const saveChanges = async () => {
  if (!name.value.trim() || !email.value.trim()) {
    alert('이름과 이메일을 모두 입력해주세요.')
    return
  }

  try {
    await axios.patch('/api/clients/me/edit', {
      oauthName: name.value,
      email: email.value
    })
    alert('수정이 완료되었습니다.')
    router.back()
  } catch (err) {
    console.error('수정 실패:', err)
    alert('오류가 발생했습니다.')
  }
}

onMounted(async () => {
  try {
    const res = await axios.get('/api/clients/me')
    name.value = res.data.oauthName
    email.value = res.data.email
  } catch (err) {
    console.error('프로필 정보 로딩 실패:', err)
  }
})
</script>

<style scoped>
.profile-edit-container {
  max-width: 800px;
  margin: 80px auto;
  padding: 40px;
  background-color: #ffffff;
  border-radius: 12px;
  font-family: 'Pretendard', sans-serif;
  color: #2B2F38;
}

.header-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}

.back-btn {
  background-color: #ffffff;
  border: none;
  color: #2B2F38;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

h2 {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 32px;
  color: #2B2F38;
}

.section {
  margin-top: 32px;
}

.section h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #2B2F38;
}

input[type="text"] {
  width: 100%;
  padding: 12px;
  border: 1px solid #D5DAE0;
  border-radius: 8px;
  font-size: 14px;
  background-color: #ffffff;
  color: #2B2F38;
}

input::placeholder {
  color: #8590A6;
}

.footer {
  margin-top: 40px;
  text-align: center;
}

.footer button {
  padding: 10px 24px;
  background-color: #1d2b50;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.footer button:hover {
  background-color: #1A2F8F;
}
</style>
