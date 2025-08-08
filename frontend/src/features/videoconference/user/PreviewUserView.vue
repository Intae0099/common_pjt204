<template>
  <div class="preview-page">
    <div class="preview-left">
      <h2>화면 미리보기</h2>
      <PreviewCamera />
      <div class="before-consult-msg">
        <p class="title">
          <Smile class="smile-icon" />
          상담 전 궁금한 게 있으신가요?
        </p>
        <p class="desc">
          상담 전에 궁금한 내용을 AI에게 먼저 물어보세요.<br />
          빠르고 간편하게 상담서를 자동으로 작성할 수 있어요!
        </p>
        <router-link to="/ai-consult" class="ai-link">
          AI 상담 받으러 가기
          <MoveRight class="arrow-icon" />
        </router-link>
      </div>
    </div>

    <div class="preview-right">
      <h3>오늘 예약된 상담</h3>
      <div class="appointment-wrapper">
        <div v-if="appointments.length">
          <div
            v-for="appointment in appointments"
            :key="appointment.appointmentId"
            class="appointment-card"
            :class="{ selected: selectedAppointmentId === appointment.appointmentId }"
            @click="selectAppointment(appointment.appointmentId)"
          >
            <div class="card-header">
              <span class="card-time">
                {{ formatFullDateTime(appointment.startTime) }} ~
                {{ formatTime(appointment.endTime) }}
              </span>
              <span class="time-diff">
                {{ getTimeDifference(appointment.startTime) }}
              </span>
            </div>
          <div class="card-body">
            <img :src="appointment.profileImage || defaultImage" class="lawyer-img" />
          <div class="card-info">
            <p class="lawyer-name">
              <strong class="name-bold">{{ appointment.lawyerName }}</strong>
              <span class="name-medium"> 변호사</span>
            </p>

            <div class="tags">
              <span
                class="tag"
                v-for="tagId in appointment.tags.slice(0, 3)"
                :key="tagId"
              >
                #{{ tagMap[tagId] || '기타' }}
              </span>

              <button
                v-if="appointment.tags.length > 3"
                class="more-tags-btn"
                @click.stop="toggleTags(appointment.appointmentId)"
              >
                <ChevronUp v-if="expandedCards.has(appointment.appointmentId)" class="more-tags-icon" />
                <ChevronDown v-else class="more-tags-icon" />
              </button>

              <template v-if="expandedCards.has(appointment.appointmentId)">
                <span
                  class="tag"
                  v-for="tagId in appointment.tags.slice(3)"
                  :key="tagId"
                >
                  #{{ tagMap[tagId] || '기타' }}
                </span>
              </template>
            </div>

          <button class="view-btn" @click.stop="goToApplication(appointment.applicationId)">
            상담신청서 확인하기
          </button>
          </div>
            </div>
          </div>
        </div>

        <div v-else class="no-appointments">
          <img src="@/assets/bot-no-consult.png" class="no-img" />
          <p class="no-msg">앗! 오늘 상담 일정이 없어요!</p>
          <div class="links">
            <router-link to="/lawyers">변호사 조회</router-link> |
            <router-link to="/ai-consult">AI 상담받기</router-link>
          </div>
        </div>
      </div>

      <div class="enter-btn-wrapper">
        <button
          class="enter-btn"
          :disabled="!selectedAppointment || !canEnterMeeting(selectedAppointment.startTime, selectedAppointment.endTime)"
          @click="enterMeeting(selectedAppointmentId)"
        >
          화상상담 입장하기
        </button>
      </div>
    </div>
    <ApplicationDetail
      v-if="showDetailModal"
      :data="selectedApplicationData"
      @close="showDetailModal = false"
    />
  </div>
</template>

<script setup>
import PreviewCamera from '../components/PreviewCamera.vue';
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from '@/lib/axios';
import ApplicationDetail from '@/features/profile/user/ApplicationDetail.vue';
import { Smile, MoveRight, ChevronDown, ChevronUp } from 'lucide-vue-next';
import { TAG_MAP as tagList } from '@/constants/lawyerTags';

const appointments = ref([]);
const defaultImage = '/default-profile.png';
const router = useRouter();
const showDetailModal = ref(false);
const selectedApplicationData = ref(null);
const selectedAppointmentId = ref(null);
const expandedCards = ref(new Set());

const tagMap = tagList.reduce((map, tag) => {
  map[tag.id] = tag.name;
  return map;
}, {});

const toggleTags = (appointmentId) => {
  if (expandedCards.value.has(appointmentId)) {
    expandedCards.value.delete(appointmentId);
  } else {
    expandedCards.value.add(appointmentId);
  }
};

