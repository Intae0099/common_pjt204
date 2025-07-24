<template>
  <div class="preview-wrapper">
    <video ref="videoRef" autoplay playsinline muted class="preview-video" />
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'

const videoRef = ref(null)
let stream = null

onMounted(async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true
    })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
    }
  } catch (err) {
    console.error('카메라/마이크 접근 실패:', err)
  }
})

onBeforeUnmount(() => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
  }
})
</script>

<style scoped>

</style>
