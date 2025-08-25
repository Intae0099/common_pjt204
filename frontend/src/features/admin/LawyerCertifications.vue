<template>
  <div class="container">
    <h1>관리자 - 변호사 자격 인증 관리</h1>
    <div class="search-form">
      <label for="status-select">인증 상태 선택:</label>
      <select class="status-select" id="status-select" v-model="selectedStatus" @change="fetchLawyerCertifications">
        <option value="PENDING">대기중 (PENDING)</option>
        <option value="APPROVED">승인됨 (APPROVED)</option>
        <option value="REJECTED">거절됨 (REJECTED)</option>
      </select>
    </div>

    <p v-if="loading">
      조회 중...
    </p>
    <p v-if="error" class="error-message">
      오류가 발생했습니다: {{ error }}
    </p>

    <div v-if="lawyers.length > 0">
      <h3>'{{ selectedStatus }}' 상태의 변호사 목록</h3>
      <table>
        <thead>
          <tr>
            <th>변호사 ID</th>
            <th>이름</th>
            <th>로그인 이메일</th>
            <th>소개</th>
            <th>시험 종류</th>
            <th>등록 번호</th>
            <th>상담 횟수</th>
            <th>태그</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lawyer in lawyers" :key="lawyer.lawyerId">
            <td>{{ lawyer.lawyerId }}</td>
            <td>{{ lawyer.name }}</td>
            <td>{{ lawyer.loginEmail }}</td>
            <td>{{ lawyer.introduction }}</td>
            <td>{{ lawyer.exam }}</td>
            <td>{{ lawyer.registrationNumber }}</td>
            <td>{{ lawyer.consultationCount }}</td>
            <td>{{ lawyer.tags.join(', ') }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else-if="!loading && !error">
      해당 상태의 변호사가 없습니다. (204 No Content)
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import instance from '@/lib/axios' // 제공된 axios 설정 파일 경로

const lawyers = ref([])
const selectedStatus = ref('APPROVED') // 기본값 설정
const loading = ref(false)
const error = ref(null)

const fetchLawyerCertifications = async () => {
  loading.value = true
  error.value = null
  lawyers.value = [] // 새로운 검색 시 목록 초기화

  try {
    const response = await instance.get('/api/admin/lawyers/certifications', {
      params: {
        status: selectedStatus.value
      }
    })

    // 204 No Content의 경우 data가 없을 수 있음
    if (response.data) {
      lawyers.value = response.data
    }
  } catch (err) {
    console.error('변호사 인증 목록 조회 실패:', err)
    error.value = '데이터를 불러오는 데 실패했습니다.'
  } finally {
    loading.value = false
  }
}

// 컴포넌트가 마운트될 때 PENDING 상태의 목록을 기본으로 불러옵니다.
onMounted(fetchLawyerCertifications)
</script>

<style scoped>
/* 이전 컴포넌트와 동일한 스타일 사용 */
.container {
  font-family: 'Noto Sans KR', sans-serif;
  padding: 20px;
}
h1 {
  font-size: 1.8rem;
  margin-bottom: 16px;
  font-weight: bold;
}
h3 {
  font-size: 1.2rem;
  margin-bottom: 16px;
  font-weight: bold;
}

.search-form {
  margin-bottom: 20px;
  color: #333333;
}
.status-select{
  padding: 4px;
  font-size: 0.8rem;
  border: 1px solid #cfcfcf;
  border-radius: 15px;
  color: #888;
  margin-left: 10px;
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