const selectedAppointment = computed(() => {
  if (!selectedAppointmentId.value) return null;
  return appointments.value.find(
    (app) => app.appointmentId === selectedAppointmentId.value
  );
});

const selectAppointment = (id) => {
  if (selectedAppointmentId.value === id) {
    selectedAppointmentId.value = null;
  } else {
    selectedAppointmentId.value = id;
  }
};

const formatFullDateTime = (datetimeStr) => {
  const date = new Date(datetimeStr);
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const formatTime = (datetimeStr) => {
  const date = new Date(datetimeStr);
  return date.toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  });
};

const getTimeDifference = (startTime) => {
  const start = new Date(startTime);
  const now = new Date();

  if (isNaN(start)) return '시간 정보 오류';

  const diffMs = start - now;
  const diffMinutes = Math.floor(diffMs / (1000 * 60));

  if (diffMinutes < 0) return '진행중';
  if (diffMinutes < 60) return `${diffMinutes}분 후`;

  const hours = Math.floor(diffMinutes / 60);
  const minutes = diffMinutes % 60;
  return `${hours}시간 ${minutes}분 후`;
};

const canEnterMeeting = (startTime, endTime) => {
  const now = new Date();
  const start = new Date(startTime);
  const end = new Date(endTime);

  return now >= new Date(start.getTime() - 10 * 60 * 1000) && now < end;
};

onMounted(async () => {
  try {
    const { data: appointmentData } = await axios.get('/api/appointments/me');
    const appointmentsWithLawyerInfo = await Promise.all(
      appointmentData.map(async (appointment) => {
        try {
          const { data: lawyer } = await axios.get(`/api/lawyers/${appointment.lawyerId}`);
          return {
            ...appointment,
            lawyerName: lawyer.name,
            profileImage: lawyer.photo,
            tags: lawyer.tags,
          };
        } catch (e) {
          console.error('변호사 정보 불러오기 실패:', e);
          return { ...appointment, tags: [] };
        }
      })
    );

    // 오늘 날짜의, 아직 끝나지 않은 예약만 필터링합니다.
    const now = new Date();
    const todaysAppointments = appointmentsWithLawyerInfo.filter(
      (appointment) => {
        const startTime = new Date(appointment.startTime);
        const endTime = new Date(appointment.endTime);

        // 조건 1: 상담 시작일이 오늘인지 확인 (연, 월, 일 비교)
        const isToday =
          startTime.getFullYear() === now.getFullYear() &&
          startTime.getMonth() === now.getMonth() &&
          startTime.getDate() === now.getDate();

        // 조건 2: 상담 종료 시간이 현재 시간 이후인지 확인
        const hasNotEnded = endTime > now;

        return isToday && hasNotEnded;
      }
    );

    appointments.value = todaysAppointments;
  } catch (e) {
    console.error('상담 일정 불러오기 실패:', e);
  }
});

const goToApplication = async (applicationId) => {
  try {
    // API 응답에서 data 필드를 responseData라는 변수명으로 받습니다.
    const { data: responseData } = await axios.get(`/api/applications/${applicationId}`);

    // API 요청이 성공했고, 응답 데이터 안에 application 객체가 있는지 확인합니다.
    if (responseData.success && responseData.data.application) {
      // 실제 신청서 데이터인 application 객체를 추출합니다.
      const applicationDetails = responseData.data.application;
      const questions = Object.values(applicationDetails.recommendedQuestion || {});

      // 추출한 실제 데이터를 selectedApplicationData에 할당합니다.
      selectedApplicationData.value = {
        ...applicationDetails,
        recommendedQuestions: questions,
      };

      showDetailModal.value = true;
    } else {
      // API는 성공했지만 데이터가 없는 경우 등 예외처리
      alert(responseData.message || '상담신청서 내용을 불러오는 데 실패했습니다.');
    }
  } catch (err) {
    console.error('상담신청서 상세 조회 실패:', err);
    // API 호출 자체가 실패했을 때 사용자에게 에러 메시지를 보여줍니다.
    const errorMessage = err.response?.data?.message || '상담신청서를 불러오는 데 실패했습니다.';
    alert(errorMessage);
  }
};

