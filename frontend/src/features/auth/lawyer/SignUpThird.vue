<template>
  <div class="signup-wrapper">
    <div class="signup-header">
      <h2 class="signup-title">변호사 회원가입</h2>
      <p class="signup-subtitle">회원정보를 입력해주세요</p>
    </div>

    <div class="step-indicator">
      <span class="step" @click="goToFirstStep">1</span>
      <span class="dot"></span>
      <span class="step" @click="goToSecondStep">2</span>
      <span class="dot"></span>
      <span class="step active">3</span>
    </div>

    <div class="signup-box">
      <form @submit.prevent="handleSubmit" class="form-area">
        <div class="form-group">
          <label>프로필 사진 (필수, 1MB 미만)</label>
          <input type="file" accept="image/*" class="file-choice" @change="handleImageUpload" />

          <p v-if="imageError" class="error-message">{{ imageError }}</p>

          <div v-if="form.photoPreview">
            <img :src="form.photoPreview" alt="사진 미리보기" class="profile-preview" />
          </div>
        </div>

        <div class="form-group">
          <label>소개글 (필수)</label>
          <textarea
            v-model="form.introduction"
            placeholder="의뢰인들에게 나를 소개하는 글을 작성해주세요."
            class="textarea-input"
            rows="4"
          ></textarea>
        </div>

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
import { TAG_MAP } from '@/constants/lawyerTags';

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
      tagMap: TAG_MAP,
      showModal: false,
      // [수정 2] 이미지 에러 메시지를 위한 상태 추가
      imageError: ''
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

    goToFirstStep() {
      this.$router.push('/signup/step1'); // SignUpFirst.vue의 경로
    },
    goToSecondStep() {
      this.$router.push('/signup/step2'); // SignUpFirst.vue의 경로
    },


    // [수정 3] 파일 크기 검증 로직 추가된 handleImageUpload 메소드
    handleImageUpload(event) {
      const file = event.target.files[0];
      this.imageError = ''; // 새 파일 선택 시 기존 에러 메시지 초기화

      if (!file) return;

      // 1MB 파일 크기 제한 설정 (1 * 1024 * 1024 bytes)
      const MAX_SIZE = 1048576;
      if (file.size > MAX_SIZE) {
        this.imageError = '이미지 파일은 1MB를 초과할 수 없습니다.';
        // input 값과 미리보기 초기화
        event.target.value = null;
        this.form.photo = '';
        this.form.photoPreview = '';
        return; // 파일이 크면 여기서 함수를 중단
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        const base64String = e.target.result.split(',')[1];
        this.form.photo = base64String;
        this.form.photoPreview = `data:image/jpeg;base64,${base64String}`;
      };
      reader.readAsDataURL(file);
    },

    async handleSubmit() {
      const previousSignupData = this.authStore.signupData;

      const payload = {
        ...previousSignupData,
        introduction: this.form.introduction,
        tags: this.form.tags,
        photoBase64: this.form.photo
      };

      try {
        await axios.post('/api/lawyers/signup', payload);
        this.showModal = true;
      } catch (error) {
        console.error('회원가입 실패:', error.response?.data || error.message);
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
/* 기존 스타일은 그대로 유지 */
.signup-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 120px;
  margin-bottom: 50px;
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
.file-choice {
  width: 100%;
  padding: 2px;
  font-size: 14px;
  border-radius: 6px;
  /* border: 1px solid #ccc; */
  margin-top: 8px;
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
  padding: 4px 8px;
  border-radius: 12px;
  border: 1px solid #ccc;
  background-color: #f1f1f1;
  font-size: 13px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s;
}
.tag-btn.selected {
  background-color: #1d2b50;
  color: white;
  border-color: #1d2b50;
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

/* [수정 4] 에러 메시지 스타일 추가 */
.error-message {
  color: #d9534f; /* 에러를 나타내는 빨간색 */
  font-size: 12px;
  margin-top: 5px;
}
</style>
