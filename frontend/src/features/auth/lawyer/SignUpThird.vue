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
      <span class="step">2</span>
      <span class="dot">···</span>
      <span class="step active">3</span>
    </div>

    <!-- 회원가입 폼 -->
    <div class="signup-box">
      <form @submit.prevent="handleSubmit" class="form-area">
        <!-- 프로필 사진 -->
        <div class="form-group">
          <label>프로필 사진 (필수)</label>
          <input type="file" accept="image/*" @change="handleImageUpload" />
          <div v-if="form.photoPreview">
            <img :src="form.photoPreview" alt="사진 미리보기" class="profile-preview" />
          </div>
        </div>

        <!-- 소개글 -->
        <div class="form-group">
          <label>소개글 (필수)</label>
          <textarea
            v-model="form.introduction"
            placeholder="의뢰인들에게 나를 소개하는 글을 작성해주세요."
            class="textarea-input"
            rows="4"
          ></textarea>
        </div>

        <!-- 태그 선택 -->
        <div class="form-group">
          <label>태그 선택 (1개 이상 필수 선택)</label>
          <div class="tag-list">
            <button
              v-for="tag in tagMap"
              :key="tag.id"
              type="button"
              class="tag-btn"
              :class="{ selected: form.tags.includes(tag.id) }"
              @click="toggleTag(tag.id)"
            >
              #{{ tag.name }}
            </button>
          </div>
        </div>

        <button type="submit" class="next-btn" :disabled="form.tags.length === 0">가입하기</button>
      </form>
    </div>

    <!-- 완료 모달 -->
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
        tags: [],
        photo: '',
        photoPreview: ''
      },
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
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        const base64String = e.target.result.split(',')[1];
        this.form.photo = base64String;
        this.form.photoPreview = `data:image/jpeg;base64,${base64String}`;
      };
      reader.readAsDataURL(file);
    },
    async handleSubmit() {
      this.authStore.updateSignup({
        introduction: this.form.introduction,
        tags: this.form.tags,
        photo: this.form.photo
      });
      const payload = { ...this.authStore.signupData };
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
/* 기존 스타일 유지 */
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
  margin: 20px 0 30px 0;
}
.step {
  line-height: 40px;
  text-align: center;
  border-radius: 50%;
  font-weight: bold;
  color: #B9D0DF;
}
.step.active {
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
.textarea-input {
  width: 100%;
  padding: 10px;
  font-size: 14px;
  border-radius: 6px;
  border: 1px solid #ccc;
  resize: none;
}
.profile-preview {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
  margin-top: 8px;
}
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.tag-btn {
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid #ccc;
  background-color: #f1f5f9;
  font-size: 13px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s;
}
.tag-btn.selected {
  background-color: #0c2c46;
  color: white;
  border-color: #0c2c46;
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
button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.7;
}
</style>
