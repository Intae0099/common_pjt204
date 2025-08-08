<template>
  <div class="modal-backdrop" @click.self="closeDropdown">
    <div class="modal-box">
      <button class="close-btn" @click="emit('close')">
        <XMarkIcon class="x-icon" />
      </button>
      <h3 class="modal-title">사건 경위서 선택</h3>

      <!-- ✅ [수정] 데이터 있을 때: 기본 select를 커스텀 드롭다운으로 변경 -->
      <div v-if="applications.length > 0" class="custom-select-wrapper">
        <div class="custom-select" @click="toggleDropdown">
          <div class="custom-select-trigger">
            <!-- computed 속성을 사용하여 선택된 제목 또는 플레이스홀더 표시 -->
            <span>{{ selectedApplicationTitle || '사건 경위서를 선택해주세요' }}</span>
            <div class="arrow" :class="{ 'open': isDropdownOpen }"></div>
          </div>
        </div>
        <!-- 드롭다운 메뉴 (isDropdownOpen 값에 따라 표시/숨김) -->
        <div class="custom-options" v-if="isDropdownOpen">
          <div
            class="custom-option"
            v-for="app in applications"
            :key="app.applicationId"
            :title="app.title"
            @click="selectApplication(app)"
          >
            {{ app.title }}
          </div>
        </div>
      </div>

      <!-- ❗ 데이터 없을 때 -->
      <p v-else class="no-data-message">
        불러올 사건 경위서가 없습니다.
      </p>

      <div class="modal-buttons">
        <button @click="emit('close')" class="cancel-btn">취소</button>
        <button @click="confirm" class="confirm-btn" :disabled="!selectedId">확인</button>
      </div>
    </div>
  </div>
</template>

<script setup>
// ✅ [추가] computed를 import 합니다.
import { ref, onMounted, computed } from 'vue'
import axios from '@/lib/axios'
// ✅ [수정] ChevronDownIcon은 더 이상 사용하지 않습니다.
import { XMarkIcon } from '@heroicons/vue/24/solid'

const emit = defineEmits(['select', 'close'])
const applications = ref([])
const selectedId = ref('')

// ✅ [추가] 드롭다운 메뉴의 열림/닫힘 상태를 관리하는 ref
const isDropdownOpen = ref(false)

// ✅ [추가] 선택된 사건 경위서의 제목을 실시간으로 반영하기 위한 computed 속성
const selectedApplicationTitle = computed(() => {
  const selectedApp = applications.value.find(
    (app) => app.applicationId === selectedId.value
  )
  return selectedApp ? selectedApp.title : ''
})

onMounted(async () => {
  const res = await axios.get('api/applications/me?isCompleted=false')
  applications.value = res.data.data.applicationList
})

// ✅ [추가] 드롭다운 메뉴를 토글하는 함수
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

// ✅ [추가] 드롭다운 메뉴를 닫는 함수
const closeDropdown = () => {
  isDropdownOpen.value = false
}

// ✅ [추가] 옵션을 선택했을 때 실행되는 함수
const selectApplication = (app) => {
  selectedId.value = app.applicationId // 선택된 ID를 저장
  closeDropdown() // 드롭다운 메뉴를 닫음
}

const confirm = () => {
  const selected = applications.value.find(app => app.applicationId === selectedId.value)
  emit('select', {
    applicationId: selected.applicationId,
    title: selected.title,
    content: selected.content,
    summary: selected.summary,
  })
    emit('close')
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-box {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 400px;
  text-align: center;
  border: 1px solid #cfdfe9;
  position: relative;
  overflow: hidden;
}

.modal-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #072D45;
}

/* --- ✅ [추가] 커스텀 드롭다운 스타일 --- */
.custom-select-wrapper {
  position: relative; /* 자식 요소인 custom-options의 기준점이 됨 */
  width: 100%;
  margin-bottom: 1rem;
}

.custom-select {
  position: relative;
  cursor: pointer;
  border: 1px solid #072d45;
  border-radius: 8px;
  background: #fff;
  padding: 0.6rem 2.5rem 0.6rem 0.75rem;
  font-size: 1rem;
  color: #072D45;
  text-align: left;
}

.custom-select-trigger {
  display: flex;
  justify-content: space-between;
  align-items: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 플레이스홀더 스타일 */
.custom-select-trigger span:empty::before {
  content: '사건 경위서를 선택해주세요';
  color: #94a3b8;
}

.arrow {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 5px solid #072D45;
  transition: transform 0.2s ease;
}

.arrow.open {
  transform: translateY(-50%) rotate(180deg);
}

.custom-options {
  position: absolute;
  top: 100%; /* custom-select 바로 아래에 위치 */
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #072d45;
  border-top: none;
  border-radius: 0 0 8px 8px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1001; /* 다른 요소들 위로 올라오도록 설정 */
  margin-top: -1px; /* select 박스와 경계선이 겹치도록 */
}

.custom-option {
  padding: 0.6rem 0.75rem;
  cursor: pointer;
  font-size: 1rem;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.custom-option:hover {
  background-color: #f0f4f8;
}
/* --- 여기까지 커스텀 드롭다운 스타일 --- */

.no-data-message {
  padding: 1rem 0;
  color: #64748b;
}

.modal-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.confirm-btn {
  margin-top: 1.5rem;
  padding: 0.3rem 1.2rem;
  background-color: #fff;
  color: #072D45;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}
.confirm-btn:disabled {
  cursor: not-allowed;
  color: #cbd5e1;
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  cursor: pointer;
}

.x-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: #64748b;
}

.cancel-btn {
  margin-top: 1.5rem;
  padding: 0.3rem 1.2rem;
  background-color: #fff;
  color: #334155;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}
</style>
