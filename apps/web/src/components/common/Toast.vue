<script setup lang="ts">
import { ref, watch } from "vue";

export interface ToastProps {
  message: string;
  type?: "success" | "error" | "info" | "warning";
  duration?: number;
}

const props = withDefaults(defineProps<ToastProps>(), {
  type: "info",
  duration: 3000,
});

const emit = defineEmits<{
  close: [];
}>();

const visible = ref(true);

const icons = {
  success: "✅",
  error: "❌",
  info: "ℹ️",
  warning: "⚠️",
};

watch(
  () => props.message,
  () => {
    visible.value = true;
    if (props.duration > 0) {
      setTimeout(() => {
        visible.value = false;
        emit("close");
      }, props.duration);
    }
  },
  { immediate: true }
);
</script>

<template>
  <Transition name="toast">
    <div v-if="visible" :class="['toast', type]">
      <span class="toast-icon">{{ icons[type] }}</span>
      <span class="toast-message">{{ message }}</span>
      <button class="toast-close" @click="visible = false; emit('close')">×</button>
    </div>
  </Transition>
</template>

<style scoped>
.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  backdrop-filter: blur(8px);
}

.toast.success {
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.toast.error {
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
  color: #991b1b;
  border: 1px solid #fecaca;
}

.toast.info {
  background: linear-gradient(135deg, #eff6ff, #dbeafe);
  color: #1e40af;
  border: 1px solid #bfdbfe;
}

.toast.warning {
  background: linear-gradient(135deg, #fffbeb, #fef3c7);
  color: #92400e;
  border: 1px solid #fde68a;
}

.toast-icon {
  font-size: 16px;
}

.toast-message {
  flex: 1;
}

.toast-close {
  width: 20px;
  height: 20px;
  border: none;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.toast-close:hover {
  opacity: 1;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
