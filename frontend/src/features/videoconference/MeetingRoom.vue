<template>
  <div class="meeting-room">
  <div class="video-section" :class="{ sharing: isScreenSharing }">
    <!-- 왼쪽: 변호사/의뢰인 비디오 (한 세트만 유지) -->
    <div class="video-box" id="lawyer-video">
      <p class="role-label">상대방</p>
    </div>

    <div class="video-box" id="publisher" ref="publisherRef">
      <p class="role-label">나</p>
    </div>

    <!-- 가운데: 공유화면 (평소엔 숨김만) -->
    <div class="video-box shared-screen" id="client-video"
         :style="{ display: isScreenSharing ? 'flex' : 'none' }">
      <canvas id="draw-canvas" class="drawing-canvas"></canvas>
    </div>

    <!-- 오른쪽: 채팅 -->
    <div class="chat-area">
      <div class="chat-content">
        <RealtimeChatView
          v-show="activeChat === 'realtime'"
          :messages="messages"
          @send-message="sendChatMessage"
        />
        <ChatbotView v-show="activeChat === 'chatbot'" />
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
    <button class="footer-btn only-share" @click="isScreenSharing ? stopScreenShare() : shareScreen()">
      <span class="footer-label">{{ isScreenSharing ? '공유중지' : '화면공유' }}</span>
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
import { ref, onMounted, onBeforeUnmount, nextTick, provide } from 'vue';
import { OpenVidu } from 'openvidu-browser';
import { useRoute, useRouter } from 'vue-router';
import axios from '@/lib/axios';
import RealtimeChatView from '@/features/chatting/RealtimeChatView.vue';
import ChatbotView from '@/features/chatting/ChatbotView.vue';
import { EllipsisVertical, Pencil, Eraser, MousePointer2, MessageSquareText, Share, Video, VideoOff, Mic, MicOff } from 'lucide-vue-next';

const activeChat = ref('realtime');
const toggleChat = (type) => {
  activeChat.value = activeChat.value === type ? null : type;
};

// 채팅 더미 (나중에 실제 스토어/소켓 연동으로 교체)
const messages = ref([])
const sendChatMessage = (msg) => { messages.value.push({ me:true, text: msg }) }


// OpenVidu 관련 객체들 상태로 관리
const OV = ref(null);
const session = ref(null);  //메인(카메라/마이크)
const mainStreamManager = ref(null);
const subscribers = ref([]);

//화면공유 전용
const screenOV = ref(null)
const screenSession = ref(null)        // 화면공유용 세션 (두 번째 연결)
const screenPublisher = ref(null)      // 화면공유 Publisher

const isMenuOpen = ref(false);
const route = useRoute();
const router = useRouter();

const publisherRef = ref(null); // 내 비디오를 붙일 DOM 요소

// 상태 관리
const isCameraOn = ref(true);
const isMicOn = ref(true);
const isScreenSharing = ref(false);

const DRAW_SIG = 'drawing';
let sendBuf = [];
let rafId = null;

function nxy(x, y) {                // normalize 0..1
  return { x: x / canvas.width, y: y / canvas.height };
}
function dxy(p) {                    // denormalize to local canvas px
  return { x: p.x * canvas.width, y: p.y * canvas.height };
}

function flushSegments(tool){
  if (!session.value || sendBuf.length === 0) return;
  const pts = sendBuf; sendBuf = []; rafId = null;
  session.value.signal({
    type: DRAW_SIG,
    data: JSON.stringify({ op: 'seg', t: tool, pts })
  });
}

/* ---------- 그리기 상태 ---------- */
const currentTool = ref('pointer');
const isDrawing = ref(false);
let canvas, ctx;

function setTool(tool) {
  currentTool.value = tool;
  if (!canvas) return;
  canvas.style.pointerEvents = tool === 'pointer' ? 'none' : 'auto';
  canvas.classList.toggle('pen-cursor', tool === 'pen');
  canvas.classList.toggle('eraser-cursor', tool === 'eraser');
}

// URL 쿼리에서 토큰과 예약 ID 받아오기
const token = route.query.token;
const appointmentId = route.query.appointmentId;

// 카메라 토글 함수
const toggleCamera = () => {
  if (mainStreamManager.value) {
    isCameraOn.value = !isCameraOn.value;
    mainStreamManager.value.publishVideo(isCameraOn.value);
  }
};

