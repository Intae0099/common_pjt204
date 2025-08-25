<template>
  <div>
    <ChatComponent
      :title="chatTitle"
      :messages="messages"
      :is-loading="isBotReplying"
      @send-message="handleSendMessage"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import ChatComponent from './components/ChatComponent.vue';
import axios, { fastapiApiClient } from '@/lib/axios';
import { useAuthStore } from '@/stores/auth';

const chatTitle = ref('AI 법률 전문가');
const messages = ref([
  { id: 1, text: '안녕하세요! 법률과 관련하여 무엇을 도와드릴까요?', sender: 'other', name: 'AI 챗봇' }
]);
const isBotReplying = ref(false);
const userName = ref('나');

onMounted(async () => {
  const authStore = useAuthStore();
  if (!authStore.isLoggedIn) {
    // 비로그인 상태면 함수 종료
    return;
  }

  const userType = authStore.userType;
  let endpoint = '';

  // userType에 따라 API 엔드포인트 결정
  if (userType === 'USER') {
    endpoint = '/api/clients/me';
  } else if (userType === 'LAWYER') {
    endpoint = '/api/lawyers/me'; // 변호사 정보 엔드포인트
  } else {
    console.warn('알 수 없는 사용자 타입:', userType);
    return; // 지원하지 않는 타입이면 함수 종료
  }

  try {
    // ✅ 기본 axios 인스턴스를 사용하여 사용자 정보 API 호출
    const response = await axios.get(endpoint);

    // API 응답에서 이름을 찾아 할당합니다.
    // 'name' 또는 'oauthName' 필드를 모두 확인하여 더 안정적으로 처리합니다.
    const nameFromApi = response.data.name || response.data.oauthName;

    if (nameFromApi) {
      userName.value = nameFromApi;
    }
  } catch (error) {
    console.error('사용자 이름 로딩 실패:', error);
    // 에러가 발생해도 기본값인 '나'가 사용됩니다.
  }
});

// 이전 대화 내용을 API가 요구하는 'history' 형식의 문자열로 변환하는 함수
const formatHistory = () => {
  return messages.value
    .map(msg => {
      const prefix = msg.sender === 'me' ? 'User' : 'AI';
      return `${prefix}: ${msg.text}`;
    })
    .join('\n');
};

const handleSendMessage = async (text) => {
  // 1. 내가 보낸 메시지 추가
  const userMessage = {
    id: Date.now(),
    text: text,
    sender: 'me',
    name: userName.value // 실제 사용자 이름으로 교체 가능
  };
  messages.value.push(userMessage);

  // 2. 챗봇 응답 시작 & 로딩 상태 활성화
  isBotReplying.value = true;

  // 3. AI 응답을 실시간으로 표시할 빈 메시지 객체 생성
  const botMessageId = Date.now() + 1;
  const botResponse = {
    id: botMessageId,
    text: '', // 스트리밍 응답으로 채워질 공간
    sender: 'other',
    name: 'AI 챗봇'
  };
  messages.value.push(botResponse);

  try {
    // 4. API 요청 준비
    const authStore = useAuthStore();
    const token = authStore.accessToken;

    if (!token) {
      throw new Error('인증 토큰이 없습니다. 로그인이 필요합니다.');
    }

    const history = formatHistory();
    const endpoint = '/ai/chat/stream'; // FastAPI 엔드포인트

    // 5. `fetch` API를 사용하여 스트리밍 요청 전송
    const response = await fetch(fastapiApiClient.defaults.baseURL + endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        message: text,
        history: history,
      }),
    });

    // 스트림 시작 전 발생하는 오류 처리 (4xx, 5xx)
    if (!response.ok) {
      const errorData = await response.json(); // 오류 응답은 JSON 형식이라고 가정
      throw new Error(errorData.error.message || 'API 요청에 실패했습니다.');
    }

    // 6. 응답 스트림 처리
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    // 로딩 UI를 숨기고 스트리밍을 시작했으므로 false로 설정
    isBotReplying.value = false;

    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        break; // 스트림 종료
      }

      // 받은 데이터를 문자열로 디코딩하고 버퍼에 추가
      buffer += decoder.decode(value, { stream: true });

      // SSE 이벤트는 '\n\n'으로 구분되므로, 이를 기준으로 파싱
      const events = buffer.split('\n\n');
      buffer = events.pop(); // 마지막 불완전한 이벤트를 다음 처리를 위해 남겨둠

      for (const event of events) {
        if (event.startsWith('data:')) {
          const data = event.substring(5).trim();

          if (data === '[DONE]') {
            return; // 스트림 처리 완전 종료
          }

          try {
            const parsed = JSON.parse(data);
            if (parsed.reply) {
              // ID로 챗봇 메시지를 찾아 텍스트를 추가
              const targetMessage = messages.value.find(m => m.id === botMessageId);
              if (targetMessage) {
                targetMessage.text += parsed.reply;
              }
            }
          } catch (e) {
            console.error('스트림 데이터 파싱 오류:', e);
          }
        }
      }
    }

  } catch (error) {
    console.error('챗봇 API 연동 중 오류 발생:', error);
    // 에러 메시지를 챗봇 UI에 표시
    const targetMessage = messages.value.find(m => m.id === botMessageId);
    if (targetMessage) {
      targetMessage.text = `오류가 발생했습니다: ${error.message}`;
    }
  } finally {
    // 7. 모든 과정이 끝나면(성공/실패/완료) 로딩 상태 비활성화
    isBotReplying.value = false;
  }
};
</script>
