<!-- src/components/layout/CaseLayout.vue -->
<template>
  <div>
    <!-- 배너 영역 -->
    <div class="banner">
      <h2>
        빠르고 정확한 <span class="highlight">판례 조회</span>,<br />
        지금 바로 확인하세요!
      </h2>
    </div>

    <!-- 하위 콘텐츠 슬롯 -->
    <div class="content-wrapper">
      <slot />
    </div>
  </div>
</template>

<script setup>

</script>

<style scoped>
.banner {
  background: linear-gradient(135deg, #1f3c88, #2a5298);
  color: white;
  text-align: center;
  padding: 60px 0;
}

.highlight {
  font-weight: bold;
  color: #ffe600;
}

.content-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
  background: white;
  border-radius: 8px;
}
</style>
