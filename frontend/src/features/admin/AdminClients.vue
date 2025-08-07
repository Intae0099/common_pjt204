<template>
  <div class="container">
    <h1>관리자 - 클라이언트 목록</h1>
    <button @click="fetchClients" :disabled="loading">
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
    console.log('클라이언트 목록:', response.data)
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
  padding: 20px;
}
.error-message {
  color: red;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}
th, td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}
th {
  background-color: #f2f2f2;
}
</style>