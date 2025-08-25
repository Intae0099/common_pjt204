<template>
  <div class="search-layout">
     <div class="banner-wrapper">
       <div class="banner">
         <img src="@/assets/banner-lawyersearch.png" alt="배경" class="banner-bg" />
         <div class="banner-text">
           <p><span class="highlight">분야별 전문가</span> 조회,<br />원하는 변호사에게 빠르게 상담 신청하세요!</p>
         </div>
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
.search-layout {
  overflow-x: hidden;
}
.banner-wrapper {
  width: 100vw;
  position: relative;
  left: 50%;
  right: 50%;
  margin-left: -50vw;
  margin-right: -50vw;
  max-width: 100vw;
  overflow: hidden;
}

.banner {
  width: 100vw;
  height: 250px;
  position: relative;
}

.banner-bg {
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
  color: rgb(58, 58, 58);
  font-size: 30px;
  font-weight: 350;
  line-height: 1.4;
}

.highlight {
  font-weight: bold;
}

.content-wrapper {
  margin: 0 auto;
  padding: 40px 0px;
  background: white;
  border-radius: 8px;
}
</style>
