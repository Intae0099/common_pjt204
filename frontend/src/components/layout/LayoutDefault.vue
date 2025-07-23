<template>
  <Navbar />
  <div class="container">
    <slot />
  </div>
</template>

<script setup>
import Navbar from '@/components/Navbar.vue'
</script>

<style scoped>
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
  box-sizing: border-box;
  min-height: 100vh;
}
</style>
