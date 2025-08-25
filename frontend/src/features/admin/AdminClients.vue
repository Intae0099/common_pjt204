<template>
  <div class="container">
    <h1>관리자 - 클라이언트 목록</h1>
    <button class="reset-btn" @click="fetchClients" :disabled="loading">
      {{ loading ? '불러오는 중...' : '클라이언트 목록 새로고침' }}
    </button>
    <p v-if="error" class="error-message">
      오류가 발생했습니다: {{ error }}
    </p>
    <table v-if="clients.length > 0">
      <thead>
        <tr>
          <th>클라이언트 ID</th>
          <th>이름</th>
          <th>이메일</th>
          <th>Provider</th>
          <th>Provider 고유 ID</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="client in clients" :key="client.clientId">
          <td>{{ client.clientId }}</td>
          <td>{{ client.oauthName }}</td>
          <td>{{ client.email || 'N/A' }}</td>
          <td>{{ client.oauthProvider }}</td>
          <td>{{ client.oauthIdenifier }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else-if="!loading">
      표시할 클라이언트가 없습니다.
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import instance from '@/lib/axios' // 제공된 axios 설정 파일 경로

const clients = ref([])
const loading = ref(false)
const error = ref(null)

const fetchClients = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await instance.get('/api/admin/clients')
    clients.value = response.data
  } catch (err) {
    console.error('클라이언트 목록 조회 실패:', err)
    error.value = '데이터를 불러오는 데 실패했습니다. 권한을 확인해주세요 (403 Forbidden).'
  } finally {
    loading.value = false
  }
}

// 컴포넌트가 마운트될 때 자동으로 데이터를 불러옵니다.
onMounted(fetchClients)
</script>

<style scoped>
.container {
  font-family: 'Noto Sans KR', sans-serif;
  padding: 20px;
}
h1 {
  font-size: 1.8rem;
  margin-bottom: 16px;
  font-weight: bold;
}
.reset-btn {
  background-color: #f4f7fb;
  color: #333333;
  padding: 4px 8px;
  border: 1px solid #6c9bcf;
  border-radius: 15px;
  cursor: pointer;
  margin-bottom: 20px;
  font-size: 0.8rem;
}
.error-message {
  color: red;
}
table {
  width: 100%;
  border : 1px solid #888;
  margin-top: 20px;
  color:#333333;
  font-size: 0.8rem;

}
tr {
  font-style: bold;
  background-color: #f4f7fb;
}
th, td {
  border: 1px solid #ddd;
  padding: 6px;
  text-align: center;
}
th {
  background-color: #f2f2f2;
}

table th:nth-child(2),
table td:nth-child(2) {
  white-space: nowrap; /* 줄바꿈 방지 */
}

table th:nth-child(5),
table td:nth-child(5) {
  white-space: nowrap; /* 줄바꿈 방지 */
}
</style>
