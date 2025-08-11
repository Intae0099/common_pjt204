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
// --- 라이브러리 및 컴포넌트 불러오기 ---
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { OpenVidu } from 'openvidu-browser';
import { useRoute, useRouter } from 'vue-router';
import axios from '@/lib/axios';
import RealtimeChatView from '@/features/chatting/RealtimeChatView.vue';
import ChatbotView from '@/features/chatting/ChatbotView.vue';
import { EllipsisVertical, Pencil, Eraser, MousePointer2, MessageSquareText, Share, Video, VideoOff, Mic, MicOff } from 'lucide-vue-next';

// --- 전역 상태 관리 ---

// 현재 활성화된 채팅창이 무엇인지 관리 ('realtime' 또는 'chatbot')
const activeChat = ref('realtime');
// OpenVidu 화상 통신 관련 핵심 객체들
const OV = ref(null);                  // OpenVidu 라이브러리의 메인 객체 (엔진)
const session = ref(null);             // 화상회의 방(세션) 정보를 담는 객체
const mainStreamManager = ref(null);   // '나'의 비디오/오디오 정보를 관리하는 객체
const subscribers = ref([]);           // '상대방'들의 비디오/오디오 정보를 담는 배열

// Vue 라우터 관련 객체들
const route = useRoute();   // 현재 페이지의 URL 정보에 접근하기 위함
const router = useRouter(); // 다른 페이지로 이동시키기 위함

// UI 상태를 관리하는 변수들
const isMenuOpen = ref(false);      // 모바일 화면에서 메뉴가 열렸는지 여부
const isCameraOn = ref(true);       // 카메라가 켜져 있는지 여부
const isMicOn = ref(true);          // 마이크가 켜져 있는지 여부
const isScreenSharing = ref(false); // 화면 공유 중인지 여부

// 채팅 기능을 위한 상태 변수들
const messages = ref([]);     // 모든 채팅 메시지를 저장하는 배열
const myUserName = ref('나'); // 내 이름 (세션 연결 시 실제 이름으로 설정됨)

// 그리기 기능을 위한 상태 변수들
const currentTool = ref('pointer'); // 현재 선택된 그리기 도구 ('pen', 'eraser', 'pointer')
const isDrawing = ref(false);       // 현재 그림을 그리고 있는 중인지 여부
let canvas, ctx;                    // 그림을 그릴 캔버스(DOM 요소)와 그리기 도구(context)

// --- 함수 정의 ---

// 채팅창 타입을 변경하는 함수 (실시간 채팅 ↔ 챗봇)
const toggleChat = (type) => {
  // 이미 열려있는 탭을 다시 누르면 닫고, 아니면 해당 탭으로 교체
  activeChat.value = activeChat.value === type ? null : type;
};

// 채팅 메시지를 전송하는 함수
const sendChatMessage = (text) => {
  // 세션이 없거나 메시지가 비어있으면 아무것도 하지 않음
  if (!session.value || text.trim() === '') return;

  // 서버로 보낼 메시지 데이터 객체 생성
  const messageData = { text: text, name: myUserName.value };

  // 1. (사용자 경험 향상) 내 메시지를 서버 응답 기다리지 않고 즉시 내 화면에 추가 (Local Echo)
  messages.value.push({
    id: Date.now(),
    text: messageData.text,
    name: messageData.name,
    sender: 'me'
  });

  // 새 메시지가 추가되면 스크롤을 맨 아래로 이동
  nextTick(() => {
    const chatContent = document.querySelector('.chat-content');
    if (chatContent) {
      chatContent.scrollTop = chatContent.scrollHeight;
    }
  });

  // 2. OpenVidu의 Signal 기능을 이용해 다른 모든 참가자에게 메시지 데이터 전송
  session.value.signal({
    type: 'chat', // 'chat'이라는 이름표를 붙여서 보냄
    data: JSON.stringify(messageData),
  });
};

// 그리기 도구를 변경하는 함수
function setTool(tool){
  currentTool.value = tool;
  if (!canvas) return;
  // 포인터일 때는 캔버스에 그림을 그릴 수 없도록 설정
  canvas.style.pointerEvents = (tool === 'pointer') ? 'none' : 'auto';
  // CSS 클래스를 이용해 마우스 커서 모양 변경
  canvas.classList.toggle('pen-cursor'   , tool==='pen');
  canvas.classList.toggle('eraser-cursor', tool==='eraser');
}

// 이전 페이지(Preview)에서 URL을 통해 전달받은 토큰과 예약 ID
const token = route.query.token;
const appointmentId = route.query.appointmentId;

