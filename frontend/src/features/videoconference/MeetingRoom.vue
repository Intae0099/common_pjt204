<template>
  <div class="meeting-room">
    <div class="video-section">
      <!-- 화면 공유 중일 때 -->
      <template v-if="isScreenSharing">
        <!-- 왼쪽: 변호사 + 의뢰인 세로 정렬 -->
        <div class="video-box vertical-video">
          <div class="video-inner" id="lawyer-video">
            <p class="role-label">변호사</p>
          </div>
          <div class="video-inner" id="publisher">
            <p class="role-label">의뢰인</p>
          </div>
        </div>

        <!-- 가운데: 공유된 화면 -->
        <div class="video-box shared-screen" id="client-video">
          <canvas id="draw-canvas" class="drawing-canvas"></canvas>
        </div>
      </template>

      <!-- 평소(공유 X) 화면: 좌우 나란히 -->
      <template v-else>
        <div class="video-box" id="lawyer-video">
          <p class="role-label">변호사</p>
        </div>
        <div class="video-box" id="publisher">
          <p class="role-label">의뢰인</p>
        </div>
      </template>

      <!-- 오른쪽: 채팅 -->
      <div class="chat-area">
        <div class="chat-content">
          <RealtimeChatView v-if="activeChat === 'realtime'" />
          <ChatbotView v-if="activeChat === 'chatbot'" />
        </div>
      </div>
    </div>
  </div>

<!-- 하단 푸터 -->
<div class="meeting-footer">
  <!-- 왼쪽 툴 모음 -->
  <div class="footer-left">

    <!-- ⋮ 버튼 (모바일 전용) -->
    <button class="footer-btn ellipsis-btn" @click="isMenuOpen = !isMenuOpen">
      <EllipsisVertical class="footer-icon" />
    </button>

    <!-- ▼ ① 툴그룹: “화면공유”를 빼고 나머지만 넣기 -->
    <div class="tool-group" :class="{ show: isMenuOpen }">
      <!-- 펜 / 지우개 / 포인터 -->
      <button class="footer-btn" @click="setTool('pen')"     :disabled="!isScreenSharing" :class="{ active: currentTool==='pen' }"><Pencil class="footer-icon" /></button>
      <button class="footer-btn" @click="setTool('eraser')"  :disabled="!isScreenSharing" :class="{ active: currentTool==='eraser' }"><Eraser class="footer-icon" /></button>
      <button class="footer-btn" @click="setTool('pointer')" :disabled="!isScreenSharing" :class="{ active: currentTool==='pointer' }"><MousePointer2 class="footer-icon" /></button>

      <!-- 카메라 / 마이크 -->
      <button class="footer-btn" @click="toggleCamera"><component :is="isCameraOn ? Video : VideoOff" class="footer-icon" /></button>
      <button class="footer-btn" @click="toggleMic"><component :is="isMicOn ? Mic : MicOff" class="footer-icon" /></button>
    </div>

    <!-- ▼ ② “화면공유” 버튼은 메뉴 밖, 항상 노출 -->
    <button class="footer-btn only-share" @click="shareScreen">
      <span class="footer-label">화면공유</span>
      <Share class="footer-icon" />
    </button>

  </div>

  <!-- 오른쪽: 채팅·챗봇·나가기 (기존 그대로) -->
  <div class="footer-right">
    <div class="chat-btn-wrapper">
      <button class="footer-btn" @click="toggleChat('realtime')">
        <MessageSquareText class="footer-icon" />
      </button>
      <button class="footer-btn" @click="toggleChat('chatbot')">
        <img src="@/assets/ai-bot.png" class="footer-icon" />
      </button>
    </div>

    <button class="footer-btn leave-btn" @click="leaveSession">
      나가기
    </button>
  </div>
</div>

</template>


<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { OpenVidu } from 'openvidu-browser'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/lib/axios'
import RealtimeChatView from '@/features/chatting/RealtimeChatView.vue'
import ChatbotView from '@/features/chatting/ChatbotView.vue'
import { EllipsisVertical,Pencil, Eraser, MousePointer2, MessageSquareText, Share, Video, VideoOff, Mic, MicOff } from 'lucide-vue-next'
const activeChat = ref('realtime')
const toggleChat = (type) => {
  activeChat.value = activeChat.value === type ? null : type
}
// OpenVidu 관련 객체들 상태로 관리
const OV = ref(null)                  // OpenVidu 객체 (엔진 역할)
const session = ref(null)            // 세션 객체 (참여자 연결, 스트림 관리)
const mainStreamManager = ref(null)  // 내 비디오 스트림을 담는 객체
const subscribers = ref([])          // 다른 사람들(상대방)의 스트림 목록
const isMenuOpen = ref(false)
const route = useRoute()
const router = useRouter()

// 상태 관리
const isCameraOn = ref(true)
const isMicOn = ref(true)

// 화면 공유 중 여부
const isScreenSharing = ref(false)

