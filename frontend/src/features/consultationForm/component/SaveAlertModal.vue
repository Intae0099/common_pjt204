<template>
  <div class="modal-overlay">
    <div class="modal-content">
      <DotLottieVue
        autoplay
        style="width: 100px; height: 100px; margin: 0 auto"
        src="https://lottie.host/1db4646a-279b-49ec-bf52-95b98de444e6/i1slxahsMy.lottie"
      />
      <p class="message">보관함에 저장되었습니다.</p>
      <p class="subtext">마이페이지 &gt; 상담신청서 보관함</p>
      <button class="confirm-btn" @click="$emit('close')">확인</button>
    </div>
  </div>
</template>
<script setup>
import { DotLottieVue } from '@lottiefiles/dotlottie-vue';
</script>
<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(255, 255, 255, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 0 15px rgba(0,0,0,0.15);
  padding: 2rem 2.5rem;
  text-align: center;
  max-width: 350px;
}

.message {
  font-weight: bold;
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  color: #072D45;
}

.subtext {
  font-size: 0.9rem;
  color: #6b7280;
  margin-bottom: 1.5rem;
}

.confirm-btn {
  background-color: #072D45;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
}
</style>
