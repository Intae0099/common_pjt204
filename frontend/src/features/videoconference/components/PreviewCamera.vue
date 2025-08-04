<template>
  <div class="preview-camera">
    <video ref="videoRef" autoplay playsinline muted></video>
    <div class="controls">
      <button @click="toggleAudio" :class="{ off: !isAudioOn }">
        <component :is="isAudioOn ? Mic : MicOff" class="icon" />
      </button>
      <button @click="toggleVideo" :class="{ off: !isVideoOn }">
        <component :is="isVideoOn ? Video : VideoOff" class="icon" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { OpenVidu } from 'openvidu-browser'
import { Mic, MicOff, Video, VideoOff } from 'lucide-vue-next'


const OV = ref(null)
const publisher = ref(null)
const videoRef = ref(null)

const isAudioOn = ref(false)
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
  height: 400px;
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
  left: 17px;
  display: flex;
  gap: 0.5rem;
}

button {
  background-color: rgba(0, 0, 0, 0.6);
  border: none;
  padding: 0.5rem;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s;
}
button:hover {
  background-color: rgba(0, 0, 0, 0.8);
}
.icon {
  width: 24px;
  height: 24px;
  color: white;
}
</style>
