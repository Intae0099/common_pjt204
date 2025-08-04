<template>
  <div class="preview-camera">
    <video ref="videoRef" autoplay playsinline muted></video>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const videoRef = ref(null)

onMounted(async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
    }
  } catch (err) {
    console.error('카메라 연결 실패:', err)
  }
})
</script>

<style scoped>
.preview-camera {
  width: 100%;
  height: 450px;
  border-radius: 10px;
  background-color: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
}
video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 10px;
}
</style>
