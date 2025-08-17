<template>
  <div class="signup-wrapper">
    <div class="signup-header">
      <h2 class="signup-title">변호사 회원가입</h2>
      <p class="signup-subtitle">회원정보를 입력해주세요</p>
    </div>

    <div class="step-indicator">
      <span class="step active">1</span>
      <span class="dot"></span>
      <span class="step">2</span>
      <span class="dot"></span>
      <span class="step">3</span>
    </div>

    <div class="signup-box">
      <form @submit.prevent="handleSubmit" class="form-area">
        <div class="form-group">
          <label>성함</label>
          <input type="text" placeholder="예시) 홍길동" v-model="form.name" required />
        </div>

        <div class="form-group">
          <label>이메일</label>
          <div class="email-input-wrapper">
            <input
              class="inline-email"
              type="email"
              placeholder="예시) honggildong@naver.com"
              v-model="form.loginEmail"
              :disabled="emailDisabled"
              @blur="validateEmailFormat"
              required
            />
            <button
              type="button"
              v-if="showDuplicateCheckButton"
              @click="checkEmailDuplicate"
              class="duplicate-check-btn"
            >
              중복검사
            </button>
          </div>
          <p v-if="!isEmailValid" class="error-message">이메일 형식으로 입력해주세요.</p>
          <p v-if="isEmailChecked" class="success-message">사용 가능한 이메일입니다.</p>
        </div>

        <div class="form-group">
          <label>비밀번호</label>
          <input
            type="password"
            placeholder="영문, 숫자 포함 8자리 이상"
            v-model="form.password"
            required
          />
        </div>

        <div class="form-group">
          <label>비밀번호 확인</label>
          <input type="password" v-model="form.passwordConfirm" required />
        </div>

        <button type="submit" class="next-btn">다음</button>
      </form>
    </div>

    <div class="footer-links">
      <router-link to="/" class="main_link">메인화면으로</router-link>
    </div>
  </div>
</template>


<script>
import { useAuthStore } from '@/stores/auth';
import axios from '@/lib/axios';

export default {
  name: 'SignUpFirst',
  data() {
    return {
      form: {
        name: '',
        loginEmail: '',   // 기존 email → loginEmail 로 변경
        password: '',
        passwordConfirm: '',
      },
      isEmailValid: true,
      isEmailChecked: false,
      emailDisabled: false,
    };
  },
  computed: {
    showDuplicateCheckButton() {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(this.form.loginEmail) && !this.isEmailChecked;
    }
  },
  watch: {
    'form.loginEmail'(newValue, oldValue) {
      if (newValue !== oldValue) {
        this.isEmailChecked = false;
        this.validateEmailFormat();
      }
    }
  },
  methods: {
    validateEmailFormat() {
      if (this.form.loginEmail === '') {
        this.isEmailValid = true;
        return;
      }
      const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      this.isEmailValid = regex.test(this.form.loginEmail);
    },

    async checkEmailDuplicate() {
      this.validateEmailFormat();
      if (!this.isEmailValid) {
        alert('이메일 형식이 올바르지 않습니다.');
        return;
      }

      try {
        const res = await axios.post('/api/lawyers/emails/check', {
          loginEmail: this.form.loginEmail
        });

        if (res.data.isAvailable === 'true') {
          alert('사용 가능한 이메일입니다.');
          this.isEmailChecked = true;
          this.emailDisabled = true;
        } else {
          alert('이미 사용 중인 이메일입니다.');
          this.isEmailChecked = false;
        }
      } catch (err) {
        alert('이메일 중복 확인 중 오류가 발생했습니다.');
        console.error(err);
        this.isEmailChecked = false;
      }
    },


    handleSubmit() {
      // 비밀번호 일치 여부 확인
      if (this.form.password !== this.form.passwordConfirm) {
        alert('비밀번호가 일치하지 않습니다.');
        return;
      }

      // 이메일 중복 확인을 통과했는지 확인
      if (!this.isEmailChecked) {
        alert('이메일 중복 확인을 완료해주세요.');
        return;
      }

      const authStore = useAuthStore();
      authStore.updateSignup({
        name: this.form.name,
        loginEmail: this.form.loginEmail,
        password: this.form.password,
        // exam, registrationNumber, introduction, tags 등은 다음 단계에서 추가
      });

      this.$router.push('/signup/step2');
    }
  }
};
</script>

<style scoped>
*{
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
  color: #6c9bcf;
  font-size: 0rem;
  display: flex;
  align-items: center;
  margin-top: 15px;
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

.form-group input:not(.inline-email) {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
}

.email-input-wrapper input.inline-email {
  flex-grow: 1;
  min-width: 0;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
}

.email-input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}
.email-input-wrapper input {
  flex-grow: 1;
}

.duplicate-check-btn {
  padding: 8px 12px;
  background-color: #f2f2f2;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
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

}
.main_link {
  color: #888;
  font-style: none;
  text-decoration: none;
}
.main_link:hover {
  color: #6c9bcf;
}

.error-message {
  color: red;
  font-size: 0.8rem;
  margin-top: 4px;
}
.success-message {
  color: green;
  font-size: 0.8rem;
  margin-top: 4px;
}

</style>
