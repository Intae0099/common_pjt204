<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-box">
      <p class="modal-message">{{ message }}</p>
      <div class="modal-buttons">
        <button class="confirm-btn" @click="onConfirm">{{ confirmText }}</button>
        <button v-if="showCancel" class="cancel-btn" @click="onCancel">{{ cancelText }}</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BaseModal',
  props: {
    visible: Boolean,
    message: {
      type: String,
      required: true
    },
    confirmText: {
      type: String,
      default: '확인'
    },
    cancelText: {
      type: String,
      default: '취소'
    },
    showCancel: {
      type: Boolean,
      default: false
    }
  },
  emits: ['confirm', 'cancel'],
  methods: {
    onConfirm() {
      this.$emit('confirm');
    },
    onCancel() {
      this.$emit('cancel');
    }
  }
};
</script>
<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(10, 25, 47, 0.3); /* 어두운 반투명 배경 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.modal-box {
  background-color: white;
  padding: 24px 30px;
  border-radius: 12px;
  border: 1px solid #d3e1ec;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  min-width: 280px;
  max-width: 90%;
  text-align: center;
}

.modal-message {
  padding: 10px 0px;
  font-size: 15px;
  color: #1e2c3a;
  margin-bottom: 20px;
  white-space: pre-line;
}

.modal-buttons {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.confirm-btn {
  padding: 0px 20px;
  background-color: white;
  color: #0c2c46;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  font-size: 14px;
  cursor: pointer;
}

.cancel-btn {
  padding: 8px 20px;
  background-color: #e4e4e4;
  color: #333;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  font-size: 14px;
  cursor: pointer;
}
</style>
