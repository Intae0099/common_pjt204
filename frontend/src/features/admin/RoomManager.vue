<template>
  <div class="container">
    <h1>관리자 - 화상 상담방 강제 종료</h1>
    <div class="form-section">
      <label for="appointment-id">상담 ID (appointmentId):</label>
      <input type="number" id="appointment-id" v-model.number="appointmentId" placeholder="종료할 상담의 ID를 입력하세요" />
      <button class="cancel-btn" @click="terminateRoom" :disabled="loading || !appointmentId">
        {{ loading ? '종료 중...' : '상담방 강제 종료' }}
      </button>
    </div>
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>
    <div class="notes">
      <p><strong>경고:</strong></p>
      <ul>
        <li>이 요청은 지정된 상담의 화상상담방을 즉시 종료시킵니다.</li>
        <li>사용자에게는 <strong>"관리자에 의해 상담이 종료되었습니다."</strong>와 같은 안내 메시지가 표시됩니다.</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import instance from '@/lib/axios'; // 제공된 axios 설정 파일 경로

const appointmentId = ref(null);
const loading = ref(false);
const message = ref('');
const messageType = ref(''); // 'success' or 'error'

const terminateRoom = async () => {
  if (!appointmentId.value || isNaN(appointmentId.value)) {
    message.value = '유효한 상담 ID를 입력해주세요.';
    messageType.value = 'error';
    return;
  }

  if (!confirm(`정말로 상담 ID ${appointmentId.value}의 화상상담방을 강제 종료하시겠습니까?`)) {
    return;
  }

  loading.value = true;
  message.value = '';

  try {
    await instance.delete(`/api/admin/rooms/${appointmentId.value}`);
    message.value = `상담(ID: ${appointmentId.value})의 화상상담방이 성공적으로 종료되었습니다.`;
    messageType.value = 'success';
    appointmentId.value = null; // 성공 후 입력 필드 초기화
  } catch (err) {
    console.error(`상담방(ID: ${appointmentId.value}) 강제 종료 실패:`, err);
    message.value = `상담방 종료에 실패했습니다. (오류: ${err.response?.statusText || err.message})`;
    messageType.value = 'error';
  } finally {
    loading.value = false;
  }
};
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

.cancel-btn {
  background-color: #f9e3df;
  color: #333333;
  padding: 4px 8px;
  border: 1px solid #d32f2f;
  border-radius: 15px;
  cursor: pointer;
  font-size: 0.8rem;
}

.form-section {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.message {
  padding: 10px;
  border-radius: 5px;
  margin-top: 15px;
}
.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}
.message.error {
  background-color: #f8d7da;
  color: #d32f2f;
  border: 1px solid #f5c6cb;
}
.notes {
  margin-top: 25px;
  padding: 15px;
  background-color:#f8f9fa;
  border-left: 4px solid #d32f2f;
  list-style-type: none;
}
.notes p {
  font-weight: bold;
  color:#d32f2f;
}
.notes ul {
  list-style-type: none;
  margin-top: 10px;
  padding-left: 20px;
}
</style>
