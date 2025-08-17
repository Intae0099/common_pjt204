<template>
  <div class="meeting-room">
  <div
    class="video-section"
    :class="{
      sharing: isAnyScreenSharing,
      'chat-open': isChatOpen,
      'chat-closed': !isChatOpen
    }"
  >
    <div class="video-box" id="lawyer-video">
      <p class="role-label">상대방</p>
    </div>

    <div class="video-box" id="publisher" ref="publisherRef">
      <p class="role-label">나</p>
    </div>

    <div class="video-box shared-screen" id="client-video"
         :style="{ display: isAnyScreenSharing ? 'flex' : 'none' }">
      <canvas id="draw-canvas" class="drawing-canvas"></canvas>
    </div>

    <div class="chat-area" v-show="isChatOpen">
      <div class="chat-content">
        <RealtimeChatView
          v-show="activeChat === 'realtime'"
          :session="session"
        />
        <ChatbotView v-show="activeChat === 'chatbot'" />
      </div>
    </div>
  </div>
</div>


<div class="meeting-footer">
  <div class="footer-left">

    <button class="footer-btn ellipsis-btn" @click="isMenuOpen = !isMenuOpen">
      <EllipsisVertical class="footer-icon" />
    </button>

    <div class="tool-group" :class="{ show: isMenuOpen }">
      <button class="footer-btn" @click="clearCanvas" :disabled="!isAnyScreenSharing" title="전체 지우기">
        <RefreshCcw class="footer-icon" />
      </button>
      <button class="footer-btn" @click="setTool('pen')"     :disabled="!isAnyScreenSharing" :class="{ active: currentTool==='pen' }"><Pencil class="footer-icon" /></button>
      <button class="footer-btn" @click="setTool('eraser')"  :disabled="!isAnyScreenSharing" :class="{ active: currentTool==='eraser' }"><Eraser class="footer-icon" /></button>
      <button class="footer-btn" @click="setTool('pointer')" :class="{ active: currentTool==='pointer' }"><MousePointer2 class="footer-icon" /></button>


      <button class="footer-btn" @click="toggleCamera"><component :is="isCameraOn ? Video : VideoOff" class="footer-icon" /></button>
      <button class="footer-btn" @click="toggleMic"><component :is="isMicOn ? Mic : MicOff" class="footer-icon" /></button>
    </div>

    <button
      class="footer-btn only-share"
      :disabled="isAnyScreenSharing && !isMyScreenSharing"
      @click="isMyScreenSharing ? stopScreenShare() : shareScreen()"
    >
      <span class="footer-label">{{ isMyScreenSharing ? '공유중지' : '화면공유' }}</span>
      <Share class="footer-icon" />
    </button>
  </div>

  <div class="footer-right">
    <div class="chat-btn-wrapper">
      <button class="footer-btn" @click="toggleChat('realtime')" :aria-pressed="activeChat==='realtime'">
        <MessageSquareText class="footer-icon icon-chat" :class="{ active: activeChat === 'realtime' }"/>
      </button>
      <button class="footer-btn" @click="toggleChat('chatbot')" :aria-pressed="activeChat==='chatbot'">
        <img src="@/assets/ai-bot.png" class="footer-icon bot-img" :class="{ active: activeChat === 'chatbot' }"/>
      </button>
    </div>

    <button class="footer-btn leave-btn" @click="leaveSession">
      나가기
    </button>
  </div>
</div>

</template>


<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, computed } from 'vue';
import { OpenVidu } from 'openvidu-browser';
import { useRoute, useRouter } from 'vue-router';
import axios from '@/lib/axios';
import RealtimeChatView from '@/features/chatting/RealtimeChatView.vue';
import ChatbotView from '@/features/chatting/ChatbotView.vue';
import { EllipsisVertical, Pencil, Eraser, MousePointer2, MessageSquareText, Share, Video, VideoOff, Mic, MicOff, RefreshCcw } from 'lucide-vue-next';