// 카메라를 켜고 끄는 함수
const toggleCamera = () => {
  if (mainStreamManager.value) {
    isCameraOn.value = !isCameraOn.value;
    // 내 비디오 스트림에 영상 송출 여부를 변경하라고 명령
    mainStreamManager.value.publishVideo(isCameraOn.value);
  }
};

// 마이크를 켜고 끄는 함수
const toggleMic = () => {
  if (mainStreamManager.value) {
    isMicOn.value = !isMicOn.value;
    // 내 오디오 스트림에 음성 송출 여부를 변경하라고 명령
    mainStreamManager.value.publishAudio(isMicOn.value);
  }
};

// 캔버스에 그리기 시작할 때 (마우스 클릭)
function startDraw(e){
  if(currentTool.value === 'pointer') return;
  isDrawing.value = true;
  ctx.beginPath();
  ctx.moveTo(e.offsetX, e.offsetY);
}

// 캔버스 위에서 그리기를 진행할 때 (마우스 이동)
function draw(e){
  if(!isDrawing.value) return;
  // 펜/지우개 도구에 따라 선 색상, 굵기 등 설정
  if(currentTool.value === 'pen'){
    ctx.globalCompositeOperation='source-over';
    ctx.lineWidth = 2;
    ctx.strokeStyle = 'red';
  } else if(currentTool.value === 'eraser'){
    ctx.globalCompositeOperation='destination-out';
    ctx.lineWidth = 20;
  }
  ctx.lineTo(e.offsetX, e.offsetY);
  ctx.stroke();

  // 내가 그린 좌표를 다른 사람에게 Signal로 전송
  sendDrawSignal({ x:e.offsetX, y:e.offsetY, t:currentTool.value, a:isDrawing.value });
}

// 캔버스에서 그리기를 멈출 때 (마우스 떼기)
function endDraw(){
  if(isDrawing.value){
    isDrawing.value=false;
    ctx.closePath();
  }
}

// 그리기 정보를 Signal로 전송하는 함수
function sendDrawSignal(payload){
  if(!session.value) return;
  session.value.signal({ type:'drawing', data:JSON.stringify(payload) });
}

// 다른 사람의 그리기 Signal을 받았을 때 내 캔버스에 그려주는 함수
function handleRemoteDraw({data}){
  const {x,y,t,a} = JSON.parse(data);
  if(t === 'pointer') return;
  // 상대방이 사용한 도구에 맞춰 내 캔버스 설정 변경
  ctx.globalCompositeOperation = t === 'pen' ? 'source-over' : 'destination-out';
  ctx.lineWidth = t === 'pen' ? 2 : 20;
  // 상대방이 그린 좌표를 따라 선을 그림
  if(a){ ctx.lineTo(x,y); ctx.stroke(); }
  else{ ctx.beginPath(); ctx.moveTo(x,y); }
}

// 화면 공유 시 그리기 캔버스를 초기화하는 함수
async function initCanvas(){
  await nextTick(); // DOM이 완전히 업데이트될 때까지 기다림
  canvas = document.getElementById('draw-canvas');
  if(!canvas) return;
  ctx = canvas.getContext('2d');
  // 캔버스 크기를 부모 요소에 맞춤
  canvas.width  = canvas.offsetWidth;
  canvas.height = canvas.offsetHeight;

  // 캔버스에 마우스 이벤트 리스너 등록
  canvas.addEventListener('mousedown', startDraw);
  canvas.addEventListener('mousemove', draw);
  canvas.addEventListener('mouseup', endDraw);
  canvas.addEventListener('mouseleave', endDraw);
}

