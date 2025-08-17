<template>
  <div class="case-layout">
     <div class="banner-wrapper">
       <div class="banner">
         <img src="@/assets/banner-bg2.png" alt="배경" class="banner-bg" />
         <div class="banner-text">
           <p><span class="highlight">AI기반</span> 변호사 상담,<br />쉽고 빠르게 신청하세요!</p>
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
.case-layout {
  overflow-x: hidden;
}
.banner-wrapper {
  width: 100vw;
  position: relative;
  left: 50%;
  right: 50%;
  margin-left: -50vw;
  margin-right: -50vw;
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
  color: white;
  font-size: 35px;
  font-weight: 350;
  line-height: 1.4;
}

.highlight {
  font-weight: bold;
}

.content-wrapper {
  font-family: 'Noto Sans KR', sans-serif;
  margin: 0 auto;
  padding: 40px 0px;
  background: white;
  border-radius: 8px;
}
</style>