const activeChat = ref('realtime');
const isChatOpen = computed(() => !!activeChat.value)
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
const screenVideoEl = ref(null);
// 상태 관리
const isCameraOn = ref(true);
const isMicOn = ref(true);
const isAnyScreenSharing = ref(false);   // 누군가 공유 중
const isMyScreenSharing  = ref(false);   // 내가 공유 중

const DRAW_SIG = 'drawing';
let sendBuf = [];
let rafId = null;


function flushSegments(tool, color, width){
  if (!session.value || sendBuf.length === 0) return;
  const pts = sendBuf; sendBuf = []; rafId = null;
  session.value.signal({
    type: DRAW_SIG,
    data: JSON.stringify({ op: 'seg', t: tool, c: color, w: width, pts })
  });
}

function clearHolderKeepCanvas(holder) {
  if (!holder) return;
  // 우리가 만든 미리보기만 제거
  const local = holder.querySelector('.local-preview');
  if (local?.parentNode) local.parentNode.removeChild(local);
  // ❗ OpenVidu가 만든 요소(OV_video-container, <video> 등)는 절대 건드리지 않기
}

//펜 컬러/굵기
const penColor = ref('#4da3ff');
const penWidth = ref(2);
const eraserWidth = ref(20);

// 공통 선 스타일(끝 삐죽 방지)
function applyCommonStrokeStyle(context) {
  context.lineCap = 'round';
  context.lineJoin = 'round';
}

function applyToolToCanvas() {
  // 항상 최신 DOM에서 다시 찾아서 보장
  const el = document.getElementById('draw-canvas');
  if (!el) return;

  // 전역 참조도 갱신 (혹시 바뀌었을 수 있음)
  if (canvas !== el) {
    canvas = el;
    ctx = canvas.getContext('2d');
  }

  // 툴 상태 강제 적용
  const tool = currentTool.value;
  el.style.pointerEvents = tool === 'pointer' ? 'none' : 'auto';
  el.classList.remove('pen-cursor', 'eraser-cursor');
  if (tool === 'pen') el.classList.add('pen-cursor');
  if (tool === 'eraser') el.classList.add('eraser-cursor');

  el.style.cursor = (tool === 'pointer') ? 'default' : 'crosshair';

  // 비디오가 포인터를 가로채지 못하게 최상단 확보
  el.style.zIndex = '999';
  const holder = document.getElementById('client-video');
  if (holder) holder.style.position = 'relative';
}


function isScreenStream(stream) {
  const t = stream?.typeOfVideo?.toUpperCase?.();
  if (t === 'SCREEN') return true;
  const label = stream?.getMediaStream?.()?.getVideoTracks?.()?.[0]?.label?.toLowerCase?.() || '';
  return label.includes('screen') || label.includes('share');
}




/* ---------- 그리기 상태 ---------- */
const currentTool = ref('pointer');
const isDrawing = ref(false);
let canvas, ctx;
let rect, dpr = 1;

// rect/DPR 기반으로 캔버스를 세팅
function resizeCanvas() {
  if (!canvas) return;
  rect = canvas.getBoundingClientRect();
  dpr = window.devicePixelRatio || 1;

  // 내부 비트맵 크기를 DPR 반영해서 설정
  canvas.width  = Math.round(rect.width  * dpr);
  canvas.height = Math.round(rect.height * dpr);

  // 논리 좌표(화면상의 CSS 픽셀)로 그리기 위해 변환
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0); // reset + scale
  applyCommonStrokeStyle(ctx);
}

// 마우스 좌표: 항상 CSS 좌표로
function getPos(e) {
  // clientX/Y - rect.left/top = CSS 픽셀 상의 좌표
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  return { x, y };
}

// 정규화(보낼 때): rect 기준
function nxy_css(x, y) {
  return { x: x / rect.width, y: y / rect.height };
}

