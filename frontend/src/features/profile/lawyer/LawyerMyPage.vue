<template>
  <div class="lawyer-mypage">
    <h2>변호사 마이페이지</h2>

    <!-- ✅ 프로필 정보 -->
    <section v-if="lawyer">
      <h3>👤 프로필 정보</h3>
      <p><strong>이름:</strong> {{ lawyer.name }}</p>
      <p><strong>이메일:</strong> {{ lawyer.loginEmail }}</p>
      <p><strong>소개:</strong> {{ lawyer.introduction }}</p>
      <p><strong>전문분야:</strong>
        <span v-for="tag in lawyer.tags" :key="tag" class="tag">{{ tag }}</span>
      </p>
    </section>

    <!-- ✅ 오늘 이후 상담 예약 -->
    <section>
      <h3>📅 예약된 상담</h3>
      <ul v-if="upcomingAppointments.length > 0">
        <li v-for="appt in upcomingAppointments" :key="appt.appointmentId">
          <p><strong>의뢰인:</strong> {{ appt.client.name }} ({{ appt.client.email }})</p>
          <p><strong>상담 일시:</strong> {{ formatDateTime(appt.startTime) }}</p>
        </li>
      </ul>
      <p v-else>예정된 상담이 없습니다.</p>
    </section>

    <!-- ✅ 이후 구현 예정 기능 안내 -->
    <section>
      <h3>📁 기타</h3>
      <ul>
        <li>📝 상담신청서 보관함 (구현 예정)</li>
        <li>📜 이전 상담 내역 (구현 예정)</li>
        <li>🚨 <button @click="handleDelete">회원 탈퇴</button></li>
      </ul>
    </section>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'LawyerMyPage',
  data() {
    return {
      lawyer: null,
      appointments: [],
      clients: [],
    };
  },
  computed: {
    // 오늘 이후 예약만 필터링
    upcomingAppointments() {
      const now = new Date();
      return this.appointments
        .filter(appt => new Date(appt.startTime) > now)
        .map(appt => {
          const client = this.clients.find(c => c.clientId === appt.clientId);
          return {
            ...appt,
            client: client || { name: '알 수 없음', email: '알 수 없음' },
          };
        });
    }
  },
  methods: {
    async fetchLawyerProfile() {
      try {
        const res = await axios.get('/api/lawyers/me');
        this.lawyer = res.data;
      } catch (err) {
        console.error('변호사 정보 조회 실패:', err);
      }
    },

    async fetchAppointments() {
      try {
        const res = await axios.get('/api/appointments/me');
        this.appointments = res.data;
      } catch (err) {
        console.error('상담 예약 조회 실패:', err);
      }
    },

    async fetchClients() {
      try {
        const res = await axios.get('/api/admin/clients/list');
        this.clients = res.data;
      } catch (err) {
        console.error('클라이언트 목록 조회 실패:', err);
      }
    },

    formatDateTime(dateString) {
      const options = {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
      };
      return new Date(dateString).toLocaleString(undefined, options);
    },

    handleDelete() {
      alert('회원 탈퇴 기능은 아직 구현되지 않았습니다.');
    }
  },
  async mounted() {
    await Promise.all([
      this.fetchLawyerProfile(),
      this.fetchAppointments(),
      this.fetchClients()
    ]);
  }
};
</script>

<style scoped>
.lawyer-mypage {
  padding: 1rem;
}
.tag {
  background-color: #5A45FF;
  color: white;
  padding: 3px 8px;
  margin-right: 4px;
  border-radius: 12px;
  font-size: 0.85rem;
}
</style>
