<template>
  <div class="preview-camera">
    <video ref="videoRef" autoplay playsinline muted></video>
    <div class="controls">
      <button @click="toggleAudio">
        {{ isAudioOn ? '🔈 마이크 끄기' : '🔇 마이크 켜기' }}
      </button>
      <button @click="toggleVideo">
        {{ isVideoOn ? '📷 카메라 끄기' : '🚫 카메라 켜기' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { OpenVidu } from 'openvidu-browser'

const OV = ref(null)
const publisher = ref(null)
const videoRef = ref(null)

const isAudioOn = ref(false) // 초기에는 음소거 상태
const isVideoOn = ref(true)

onMounted(async () => {
  try {
    OV.value = new OpenVidu()

    publisher.value = await OV.value.initPublisher(undefined, {
      videoSource: undefined,
      audioSource: undefined,
      publishAudio: isAudioOn.value,
      publishVideo: isVideoOn.value,
      mirror: true,
    })

    publisher.value.addVideoElement(videoRef.value)
  } catch (err) {
    console.error('OpenVidu 미리보기 실패:', err)
  }
})

const toggleAudio = () => {
  if (!publisher.value) return
  isAudioOn.value = !isAudioOn.value
  publisher.value.publishAudio(isAudioOn.value)
}

const toggleVideo = () => {
  if (!publisher.value) return
  isVideoOn.value = !isVideoOn.value
  publisher.value.publishVideo(isVideoOn.value)
}

onBeforeUnmount(() => {
  if (publisher.value) {
    publisher.value.stream.dispose()
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
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 10px;
}

.controls {
  position: absolute;
  bottom: 15px;
  display: flex;
  gap: 1rem;
}

button {
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
}
</style>
