<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-box">
      <p>{{ message }}</p>
      <div>
        <button @click="onConfirm">{{ confirmText }}</button>
        <button v-if="showCancel" @click="onCancel">{{ cancelText }}</button>
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
