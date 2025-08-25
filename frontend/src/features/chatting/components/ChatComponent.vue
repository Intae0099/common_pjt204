<template>
  <div class="chat-container">
    <div class="message-area" ref="messageAreaRef">
      <div
        v-for="message in messages"
        :key="message.id"
        class="message-bubble-container"
        :class="[
          message.sender === 'me' ? 'my-message-container' : 'other-message-container',
          message.name === 'AI 챗봇' ? 'ai-bot' : ''
        ]"
      >
        <div class="sender-name">{{ message.name }}</div>
        <div class="message-bubble">
          {{ message.text }}
        </div>
      </div>
      <div v-if="isLoading" class="other-message-container">
        <div class="sender-name">Chatbot</div>
        <div class="message-bubble loading-bubble">
          <span>.</span><span>.</span><span>.</span>
        </div>
      </div>
    </div>

    <div class="input-area">
      <input
        type="text"
        v-model="newMessage"
        @keydown.enter.prevent="sendMessage"
        placeholder="메시지를 입력하세요..."
      />
      <button @click="sendMessage">전송</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';

const props = defineProps({
  title: {
    type: String,
    default: 'Chat',
  },
  // [수정됨] messages 배열에 'name' 속성 추가
  // [{ id: 1, text: '안녕하세요', sender: 'me', name: '홍길동' },
  //  { id: 2, text: '반갑습니다', sender: 'other', name: 'AI 챗봇' }]
  messages: {
    type: Array,
    required: true,
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['send-message']);

const newMessage = ref('');
const messageAreaRef = ref(null);

const sendMessage = () => {
  if (newMessage.value.trim() !== '') {
    emit('send-message', newMessage.value);
    newMessage.value = '';
  }
};

watch(
  () => props.messages,
  async () => {
    await nextTick();
    if (messageAreaRef.value) {
      messageAreaRef.value.scrollTop = messageAreaRef.value.scrollHeight;
    }
  },
  { deep: true }
);
</script>

<style scoped>
/* 기존 스타일은 그대로 유지 */
*{
  font-family: 'Noto Sans KR', sans-serif;
}
.chat-container {
  flex: 1;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  font-family: Arial, sans-serif;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: none;
}
.message-area {
  flex: 1 1 auto;
  min-height: 0;
  padding: 20px 10px;
  overflow-y: auto;
  background-color: #2C2C2C;
  display: flex;
  flex-direction: column;
}
.message-bubble-container {
  display: flex;
  flex-direction: column; /* [수정됨] 이름과 말풍선을 수직으로 배치 */
  margin-bottom: 15px; /* 간격 조정 */
  max-width: 80%;
}
.my-message-container {
  align-self: flex-end;
  align-items: flex-end; /* [수정됨] 내부 아이템 오른쪽 정렬 */
}
.other-message-container {
  align-self: flex-start;
  align-items: flex-start; /* [수정됨] 내부 아이템 왼쪽 정렬 */
}

/* [추가됨] 발신자 이름 스타일 */
.sender-name {
  font-size: 0.8em;
  color: #C5C5C5;
  margin-bottom: 4px;
  padding: 0 5px;
}

.message-bubble {
  padding: 10px 15px;
  border-radius: 10px;
  word-wrap: break-word;
   white-space: pre-wrap;
}
.my-message-container .message-bubble {
  background-color: #C5C5C5;
}
.other-message-container .message-bubble {
  background-color: #5A5A5A;
  color: #C5C5C5;
}
/* AI 챗봇의 말풍선만 파란색으로 */
.other-message-container.ai-bot .message-bubble {
  background-color: #4da3ff; /* 파란색 */
  color: #fff;
}

.input-area {
  display: flex;
  padding: 10px;
  background-color: #2C2C2C;
}
.input-area input {
  flex-grow: 1;
  border-radius: 10px;
  padding: 10px 15px;
  font-size: 1em;
  margin-right: 10px;
  border: none;
  background-color: #C5C5C5;
}
.input-area input:focus {
  outline: none;
  border-color: #6c9bcf ;
}
.input-area button {
  padding: 10px 20px;
  border: none;
  background-color: #131516;
  color: #B9D0DF;
  border-radius: 10px;
  cursor: pointer;
  font-size: 1em;
  font-weight: bold;
}
.input-area button:hover {
  background-color: #1b1e1f;
}
.loading-bubble { display: flex; align-items: center; justify-content: center; }
.loading-bubble span { animation: blink 1.4s infinite both; font-size: 2em; line-height: 0.5; }
.loading-bubble span:nth-child(2) { animation-delay: 0.2s; }
.loading-bubble span:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink {
  0% { opacity: 0.2; }
  20% { opacity: 1; }
  100% { opacity: 0.2; }
}
</style>
