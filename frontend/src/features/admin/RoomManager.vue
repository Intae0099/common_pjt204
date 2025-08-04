<template>
  <div class="container">
    <h1>관리자 - 화상 상담방 강제 종료</h1>
    <div class="form-section">
      <label for="appointment-id">상담 ID (appointmentId):</label>
      <input type="number" id="appointment-id" v-model.number="appointmentId" placeholder="종료할 상담의 ID를 입력하세요" />
      <button @click="terminateRoom" :disabled="loading || !appointmentId">
        {{ loading ? '종료 중...' : '상담방 강제 종료' }}
      </button>
    </div>
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>
    <div class="notes">
      <p><strong>참고:</strong></p>
      <ul>
        <li>이 요청은 지정된 상담의 화상상담방을 즉시 종료시킵니다.</li>
        <li>성공적으로 종료되면, 해당 상담방에 접속해 있던 사용자(클라이언트, 변호사)들에게 <code>sessionDestroyed</code> 이벤트가 발생합니다.</li>
        <li>프론트엔드에서는 이 이벤트에 대한 핸들러를 구현하여 "관리자에 의해 상담이 종료되었습니다."와 같은 안내 메시지를 표시해야 합니다.</li>
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
    console.log(`상담방(ID: ${appointmentId.value}) 강제 종료 성공`);
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
  padding: 20px;
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
  color: #721c24;
  border: 1px solid #f5c6cb;
}
.notes {
  margin-top: 25px;
  padding: 15px;
  background-color: #f8f9fa;
  border-left: 4px solid #6c757d;
}
</style>