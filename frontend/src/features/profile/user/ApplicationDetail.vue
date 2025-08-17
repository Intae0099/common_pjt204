<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-content">
      <button class="close-btn" @click="$emit('close')">
        <XMarkIcon class="x-icon" />
      </button>
      <div class="modal-scroll-area">
        <form class="consult-form">
          <input
            type="text"
            :value="data.title"
            readonly
            class="readonly-input-title"
          />

          <div v-if="data.summary" class="form-group scrollable-group">
            <label>사건 개요</label>
            <textarea
              class="scrollable-content"
              :value="data.summary"
              readonly
            ></textarea>
          </div>

          <div v-if="data.outcome" class="form-group scrollable-group">
            <label>원하는 결과</label>
            <textarea
              class="scrollable-content"
              :value="data.outcome"
              readonly
            ></textarea>
          </div>

          <div v-if="data.disadvantage" class="form-group scrollable-group">
            <label>사건에서 불리한 점</label>
            <textarea
              class="scrollable-content"
              :value="data.disadvantage"
              readonly
            ></textarea>
          </div>

          <div v-if="data.recommendedQuestions && Object.keys(data.recommendedQuestions).length > 0" class="form-group scrollable-group">
            <label>변호사에게 궁금한 점</label>
            <textarea
              class="scrollable-content"
              :value="Object.values(data.recommendedQuestions).join('\n')"
              readonly
            ></textarea>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { XMarkIcon } from '@heroicons/vue/24/solid'
defineProps({
  data: Object
})
defineEmits(['close'])
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
  font-family: 'Noto Sans KR', sans-serif;
  color: #333333;
}

.modal-content {
  position: relative;
  background: #f4f7fb;
  border-radius: 12px;
  padding: 3rem 0 3rem 0;
  width: 800px;
  max-height: 90vh;
}

.modal-scroll-area {
  overflow-y: auto;
  max-height: 80vh;
  padding: 0 1rem 2rem 2rem;
}
.modal-scroll-area::-webkit-scrollbar,
.scrollable-content::-webkit-scrollbar {
  width: 6px;
}

.modal-scroll-area::-webkit-scrollbar-thumb,
.scrollable-content::-webkit-scrollbar-thumb {
  background-color: #d4e1ed; /* 💡 연한 하늘색 느낌 */
  border-radius: 3px;
}

.modal-scroll-area::-webkit-scrollbar-track,
.scrollable-content::-webkit-scrollbar-track {
  background-color: transparent;
}

.consult-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding-right: 10px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

input,
textarea {
  padding: 0.75rem;
  border: 1px solid #cfcfcf;
  border-radius: 8px;
  font-size: 1rem;
  resize: none;
}

.readonly-input {
  background-color: #fff;
  color: #888;
}
.readonly-input-title{
  border: none;
  padding: 0;
  font-size: 1.5rem;
  font-weight: bold;
  background-color: transparent;
}
.scrollable-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;

}

.scrollable-content {
  min-height: 100px;
  max-height: 150px;
  overflow-y: auto;
  background-color: #fff;
  border: 1px solid #cfcfcf;
  color: #888;
  border-radius: 8px;
  padding: 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: #B9D0DF;
  box-shadow: none;
}
.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  cursor: pointer;
  z-index: 10;
}

.x-icon {
  width: 24px;
  height: 24px;
  color: #B9D0DF;
  transition: transform 0.2s ease;
}

.close-btn:hover .x-icon {
  transform: scale(1.2);
  color: #888;
}

</style>
