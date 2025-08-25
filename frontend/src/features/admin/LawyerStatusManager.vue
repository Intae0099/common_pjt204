<template>
  <div class="container">
    <h1>관리자 - 변호사 자격 처리</h1>
    <p>주로 '대기중(PENDING)' 상태의 변호사를 조회하고 처리합니다.</p>

    <div class="search-section">
      <button class="reset-btn" @click="fetchPendingLawyers" :disabled="loading">
        {{ loading ? '조회 중...' : '대기중인 변호사 목록 조회' }}
      </button>
      <p v-if="error" class="error-message">{{ error }}</p>
    </div>

    <table v-if="lawyers.length > 0">
      <thead>
        <tr>
          <th>ID</th>
          <th>이름</th>
          <th>이메일</th>
          <th>상태</th>
          <th>처리</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="lawyer in lawyers" :key="lawyer.lawyerId">
          <td>{{ lawyer.lawyerId }}</td>
          <td>{{ lawyer.name }}</td>
          <td>{{ lawyer.loginEmail }}</td>
          <td>
            <span :class="`status-${lawyer.certificationStatus.toLowerCase()}`">
              {{ lawyer.certificationStatus }}
            </span>
          </td>
          <td>
            <button @click="approveLawyer(lawyer.lawyerId)" :disabled="isProcessing(lawyer.lawyerId)">
              승인
            </button>
            <button @click="rejectLawyer(lawyer.lawyerId)" :disabled="isProcessing(lawyer.lawyerId)" class="reject-btn">
              거절
            </button>
             <span v-if="isProcessing(lawyer.lawyerId)">처리 중...</span>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else-if="!loading" class="no-lawyer">처리할 변호사가 없습니다.</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import instance from '@/lib/axios'; // 제공된 axios 설정 파일 경로

const lawyers = ref([]);
const loading = ref(false);
const processingIds = ref(new Set()); // 현재 처리 중인 lawyerId를 저장
const error = ref(null);

// 대기중인 변호사 목록을 가져오는 함수
const fetchPendingLawyers = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await instance.get('/api/admin/lawyers/certifications', {
      params: { status: 'PENDING' }
    });
    lawyers.value = response.data || [];
  } catch (err) {
    console.error('대기중인 변호사 목록 조회 실패:', err);
    error.value = '목록을 불러오는 데 실패했습니다.';
  } finally {
    loading.value = false;
  }
};

// 특정 변호사를 승인하는 함수
const approveLawyer = async (lawyerId) => {
  if (processingIds.value.has(lawyerId)) return;
  processingIds.value.add(lawyerId);

  try {
    await instance.patch(`/api/admin/${lawyerId}/approve`, {
      certificationStatus: "APPROVED"
    });
    alert(`변호사(ID: ${lawyerId})가 성공적으로 승인되었습니다.`);
    // 목록에서 해당 변호사 제거 또는 목록 새로고침
    lawyers.value = lawyers.value.filter(l => l.lawyerId !== lawyerId);
  } catch (err) {
    console.error(`변호사(ID: ${lawyerId}) 승인 실패:`, err);
    if (err.response?.status === 404) {
      alert('해당 변호사를 찾을 수 없습니다.');
    } else if (err.response?.status === 403) {
      alert('이 작업을 수행할 권한이 없습니다.');
    } else {
      alert('승인 처리 중 오류가 발생했습니다.');
    }
  } finally {
    processingIds.value.delete(lawyerId);
  }
};

// 특정 변호사를 거절하는 함수
const rejectLawyer = async (lawyerId) => {
  if (processingIds.value.has(lawyerId)) return;
  processingIds.value.add(lawyerId);

  try {
    // API 명세가 /api/adimin/... 으로 되어있어 /api/admin/...으로 수정하여 요청합니다.
    await instance.patch(`/api/admin/${lawyerId}/reject`, {
      certificationStatus: "REJECTED"
    });
    alert(`변호사(ID: ${lawyerId})가 거절 처리되었습니다.`);
    // 목록에서 해당 변호사 제거 또는 목록 새로고침
    lawyers.value = lawyers.value.filter(l => l.lawyerId !== lawyerId);
  } catch (err) {
    console.error(`변호사(ID: ${lawyerId}) 거절 실패:`, err);
     if (err.response?.status === 404) {
      alert('해당 변호사를 찾을 수 없습니다.');
    } else if (err.response?.status === 403) {
      alert('이 작업을 수행할 권한이 없습니다.');
    } else {
      alert('거절 처리 중 오류가 발생했습니다.');
    }
  } finally {
    processingIds.value.delete(lawyerId);
  }
};

// 해당 lawyerId가 처리 중인지 확인하는 함수
const isProcessing = (lawyerId) => {
  return processingIds.value.has(lawyerId);
};

</script>

<style scoped>
/* 이전 컴포넌트와 유사한 스타일 */
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
.error-message { color: red; }
.search-section { margin-bottom: 20px; }
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
td button { margin-right: 5px; }
.reject-btn { background-color: #f44336; color: white; }
.status-pending { color: orange; font-weight: bold; }
.status-approved { color: green; font-weight: bold; }
.status-rejected { color: red; font-weight: bold; }
.no-lawyer {
  color: #888;
}
</style>
