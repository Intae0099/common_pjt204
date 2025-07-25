<template>
  <div class="meeting-room">
    <h2>화상상담방</h2>

    <div class="video-wrapper">
      <div class="video-box">
        <p>나</p>
        <video ref="localVideo" autoplay muted playsinline></video>
      </div>

      <div class="video-box">
        <p>상대방</p>
        <video ref="remoteVideo" autoplay playsinline></video>
      </div>
    </div>
    <button @click="leaveMeeting">나가기</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { io } from 'socket.io-client'
import { useRoute, useRouter } from 'vue-router'
// import axios from '@/lib/axios'

const localVideo = ref(null)
const remoteVideo = ref(null)
const route = useRoute()
const router = useRouter()
const socket = io('http://localhost:3000')
const roomId = route.query.sessionId || 'default-room'

let localStream = null
let peerConnection = null
let remoteStream = new MediaStream()

onMounted(async () => {
  // 1. 내 캠 가져오기
  try {
    localStream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true,
    })
    localVideo.value.srcObject = localStream
    console.log('카메라 연결 성공')
  } catch (error) {
    console.error('카메라 연결 실패:', error)
  }

  // 2. 참가자 등록
  // try {
  //   await axios.post(`/api/${sessionId}/participants`)
  // } catch (e) {
  //   console.error('참가자 등록 실패:', e)
  // }

  socket.emit('join', roomId)
})

function createPeerConnection() {
  peerConnection = new RTCPeerConnection({
    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
  })

  // 상대방 스트림 추가
  peerConnection.ontrack = (event) => {
    event.streams[0].getTracks().forEach((track) => {
      remoteStream.addTrack(track)
    })
    remoteVideo.value.srcObject = remoteStream
  }

  // ICE 후보 전송
  peerConnection.onicecandidate = (event) => {
    if (event.candidate) {
      socket.emit('ice-candidate', { roomId, candidate: event.candidate })
    }
  }
}

socket.on('joined', async () => {
  createPeerConnection()
  localStream.getTracks().forEach((track) => {
    peerConnection.addTrack(track, localStream)
  })

  const offer = await peerConnection.createOffer()
  await peerConnection.setLocalDescription(offer)
  socket.emit('offer', { roomId, offer })
})

socket.on('offer', async ({ offer }) => {
  createPeerConnection()
  localStream.getTracks().forEach((track) => {
    peerConnection.addTrack(track, localStream)
  })

  await peerConnection.setRemoteDescription(new RTCSessionDescription(offer))
  const answer = await peerConnection.createAnswer()
  await peerConnection.setLocalDescription(answer)
  socket.emit('answer', { roomId, answer })
})

socket.on('answer', async ({ answer }) => {
  await peerConnection.setRemoteDescription(new RTCSessionDescription(answer))
})

socket.on('ice-candidate', async ({ candidate }) => {
  try {
    await peerConnection.addIceCandidate(new RTCIceCandidate(candidate))
  } catch (error) {
    console.error('ICE 추가 실패:', error)
  }
})

const leaveMeeting = async () => {
  // try {
  //   await axios.delete('/api/participants/me')
  // } catch (e) {
  //   console.error('회의방 나가기 실패:', e)
  // }
  socket.disconnect()
  router.push('/')
}

</script>
