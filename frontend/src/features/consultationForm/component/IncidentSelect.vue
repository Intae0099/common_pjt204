<template>
  <div class="modal-backdrop">
    <div class="modal-box">
      <button class="close-btn" @click="emit('close')">
        <XMarkIcon class="x-icon" />
      </button>
      <h3 class="modal-title">사건 경위서 선택</h3>
      <div class="select-wrapper">
        <select v-model="selectedId" class="modal-select" required>
          <option disabled hidden value="" class="placeholder-option">사건 경위서를 선택해주세요</option>
          <option
            v-for="item in applications"
            :key="item.applicationId"
            :value="item.applicationId"
          >
            {{ item.title }}
          </option>
        </select>
        <ChevronDownIcon class="select-icon" />
      </div>

      <div class="modal-buttons">
        <button @click="emit('close')" class="cancel-btn">취소</button>
        <button @click="confirm" class="confirm-btn" :disabled="!selectedId">확인</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ChevronDownIcon, XMarkIcon } from '@heroicons/vue/24/solid'

const emit = defineEmits(['select', 'close'])
const applications = ref([])
const selectedId = ref('')

onMounted(async () => {
  const res = await axios.get('https://i13b204.p.ssafy.io/swagger-ui.html/api/applications/me?isCompleted=false')
  applications.value = res.data
})

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
}

.modal-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #072D45;
}

.modal-select {
  width: 100%;
  padding: 0.6rem 2.5rem 0.6rem 0.75rem;
  border-radius: 8px;
  border: 1px solid #072d45;
  font-size: 1rem;
  appearance: none;
  background-color: white;
  color: #072D45;
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
.select-wrapper {
  position: relative;
  width: 100%;
}
.select-icon {
  width: 1.2rem;
  height: 1.2rem;
  color: #072D45;
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}
:deep(.modal-select:invalid){
  color: #94a3b8;
}

/* 닫기(X) 버튼 */
.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  cursor: pointer;
}

/* X 아이콘 */
.x-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: #64748b;
}
/* 취소 버튼 */
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
