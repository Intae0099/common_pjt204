<template>
  <div class="meeting-room">
    <h2>화상상담방</h2>
    <div id="publisher" class="video-box"></div> <!-- 내가 보게 될 내 영상 -->
    <div id="subscribers" class="video-box"></div> <!-- 상대방 영상 -->
    <button @click="leaveSession">퇴장하기</button>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { OpenVidu } from 'openvidu-browser'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/lib/axios'

const OV = ref(null)
const session = ref(null)
const mainStreamManager = ref(null)
const subscribers = ref([])

const route = useRoute()
const router = useRouter()

const token = route.query.token
const appointmentId = route.query.appointmentId

onMounted(async () => {
  OV.value = new OpenVidu()
  session.value = OV.value.initSession()

  session.value.on('streamCreated', (event) => {
    const subscriber = session.value.subscribe(event.stream, undefined)
    subscriber.addVideoElement(document.getElementById('subscribers'))
    subscribers.value.push(subscriber)
  })

  session.value.on('streamDestroyed', (event) => {
    subscribers.value = subscribers.value.filter(
      (sub) => sub.stream.streamId !== event.stream.streamId
    )
  })

  await session.value.connect(token, {
    clientData: '사용자 이름 등',
  })

  const publisher = await OV.value.initPublisher(undefined, {
    audioSource: undefined,
    videoSource: undefined,
    publishAudio: true,
    publishVideo: true,
    resolution: '640x480',
    frameRate: 30,
    mirror: true,
  })

  publisher.addVideoElement(document.getElementById('publisher')) // 내 영상도 붙이기
  await session.value.publish(publisher)
  mainStreamManager.value = publisher
})

const leaveSession = async () => {
  if (session.value) session.value.disconnect()
  await axios.delete(`/api/rooms/${appointmentId}/participants/me`)
  router.push('/')
}

onBeforeUnmount(() => {
  leaveSession()
})
</script>

<style scoped>
.meeting-room {
  padding: 2rem;
}
.video-box {
  width: 640px;
  height: 480px;
  background: #eee;
  margin-bottom: 1rem;
}
</style>
