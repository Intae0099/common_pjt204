<template>
  <div class="action-bar">
    <button class="action-button" @click="$emit('predict')">
      실제 판례 기반 예측하기
      <span class="arrow">→</span>
    </button>
    <button class="quick-button" @click="$emit('quick-consult')">
      바로 상담받기
    </button>
  </div>
</template>

<script setup>
defineEmits(['predict', 'quick-consult'])
</script>

<style scoped>
*{
  font-family: 'Noto Sans KR', sans-serif;
}
.action-bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-top: 50px;
}

.action-button {
  background-color: #0F2C59;
  color: white;
  font-size: 14px;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: medium;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.action-button:hover {
  background-color: #1c3d78;
}

.arrow {
  margin-left: 8px;
}

.quick-button {
  background: none;
  border: none;
  color: #82A0B3;
  font-size: 12px;
  cursor: pointer;
  margin-top: 4px;
}

.quick-button:hover {
  color: #6b8799;
}
</style>
