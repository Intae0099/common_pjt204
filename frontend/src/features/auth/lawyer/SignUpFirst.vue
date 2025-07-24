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
            v-model="form.email"
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

export default {
  name: 'SignUpFirst',
  data() {
    return {
      form: {
        name: '',
        email: '',
        password: '',
        passwordConfirm: '',
        phone: '',
        officeNumber: ''
      },
      // 이메일 유효성 상태를 관리하기 위한 데이터 추가
      isEmailValid: true, // 처음에는 에러 메시지를 보여주지 않기 위해 true로 설정
      isEmailChecked: false, // 이메일 중복 확인을 통과했는지 여부
    };
  },
  computed: {
    // 중복검사 버튼을 보여줄지 결정하는 computed 속성
    showDuplicateCheckButton() {
      // 이메일 형식을 검사하는 정규식
      // user@domain.com 과 같은 전체 형식을 만족하는지 확인합니다.
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

      // 정규식 검사를 통과하고, 아직 중복 확인을 완료하지 않았을 때만 버튼을 보여줍니다.
      return emailRegex.test(this.form.email) && !this.isEmailChecked;
    }
  },
  watch: {
    // 사용자가 이메일을 수정한 경우, 중복 확인 상태를 초기화
    'form.email'(newValue, oldValue) {
      if (newValue !== oldValue) {
        this.isEmailChecked = false;
        this.validateEmailFormat(); // 이메일이 변경될 때마다 형식 유효성도 다시 체크
      }
    }
  },
  methods: {
    // 이메일 형식을 검사하는 메소드
    validateEmailFormat() {
      if (this.form.email === '') {
        this.isEmailValid = true; // 비어있을 때는 에러 메시지 숨김
        return;
      }
      const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      this.isEmailValid = regex.test(this.form.email);
    },

    // 이메일 중복을 확인하는 메소드 (API 호출 시뮬레이션)
    checkEmailDuplicate() {
      // 먼저 이메일 형식이 올바른지 확인
      this.validateEmailFormat();
      if (!this.isEmailValid) {
        alert('이메일 형식이 올바르지 않습니다.');
        return;
      }

      // --- 실제로는 여기에서 백엔드 API를 호출합니다 ---
      console.log(`'${this.form.email}' 이메일 중복 확인 요청...`);
      // 가상으로 이미 사용 중인 이메일 목록
      const takenEmails = ['test@test.com', 'admin@example.com'];

      // setTimeout으로 네트워크 지연 시뮬레이션
      setTimeout(() => {
        if (takenEmails.includes(this.form.email)) {
          alert('이미 사용 중인 이메일입니다. 다른 이메일을 입력해주세요.');
          this.isEmailChecked = false;
        } else {
          alert('사용 가능한 이메일입니다.');
          this.isEmailChecked = true; // 중복 확인 통과!
        }
      }, 500); // 0.5초 딜레이
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
        email: this.form.email,
        password: this.form.password,
        phone: this.form.phone,
        officeNumber: this.form.officeNumber
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
