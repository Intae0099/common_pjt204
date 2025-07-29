<template>
  <div>
    <!-- 상단 제목 -->
    <div>
      <h2>변호사 회원가입</h2>
      <p>회원정보를 입력해주세요</p>
    </div>

    <!-- 페이지 단계 표시 -->
    <div>
      <span>1</span>
      <span>2</span>
      <span>3</span>
    </div>

    <!-- 회원가입 폼 -->
    <form @submit.prevent="handleSubmit">
      <div>
        <label>성함</label>
        <input type="text" placeholder="예시) 홍길동" v-model="form.name" required />
      </div>

      <!-- 이메일 입력 섹션 -->
      <div>
        <label>이메일</label>
        <div class="email-input-wrapper">
          <input
            type="email"
            placeholder="예시) honggildong@naver.com"
            v-model="form.loginEmail"
            @blur="validateEmailFormat"
            required
          />
          <!-- v-if를 사용해 조건에 따라 중복검사 버튼 표시 -->
          <button
            type="button"
            v-if="showDuplicateCheckButton"
            @click="checkEmailDuplicate"
            class="duplicate-check-btn"
          >
            중복검사
          </button>
        </div>
        <!-- 이메일 유효성 및 중복 확인 메시지 -->
        <p v-if="!isEmailValid" class="error-message">이메일 형식으로 입력해주세요.</p>
        <p v-if="isEmailChecked" class="success-message">사용 가능한 이메일입니다.</p>
      </div>

      <div>
        <label>비밀번호</label>
        <input type="password" placeholder="영문, 숫자 포함 8자리 이상" v-model="form.password" required />
      </div>

      <div>
        <label>비밀번호 확인</label>
        <input type="password" v-model="form.passwordConfirm" required />
      </div>

      <div>
        <label>휴대번호</label>
        <input type="tel" v-model="form.phone" placeholder="010-1234-5678" required />
      </div>

      <div>
        <label>사무실 번호(선택 사항)</label>
        <input type="text" v-model="form.officeNumber" />
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

        if (res.data.isAvailable) {
          alert('사용 가능한 이메일입니다.');
          this.isEmailChecked = true;
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
/* 이메일 유효성 검사 임시 CSS */
/* 이메일 입력창과 버튼을 한 줄에 배치하기 위한 스타일 */
.email-input-wrapper {
  display: flex;
  align-items: center;
}

.email-input-wrapper input {
  flex-grow: 1; /* 입력창이 남은 공간을 모두 차지하도록 함 */
}

/* 중복검사 버튼 스타일 */
.duplicate-check-btn {
  margin-left: 8px; /* 입력창과의 간격 */
  padding: 8px 12px;
  flex-shrink: 0; /* 버튼 크기가 줄어들지 않도록 함 */
}

/* 에러 메시지 스타일 */
.error-message {
  color: red;
  font-size: 0.8rem;
  margin-top: 4px;
}

/* 성공 메시지 스타일 */
.success-message {
  color: green;
  font-size: 0.8rem;
  margin-top: 4px;
}
</style>
