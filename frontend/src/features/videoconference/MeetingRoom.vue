<template>
  <div class="meeting-room">
    <h2>화상상담방</h2>
    <!-- 내가 보는 내 영상 -->
    <div id="publisher" class="video-box"></div>
    <!-- 상대방의 영상들이 들어올 공간 -->
    <div id="subscribers" class="video-box"></div>
    <button @click="leaveSession">퇴장하기</button>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { OpenVidu } from 'openvidu-browser'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/lib/axios'

// OpenVidu 관련 객체들 상태로 관리
const OV = ref(null)                  // OpenVidu 객체 (엔진 역할)
const session = ref(null)            // 세션 객체 (참여자 연결, 스트림 관리)
const mainStreamManager = ref(null)  // 내 비디오 스트림을 담는 객체
const subscribers = ref([])          // 다른 사람들(상대방)의 스트림 목록

const route = useRoute()
const router = useRouter()

// URL 쿼리에서 토큰과 예약 ID 받아오기 (백엔드에서 발급해준 값)
const token = route.query.token
const appointmentId = route.query.appointmentId

// 세션 참가 함수 (컴포넌트 마운트 시 자동 실행)
onMounted(async () => {
  // 1. OpenVidu 객체 생성
  OV.value = new OpenVidu()

  // 2. 세션 초기화 (로컬에서 관리할 세션 객체 생성)
  session.value = OV.value.initSession()

  // 3. 상대방이 입장해 스트림을 게시하면 구독하기
  session.value.on('streamCreated', (event) => {
    const subscriber = session.value.subscribe(event.stream, undefined)
    subscriber.addVideoElement(document.getElementById('subscribers')) // 구독자 영상 붙이기
    subscribers.value.push(subscriber)
  })

  // 4. 상대방이 나가거나 스트림 중단하면 제거하기
  session.value.on('streamDestroyed', (event) => {
    subscribers.value = subscribers.value.filter(
      (sub) => sub.stream.streamId !== event.stream.streamId
    )
  })

  // 5. 발급받은 토큰으로 세션 연결
  await session.value.connect(token, {
    clientData: '사용자 이름 등', // 이름, 역할 등 원하는 데이터 문자열로 전달 가능
  })

  // 6. 내 비디오/오디오 스트림 초기화
  const publisher = await OV.value.initPublisher(undefined, {
    audioSource: undefined,    // 기본 오디오 장치 사용
    videoSource: undefined,    // 기본 카메라 사용
    publishAudio: true,        // 오디오 켜기
    publishVideo: true,        // 비디오 켜기
    resolution: '640x480',     // 해상도 설정
    frameRate: 30,             // 프레임 수
    mirror: true               // 미러링 여부 (보통 셀카 느낌)
  })

  // 7. 내 비디오 태그에 스트림 연결
  publisher.addVideoElement(document.getElementById('publisher'))

  // 8. 세션에 내 스트림 게시 (다른 사람에게도 보이도록)
  await session.value.publish(publisher)

  // 9. 내 스트림 객체 저장
  mainStreamManager.value = publisher
})

// 퇴장 함수
const leaveSession = async () => {
  if (session.value) {
    session.value.disconnect()
    session.value = null
  }
  if (OV.value) OV.value = null
  mainStreamManager.value = null
  subscribers.value = []
  try {
    await axios.delete(`/api/rooms/${appointmentId}/participants/me`)
  } catch (e) {
    console.warn('퇴장 요청 실패:', e)
  }
  router.push('/')
}


// 컴포넌트 언마운트 시 세션 정리
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