// 마이크를 켜고 끄는 함수
const toggleMic = () => {
  if (mainStreamManager.value) {
    isMicOn.value = !isMicOn.value;
    mainStreamManager.value.publishAudio(isMicOn.value);
  }
};

/* ---------- 로컬 그리기 (이하 생략된 부분은 기존 코드와 동일) ---------- */
function startDraw(e) {
  if (currentTool.value === 'pointer') return;
  isDrawing.value = true;

  ctx.beginPath();
  ctx.moveTo(e.offsetX, e.offsetY);

  // 상대에게 "시작" 알림 + 시작점
  const p = nxy(e.offsetX, e.offsetY);
  session.value?.signal({
    type: DRAW_SIG,
    data: JSON.stringify({ op: 'start', t: currentTool.value, p })
  });
}

function draw(e) {
  if (!isDrawing.value) return;

  const tool = currentTool.value;           // ← 캡쳐

  if (tool === 'pen') {
    ctx.globalCompositeOperation = 'source-over';
    ctx.lineWidth = 2;
    ctx.strokeStyle = 'red';
  } else if (tool === 'eraser') {
    ctx.globalCompositeOperation = 'destination-out';
    ctx.lineWidth = 20;
  }

  ctx.lineTo(e.offsetX, e.offsetY);
  ctx.stroke();

  sendBuf.push(nxy(e.offsetX, e.offsetY));
  if (!rafId) {
    const t = tool;                         // ← 캡쳐한 값으로 고정
    rafId = requestAnimationFrame(() => flushSegments(t));
  }
}


function endDraw() {
  if (!isDrawing.value) return;
  isDrawing.value = false;
  ctx.closePath();

  // 남은 포인트 있으면 마지막으로 flush
  flushSegments(currentTool.value);

  // 상대에게 "끝" 알림
  session.value?.signal({
    type: DRAW_SIG,
    data: JSON.stringify({ op: 'end' })
  });
}

function sendSignal(payload) {
  if(!session.value) return;
  session.value.signal({ type: 'drawing', data: JSON.stringify(payload) });
}

function handleRemoteDraw({ data }) {
  const msg = JSON.parse(data);

  if (msg.op === 'start') {
    // 툴 미리 적용
    ctx.globalCompositeOperation = msg.t === 'pen' ? 'source-over' : 'destination-out';
    ctx.lineWidth = msg.t === 'pen' ? 2 : 20;

    const { x, y } = dxy(msg.p);
    ctx.beginPath();
    ctx.moveTo(x, y);
    return;
  }

  if (msg.op === 'seg') {
    ctx.globalCompositeOperation = msg.t === 'pen' ? 'source-over' : 'destination-out';
    ctx.lineWidth = msg.t === 'pen' ? 2 : 20;
    for (const pt of msg.pts) {
      const { x, y } = dxy(pt);
      ctx.lineTo(x, y);
    }
    ctx.stroke();
    return;
  }

  if (msg.op === 'end') {
    ctx.closePath();
  }
}



async function initCanvas() {
  await nextTick();
  canvas = document.getElementById('draw-canvas');
  if(!canvas) return;
  ctx = canvas.getContext('2d');
  canvas.width = canvas.offsetWidth;
  canvas.height = canvas.offsetHeight;

  console.log('PE before tool =', getComputedStyle(canvas).pointerEvents);
  canvas.addEventListener('mousedown', startDraw);
  canvas.addEventListener('mousemove', draw);
  canvas.addEventListener('mouseup', endDraw);
  canvas.addEventListener('mouseleave', endDraw);
}

