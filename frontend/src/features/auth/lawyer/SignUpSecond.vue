<template>
  <div class="signup-wrapper">
    <!-- 상단 제목 -->
    <div class="signup-header">
      <h2 class="signup-title">변호사 회원가입</h2>
      <p class="signup-subtitle">회원정보를 입력해주세요</p>
    </div>

    <!-- 페이지 단계 표시 -->
    <div class="step-indicator">
      <span class="step">1</span>
      <span class="dot">···</span>
      <span class="step active">2</span>
      <span class="dot">···</span>
      <span class="step">3</span>
    </div>

    <!-- 회원가입 폼 -->
    <div class="signup-box">
      <form @submit.prevent="handleSubmit" class="form-area">
        <div class="form-group">
          <label>출신시험</label>
          <select v-model="form.exam" required class="custom-select">
            <option disabled value="">시험선택</option>
            <option value="사법시험">사법시험</option>
            <option value="로스쿨">로스쿨</option>
          </select>
        </div>

        <div class="form-group">
          <label>변호사 등록번호</label>
          <input
            type="text"
            placeholder="숫자만 입력해주세요"
            v-model="form.registrationNumber"
            required
          />
        </div>

        <button type="submit" class="next-btn">다음</button>
      </form>
    </div>

    <!-- 하단 링크 -->
    <div class="footer-links">
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

<style scoped>
* {
  font-family: 'Noto Sans KR', sans-serif;
}

.signup-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 120px;
  font-family: 'Pretendard', sans-serif;
}

.signup-header {
  text-align: center;
}

.signup-title {
  font-size: 25px;
  font-weight: bold;
}

.signup-subtitle {
  font-size: 14px;
  color: #82A0B3;
  margin-top: 6px;
}

.step-indicator {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin: 20px 0px 30px 0px;
}

.step {
  line-height: 40px;
  text-align: center;
  border-radius: 50%;
  font-weight: bold;
  color: #B9D0DF;
}

.step.active {
  line-height: 35px;
  width: 40px;
  height: 40px;
  background-color: #0c2c46;
  color: white;
  border: none;
  font-size: 1.5rem;
}

.dot {
  color: #B9D0DF;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  letter-spacing: 0.2rem;
}

.signup-box {
  width: 400px;
  background-color: white;
  border: 1px solid #E4EEF5;
  border-radius: 10px;
  padding: 40px 30px;
  box-shadow: 0 1px 5px #E4EEF5;
}

.form-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.form-group label {
  font-size: 14px;
  margin-bottom: 6px;
  font-weight: bold;
  color: #072D45;
}

.form-group input,
.custom-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
}

.next-btn {
  background-color: #0c2c46;
  color: white;
  border: none;
  padding: 12px;
  width: 100%;
  border-radius: 6px;
  font-weight: bold;
  font-size: 15px;
  cursor: pointer;
  margin-top: 10px;
}

.footer-links {
  margin-top: 20px;
  font-size: 13px;
  color: #777;
}
</style>
