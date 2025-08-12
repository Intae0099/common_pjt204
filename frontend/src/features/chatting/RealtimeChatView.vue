<template>
  <div>
    <ChatComponent :title="chatTitle" :messages="messages" @send-message="sendChatMessage" />
  </div>
</template>

<script setup>
// 1. watch와 defineProps를 import 합니다. defineEmits는 필요 없습니다.
import { ref, watch, defineProps, onMounted } from 'vue';
import ChatComponent from './components/ChatComponent.vue';
import axios from '@/lib/axios'; // axios 기본 인스턴스 import
import { useAuthStore } from '@/stores/auth'; // Pinia 스토어 import

// 2. 부모(MeetingRoom)로부터 받을 props를 정의합니다.
//    (기존 defineProps({ messages: ... })는 삭제합니다.)
const props = defineProps({
  session: {
    type: Object, // OpenVidu Session 객체
    // session 객체는 비동기로 로드되므로 처음엔 null일 수 있어 required: false 가 더 안전합니다.
    // 하지만 template에서 v-show로 제어되므로 true로 두어도 무방합니다.
    required: true,
  },
  userName: {
    type: String,
    default: '사용자',
  },
});

// 3. emit 정의는 삭제합니다.
// const emit = defineEmits(['send-message']);

const chatTitle = ref('실시간 채팅');

// 4. messages 상태를 여기서 직접 관리합니다.
const messages = ref([]);

// [추가] 사용자 이름을 저장할 내부 ref를 만듭니다. props.userName을 초기값으로 설정합니다.
const userName = ref(props.userName);

// [추가] ChatbotView.vue에서 가져온 사용자 이름 로딩 로직
onMounted(async () => {
  const authStore = useAuthStore();
  if (!authStore.isLoggedIn) {
    return; // 비로그인 상태면 함수 종료
  }

  const userType = authStore.userType;
  let endpoint = '';

  if (userType === 'USER') {
    endpoint = '/api/clients/me';
  } else if (userType === 'LAWYER') {
    endpoint = '/api/lawyers/me';
  } else {
    return; // 지원하지 않는 타입이면 종료
  }

  try {
    const response = await axios.get(endpoint);
    const nameFromApi = response.data.name || response.data.oauthName;

    if (nameFromApi) {
      userName.value = nameFromApi; // API에서 가져온 이름으로 업데이트
    }
  } catch (error) {
    console.error('사용자 이름 로딩 실패 (실시간 채팅):', error);
  }
});
// 5. 메시지 전송 함수를 여기서 직접 구현합니다.
//    (기존 handleSendMessage 함수를 이 내용으로 대체합니다.)
const sendChatMessage = (text) => {
  // session prop이 유효한지 확인합니다.
  if (props.session && props.session.signal) {
    const messageData = {
      text: text,
      name: userName.value,
    };

    props.session.signal({
      data: JSON.stringify(messageData),
      to: [],
      type: 'chat'
    }).catch(error => {
      console.error('메시지 전송 실패:', error);
    });

    // 내 화면에도 즉시 메시지를 표시합니다.
    messages.value.push({
      ...messageData,
      sender: 'me',
      id: Date.now()
    });
  } else {
    console.error("세션이 유효하지 않아 메시지를 보낼 수 없습니다.");
  }
};

// 6. session 객체를 감시하여 시그널 리스너를 등록하는 watch 로직을 추가합니다.
watch(() => props.session, (newSession, oldSession) => {
  if (oldSession) {
    oldSession.off('signal:chat'); // 이전 리스너 정리
  }
  if (newSession) {
    newSession.on('signal:chat', (event) => {
      if (event.from.connectionId === newSession.connection.connectionId) {
        return; // 내가 보낸 메시지는 무시
      }
      const receivedMessage = JSON.parse(event.data);
      messages.value.push({
        ...receivedMessage,
        sender: 'other',
        id: Date.now(),
      });
    });
  }
}, { immediate: true });
</script>