// 역정규화(받을 때): rect 기준
function dxy_css(p) {
  return { x: p.x * rect.width, y: p.y * rect.height };
}

function setTool(tool) {
  currentTool.value = tool;
  applyToolToCanvas();
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
  if (!isAnyScreenSharing.value) return;
  if (currentTool.value === 'pointer') return;
  isDrawing.value = true;

  applyCommonStrokeStyle(ctx);

  const tool = currentTool.value;
  if (tool === 'pen') {
    ctx.globalCompositeOperation = 'source-over';
    ctx.lineWidth = penWidth.value;
    ctx.strokeStyle = penColor.value;
  } else {
    ctx.globalCompositeOperation = 'destination-out';
    ctx.lineWidth = eraserWidth.value;
  }

  const { x, y } = getPos(e);
  ctx.beginPath();
  ctx.moveTo(x, y);

  const p = nxy_css(x, y);
  session.value?.signal({
    type: DRAW_SIG,
    data: JSON.stringify({
      op: 'start',
      t: tool,
      p,
      c: penColor.value,
      w: tool === 'pen' ? penWidth.value : eraserWidth.value
    })
  });
}

function draw(e) {
  if (!isDrawing.value) return;

  const tool = currentTool.value;
  if (tool === 'pen') {
    ctx.globalCompositeOperation = 'source-over';
    ctx.lineWidth = penWidth.value;
    ctx.strokeStyle = penColor.value;
  } else {
    ctx.globalCompositeOperation = 'destination-out';
    ctx.lineWidth = eraserWidth.value;
  }

  const { x, y } = getPos(e);
  ctx.lineTo(x, y);
  ctx.stroke();

  const np = nxy_css(x, y);
  sendBuf.push(np);

  if (!rafId) {
    const t = tool;
    const color = penColor.value;
    const width = tool === 'pen' ? penWidth.value : eraserWidth.value;
    rafId = requestAnimationFrame(() => flushSegments(t, color, width));
  }
}


function endDraw() {
  if (!isDrawing.value) return;
  isDrawing.value = false;
  ctx.closePath();

  // 남은 포인트 flush
  const tool = currentTool.value;
  const color = penColor.value;
  const width = tool === 'pen' ? penWidth.value : eraserWidth.value;
  flushSegments(tool, color, width);

  session.value?.signal({
    type: DRAW_SIG,
    data: JSON.stringify({ op: 'end' })
  });
}


function safeEnsureCanvasReady() {
  if (!canvas || !ctx) {
    const el = document.getElementById('draw-canvas');
    if (el) {
      canvas = el;
      ctx = canvas.getContext('2d');
      resizeCanvas();
    }
  }
}

// === 상대방 그리기: 받은 색/굵기 그대로 적용
async function handleRemoteDraw({ data }) {
  const msg = JSON.parse(data);

  // 캔버스가 아직이면 한 틱 뒤 재시도
  if (!canvas || !ctx) {
    await nextTick();
    safeEnsureCanvasReady();
    if (!canvas || !ctx) return; // 아직 레이아웃이 안 열렸으면 무시(다음 메시지에서 그려짐)
  }

  if (msg.op === 'clear') { clearCanvasLocal(); return; }

  const isPen = msg.t === 'pen';
  const color = msg.c ?? '#000000';
  const width = msg.w ?? (isPen ? 2 : 20);

  applyCommonStrokeStyle(ctx);

  if (msg.op === 'start') {
    ctx.globalCompositeOperation = isPen ? 'source-over' : 'destination-out';
    ctx.lineWidth = width;
    if (isPen) ctx.strokeStyle = color;
    const { x, y } = dxy_css(msg.p);
    ctx.beginPath();
    ctx.moveTo(x, y);
    return;
  }

  if (msg.op === 'seg') {
    ctx.globalCompositeOperation = isPen ? 'source-over' : 'destination-out';
    ctx.lineWidth = width;
    if (isPen) ctx.strokeStyle = color;
    for (const pt of msg.pts) {
      const { x, y } = dxy_css(pt);
      ctx.lineTo(x, y);
    }
    ctx.stroke();
    return;
  }

  if (msg.op === 'end') ctx.closePath();
}


