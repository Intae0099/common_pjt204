<template>
  <div class="preview-camera">
    <video ref="videoRef" autoplay playsinline muted></video>
    <div class="controls">
      <button @click="toggleAudio">
        <component :is="isAudioOn ? Mic : MicOff" class="icon" />
      </button>
      <button @click="toggleVideo">
        <component :is="isVideoOn ? Video : VideoOff" class="icon" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { Mic, MicOff, Video, VideoOff } from 'lucide-vue-next';

// 템플릿의 <video> 엘리먼트를 참조하기 위한 ref
const videoRef = ref(null);
// 카메라/마이크의 미디어 스트림 객체를 저장하기 위한 ref
const localStream = ref(null);

// 오디오/비디오 활성화 상태
const isAudioOn = ref(false); // 오디오는 기본적으로 끔
const isVideoOn = ref(true);

// 컴포넌트가 마운트되면 카메라/마이크 접근 요청
onMounted(async () => {
  try {
    // 1. 브라우저의 mediaDevices API를 사용해 미디어 장치에 접근
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: true,
      video: true,
    });

    // 2. 받아온 미디어 스트림을 상태에 저장
    localStream.value = stream;

    // 3. <video> 태그의 소스로 스트림을 지정하여 화면에 표시
    if (videoRef.value) {
      videoRef.value.srcObject = stream;
    }

    // 4. 오디오는 기본적으로 끄기 위해 오디오 트랙을 비활성화
    stream.getAudioTracks().forEach(track => (track.enabled = isAudioOn.value));

  } catch (err) {
    console.error('카메라/마이크 접근 실패:', err);
    alert('카메라와 마이크 접근 권한을 허용해야 미리보기를 사용할 수 있습니다.');
  }
});

// 오디오 켜고 끄는 함수
const toggleAudio = () => {
  if (!localStream.value) return;
  isAudioOn.value = !isAudioOn.value;
  // 스트림의 모든 오디오 트랙의 활성화 상태를 변경
  localStream.value.getAudioTracks().forEach(track => (track.enabled = isAudioOn.value));
};

// 비디오 켜고 끄는 함수
const toggleVideo = () => {
  if (!localStream.value) return;
  isVideoOn.value = !isVideoOn.value;
  // 스트림의 모든 비디오 트랙의 활성화 상태를 변경
  localStream.value.getVideoTracks().forEach(track => (track.enabled = isVideoOn.value));
};

// 컴포넌트가 사라지기 직전에 실행되어 리소스를 정리 (매우 중요!)
onBeforeUnmount(() => {
  if (localStream.value) {
    // 모든 미디어 트랙을 중지시켜 카메라/마이크 사용을 완전히 해제
    // 이 코드가 없으면 컴포넌트를 떠나도 카메라 불빛이 꺼지지 않습니다.
    localStream.value.getTracks().forEach(track => track.stop());
  }
});
</script>

<style scoped>
/* 스타일은 기존과 동일하게 유지됩니다. */
.preview-camera {
  width: 100%;
  height: 400px;
  border-radius: 10px;
  background-color: #ddd;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 10px;
}

.controls {
  position: absolute;
  bottom: 15px;
  left: 17px;
  display: flex;
  gap: 0.5rem;
}

button {
  background-color: rgba(0, 0, 0, 0.6);
  border: none;
  padding: 0.5rem;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s;
}
button:hover {
  background-color: rgba(0, 0, 0, 0.8);
}
.icon {
  width: 24px;
  height: 24px;
  color: white;
}
</style>
