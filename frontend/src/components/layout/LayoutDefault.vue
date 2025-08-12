<template>
  <div class="container">
    <BaseNavbar />
    <slot />
  </div>
</template>

<script setup>
import BaseNavbar from '@/components/BaseNavbar.vue'
</script>

<style scoped>
.container {
  font-family: 'Noto Sans KR', sans-serif;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
  box-sizing: border-box;
  min-height: 100vh;
}
</style>
