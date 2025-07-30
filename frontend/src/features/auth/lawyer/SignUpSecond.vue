<template>
  <div>
    <!-- 상단 제목 -->
    <div>
      <h2>변호사 회원가입</h2>
      <p>회원정보를 입력해주세요</p>
    </div>

    <!-- 단계 표시 -->
    <div>
      <span>1</span>
      <span>2</span>
      <span>3</span>
    </div>

    <!-- 회원가입 2단계 폼 -->
    <form @submit.prevent="handleSubmit">
      <div>
        <label>출신시험</label>
        <select v-model="form.exam" required>
          <option disabled value="">시험선택</option>
          <option value="사법시험">사법시험</option>
          <option value="로스쿨">로스쿨</option>
        </select>
      </div>

      <div>
        <label>변호사 등록번호</label>
        <input
          type="text"
          placeholder="숫자만 입력해주세요"
          v-model="form.registrationNumber"
          required
        />
      </div>

      <button type="submit">다음</button>
    </form>

    <!-- 하단 링크 -->
    <div>
      <router-link to="/">메인화면으로</router-link>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth';

export default {
  name: 'SignUpSecond',
  data() {
    return {
      form: {
        exam: '',
        registrationNumber: ''
      }
    };
  },
  methods: {
    handleSubmit() {
      const authStore = useAuthStore();

      authStore.updateSignup({
        exam: this.form.exam,
        registrationNumber: this.form.registrationNumber
      });

      this.$router.push('/signup/step3');
    }
  }
};
</script>