// ✅ [핵심 수정] 안정적인 콜백 기반으로 전체 로직 변경
onMounted(() => {
  OV.value = new OpenVidu();
  OV.value.enableProdMode();
  session.value = OV.value.initSession();

  // 1. 상대방 스트림이 생겼을 때의 이벤트 핸들러
  // 바꿔치기
  session.value.on('streamCreated', (event) => {
    // 화면공유 스트림인지 판별
    const isScreen =
      event.stream?.typeOfVideo === 'SCREEN' ||
      event.stream?.getMediaStream()?.getVideoTracks()?.[0]?.label
        ?.toLowerCase()
        .includes('screen');

    const targetId = isScreen ? 'client-video' : 'lawyer-video';

    const subscriber = session.value.subscribe(event.stream, targetId);
    subscribers.value.push(subscriber);

    if (isScreen) {
      isScreenSharing.value = true;     // 보는 사람 쪽도 레이아웃 전환
      nextTick(() => initCanvas());     // 캔버스 초기화
    }
  });


  session.value.on('streamDestroyed', (event) => {
    subscribers.value = subscribers.value.filter(
      (sub) => sub.stream.streamId !== event.stream.streamId
    );

    const isScreen = event.stream?.typeOfVideo === 'SCREEN';
    if (isScreen) {
      isScreenSharing.value = false;
      const el = document.getElementById('client-video');
      if (el) el.innerHTML = '<canvas id="draw-canvas" class="drawing-canvas"></canvas>';
    }
  });

  // 3. 드로잉 시그널 이벤트 핸들러
  session.value.on('signal:drawing', handleRemoteDraw);

  // 4. 세션에 연결
  session.value.connect(token, { clientData: '사용자' })
    .then(() => {
      console.log("세션 연결 성공!");

      // 5. 내 카메라/마이크(Publisher) 초기화
      const publisher = OV.value.initPublisher(
        publisherRef.value, // 비디오를 붙일 DOM 요소를 직접 전달
        {
          audioSource: undefined,
          videoSource: undefined,
          publishAudio: true,
          publishVideo: true,
          resolution: '640x480',
          frameRate: 30,
          mirror: true,
        },
        (error) => {
          if (error) {
            console.error('Publisher 초기화 실패:', error);
            alert("카메라/마이크를 초기화하는 데 실패했습니다.");
          } else {
            console.log('Publisher 초기화 성공!');

            // 6. Publisher 초기화 성공 시, 세션에 내 스트림을 게시
            session.value.publish(publisher)
              .then(() => {
                console.log("스트림 게시 성공!");
                mainStreamManager.value = publisher; // 상태에 저장
              })
              .catch(error => {
                console.error('스트림 게시 실패:', error);
              });
          }
        }
      );
    })
    .catch(error => {
      console.error('세션 연결 실패:', error);
      alert("화상회의 서버에 연결할 수 없습니다.");
    });
    // 파일 상단 어디든(예: onMounted 끝부분)
    console.log('axios baseURL =', axios.defaults.baseURL)
    console.log('axios Authorization =', axios.defaults.headers.common?.Authorization)

});


const stopScreenShare = ({ silent = false } = {}) => {
  try {
    if (screenPublisher.value) {
      try { screenPublisher.value.stream.getMediaStream().getTracks().forEach(t => t.stop()) } catch {}
      screenPublisher.value.destroy?.()
    }
    if (screenSession.value) screenSession.value.disconnect()
    // 공유 미리보기 비우기
    const el = document.getElementById('client-video')
    if (el) el.innerHTML = ''
  } finally {
    screenPublisher.value = null
    screenSession.value = null
    screenOV.value = null
    isScreenSharing.value = false
    if (!silent) console.log('화면공유 종료')
  }
}



// 화면 공유를 시작하는 함수
const shareScreen = async () => {
  console.log('token from query=', token)
  console.log('appointmentId from query=', appointmentId)

  try {
    // 1) 백엔드에서 화면공유 토큰 받기
    console.log('screenshare call:', `/api/rooms/${appointmentId}/screenshare`)
    const { data } = await axios.post(`/api/rooms/${appointmentId}/screenshare`)
    if (!data?.success) throw new Error(data?.message || '화면공유 토큰 발급 실패')
    const screenToken = data.data.openviduToken

    // 2) 화면공유용 OpenVidu/Session 별도 생성
    screenOV.value = new OpenVidu()
    screenOV.value.enableProdMode()
    screenSession.value = screenOV.value.initSession()

    // (선택) 이벤트: 재연결/종료 로그 등 필요시 추가
    screenSession.value.on('sessionDisconnected', (e) => {
      console.log('화면공유 세션 종료', e)
      stopScreenShare({ silent: true })
    })

    // 3) 화면공유 세션 연결
    await screenSession.value.connect(screenToken, { clientData: 'screenshare' })

    // 4) 화면공유 Publisher 생성 (오직 비디오만, 오디오X 권장)
    screenPublisher.value = await screenOV.value.initPublisherAsync(undefined, {
      videoSource: 'screen',
      publishAudio: false,
      publishVideo: true,
      mirror: false,
    })

    // 5) 해당 세션에 화면공유 스트림 게시
    await screenSession.value.publish(screenPublisher.value)

    // 7) 브라우저 화면공유 종료 이벤트(사용자가 ‘공유 중지’ 누르면)
    const track = screenPublisher.value.stream.getMediaStream().getVideoTracks()[0]
    if (track) {
      track.addEventListener('ended', () => {
        stopScreenShare()
      })
    }

    await initCanvas()
    isScreenSharing.value = true
    console.log('화면공유 시작')

  } catch (err) {
    console.error('화면공유 실패:', err)
    console.error('status=', err.response?.status)
    console.error('data=', JSON.stringify(err.response?.data, null, 2))
    alert(err.response?.data?.message || '화면공유를 시작할 수 없습니다.')
  }
}



