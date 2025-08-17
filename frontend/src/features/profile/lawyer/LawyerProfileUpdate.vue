<template>
  <div class="profile-edit-container">
    <div class="back-button" @click="goBack">
      <ChevronLeftIcon class="chevron-icon" />
      <span>마이페이지</span>
    </div>

    <h2>프로필 수정</h2>

    <div class="profile-photo-wrapper">
      <img
        v-if="photo"
        :src="`data:image/jpeg;base64,${photo}`"
        alt="프로필 이미지"
        class="profile-img"
      />
      <img
        v-else
        src="https://via.placeholder.com/120"
        alt="기본 프로필 이미지"
        class="profile-img"
      />
      <div class="upload-section">
        <label class="upload-label">
          사진 변경 (1MB 미만)
          <input type="file" accept="image/*" @change="onFileChange" />
        </label>
        <p v-if="imageError" class="error-message">{{ imageError }}</p>
      </div>
    </div>

    <div class="section">
      <h3>이름</h3>
      <input type="text" v-model="name" placeholder="이름을 입력하세요" />
    </div>

    <div class="section">
      <h3>소개글</h3>
      <textarea
        v-model="introduction"
        maxlength="100"
        placeholder="의뢰인들에게 나를 소개하는 글을 작성해주세요. (100자 이내)"
      />
    </div>

    <div class="section">
      <h3>태그 선택</h3>
      <div class="tag-container">
        <button
          v-for="tag in tagMap"
          :key="tag.id"
          :class="['tag-button', { selected: selectedTagIds.has(tag.id) }]"
          @click="toggleTag(tag.id)"
        >
          #{{ tag.name }}
        </button>
      </div>
    </div>

    <div class="footer">
      <button @click="saveChanges">변경사항 저장</button>
    </div>
  </div>
</template>




<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/lib/axios'
import { TAG_MAP } from '@/constants/lawyerTags'
import { ChevronLeftIcon } from '@heroicons/vue/24/solid'

const router = useRouter()

const name = ref('')
const introduction = ref('')
const selectedTagIds = ref(new Set())
const photo = ref('')
const imageError = ref('')

// 🧠 프론트에 고정된 tagMap
const tagMap = TAG_MAP

const goBack = () => {
  router.push('/lawyer/mypage')  // 마이페이지 경로로 이동
}

const toggleTag = (tagId) => {
  if (selectedTagIds.value.has(tagId)) {
    selectedTagIds.value.delete(tagId)
  } else {
    selectedTagIds.value.add(tagId)
  }
}

const onFileChange = (e) => {
  const file = e.target.files[0]
  imageError.value = ''

  if (!file) return;

  const MAX_SIZE = 1 * 1024 * 1024;
  if (file.size > MAX_SIZE) {
    imageError.value = '이미지 파일은 1MB를 초과할 수 없습니다.';
    e.target.value = null; // input 값 초기화 (같은 파일 재선택 가능하게)
    return; // 파일이 크면 여기서 함수를 중단
  }

  const reader = new FileReader()
  reader.onload = () => {
    const base64 = reader.result.split(',')[1]
    photo.value = base64
  }
  reader.readAsDataURL(file)

}

const saveChanges = async () => {
  const payload = {
    name: name.value,
    introduction: introduction.value,
    tags: Array.from(selectedTagIds.value),
    photoBase64: photo.value,
  }


  try {
    await axios.patch('/api/lawyers/me/edit', payload)
    alert('수정이 완료되었습니다.')
    router.back()
  } catch (err) {
    console.error('저장 실패:', err)
    alert('오류가 발생했습니다.')
  }
}

onMounted(async () => {
  try {
    const res = await axios.get('/api/lawyers/me')
    name.value = res.data.name
    introduction.value = res.data.introduction
    selectedTagIds.value = new Set(res.data.tags) // ID만 받음
    photo.value = res.data.photoBase64
  } catch (err) {
    console.error('변호사 정보 로딩 실패:', err)
  }
})
</script>


<style scoped>
.upload-section {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  margin-left: 14px;
}

.error-message {
  color: #d32f2f; /* 에러를 나타내는 빨간색 */
  font-size: 12px;
  font-weight: 500;
}

.header-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}

.back-btn {
  background-color: #ffffff;
  border: none;
  color: #2B2F38;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}



.profile-edit-container {
  max-width: 800px;
  margin: 80px auto;
  padding: 40px;
  background-color: #ffffff;
  border-radius: 12px;
  font-family: 'Noto Sans KR', sans-serif;
  color: #333333;
}
.back-button {
  margin-top: 10px;
  margin-bottom: 20px;
  margin-left: -10px;
  font-size: 1rem;
  color: #6c9bcf;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  width: 100px;
  transition: color 0.2s ease-in-out;
}

.back-button:hover {
  color: #cfcfcf;
}
.chevron-icon {
  width: 20px;
  height: 20px;
}


.profile-edit-container h2 {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 32px;
  text-align: center;
}

.section {
  margin-top: 32px;
}

.section h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333333;
}

input[type="text"],
textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #cfcfcf;
  border-radius: 8px;
  font-size: 14px;
  resize: none;
  background-color: #ffffff;
  color: #333333;
}

textarea::placeholder {
  color: #888;
}

/* 프로필 사진 업로드 */
.profile-photo-wrapper {
  display: flex;
  flex-direction: column;   /* ⬅️ 핵심: 세로 배치 */
  align-items: flex-start;      /* ⬅️ 이미지 기준 중앙 정렬 (왼쪽 정렬 원하면 flex-start) */
  gap: 12px;                /* 이미지와 버튼 간격 */
  width: 100%;
}

.profile-img {
  width: 180px;
  height: 200px;
  border-radius: 8px;
  object-fit: cover;
  border: 1px solid #f1f1f1;
}

.upload-label {
  font-size: 14px;
  color: #1d2b50;
  cursor: pointer;
  padding: 8px 12px;
  border: 1px solid #1d2b50;
  border-radius: 8px;
  display: inline-block;
  transition: background-color 0.2s;
}

.upload-label:hover {
  background-color: #1d2b50;
  color: white;
}

input[type="file"] {
  display: none;
}

/* 태그 버튼 */
.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.tag-button {
  padding: 4px 8px;
  border: 1px solid #f1f1f1;
  border-radius: 12px;
  background-color: #f1f1f1;
  font-size: 13px;
  cursor: pointer;
  color: #333;
  transition: all 0.2s;
}

.tag-button.selected {
  background-color: #1d2b50;
  color: white;
  border-color: #1d2b50;
}

/* 저장 버튼 */
.footer {
  margin-top: 40px;
  text-align: center;
}

.footer button {
  padding: 10px 24px;
  background-color: #1d2b50;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.footer button:hover {
  background-color: #6c9bcf;
}

</style>

