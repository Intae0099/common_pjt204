<!-- RealtimeChatView.vue -->
<template>
  <div>
    <ChatComponent
      :title="chatTitle"
      :messages="messages"
      @send-message="handleSendMessage"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import ChatComponent from './components/ChatComponent.vue';

const chatTitle = ref('이순신님과의 대화');
const currentUser = { name: '홍길동' };
const otherUser = { name: '이순신' };

const messages = ref([
  { id: 1, text: '안녕하세요, 홍길동님.', sender: 'other', name: otherUser.name }
]);

// 실제 웹소켓(Socket.IO 등)을 사용한다면 아래와 같은 로직이 들어갑니다.
// const socket = io("http://localhost:3000");
// socket.on('receive-message', (data) => {
//   const receivedMessage = {
//     id: data.id,
//     text: data.text,
//     sender: 'other',
//     name: data.name
//   };
//   messages.value.push(receivedMessage);
// });

// 자식 컴포넌트에서 메시지 전송 이벤트 발생 시 호출
const handleSendMessage = (text) => {
  // 1. 내가 보낸 메시지를 화면에 즉시 표시
  const myMessage = {
    id: Date.now(),
    text: text,
    sender: 'me',
    name: currentUser.name
  };
  messages.value.push(myMessage);

  // 2. (실제 로직) 웹소켓 서버로 메시지 전송
  // socket.emit('send-message', { text: myMessage.text, name: myMessage.name });

  // 3. (시뮬레이션) 1초 뒤에 상대방에게서 답장이 오는 것처럼 시뮬레이션
  console.log(`'${text}' 메시지를 서버로 전송했습니다.`);
  setTimeout(() => {
    const otherMessage = {
      id: Date.now() + 1,
      text: '아, 그렇군요! 확인했습니다.',
      sender: 'other',
      name: otherUser.name,
    };
    messages.value.push(otherMessage);
    console.log("상대방으로부터 메시지를 수신했습니다.");
  }, 1000);
};
</script>
