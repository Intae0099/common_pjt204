<template>
  <div>
    <div class="banner">
      <img src="@/assets/banner-bg.png" alt="배경" class="banner-bg" />
      <img src="@/assets/banner-character.png" alt="캐릭터" class="banner-character" />
      <div class="banner-text">
        <p>빠르고 정확한 <span class="highlight">판례 조회</span>,<br />지금 바로 확인하세요!</p>
      </div>
    </div>

    <div class="content-wrapper">
      <slot />
    </div>
  </div>
</template>

<script setup>

</script>

<style scoped>
.banner {
  position: relative;
  width: 99vw;
  height: 250px;
  margin-left: calc(-50vw + 50%);
  overflow: hidden;
}

.banner-bg,
.banner-character {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.banner-text {
  font-family: 'Noto Sans KR', sans-serif;
  position: absolute;
  top: 55%;
  left: 35%;
  transform: translateY(-50%);
  color: white;
  font-size: 35px;
  font-weight: 350;
  line-height: 1.4;
}

.highlight {
  font-weight: bold;
}

.content-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
  background: white;
  border-radius: 8px;
}
</style>
