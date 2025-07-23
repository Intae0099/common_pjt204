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
            v-for="tag in tagList"
            :key="tag"
            type="button"
            @click="toggleTag(tag)"
          >
            {{ tag }}
          </button>
        </div>
      </div>

      <button type="submit">가입하기</button>
    </form>

    <!-- 건너뛰기 링크 -->
    <div>
      <button type="button" @click="handleSkip">건너뛰기</button>
    </div>

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

export default {
  name: 'SignUpThird',
  components: {
    BaseModal
  },
  data() {
    return {
      form: {
        introduction: '',
        tags: []
      },
      tagList: [
        '합의금', '교통사고', '무면허', '음주운전',
        '재산분할', '위자료', '상간소송', '양육권',
        '폭행', '명예훼손', '전세사기', '의료사고'
      ],
      showModal: false
    };
  },
  methods: {
    toggleTag(tag) {
      const tags = this.form.tags;
      if (tags.includes(tag)) {
        this.form.tags = tags.filter(t => t !== tag);
      } else {
        this.form.tags.push(tag);
      }
    },
    handleSubmit() {
      console.log('3단계 입력 정보:', this.form);
      this.showModal = true; // 모달 표시
    },
    confirmModal() {
      this.showModal = false;
      this.$router.push('/signup/complete'); // 최종 이동
    },
    handleSkip() {
      this.$router.push('/signup/complete');
    }
  }
};
</script>
