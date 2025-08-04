<template>
  <div class="profile-edit-container">
    <h2>프로필 수정</h2>

    <div>
      <img
        :src="`data:image/jpeg;base64,${photo}`"
        alt="프로필 이미지"
        style="width: 150px; height: 150px; object-fit: cover; border-radius: 8px"
      />
    </div>

    <div class="section">
      <h3>이름</h3>
      <input v-model="name" />
    </div>

    <div class="section">
      <h3>소개글</h3>
      <textarea v-model="introduction" maxlength="100" />
    </div>

    <div class="section">
      <h3>전문분야 태그</h3>
      <div class="tag-container">
        <button
          v-for="tag in tagMap"
          :key="tag.id"
          :class="['tag-button', { selected: selectedTagIds.has(tag.id) }]"
          @click="toggleTag(tag.id)"
        >
          {{ tag.name }}
        </button>
      </div>
    </div>

    <div class="footer">
      <button @click="saveChanges">변경사항 확인</button>
    </div>
  </div>
</template>



<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/lib/axios'

const router = useRouter()

const name = ref('')
const introduction = ref('')
const selectedTagIds = ref(new Set())
const photo = ref('')

// 🧠 프론트에 고정된 tagMap
const tagMap = [
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
  { id: 12, name: '금융·증권·기업' },
]


const toggleTag = (tagId) => {
  if (selectedTagIds.value.has(tagId)) {
    selectedTagIds.value.delete(tagId)
  } else {
    selectedTagIds.value.add(tagId)
  }
}

const saveChanges = async () => {
  const payload = {
    name: name.value,
    introduction: introduction.value,
    tagIds: Array.from(selectedTagIds.value),
    photo: photo.value // base64 인코딩된 이미지
  }

  try {
    await axios.patch('/api/lawyers/me', payload)
    alert('수정 완료!')
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
    photo.value = res.data.photo
  } catch (err) {
    console.error('변호사 정보 로딩 실패:', err)
  }
})
</script>


<style scoped>
.tag-button {
  padding: 6px 12px;
  border: 1px solid #ccc;
  border-radius: 12px;
  margin: 4px;
  background-color: #f1f1f1;
  cursor: pointer;
}

.tag-button.selected {
  background-color: #5A45FF;
  color: white;
  border-color: #5A45FF;
}
</style>

