<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-content">
      <h2 class="modal-title">빠르게 상담을 진행하시겠어요?</h2>
      <p class="modal-desc">
        현재 상황을 빠르게 해결하고 싶으시다면,<br/>아래 중 하나를 선택해 주세요.
      </p>

      <div class="modal-buttons">
        <button class="confirm" @click="$emit('route', 'lawyer')">
          변호사 추천받기
        </button>
        <button class="cancel" @click="$emit('close')">
          아니요, 괜찮아요
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineEmits(['close', 'route'])
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 32px 24px;
  border-radius: 16px;
  max-width: 400px;
  width: 90%;
  text-align: center;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
}

.modal-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 12px;
  color: #333;
}

.modal-desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 24px;
}

.modal-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.confirm {
  background-color: #5a45ff;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
  cursor: pointer;
}

.cancel {
  background-color: #eee;
  color: #444;
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
  cursor: pointer;
}

.confirm:hover {
  background-color: #4331e0;
}

.cancel:hover {
  background-color: #ddd;
}
</style>
