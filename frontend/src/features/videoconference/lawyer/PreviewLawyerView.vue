<template>
    <div class="preview-page">
      <!-- 왼쪽: 카메라 미리보기 -->
      <div class="preview-left">
        <h2>화면 미리보기</h2>
        <!-- <PreviewCamera /> -->
      </div>

      <!-- 오른쪽: 오늘 예약된 상담 -->
      <div class="preview-right">
        <h3>오늘 예약된 상담</h3>

        <!-- 예약이 있을 때 (todaysAppointments 기준으로 변경) -->
        <div v-if="todaysAppointments.length > 0">
          <div
            class="appointment-card"
            v-for="appointment in todaysAppointments"
            :key="appointment.appointmentId"
          >
             <p>
              {{ appointment.startTime.slice(0, 10).replace(/-/g, '.') }}
              ({{ new Date(appointment.startTime).toLocaleDateString('ko-KR', { weekday: 'short' }) }})
              {{ appointment.startTime.slice(11, 16) }} ~ {{ appointment.endTime.slice(11, 16) }}
            </p>
            <!-- API 응답에 맞춰 clientName으로 수정 -->
            <p>{{ appointment.clientName }} 의뢰인</p>
            <button>상담신청서 확인하기</button>
          </div>
          <button @click="enterMeeting" class="enter-button">화상상담 입장하기</button>
        </div>

        <!-- 예약이 없을 때 (todaysAppointments 기준으로 변경) -->
        <div v-else class="no-appointment">
          <p>앗! 오늘 예약된 상담 일정이 없어요</p>
          <button disabled>화상상담 입장하기</button>
        </div>
      </div>
    </div>
</template>

<script setup>
import PreviewCamera from '../PreviewCamera.vue'
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
// API 통신을 위해 설정한 axios 인스턴스를 가져옵니다.
// 파일 경로가 맞는지 확인해주세요. `@`는 보통 `src` 폴더를 가리킵니다.
import axios from '@/lib/axios'

const appointments = ref([])
const router = useRouter()

// 오늘 날짜의 약속만 필터링하고 시간순으로 정렬하는 computed 속성
const todaysAppointments = computed(() => {
  const today = new Date().toISOString().slice(0, 10) // 'YYYY-MM-DD' 형식

  return appointments.value.filter(appointment => {
    const appointmentDate = appointment.startTime.slice(0, 10)
    return appointmentDate === today
  }).sort((a, b) => new Date(a.startTime) - new Date(b.startTime)); // 시간순으로 정렬
});

// 컴포넌트가 마운트될 때 API를 호출하여 데이터를 가져옵니다.
onMounted(async () => {
  try {
    // 1. 나의 상담 일정 목록을 불러옵니다. (확정된 상담만 가져오도록 status 파라미터 추가)
    const { data: myAppointments } = await axios.get('/api/appointments/me', {
      params: { status: 'CONFIRMED' } // 'CONFIRMED' 상태의 상담만 조회, 필요에 따라 수정/제거 가능
    });

    if (!myAppointments || myAppointments.length === 0) {
        console.log('예약된 상담이 없습니다.');
        appointments.value = []; // 상태를 빈 배열로 확실히 초기화
        return;
    }

    // 2. 각 상담의 clientId를 기반으로 의뢰인 정보를 가져오는 API 호출 Promise 배열을 생성합니다.
    const clientInfoPromises = myAppointments.map(appointment => {
      return axios.get(`/api/clients/${appointment.clientId}`);
    });

    // 3. Promise.all을 사용해 모든 의뢰인 정보가 로드될 때까지 기다립니다. (병렬 처리로 더 빠름)
    const clientInfoResponses = await Promise.all(clientInfoPromises);

    // 4. 원래의 상담 정보에 가져온 의뢰인 이름을 추가합니다.
    const combinedAppointments = myAppointments.map((appointment, index) => {
      const clientData = clientInfoResponses[index].data; // 각 Promise의 결과(response)에서 데이터를 추출
      return {
        ...appointment, // 기존 appointment 데이터 (...appointment)
        clientName: clientData.name // 받아온 의뢰인 이름 추가
      };
    });

    // 5. 최종적으로 합쳐진 데이터를 state에 저장합니다.
    appointments.value = combinedAppointments;

  } catch (e) {
    console.error('상담 일정 또는 의뢰인 정보 불러오기 실패:', e);
    // 에러 발생 시 appointments를 빈 배열로 유지하여 "예약 없음" UI가 표시되도록 합니다.
    appointments.value = [];
  }
});

// 화상상담방 입장 함수
const enterMeeting = async () => {
  if (todaysAppointments.value.length === 0) {
    alert('입장할 수 있는 상담이 없습니다.');
    return;
  }

  // 가장 가까운 상담으로 입장한다고 가정
  const nextAppointment = todaysAppointments.value[0];
  console.log('입장할 상담 정보:', nextAppointment);

  try {
    // 이 부분은 기존 로직을 유지합니다.
    // 실제로는 nextAppointment.appointmentId 등을 서버에 보내 세션을 생성할 수 있습니다.
    const res = await axios.post('/api/rooms/create'); // 회의방 생성 요청
    const sessionId = res.data.sessionId; // 받아온 sessionId로
    router.push({ name: 'MeetingRoom', query: { sessionId } }); // 회의방 입장
  } catch (error) {
    console.error('회의방 생성 실패:', error);
    alert('회의방을 생성할 수 없습니다.');
  }
};
</script>

<style scoped>
/* 기존 스타일 유지 */
.preview-page {
  display: flex;
  gap: 2rem;
  padding: 2rem;
}
.preview-left, .preview-right {
  flex: 1;
  border: 1px solid #ccc;
  padding: 1.5rem;
  border-radius: 8px;
}
.appointment-card {
  border: 1px solid #eee;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 4px;
}
.no-appointment {
  text-align: center;
  padding: 2rem;
  color: #888;
}
button {
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: 1px solid #ddd;
}
button:disabled {
  cursor: not-allowed;
  background-color: #f0f0f0;
}
.enter-button {
    width: 100%;
    padding: 1rem;
    background-color: #007bff;
    color: white;
    border: none;
    font-size: 1.1rem;
    margin-top: 1rem;
}
</style>
