<template>
  <transition name="fade">
    <div v-if="visible" class="modal-overlay">
      <div class="modal-box">
        <p class="message">{{ message }}</p>
        <div class="actions">
          <button v-if="showCancel" class="cancel-btn" @click="onCancel">취소</button>
          <button class="ok-btn" @click="onConfirm">확인</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref } from "vue"

defineProps({
  message: String,
  showCancel: { type: Boolean, default: true }
})

const emits = defineEmits(["confirm", "cancel"])
const visible = ref(true)

const onConfirm = () => {
  emits("confirm")
  visible.value = false
}
const onCancel = () => {
  emits("cancel")
  visible.value = false
}
</script>


<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.modal-box {
  background: #fff;
  padding: 24px;
  border-radius: 12px;
  min-width: 280px;
  text-align: center;
}
.message {
  font-size: 15px;
  margin-bottom: 20px;
}
.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}
.ok-btn {
  background: #1d2b50;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.cancel-btn {
  background: #f1f1f1;
  color: #333;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
