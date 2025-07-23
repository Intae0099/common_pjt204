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
        <label>회차</label>
        <select v-model="form.examRound" required>
          <option disabled value="">회차선택</option>
          <option v-for="n in 30" :key="n" :value="n">{{ n }}회</option>
        </select>
      </div>

      <div>
        <label>경력</label>
        <input
          type="number"
          placeholder="숫자만 입력해주세요"
          v-model.number="form.careerYears"
          min="0"
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
        examRound: '',
        careerYears: ''
      }
    };
  },
  methods: {
    handleSubmit() {
      const authStore = useAuthStore();

      authStore.updateSignup({
        exam: this.form.exam,
        examRound: this.form.examRound,
        careerYears: this.form.careerYears
      });

      this.$router.push('/signup/step3');
    }
  }
};
</script>
