<template>
  <div class="chat-container">
    <div class="message-area" ref="messageAreaRef">
      <div
        v-for="message in messages"
        :key="message.id"
        class="message-bubble-container"
        :class="message.sender === 'me' ? 'my-message-container' : 'other-message-container'"
      >
        <!-- [수정됨] 발신자 이름 표시 -->
        <div class="sender-name">{{ message.name }}</div>

        <div class="message-bubble">
          {{ message.text }}
        </div>
      </div>
      <div v-if="isLoading" class="other-message-container">
        <!-- [수정됨] 로딩 버블에도 이름 표시 (옵션) -->
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
.chat-container {
  width: 350px;
  height: 660px;
  display: flex;
  flex-direction: column;
  font-family: Arial, sans-serif;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.chat-header {
  padding: 15px;
  background-color: #4A90E2;
  color: white;
  text-align: center;
  border-bottom: 1px solid #ddd;
}
.chat-header h3 { margin: 0; font-size: 1.2em; }
.message-area {
  flex-grow: 1;
  padding: 20px 10px;
  overflow-y: auto;
  background-color: #f9f9f9;
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
  color: #555;
  margin-bottom: 4px;
  padding: 0 5px;
}

.message-bubble {
  padding: 10px 15px;
  border-radius: 18px;
  color: white;
  word-wrap: break-word; /* 긴 텍스트 줄바꿈 */
}
.my-message-container .message-bubble {
  background-color: #4A90E2;
}
.other-message-container .message-bubble {
  background-color: #E5E5EA;
  color: #333;
}
.input-area {
  display: flex;
  padding: 10px;
  border-top: 1px solid #ddd;
  background-color: #fff;
}
.input-area input {
  flex-grow: 1;
  border: 1px solid #ccc;
  border-radius: 20px;
  padding: 10px 15px;
  font-size: 1em;
  margin-right: 10px;
}
.input-area input:focus {
  outline: none;
  border-color: #4A90E2;
}
.input-area button {
  padding: 10px 20px;
  border: none;
  background-color: #4A90E2;
  color: white;
  border-radius: 20px;
  cursor: pointer;
  font-size: 1em;
  font-weight: bold;
}
.input-area button:hover {
  background-color: #357ABD;
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
