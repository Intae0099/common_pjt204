<template>
  <div>
    <button @click="$emit('predict')">
      📖 실제 판례 기반 예측하기
    </button>
    <button @click="$emit('quick-consult')">
      💬 바로 상담하기
    </button>
  </div>
</template>

<script setup>
defineEmits(['predict', 'quick-consult'])
</script>

<style scoped>

</style>
