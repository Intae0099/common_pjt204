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
        <label>소개글 (필수)</label>
        <textarea
          v-model="form.introduction"
          placeholder="의뢰인들에게 나를 소개하는 글을 작성해주세요."
        ></textarea>
      </div>

      <div>
        <label>태그 선택 (1개 이상 필수 선택)</label>
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

      <button type="submit" :disabled="form.tags.length === 0">가입하기</button>
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
import axios from '@/lib/axios';

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
      ],
      showModal: false,
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
      // 1) Store에 값 병합
      this.authStore.updateSignup({
        introduction: this.form.introduction,
        tags: this.form.tags
      });

      // 2) Proxy를 풀어서 plain Object로 복사
      const payload = { ...this.authStore.signupData };

      console.log('payload to send:', payload);

      try {
        await axios.post('/api/lawyers/signup', payload);
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
button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.7;
}
</style>