// 퇴장 함수
const leaveSession = () => {
  // 1. Publisher 리소스 해제
  if (mainStreamManager.value && typeof mainStreamManager.value.destroy === 'function') {
    mainStreamManager.value.destroy();
  }

  // 2. Session 연결 해제
  if (session.value) {
    session.value.disconnect();
  }

  // 3. 모든 상태 초기화
  session.value = null;
  mainStreamManager.value = null;
  subscribers.value = [];
  OV.value = null;

  // 4. 백엔드에 퇴장 알림 (실패해도 페이지 이동은 되어야 함)
  axios.delete(`/api/rooms/${appointmentId}/participants/me`).catch(e => {
    console.warn('퇴장 요청 실패:', e);
  });

  // 5. 메인 페이지로 이동
  router.push('/');
};

// 컴포넌트 언마운트 시 세션 정리
onBeforeUnmount(() => {
  leaveSession();
});
</script>

<style scoped>
*{
  font-family: 'Noto Sans KR', sans-serif;
}
html, body, .meeting-room { background: #131516; }
.meeting-room,
.meeting-room * ,
.meeting-room *::before,
.meeting-room *::after {
  box-sizing: content-box;   /* 이 화면 안에서만 content-box로 복원 */
}
.meeting-room {
  display: flex;
  height: 660px;
  flex-direction: column;
  position: relative;
}
.video-section {
  display: grid;
  grid-template-columns: 1fr 1fr 380px;   /* 기본: 좌우 카메라 + 채팅 */
  grid-template-rows: 1fr;
  grid-template-areas: "lawyer publisher chat";
  gap: 0.5rem;
  height: 90vh;
}

#lawyer-video   { grid-area: lawyer; }
#publisher      { grid-area: publisher; }
.shared-screen  { grid-area: shared; }  /* 기본 모드에선 숨김 상태라 영역만 예약 */
.chat-area      { grid-area: chat; }

/* 화면공유 모드: 왼쪽 열(위/아래=2행), 가운데는 공유화면(2행 병합), 오른쪽은 채팅(2행 병합) */
.video-section.sharing {
  grid-template-columns: 1fr 2fr 380px;
  grid-template-rows: 1fr 1fr;
  grid-template-areas:
    "lawyer  shared chat"
    "publisher shared chat";
}

/* 변호사 / 의뢰인 화면 */
.video-box {
  min-width: 0;
  background-color: black;
  border-radius: 10px;
  position: relative;
}

/* 비디오 박스(또는 video-inner)가 좌표계 기준점이 되도록 */
.video-box,
.video-inner {
  position: relative;
}

.video-box :deep(video) {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 컨테이너를 비율에 맞게 꽉 채웁니다 */
  display: block;    /* 불필요한 여백을 제거합니다 */
  border-radius: 10px; /* 부모 요소와 스타일에 맞게 둥글게 처리 */
}

/* 내 화면(publisher)은 좌우 반전되어 있으므로, 그 안의 라벨만 다시 정상으로 돌려놓습니다 */
#publisher :deep(.role-label) {
  transform: scaleX(1);
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

.shared-screen canvas{
  position:absolute;
  inset:0;
  width:100%;
  height:100%;
  object-fit:contain;
  pointer-events: auto;
  z-index: 10;
  background: transparent;
}
.shared-screen video{
  position:absolute;
  inset:0;
  width:100%;
  height:100%;
  object-fit:contain;
  z-index: 1;
}
.drawing-canvas{
  position:absolute; inset:0;
  width:100%; height:100%;
  z-index:5;
  pointer-events: auto;
  background: transparent;
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
  width: 370px; /* 채팅 영역 너비와 일치 */
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
