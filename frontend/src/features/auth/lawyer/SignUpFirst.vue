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

      <div>
        <label>이메일</label>
        <input type="email" placeholder="예시) honggildong@naver.com" v-model="form.email" required />
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
      }
    };
  },
  methods: {
    handleSubmit() {
      if (this.form.password !== this.form.passwordConfirm) {
        alert('비밀번호가 일치하지 않습니다.');
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
