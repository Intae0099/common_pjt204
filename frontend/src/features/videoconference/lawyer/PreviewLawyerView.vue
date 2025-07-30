<template>
    <div class="preview-page">
      <!-- 왼쪽: 카메라 미리보기 -->
      <div class="preview-left">
        <h2>화면 미리보기</h2>
        <PreviewCamera />
      </div>

      <!-- 오른쪽: 오늘 예약된 상담 -->
      <div class="preview-right">
        <h3>오늘 예약된 상담</h3>

        <!-- 예약이 있을 때 -->
        <div v-if="appointments.length">
          <div
            class="appointment-card"
            v-for="(appointment, index) in todaysAppointments"
            :key="index"
          >
             <p>
              {{ appointment.startTime.slice(0, 10).replace(/-/g, '.') }}
              ({{ new Date(appointment.startTime).toLocaleDateString('ko-KR', { weekday: 'short' }) }})
              {{ appointment.startTime.slice(11, 16) }} ~ {{ appointment.endTime.slice(11, 16) }}
            </p>
            <p>{{ appointment.lawyerName }} 의뢰인</p>
            <button>상담신청서 확인하기</button>
          </div>
          <button class="enter-button">화상상담 입장하기</button>
        </div>

        <!-- 예약이 없을 때 -->
        <div v-else class="no-appointment">
          <p>앗! 상담 일정이 없어요</p>
          <button disabled>화상상담 입장하기</button>
        </div>
      </div>
    </div>
</template>

<script setup>
import PreviewCamera from '../PreviewCamera.vue'
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
// import axios from '@/lib/axios'

const appointments = ref([])
const router = useRouter()


const todaysAppointments = computed(() => {
  const today = new Date().toISOString().slice(0, 10) // 'YYYY-MM-DD' 형식

  return appointments.value.filter(appointment => {
    const appointmentDate = appointment.startTime.slice(0, 10)
    return appointmentDate === today
  }).sort((a, b) => new Date(a.startTime) - new Date(b.startTime)); // 시간순으로 정렬
});

/*
// api 요청 시
onMounted(async () => {
  try {
    // 1. 나의 상담 일정 목록을 불러옵니다.
    const { data: myAppointments } = await axios.get('/api/appointments/me')

    if (!myAppointments || myAppointments.length === 0) {
        console.log('예약된 상담이 없습니다.');
        return;
    }

    // 2. 각 상담 일정의 lawyerId를 기반으로 변호사 정보를 가져오는 API 호출 Promise 배열을 생성합니다.
    const lawyerInfoPromises = myAppointments.map(appointment => {
      // RESTful API 디자인에 따라 /api/clients/{id} 형태로 호출합니다.
      return axios.get(`/api/clients/${appointment.clientId}`)
    })

    // 3. Promise.all을 사용해 모든 변호사 정보가 로드될 때까지 기다립니다. (병렬 처리로 더 빠름)
    const clientInfoResponses = await Promise.all(clientInfoPromises)

    // 4. 원래의 상담 정보에 가져온 변호사 이름을 추가합니다.
    const combinedAppointments = myAppointments.map((appointment, index) => {
      const lawyerData = lawyerInfoResponses[index].data // 각 Promise의 결과(response)에서 데이터를 추출
      return {
        ...appointment, // 기존 appointment 데이터 (...appointment)
        lawyerName: lawyerData.name // 받아온 변호사 이름 추가
      }
    })

    // 5. 최종적으로 합쳐진 데이터를 state에 저장합니다.
    appointments.value = combinedAppointments

  } catch (e) {
    console.error('상담 일정 또는 변호사 정보 불러오기 실패:', e)
    // 에러 발생 시 appointments를 빈 배열로 유지하거나, 사용자에게 알림을 표시할 수 있습니다.
    appointments.value = []
  }
})
*/

onMounted(() => {

  // try {
  //   const { data } = await axios.get('/api/appointments/me')
  //   appointments.value = data
  // } catch (err) {
  //   console.error('API 호출 실패:', err)

  const today = new Date();
  const tomorrow = new Date();
  tomorrow.setDate(today.getDate() + 1);

  // 날짜를 'YYYY-MM-DD' 형식의 문자열로 변환하는 헬퍼 함수
  const formatDate = (date) => date.toISOString().slice(0, 10);

  appointments.value = [
    {
      appointmentId: '1',
      clientId: 11,
      lawyerId: 22,
      applicationId: 564,
      lawyerName: '홍길동', // 템플릿에서 사용하기 위해 추가
      startTime: `${formatDate(today)} 15:00:00`,
      endTime: `${formatDate(today)} 15:15:00`
    },
    {
      appointmentId: '2',
      clientId: 11,
      lawyerId: 33,
      applicationId: 565,
      lawyerName: '김영희', // 템플릿에서 사용하기 위해 추가
      startTime: `${formatDate(today)} 17:00:00`,
      endTime: `${formatDate(today)} 17:15:00`
    },
    {
      appointmentId: '3',
      clientId: 11,
      lawyerId: 44,
      applicationId: 567,
      lawyerName: '김승철', // 템플릿에서 사용하기 위해 추가
      startTime: `${formatDate(tomorrow)} 17:00:00`, // 내일 날짜 상담
      endTime: `${formatDate(tomorrow)} 17:15:00`
    },
  ]
})

// 화상상담방 입장 함수
const enterMeeting = async () => {
  if (todaysAppointments.value.length === 0) {
    alert('입장할 수 있는 상담이 없습니다.');
    return;
  }

  // 예시: 가장 가까운 상담으로 입장
  // const nextAppointment = todaysAppointments.value[0];

  try {
    const res = await axios.post('/api/rooms/create') // 회의방 생성 요청
    const sessionId = res.data.sessionId               // 받아온 sessionId로
    router.push({ name: 'MeetingRoom', query: { sessionId } }) // 회의방 입장
  } catch (error) {
    console.error('회의방 생성 실패:', error)
    alert('회의방을 생성할 수 없습니다.')
  }
}
</script>

<style scoped>

</style>
