<template>
  <div>
    <ChatComponent :title="chatTitle" :messages="messages" @send-message="handleSendMessage" />
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import ChatComponent from './components/ChatComponent.vue'

// 부모 컴포넌트로부터 메시지 목록을 props로 받습니다.
defineProps({
  messages: {
    type: Array,
    required: true,
  },
})

// 부모 컴포넌트로 이벤트를 보내기 위해 emit을 정의합니다.
const emit = defineEmits(['send-message'])

const chatTitle = ref('실시간 채팅') // 제목은 간단하게 변경

// 자식(ChatComponent)에서 메시지 전송 이벤트가 발생하면,
// 부모(MeetingRoom)에게 'send-message' 이벤트를 그대로 전달합니다.
const handleSendMessage = (text) => {
  emit('send-message', text)
}
</script>
