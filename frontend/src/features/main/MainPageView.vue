<template>
 <base-navbar/>
 <div class="main-background-container">
   <div class="left-image-area"></div>

   <div class="side-text-menu">
     <p style="background-image: linear-gradient(to bottom, #FFFFFF 0%, #DDE6FE 100%); -webkit-background-clip: text; background-clip: text; color: transparent;">챗봇과 함께하는 화상상담</p>
     <p style="background-image: linear-gradient(to bottom, #FFFFFF 0%, #B3C7FD 100%); -webkit-background-clip: text; background-clip: text; color: transparent;">고객 맞춤 판례조회</p>
     <p style="background-image: linear-gradient(to top, #FFFFFF 0%, #B3C7FD 100%); -webkit-background-clip: text; background-clip: text; color: transparent;">AI 사전상담</p>
     <p style="background-image: linear-gradient(to top, #FFFFFF 0%, #DDE6FE 100%); -webkit-background-clip: text; background-clip: text; color: transparent;">쉽게쓰는 상담신청서</p>
   </div>

   <div class="right-image-area"></div>
 </div>
</template>

<script setup>
import BaseNavbar from '@/components/BaseNavbar.vue';
</script>

<style scoped>
/* 전체 화면을 덮는 기본 컨테이너 */
.main-background-container {
 background-color: #fff;
 width: 100vw;
 height: 100vh;
 position: relative;
 overflow: hidden;
}

/* 왼쪽 텍스트 메뉴 스타일 */
.side-text-menu {
 position: absolute;
 left: 7.3rem;
 top: 15%;
 z-index: 10;

 /* 텍스트 스타일 */
 font-weight: 500;
 font-size: 0.8rem;

 /* 줄 간격 유지 */
 line-height: 1.2;
}

/* 왼쪽 이미지 영역 스타일 */
.left-image-area {
 background-image: url('@/assets/main-left.png');
 background-size: cover;
 background-position: center;
 position: absolute;
 top: 25%;
 left: 0;
 width: 300px;
 height: 60%;
 transform: translateX(calc(-100% + 20px));
 border-top-right-radius: 40px;
 border-bottom-right-radius: 40px;
}

/* 오른쪽 이미지 영역 스타일 */
.right-image-area {
 background-image: url('@/assets/main-right.png');
 background-size: cover;
 background-position: center;
 position: absolute;
 top: 0;
 right: 0;
 width: 40%;
 height: 100%;
 border-top-left-radius: 40px;
 border-bottom-left-radius: 40px;
}
</style>