/* ---------- 그리기 상태 ---------- */
const currentTool    = ref('pointer') // 'pen' | 'eraser' | 'pointer'
const isDrawing      = ref(false)
let  canvas, ctx

function setTool(tool){
  currentTool.value = tool
  if (!canvas) return;

  canvas.style.pointerEvents = (tool === 'pointer') ? 'none' : 'auto';

  // ② 클래스 토글
  canvas.classList.toggle('pen-cursor'   , tool==='pen');
  canvas.classList.toggle('eraser-cursor', tool==='eraser');
}



// URL 쿼리에서 토큰과 예약 ID 받아오기 (백엔드에서 발급해준 값)
const token = route.query.token
const appointmentId = route.query.appointmentId


// 카메라 토글 함수
const toggleCamera = () => {
  if (mainStreamManager.value) {
    isCameraOn.value = !isCameraOn.value
    mainStreamManager.value.publishVideo(isCameraOn.value)
  }
}

// 마이크 토글 함수
const toggleMic = () => {
  if (mainStreamManager.value) {
    isMicOn.value = !isMicOn.value
    mainStreamManager.value.publishAudio(isMicOn.value)
  }
}


/* ---------- 로컬 그리기 ---------- */
function startDraw(e){
  if(currentTool.value==='pointer') return
  isDrawing.value = true
  ctx.beginPath()
  ctx.moveTo(e.offsetX, e.offsetY)
}
function draw(e){
  if(!isDrawing.value) return
  if(currentTool.value==='pen'){
    ctx.globalCompositeOperation='source-over'
    ctx.lineWidth = 2
    ctx.strokeStyle = 'red'
  }else if(currentTool.value==='eraser'){
    ctx.globalCompositeOperation='destination-out'
    ctx.lineWidth = 20
  }
  ctx.lineTo(e.offsetX, e.offsetY)
  ctx.stroke()

  // 상대방에게 전파
  sendSignal({ x:e.offsetX, y:e.offsetY, t:currentTool.value, a:isDrawing.value })
}
function endDraw(){
  if(isDrawing.value){
    isDrawing.value=false
    ctx.closePath()
  }
}

/* ----------  OpenVidu signal ---------- */
function sendSignal(payload){
  if(!session.value) return
  session.value.signal({ type:'drawing', data:JSON.stringify(payload) })
}

// 수신 → 상대방 캔버스에 동일하게 그림
function handleRemoteDraw({data}){
  const {x,y,t,a} = JSON.parse(data)
  if(t==='pointer') return
  ctx.globalCompositeOperation = t==='pen' ? 'source-over' : 'destination-out'
  ctx.lineWidth = t==='pen' ? 2 : 20
  if(a){ ctx.lineTo(x,y); ctx.stroke() }
  else{ ctx.beginPath(); ctx.moveTo(x,y) }
}

/* ---------- 캔버스 초기화 ---------- */
async function initCanvas(){
  await nextTick()                     // DOM 완성 대기
  canvas = document.getElementById('draw-canvas')
  if(!canvas) return
  ctx = canvas.getContext('2d')
  canvas.width  = canvas.offsetWidth
  canvas.height = canvas.offsetHeight

  canvas.addEventListener('mousedown', startDraw)
  canvas.addEventListener('mousemove', draw)
  canvas.addEventListener('mouseup'  , endDraw)
  canvas.addEventListener('mouseleave', endDraw)
}