// 로컬 캔버스만 지우는 내부 함수
function clearCanvasLocal() {
  if (!ctx || !canvas) return;
  // 그리는 중이면 끊어주기
  isDrawing.value = false;
  // 변환 영향 없이 전체 지우기
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.restore();
}

// 버튼 클릭 -> 로컬 지우고 브로드캐스트
const clearCanvas = () => {
  if (!isAnyScreenSharing.value) return;
  clearCanvasLocal();
  session.value?.signal({
    type: DRAW_SIG,
    data: JSON.stringify({ op: 'clear' })
  });
};


let canvasRO = null;

async function initCanvas() {
  await nextTick();
  const el = document.getElementById('draw-canvas');
  if (!el) return;

  // 기존 옵저버/리스너 정리
  canvasRO?.disconnect(); canvasRO = null;
  window.removeEventListener('resize', resizeCanvas);

  canvas = el;
  ctx = canvas.getContext('2d');
  resizeCanvas();

  canvas.onmousedown  = startDraw;
  canvas.onmousemove  = draw;
  canvas.onmouseup    = endDraw;
  canvas.onmouseleave = endDraw;

  canvasRO = new ResizeObserver(() => resizeCanvas());
  canvasRO.observe(canvas);
  window.addEventListener('resize', resizeCanvas);

  setTool(currentTool.value);
  applyToolToCanvas();
}