// 컴포넌트가 화면에 표시될 때 단 한번 실행되는 초기화 함수 (가장 중요!)
onMounted(async () => {
  // --- 1. 준비 단계: OpenVidu 객체 및 세션 생성 ---
  const OPENVIDU_SERVER_URL = "https://i13b204.p.ssafy.io/openvidu";
  OV.value = new OpenVidu(OPENVIDU_SERVER_URL);
  session.value = OV.value.initSession();

  // --- 2. 수신 대기 단계: 각종 이벤트가 발생했을 때 어떻게 행동할지 미리 정의 ---
  // (중요) connect 이전에 미리 등록해야, 연결 직후 발생하는 이벤트를 놓치지 않음

  // 다른 참가자가 입장해서 스트림을 게시했을 때
  session.value.on('streamCreated', async(event) => {
    // 해당 스트림을 구독(subscribe)하고, 비디오를 화면에 표시
    const subscriber = session.value.subscribe(event.stream, undefined);
    const target = document.getElementById('lawyer-video');
    await nextTick();
    subscriber.addVideoElement(target);
    subscribers.value.push(subscriber); // 구독자 목록에 추가
  });

  // 다른 참가자가 퇴장해서 스트림이 사라졌을 때
  session.value.on('streamDestroyed', (event) => {
    // 구독자 목록에서 해당 참가자 제거
    subscribers.value = subscribers.value.filter(
      (sub) => sub.stream.streamId !== event.stream.streamId
    );
  });

  // 'chat' 타입의 Signal(채팅 메시지)이 도착했을 때
  session.value.on('signal:chat', (event) => {
    const isMe = event.from.connectionId === session.value.connection.connectionId;
    // 내가 보낸 메시지는 무시 (이미 내 화면에는 즉시 추가했기 때문)
    if (isMe) {
      return;
    }
    // 다른 사람이 보낸 메시지면 채팅 목록에 추가
    const data = JSON.parse(event.data);
    messages.value.push({
      id: Date.now() + Math.random(),
      text: data.text,
      name: data.name,
      sender: 'other',
    });
    // 스크롤 맨 아래로 이동
    nextTick(() => {
        const chatContent = document.querySelector('.chat-content');
        if (chatContent) {
            chatContent.scrollTop = chatContent.scrollHeight;
        }
    });
  });

  // 'drawing' 타입의 Signal(그리기 정보)이 도착했을 때
  session.value.on('signal:drawing', handleRemoteDraw);

  // --- 3. 연결 단계: 모든 준비가 끝나면 세션에 접속 ---
  try {
    // 실제로는 로그인 정보 등에서 가져와야 할 사용자 이름
    myUserName.value = '사용자' + Math.floor(Math.random() * 100);
    // 서버에서 받은 토큰과 내 이름을 가지고 세션에 최종 연결
    await session.value.connect(token, {
      clientData: myUserName.value,
    });

    // --- 4. 발행 단계: 내 카메라/마이크를 세션에 송출 ---
    // 세션 연결 성공 후, 내 화면과 소리를 다른 사람에게 보내기 시작
    const publisher = await OV.value.initPublisher(undefined, {
      audioSource: undefined,   // 기본 마이크 사용
      videoSource: undefined,   // 기본 카메라 사용
      publishAudio: true,       // 오디오 켜기
      publishVideo: true,       // 비디오 켜기
      resolution: '640x480',
      frameRate: 30,
      mirror: true,             // 내 화면 좌우반전 (거울 모드)
    });

    // 내 스트림을 세션에 게시(publish)
    await session.value.publish(publisher);
    // 내 비디오를 화면의 'publisher' div에 추가
    publisher.addVideoElement(document.getElementById('publisher'));
    // 내 스트림 관리 객체를 저장해두어 나중에 제어할 수 있도록 함
    mainStreamManager.value = publisher;

  } catch (error) {
    console.error('OpenVidu 연결 또는 퍼블리싱 실패:', error);
  }
});

// 화면 공유를 시작하는 함수
const shareScreen = async () => {
  try {
    // videoSource를 'screen'으로 설정하여 화면 공유용 publisher 생성
    const screenPublisher = await OV.value.initPublisher(undefined, {
      videoSource: 'screen',
      publishVideo: true,
      publishAudio: false,
      mirror: false
    });

    // 화면 공유 스트림을 화면에 표시하고 세션에 게시하는 로직
    const screenVideo = document.createElement('video');
    screenVideo.autoplay = true;
    screenVideo.playsInline = true;
    screenVideo.style.width = '100%';
    screenVideo.style.height = '100%';
    screenVideo.style.objectFit = 'cover';
    document.getElementById('client-video').appendChild(screenVideo);
    screenPublisher.addVideoElement(screenVideo);

    await session.value.publish(screenPublisher);
    await initCanvas();
    isScreenSharing.value = true;

  } catch (err) {
    console.error('화면 공유 실패:', err);
    alert('화면 공유를 허용하지 않으면 시작할 수 없습니다.');
  }
};

// 세션을 떠나는 함수 (나가기 버튼 클릭 시)
const leaveSession = async () => {
  // OpenVidu 세션 연결 해제
  if (session.value) {
    session.value.disconnect();
  }
  // 로컬에 저장했던 관련 객체들 모두 초기화
  session.value = null;
  OV.value = null;
  mainStreamManager.value = null;
  subscribers.value = [];

  // 백엔드 서버에 최종적으로 나갔음을 알리는 API 호출
  try {
    await axios.delete(`/api/rooms/${appointmentId}/participants/me`);
  } catch (e) {
    console.warn('퇴장 요청 실패:', e);
  }
  // 메인 페이지로 이동
  router.push('/');
};

// Vue 컴포넌트가 화면에서 사라지기 직전에 실행되는 함수
onBeforeUnmount(() => {
  // 사용자가 브라우저를 닫거나 다른 페이지로 이동할 때도 세션을 정리하도록 호출
  leaveSession();
});
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