// 세션 참가 함수 (컴포넌트 마운트 시 자동 실행)
onMounted(async () => {

  // 디버깅
  console.log("onMounted 진입");

  // OpenVidu 서버의 주소 (URL)
  const OPENVIDU_SERVER_URL = "https://i13b204.p.ssafy.io/openvidu";
  // 1. OpenVidu 객체 생성
  OV.value = new OpenVidu(OPENVIDU_SERVER_URL)


  // 2. 세션 초기화 (로컬에서 관리할 세션 객체 생성)
  session.value = OV.value.initSession()


  // 3. 상대방이 입장해 스트림을 게시하면 구독하기
  session.value.on('streamCreated', (event) => {
    const subscriber = session.value.subscribe(event.stream, undefined)
    const target = document.getElementById('lawyer-video')
    subscriber.addVideoElement(target)
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

  session.value.on('signal:drawing', handleRemoteDraw)
})

const shareScreen = async () => {
  try {
    const screenPublisher = await OV.value.initPublisher(undefined, {
      videoSource: 'screen',
      audioSource: undefined,
      publishVideo: true,
      publishAudio: false,
      mirror: false
    })

    const screenVideo = document.createElement('video')
    screenVideo.autoplay = true
    screenVideo.playsInline = true
    screenVideo.style.width = '100%'
    screenVideo.style.height = '100%'
    screenVideo.style.objectFit = 'cover'
    document.getElementById('client-video').appendChild(screenVideo)
    screenPublisher.addVideoElement(screenVideo)

    await session.value.publish(screenPublisher)
    await initCanvas();
    isScreenSharing.value = true

    console.log('화면 공유 시작됨')
  } catch (err) {
    console.error('화면 공유 실패:', err)
    alert('화면 공유를 허용하지 않으면 시작할 수 없습니다.')
  }
}


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
*{
  font-family: 'Noto Sans KR', sans-serif;
  background-color: #131516;
}
.meeting-room {
  display: flex;
  height: 660px;
  flex-direction: column;
  position: relative;
}
.video-section {
  display: flex;
  flex: 1;
  height: 90vh;
}

/* 변호사 / 의뢰인 화면 */
.video-box {
  flex: 1;
  min-width: 0;
  background-color: black;
  margin: 0.5rem 0.5rem 0 0.5rem ;
  border-radius: 10px;
  position: relative;
}

.vertical-video {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.video-inner {
  flex: 1;
  background-color: black;
  margin: 0.25rem;
  border-radius: 8px;
  position: relative;
}

/* 비디오 박스(또는 video-inner)가 좌표계 기준점이 되도록 */
.video-box,
.video-inner {
  position: relative;
}

/* 왼쪽-하단 라벨 공통 스타일 */
.role-label {
  position: absolute;
  bottom: 15px;
  left: 15px;
  margin: 0;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  text-shadow: 0 0 4px rgba(0, 0, 0, 0.6);
  pointer-events: none;
}
#publisher > .role-label {
  transform: scaleX(-1); /* 좌우 반전을 다시 한번 적용해 원상태로 복구 */
}

.shared-screen {
  flex: 2;
  min-width: 0;
  background-color: black;
  margin: 0.5rem;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  object-fit: cover;
}
/* 2. 비디오 & 캔버스 → 박스 꽉 채우기 */
.shared-screen video,
.shared-screen canvas{
  position:absolute;
  inset:0;
  width:100%;
  height:100%;
  object-fit:contain;
  pointer-events:none;
}
.shared-screen video{
  z-index: 1;
}
.shared-screen canvas{
  z-index: 10;
}
.drawing-canvas{
  position:absolute; inset:0;
  width:100%; height:100%;
  z-index:5;
  pointer-events:none;
}
/* 펜·지우개 커서 깜빡임 안 보이게 */
.drawing-canvas.pen-cursor{ cursor:crosshair; }
.drawing-canvas.eraser-cursor{ cursor:url('data:image/svg+xml;base64,PHN2Zy…') 6 6, crosshair; }


/* 1) 기본값: 큰 화면에서는 점 아이콘 숨김, 원래 버튼 보이기 */
.footer-btn.ellipsis-btn{ display: none; }
.tool-group{ display: flex; gap: 1rem; }

/* 2) 작은 화면일 때 (폭 960px 이하) */
@media (max-width: 960px) {
  .footer-btn.ellipsis-btn {          /* ⋮ 버튼 보이기 */
    display: flex;
  }
  .tool-group {            /* 원래 버튼 숨기기 */
    display: none;
  }
  /* 점 메뉴가 열렸을 때 */
  .tool-group.show {
    display: flex;         /* dropdown 으로 표시 */
    position: absolute;
    bottom: 60px;          /* footer 위로 살짝 띄우기 */
    left: 8px;
    flex-direction: column;
    background: #232627;
    padding: 0.6rem;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    z-index: 20;
  }
  .tool-group.show .footer-btn {
    width: 42px;           /* 버튼들을 작은 정사각형 형태로 */
    height: 42px;
    justify-content: center;
    background: #232627;
  }
}

.meeting-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 1.1rem;
  background-color: #131516;
  height: 9.5vh;
}

/* 좌우 영역 분리 */
.footer-left,
.footer-right {
  display: flex;
  gap: 1rem;
}

/* 채팅 영역과 동일한 너비를 갖도록 */
.footer-right {
  width: 380px; /* 채팅 영역 너비와 일치 */
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-btn-wrapper {
  display: flex;
  gap: 1rem;
}

.footer-btn {
  background-color: #131516;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem; /* 아이콘과 텍스트 사이 간격 */
  color: white;
  border: none;
}

.only-share {
  border: 1px solid white;
  padding: 0.5rem 2rem;
  border-radius: 8px;
}

.footer-label {
  font-size: 1rem;
  color: white;
}


.footer-btn>img{
  margin-top: 2px;
  width: 30px;
  height: 30px;
}

.footer-icon {
  width: 24px;
  height: 24px;
  color: white;
}

/* 채팅 영역 */
.chat-area {
  width: auto;
  display: flex;
  flex-direction: column;
  background-color: #131516;
}

/* 채팅 콘텐츠 (스크롤 가능) */
.chat-content {
  flex: 1;
  overflow-y: auto;
}

.leave-btn {
  color: white;
  font-size: 0.9rem;
  padding: 0.4rem 2rem;
  border-radius: 10px;
  background-color: #c0392b;
}

.leave-btn:hover {
  background-color: #e74c3c;
}

</style>