// ✅ [핵심 수정] 안정적인 콜백 기반으로 전체 로직 변경
onMounted(() => {
  OV.value = new OpenVidu();
  OV.value.enableProdMode();
  session.value = OV.value.initSession();

  // 1. 상대방 스트림이 생겼을 때의 이벤트 핸들러
  // 바꿔치기
  session.value.on('streamCreated', async (event) => {
    const stream = event.stream;

  if (isScreenStream(stream)) {
    const isOwnScreen =
      !!screenSession.value &&
      stream?.connection?.connectionId === screenSession.value.connection.connectionId;

    isAnyScreenSharing.value = true;
    await nextTick();
    const holder = document.getElementById('client-video');

    if (isOwnScreen) {
      requestAnimationFrame(() => {
        resizeCanvas();
        initCanvas();
        applyToolToCanvas();
      });
      return;
    }

    // 상대 화면 구독
    const subscriber = session.value.subscribe(stream, holder);
    subscriber.on('videoElementCreated', () => {
      // ⬇ 비디오 DOM이 붙은 직후 프레임에 initCanvas() 실행
      requestAnimationFrame(() => {
        resizeCanvas();
        initCanvas();
        applyToolToCanvas();
      });
    });
    subscribers.value.push(subscriber);
    return;
  }

    // 일반 카메라
    const sub = session.value.subscribe(stream, 'lawyer-video');
    subscribers.value.push(sub);
  });




session.value.on('streamDestroyed', (event) => {
  subscribers.value = subscribers.value.filter(
    (sub) => sub.stream.streamId !== event.stream.streamId
  );

  if (isScreenStream(event.stream)) {
    isAnyScreenSharing.value = false;
    setTool('pointer');
    clearCanvasLocal();

    // ✅ 캔버스 리스너/옵저버 재설정
    initCanvas();
    applyToolToCanvas();
  }
});



  // 3. 드로잉 시그널 이벤트 핸들러
  session.value.on('signal:drawing', handleRemoteDraw);

  // 4. 세션에 연결
  session.value.connect(token, { clientData: '사용자' })
    .then(() => {

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

            // 6. Publisher 초기화 성공 시, 세션에 내 스트림을 게시
            session.value.publish(publisher)
              .then(() => {
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
});

const isScreenStopping = ref(false);
const stopScreenShare = ({ silent = false } = {}) => {
  if (!screenPublisher.value) return;
  isScreenStopping.value=true
  try {
    const screenStream = screenPublisher.value.stream?.getMediaStream();
    if (screenStream) {
      screenStream.getTracks().forEach(track => track.stop());
    }
    if (screenSession.value) screenSession.value.disconnect();
  } catch(e) {
    console.error("Error during screen share stop:", e);
  } finally {

    try {
      screenPublisher.value?.removeVideoElement(screenVideoEl.value);
    } catch (err) {
      console.warn('removeVideoElement 실패', err);
    }
    screenVideoEl.value=null

    screenPublisher.value = null;
    screenSession.value = null;
    screenOV.value = null;

    isMyScreenSharing.value  = false;
    isAnyScreenSharing.value = false;
    setTool('pointer');
    try {
      screenPublisher.value?.removeVideoElement(screenVideoEl.value);
    } catch (err) {console.warn('removeVideoElement 실패', err);}
    screenVideoEl.value = null;
    if (!silent);
      isScreenStopping.value = false;
  }
};




// 화면 공유를 시작하는 함수
const shareScreen = async () => {
  if (isAnyScreenSharing.value && !isMyScreenSharing.value) {
    alert('이미 다른 참가자가 화면을 공유 중입니다.');
    return;
  }
  try {
    const { data } = await axios.post(`/api/rooms/${appointmentId}/screenshare`);
    const screenToken = data.data.openviduToken;

    screenOV.value = new OpenVidu();
    screenOV.value.enableProdMode();
    screenSession.value = screenOV.value.initSession();

    screenSession.value.on('sessionDisconnected', () => {
      if (!isScreenStopping.value) {
        stopScreenShare({silent: true});
      }
    });

    await screenSession.value.connect(screenToken, { clientData: 'screenshare' });
    screenPublisher.value = await screenOV.value.initPublisherAsync(undefined, {
      videoSource: 'screen',
      publishAudio: false,
      publishVideo: true,
      mirror: false,
    });
    await screenSession.value.publish(screenPublisher.value);

    // 먼저 플래그 켜서 레이아웃/컨테이너가 보이게
    isAnyScreenSharing.value = true;
    isMyScreenSharing.value  = true;
    await nextTick();

    // 내 미리보기 비디오 붙이기
    const holder = document.getElementById('client-video');
    if (holder) {
      clearHolderKeepCanvas(holder);

      const v = document.createElement('video');
      v.setAttribute('playsinline', 'true');
      v.autoplay = true;
      v.muted = true;
       v.classList.add('local-preview');
      Object.assign(v.style, {
        position: 'absolute', inset: '0',
        width: '100%', height: '100%',
        objectFit: 'contain', zIndex: 1
      });

      holder.prepend(v);
      screenPublisher.value.addVideoElement(v);
      screenVideoEl.value = v;
      applyToolToCanvas();
    }

    initCanvas(); // 캔버스는 위(z-index 10)

    const track = screenPublisher.value.stream.getMediaStream().getVideoTracks()[0];
    track?.addEventListener('ended', () => stopScreenShare());
  } catch (err) {
    console.error('화면공유 실패:', err);
    alert(err.response?.data?.message || '화면공유를 시작할 수 없습니다.');
  }
};

// 퇴장 함수
const leaveSession = () => {

  // 1. 화면 공유가 활성 상태이면 먼저 정리
  if (isMyScreenSharing.value && screenPublisher.value) {
    stopScreenShare({ silent: true }); // 조용히 종료
  }

  // 2. 메인 카메라/마이크 스트림의 모든 트랙을 직접 중지 (가장 중요)
  const mainStream = mainStreamManager.value?.stream?.getMediaStream();
  if (mainStream) {
    mainStream.getTracks().forEach(track => {
      track.stop();
    });
  }

  // 3. 메인 세션 연결을 해제
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

.meeting-room {
  display: flex;
  /* height: 660px; */
  flex-direction: column;
  position: relative;
}
.video-section {
  display: grid;
  grid-template-columns: 1fr 1fr 380px;   /* 기본: 좌우 카메라 + 채팅 */
  grid-template-rows: 1fr;
  grid-template-areas: "lawyer publisher chat";
  gap: 0.5rem;
  height: calc(100vh - 9.5vh);
  overflow: hidden;
  min-height: 0;
}
.video-section > * {
  min-height: 0;
  min-width: 0;
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

/* 평소(공유 X) + 채팅 열림 */
.video-section.chat-open:not(.sharing) {
  grid-template-columns: 1fr 1fr 380px;
  grid-template-areas: "lawyer publisher chat";
}

/* 평소(공유 X) + 채팅 닫힘 → 두 칼럼만 */
.video-section.chat-closed:not(.sharing) {
  grid-template-columns: 1fr 1fr;
  grid-template-areas: "lawyer publisher";
}

/* 화면공유 + 채팅 열림*/
.video-section.sharing.chat-open {
  grid-template-columns: 1fr 2fr 380px;
  grid-template-rows: 1fr 1fr;
  grid-template-areas:
    "lawyer  shared chat"
    "publisher shared chat";
}

/* 화면공유 + 채팅 닫힘 → 오른쪽 열 제거 */
.video-section.sharing.chat-closed {
  grid-template-columns: 1fr 2fr;
  grid-template-rows: 1fr 1fr;
  grid-template-areas:
    "lawyer  shared"
    "publisher shared";
}

/* 변호사 / 의뢰인 화면 */
.video-box {
  min-width: 0;
  min-height: 0;
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
.video-box:not(.shared-screen) :deep(video) {
  object-fit: cover;
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
.shared-screen canvas.drawing-canvas {
  pointer-events: auto;
  z-index: 10;
}
.shared-screen video{
  position:absolute;
  inset:0;
  width:100%;
  height:100%;
  object-fit:contain;
  z-index: 1;
}
.shared-screen :deep(video) {
  object-fit: contain;
  background: #000;
  pointer-events: none
}
.shared-screen :deep(.OV_video-container) {
  pointer-events: none !important;
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
/* 비활성(회색) 처리 */
.footer-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
  filter: grayscale(1);
}

/* 아이콘도 같이 흐리게 */
.footer-btn:disabled .footer-icon {
  opacity: 0.7;
}
/* 선택 상태(파란 강조) */
.footer-btn.active {
  outline: 1px solid #4da3ff;
  background: rgba(77,163,255,0.1);
  border-radius: 8px;
}

.footer-btn.active .footer-icon {
  color: #4da3ff;
}

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

.chat-btn-wrapper .icon-chat { color: #9aa3ab; transition: color .15s ease; }
.chat-btn-wrapper .icon-chat.active { color: #ffffff; }

.chat-btn-wrapper .bot-img {
  filter: grayscale(1) brightness(0.9);
  opacity: .6;
  transition: filter .15s ease, opacity .15s ease;
}
.chat-btn-wrapper .bot-img.active {
  filter: none;
  opacity: 1;
}

.chat-btn-wrapper .footer-btn:hover .icon-chat:not(.active) { color: #b7c0c7; }
.chat-btn-wrapper .footer-btn:hover .bot-img:not(.active) { opacity: .75; }

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
  min-height: 0;
  overflow: hidden;
  background-color: #131516;
}

/* 채팅 콘텐츠 (스크롤 가능) */
.chat-content {
  flex: 1;
  min-height: 0;
  display: flex;
  align-items: stretch;
}

.chat-content > * {
  display: flex;
  flex: 1 1 auto;
  min-height: 0;
}

.chat-content > * > * {
  flex: 1 1 auto;
  min-height: 0;
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
