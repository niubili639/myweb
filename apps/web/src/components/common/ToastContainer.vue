<script setup lang="ts">
import { ref } from "vue";
import Toast from "./Toast.vue";

export interface ToastItem {
  id: number;
  message: string;
  type: "success" | "error" | "info" | "warning";
  duration: number;
}

const toasts = ref<ToastItem[]>([]);
let idCounter = 0;

const show = (
  message: string,
  type: "success" | "error" | "info" | "warning" = "info",
  duration = 3000
) => {
  const id = ++idCounter;
  toasts.value.push({ id, message, type, duration });
};

const remove = (id: number) => {
  toasts.value = toasts.value.filter((t) => t.id !== id);
};

// 暴露方法给父组件
defineExpose({
  show,
  success: (msg: string, duration?: number) => show(msg, "success", duration),
  error: (msg: string, duration?: number) => show(msg, "error", duration),
  info: (msg: string, duration?: number) => show(msg, "info", duration),
  warning: (msg: string, duration?: number) => show(msg, "warning", duration),
});
</script>

<template>
  <Teleport to="body">
    <div class="toast-container">
      <Toast
        v-for="toast in toasts"
        :key="toast.id"
        :message="toast.message"
        :type="toast.type"
        :duration="toast.duration"
        @close="remove(toast.id)"
      />
    </div>
  </Teleport>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}

.toast-container > * {
  pointer-events: auto;
}
</style>
