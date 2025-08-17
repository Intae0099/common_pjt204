<template>
  <div class="preview-camera">
    <div ref="previewContainerRef" class="video-container"></div>
    <div v-if="isInitialized" class="controls">
      <button @click="toggleAudio" :class="{ off: !isAudioOn }">
        <component :is="isAudioOn ? Mic : MicOff" class="icon" />
      </button>
      <button @click="toggleVideo">
        <component :is="isVideoOn ? Video : VideoOff" class="icon" />
      </button>
    </div>
    <div v-if="!isInitialized && errorMessage" class="error-message">
      <p>{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, defineExpose } from 'vue';
import { OpenVidu } from 'openvidu-browser';
import { Mic, MicOff, Video, VideoOff } from 'lucide-vue-next';

const OV = ref(null);
const publisher = ref(null);
const previewContainerRef = ref(null);

const isAudioOn = ref(false);
const isVideoOn = ref(true);

// ✅ 새로운 상태 추가
const isInitialized = ref(false); // 초기화 성공 여부
const errorMessage = ref(''); // 에러 메시지 표시용

onMounted(() => { // async 제거

  try {
    OV.value = new OpenVidu();
    OV.value.enableProdMode();

    const newPublisher = OV.value.initPublisher(
      previewContainerRef.value, // ✅ 첫 번째 인자로 비디오를 붙일 DOM 요소를 바로 전달
      {
        videoSource: undefined,
        audioSource: undefined,
        publishAudio: isAudioOn.value,
        publishVideo: isVideoOn.value,
        mirror: false,
      },
      (error) => { // ✅ 세 번째 인자로 콜백 함수 사용
        if (error) {
          console.error('OpenVidu initPublisher 에러:', error);
          if (error.name === 'DEVICE_ACCESS_DENIED') {
            errorMessage.value = '카메라/마이크 권한이 차단되었습니다.';
          } else if (error.name === 'NO_DEVICES_FOUND') {
            errorMessage.value = '사용 가능한 카메라/마이크 장치가 없습니다.';
          } else {
            errorMessage.value = '미리보기 로딩 중 오류가 발생했습니다.';
          }
        } else {
          isInitialized.value = true;
        }
      }
    );

    // ✅ Publisher가 성공적으로 생성된 후에만 상태에 할당
    publisher.value = newPublisher;

  } catch (err) {
    console.error('OpenVidu 객체 생성 중 에러:', err);
    errorMessage.value = 'OpenVidu 초기화 중 심각한 오류가 발생했습니다.';
  }
});

// 오디오 켜고 끄는 함수
const toggleAudio = () => {
  if (!publisher.value) return;
  isAudioOn.value = !isAudioOn.value;
  publisher.value.publishAudio(isAudioOn.value);
};

// 비디오 켜고 끄는 함수
const toggleVideo = () => {
  if (!publisher.value) return;
  isVideoOn.value = !isVideoOn.value;
  publisher.value.publishVideo(isVideoOn.value);
};

const cleanup = () => {
  if (publisher.value && publisher.value.stream) {
    const mediaStream = publisher.value.stream.getMediaStream();
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => {
        track.stop();
      });
    }
  }

  if (publisher.value && typeof publisher.value.destroy === 'function') {
    publisher.value.destroy();
  }

  publisher.value = null;
  OV.value = null;
};

// 컴포넌트가 사라지기 직전에 실행되어 리소스를 정리 (매우 중요!)
onBeforeUnmount(() => {
  cleanup();
});

defineExpose({
  cleanup
});
</script>

<style scoped>
/* 스타일은 기존과 동일하게 유지됩니다. */
.preview-camera {
  width: 100%;
  height: 480px;
  border-radius: 12px;
  background-color: black;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-container {
  width: 100%;
  height: 100%;
}

.video-container :deep(video) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.controls {
  position: absolute;
  bottom: 15px;
  left: 17px;
  display: flex;
  gap: 0.5rem;
  z-index: 10;
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

.error-message {
  color: white;
  text-align: center;
  padding: 20px;
}
</style>
