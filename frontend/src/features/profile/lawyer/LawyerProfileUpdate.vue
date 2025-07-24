<template>
  <div class="profile-edit-container">
    <div class="header">
      <div class="back-button" @click="goBack">이전</div>
      <div class="title">프로필 수정</div>
    </div>

    <!-- 소개글 섹션 -->
    <div class="section">
      <h2 class="section-title">소개글</h2>
      <textarea
        class="intro-textarea"
        v-model="introduction"
        placeholder="의뢰인들에게 나를 소개하는 글을 작성해주세요. (100자 이내)"
        maxlength="100"
      ></textarea>
      <div class="char-counter">{{ introduction.length }} / 100</div>
    </div>

    <!-- 태그 선택 섹션 -->
    <div class="section">
      <h2 class="section-title">태그선택</h2>
      <div class="tag-container">
        <!-- v-for를 사용해 모든 태그를 동적으로 렌더링 -->
        <button
          v-for="tag in availableTags"
          :key="tag"
          class="tag-button"
          :class="{ 'selected': selectedTags.has(tag) }"
          @click="toggleTag(tag)"
        >
          {{ tag }}
        </button>
      </div>

      <!-- '#직접입력' 클릭 시 나타나는 입력창 -->
      <div v-if="isCustomInputVisible" class="custom-input-wrapper">
        <input
          type="text"
          v-model="customTagInput"
          class="custom-tag-input"
          placeholder="태그 입력 후 Enter"
          @keyup.enter="addCustomTag"
        />
        <button @click="addCustomTag" class="add-tag-button">추가</button>
      </div>
    </div>

    <!-- 변경사항 확인 버튼 -->
    <div class="footer">
      <button class="save-button" @click="saveChanges">변경사항 확인</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// --- 반응형 데이터 정의 ---
// 1. 소개글
const introduction = ref('');

// 2. 전체 태그 목록
const availableTags = ref([]);

// 3. 사용자가 선택한 태그 목록 (Set 사용으로 중복 방지 및 성능 향상)
const selectedTags = ref(new Set());

// 4. 직접 입력을 위한 상태
const isCustomInputVisible = ref(false);
const customTagInput = ref('');


// --- 메서드 정의 ---
const goBack = () => {
  router.go(-1);
};

// 태그 클릭 시 선택/해제 토글
const toggleTag = (tag) => {
  if (tag === '#직접입력') {
    isCustomInputVisible.value = !isCustomInputVisible.value;
    return;
  }

  if (selectedTags.value.has(tag)) {
    selectedTags.value.delete(tag);
  } else {
    selectedTags.value.add(tag);
  }
};

// 직접 입력한 태그 추가
const addCustomTag = () => {
  const newTag = customTagInput.value.trim();
  if (newTag) {
    // '#'가 없으면 붙여줌
    const formattedTag = newTag.startsWith('#') ? newTag : `#${newTag}`;

    // 선택된 태그 목록에 추가
    selectedTags.value.add(formattedTag);

    // 사용 가능한 태그 목록에도 없으면 추가 (선택사항)
    if (!availableTags.value.includes(formattedTag)) {
        availableTags.value.push(formattedTag);
    }

    // 입력창 초기화 및 숨기기
    customTagInput.value = '';
    isCustomInputVisible.value = false;
  }
};

// 변경사항 저장
const saveChanges = () => {
  // Set을 배열로 변환하여 백엔드로 전송 준비
  const payload = {
    introduction: introduction.value,
    tags: Array.from(selectedTags.value)
  };

  console.log('서버로 전송할 데이터:', payload);
  alert('변경사항이 저장되었습니다!');
  // 실제로는 여기서 API 호출
  // await api.updateProfile(payload);
};


// --- 생명주기 훅: 컴포넌트 로드 시 데이터 로딩 ---
onMounted(() => {
  // --- 실제로는 여기서 백엔드 API를 호출하여 데이터를 가져옵니다 ---

  // 1. 기존 소개글 로딩 (시뮬레이션)
  introduction.value = '안녕하세요. 10년 경력의 베테랑 변호사 홍길동입니다. 여러분의 어려운 문제를 시원하게 해결해 드리겠습니다.';

  // 2. 선택 가능한 모든 태그 목록 로딩 (시뮬레이션)
  availableTags.value = [
    '#교통사고', '#음주운전', '#무면허', '#합의금',
    '#전세사기', '#폭행', '#명예훼손', '#의료사고',
    '#상간소송', '#재산분할', '#양육권', '#위자료',
    '#직접입력' // 직접입력 버튼은 항상 포함
  ];

  // 3. 사용자가 이전에 선택했던 태그 목록 로딩 (시뮬레이션)
  const userPreSelected = ['#교통사고', '#전세사기', '#재산분할'];
  selectedTags.value = new Set(userPreSelected);
});

</script>

<style scoped>

</style>
