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

    <!-- 3단계 폼 -->
    <form @submit.prevent="handleSubmit">
      <div>
        <label>소개글 (선택사항)</label>
        <textarea
          v-model="form.introduction"
          placeholder="의뢰인들에게 나를 소개하는 글을 작성해주세요."
        ></textarea>
      </div>

      <div>
        <label>태그 선택 (선택사항)</label>
        <div>
          <button
            v-for="tag in tagMap"
            :key="tag.id"
            type="button"
            :class="{ selected: form.tags.includes(tag.id) }"
            @click="toggleTag(tag.id)"
          >
            {{ tag.name }}
          </button>
        </div>
      </div>

      <button type="submit">가입하기</button>
    </form>

    <!-- 가입 완료 모달 -->
    <BaseModal
      :visible="showModal"
      message="인증까지 2~3일이 소요됩니다."
      confirmText="확인"
      @confirm="confirmModal"
    />
  </div>
</template>

<script>
import BaseModal from '@/components/BaseModal.vue';
import { useAuthStore } from '@/stores/auth';
import axios from 'axios';

export default {
  name: 'SignUpThird',
  components: { BaseModal },
  data() {
    return {
      form: {
        introduction: '',
        tags: [] // 숫자 ID 배열
      },
      // ID ↔ 이름 매핑 테이블
      tagMap: [
        { id: 1, name: '합의금' },
        { id: 2, name: '교통사고' },
        { id: 3, name: '무면허' },
        { id: 4, name: '음주운전' },
        { id: 5, name: '재산분할' },
        { id: 6, name: '위자료' },
        { id: 7, name: '상간소송' },
        { id: 8, name: '양육권' },
        { id: 9, name: '폭행' },
        { id: 10, name: '명예훼손' },
        { id: 11, name: '전세사기' },
        { id: 12, name: '의료사고' }
      ],
      showModal: false
    };
  },
  computed: {
    authStore() {
      return useAuthStore();
    }
  },
  methods: {
    toggleTag(tagId) {
      const tags = this.form.tags;
      if (tags.includes(tagId)) {
        this.form.tags = tags.filter(id => id !== tagId);
      } else {
        this.form.tags.push(tagId);
      }
    },
    async handleSubmit() {
      // 회원가입 전 데이터 저장
      this.authStore.updateSignup({
        introduction: this.form.introduction,
        tags: this.form.tags
      });

      try {
        await axios.post('/api/lawyers/signup', this.authStore.signupData);
        this.showModal = true;
      } catch (error) {
        console.error('회원가입 실패:', error);
        alert('회원가입에 실패했습니다. 다시 시도해주세요.');
      }
    },
    confirmModal() {
      this.showModal = false;
      this.authStore.resetSignup();
      this.$router.push('/');
    }
  }
};
</script>

<style scoped>

</style>
