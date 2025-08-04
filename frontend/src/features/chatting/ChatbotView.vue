<!-- ChatbotView.vue -->
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
import { ref } from 'vue';
import ChatComponent from './components/ChatComponent.vue';

const chatTitle = ref('AI 고객센터');
const messages = ref([
  { id: 1, text: '안녕하세요! 무엇을 도와드릴까요?', sender: 'other', name: 'AI 챗봇' }
]);
const isBotReplying = ref(false);

const handleSendMessage = (text) => {
  // 내가 보낸 메시지 추가
  const newMessage = {
    id: Date.now(),
    text: text,
    sender: 'me',
    name: '홍길동' // 내 이름
  };
  messages.value.push(newMessage);

  // 챗봇 응답 시뮬레이션
  isBotReplying.value = true;
  setTimeout(() => {
    const botResponse = {
      id: Date.now() + 1,
      text: `'${text}'에 대해 답변을 준비 중입니다.`,
      sender: 'other',
      name: 'AI 챗봇' // 챗봇 이름
    };
    messages.value.push(botResponse);
    isBotReplying.value = false;
  }, 1500);
};
</script>