const enterMeeting = async (appointmentId) => {
  if (!appointmentId) {
    alert('입장할 상담을 선택해주세요.');
    return;
  }
  try {
    const res = await axios.post(`/api/rooms/${appointmentId}`);
    const token = res.data.data.openviduToken;
    router.push({ name: 'MeetingRoom', query: { token, appointmentId } });
  } catch (err) {
    if (err.response?.status === 409) {
      try {
        const res = await axios.post(`/api/rooms/${appointmentId}/participants`);
        const token = res.data.data.openviduToken;
        router.push({ name: 'MeetingRoom', query: { token, appointmentId } });
      } catch (err2) {
        console.error('방 참가 실패:', err2);
        alert('화상상담 입장에 실패했습니다.');
      }
    } else {
      console.error('방 생성 실패:', err);
      alert('화상상담 방 생성에 실패했습니다.');
    }
  }
};
</script>

<style scoped>
/* CSS는 변경할 필요가 없습니다. 기존 스타일이 그대로 적용됩니다. */
* {
  font-family: 'Noto Sans KR', sans-serif;
}
.preview-page {
  margin-top: 100px;
  display: flex;
  justify-content: space-between;
  padding: 1rem;
}

.preview-left {
  width: 60%;
}
.preview-left h2 {
  text-align: center;
  margin-bottom: 1rem;
  color: #82a0b3;
  font-size: 1rem;
  font-weight: bold;
}

.before-consult-msg {
  margin-top: 2rem;
}
.before-consult-msg .title {
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #072d45;
}
.before-consult-msg .smile-icon {
  width: 20px;
  height: 20px;
  color: #82a0b3;
}
.before-consult-msg .desc {
  margin: 0.5rem 0;
  color: #82a0b3;
  font-size: 0.9rem;
}
.before-consult-msg .ai-link {
  font-weight: medium;
  color: #2a5976;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.before-consult-msg .arrow-icon {
  width: 16px;
  height: 16px;
  stroke-width: 2;
}

/* 최종 스타일 */
.preview-right {
  width: 37%;
}
.preview-right h3 {
  color: #072d45;
  font-size: 1rem;
  font-weight: bold;
  margin-bottom: 1rem;
  margin-left: 10px;
}
.appointment-wrapper {
  border: 1px solid #b9d0df;
  border-radius: 12px;
  padding: 1.5rem;
  height: 480px;
  overflow-y: auto;
}

.appointment-card {
  border: 1px solid #ccc;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
  background-color: #f9fbff;
  transition: all 0.3s;
  cursor: pointer; /* 클릭 가능하도록 커서 변경 */
}

.appointment-card.selected {
  border-color: #2e90fa;
  box-shadow: 0 0 0 2px #2e90fa33;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
}

.card-time {
  color: #1d2939;
  font-weight: bold;
  font-size: 0.95rem;
}

.time-diff {
  font-size: 0.85rem;
  color: #94a3b8;
}

.card-body {
  display: flex;
  gap: 1rem;
}

.lawyer-img {
  width: 90px;
  height: 100px;
  border-radius: 12px;
  object-fit: cover;
  border: 1px solid #e0e7ed;
  flex-shrink: 0;
}

.card-info {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}
.card-time {
  color: #072d45;
}
.lawyer-name {
  margin-bottom: 10px;
}
.lawyer-name .name-bold {
  font-weight: bold;
}

.lawyer-name .name-medium {
  font-weight: medium;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  align-items: center;
}

.tag {
  background-color: #e6edf5;
  color: #516f90;
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 8px;
}

.view-btn {
  margin-top: auto;
  align-self: flex-end;
  padding-top: 8px;
  font-size: 0.8rem;
  background-color: transparent;
  color: #b9d0df;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
  border: none;
}
.more-tags-btn {
  background: none;
  border: none;
  padding: 0;
  margin: 0;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.more-tags-icon {
  width: 16px;
  height: 16px;
  color: #516f90;
}
.no-appointments {
  text-align: center;
}
.no-appointments .no-img {
  width: 200px;
  margin-top: 40px;
  margin-bottom: 1rem;
}
.no-appointments .no-msg {
  font-weight: bold;
  color: #82a0b3;
}
.no-appointments .links {
  margin: 0.5rem 0;
  color: #2a5976;
  font-weight: bold;
}
.no-appointments .links a {
  color: inherit;
  text-decoration: none;
}
.enter-btn-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}

.enter-btn {
  background-color: #2e90fa;
  color: white;
  padding: 0.6rem 1.5rem;
  font-size: 0.95rem;
  font-weight: bold;
  border-radius: 8px;
  border: none;
  transition: background-color 0.3s;
}

.enter-btn:disabled {
  background-color: #e4eef5;
  color: #b9d0df;
  cursor: not-allowed;
}
</style>
