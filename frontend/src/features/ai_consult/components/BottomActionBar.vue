<template>
  <div class="bottom-action-bar">
    <button class="action-button left" @click="$emit('predict')">
      📖 실제 판례 기반 예측하기
    </button>
    <button class="action-button right" @click="$emit('quick-consult')">
      💬 바로 상담하기
    </button>
  </div>
</template>

<script setup>
defineEmits(['predict', 'quick-consult'])
</script>

<style scoped>
.bottom-action-bar {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 24px;
  flex-direction: row;
}

@media (max-width: 767px) {
  .bottom-action-bar {
    flex-direction: column;
    gap: 12px;
  }
}

.action-button {
  flex: 1;
  padding: 14px 24px;
  font-size: 14px;
  font-weight: bold;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: 0.2s ease;
  color: white;
}

.action-button.left {
  background-color: #5a45ff;
}

.action-button.left:hover {
  background-color: #4331e0;
}

.action-button.right {
  background-color: #00c471;
}

.action-button.right:hover {
  background-color: #00b168;
}
</style>
