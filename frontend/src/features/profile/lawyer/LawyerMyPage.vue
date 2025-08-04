<template>
  <div class="lawyer-mypage">
    <h2>변호사 마이페이지</h2>

    <!-- ✅ 프로필 정보 -->
    <section v-if="lawyer">
      <h3>👤 프로필 정보</h3>
      <img
        :src="lawyer.photo || 'https://via.placeholder.com/150'"
        alt="변호사 프로필 사진"
        class="profile-photo"
      />
      <p><strong>이름:</strong> {{ lawyer.name }}</p>
      <p><strong>이메일:</strong> {{ lawyer.loginEmail }}</p>
      <p><strong>소개:</strong> {{ lawyer.introduction }}</p>
      <p><strong>전문분야:</strong>
        <span v-for="tagId in lawyer.tags" :key="tagId" class="tag">
          {{ getTagName(tagId) }}
        </span>
      </p>
      <button class="btn btn-outline-primary mt-3" @click="goToProfileUpdate">수정하기</button>
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

    <!-- ✅ 상담 대기 중인 목록 -->
    <section v-if="pendingAppointments.length > 0">
      <h3>수락 대기중인 상담</h3>
      <ul>
        <li v-for="appt in pendingAppointments" :key="appt.appointmentId">
          <p>의뢰인: {{ getClientName(appt.clientId) }} ({{ getClientEmail(appt.clientId) }})</p>
          <button class="btn btn-success btn-sm" @click="acceptAppointment(appt.appointmentId)">상담 수락하기</button>
        </li>
      </ul>
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
import axios from '@/lib/axios';

export default {
  name: 'LawyerMyPage',

  data() {
    return {
      lawyer: null,
      appointments: [],
      clients: [],
      tagMap: [
        { id: 1, name: '형사 분야' },
        { id: 2, name: '교통·사고·보험' },
        { id: 3, name: '가사·가족' },
        { id: 4, name: '민사·계약·채권' },
        { id: 5, name: '파산·회생·채무조정' },
        { id: 6, name: '상속·증여' },
        { id: 7, name: '지식재산권' },
        { id: 8, name: '노동·고용' },
        { id: 9, name: '행정·조세' },
        { id: 10, name: '환경·공공' },
        { id: 11, name: '의료·생명·개인정보' },
        { id: 12, name: '금융·증권·기업' }
      ]
    }
  },

  computed: {
    // 오늘 이후 예약만 필터링
    upcomingAppointments() {
      const now = new Date()
      return this.appointments
        .filter(appt =>
          appt.appointmentStatus === 'APPROVED' &&
          appt.startTime && new Date(appt.startTime) > now
        )
        .map(appt => {
          const client = this.clients.find(c => c.clientId === appt.clientId)
          return {
            ...appt,
            client: client || { name: '알 수 없음', email: '알 수 없음' },
          }
        })
    },
    pendingAppointments() {
      return this.appointments.filter(appt => appt.appointmentStatus === 'PENDING')
    },
  },

  methods: {
    async fetchLawyerProfile() {
      try {
        const res = await axios.get('/api/lawyers/me')
        this.lawyer = res.data
      } catch (err) {
        console.error('변호사 정보 조회 실패:', err)
      }
    },

    async fetchAppointments() {
      try {
        const res = await axios.get('/api/appointments/me')
        this.appointments = res.data
      } catch (err) {
        console.error('상담 예약 조회 실패:', err)
      }
    },

    async fetchClients() {
      try {
        const res = await axios.get('/api/admin/clients/list')
        this.clients = res.data
      } catch (err) {
        console.error('클라이언트 목록 조회 실패:', err)
      }
    },
    getTagName(id) {
      const tag = this.tagMap.find(t => t.id === id)
      return tag ? tag.name : '알 수 없음'
    },

    getClientName(clientId) {
      const client = this.clients.find(c => String(c.clientId) === String(clientId))
      return client ? client.name : '알 수 없음'
    },

    getClientEmail(clientId) {
      const client = this.clients.find(c => String(c.clientId) === String(clientId))
      return client ? client.email : '알 수 없음'
    },

    formatDateTime(dateString) {
      const options = {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
      }
      return new Date(dateString).toLocaleString(undefined, options)
    },

    goToProfileUpdate() {
      this.$router.push({ name: 'LawyerProfileUpdate' })
    },



    async acceptAppointment(appointmentId) {
      try {
        await axios.patch(`/api/appointments/${appointmentId}/status`, {
          appointmentStatus: 'APPROVED'
        })
        alert('상담을 수락했습니다.')

        // 상태 변경 후 다시 목록 갱신
        await this.fetchAppointments()
      } catch (err) {
        console.error('상담 수락 실패:', err)
        alert('상담 수락 중 오류가 발생했습니다.')
      }
    },

    handleDelete() {
      alert('회원 탈퇴 기능은 아직 구현되지 않았습니다.')
    },

  },

  async mounted() {
    await Promise.all([
      this.fetchLawyerProfile(),
      this.fetchAppointments(),
      this.fetchClients()
    ])
  }
}
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
