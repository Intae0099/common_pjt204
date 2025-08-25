<template>
  <div class="modal-backdrop" @click.self="closeModal">
    <div class="modal-content">
      <h4 class="modal-title">상담 내용 저장</h4>
      <p class="modal-text">지금까지의 상담 내용을 임시로 저장하시겠습니까?</p>
      <div class="modal-actions">
        <button @click="confirmAndClose" class="modal-button save">저장</button>
        <button @click="closeModal" class="modal-button cancel">취소</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineEmits } from 'vue';

// 부모 컴포넌트로 보낼 이벤트를 정의합니다.
const emit = defineEmits(['confirm-save', 'close']);

// '저장' 버튼 클릭 시, 'confirm-save' 이벤트를 발생시킵니다.
const confirmAndClose = () => {
  emit('confirm-save');
};

// '취소' 버튼 또는 배경 클릭 시, 'close' 이벤트를 발생시킵니다.
const closeModal = () => {
  emit('close');
};
</script>

<style scoped>
/* AIStep.vue에 있던 모달 스타일을 그대로 가져옵니다. */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  width: 90%;
  max-width: 400px;
}

.modal-title {
  font-family: 'Noto Sans KR', sans-serif;
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #072D45;
}

.modal-text {
  font-family: 'Noto Sans KR', sans-serif;
  font-size: 0.95rem;
  color: #516F90;
  margin-bottom: 1.5rem;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
}

.modal-button {
  font-family: 'Noto Sans KR', sans-serif;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.modal-button.save {
  background-color: #007bff;
  color: white;
}
.modal-button.save:hover {
  background-color: #0056b3;
}

.modal-button.cancel {
  background-color: #f1f3f5;
  color: #516F90;
}
.modal-button.cancel:hover {
  background-color: #e9ecef;
}
</style>
