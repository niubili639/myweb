<script setup lang="ts">
import { ref } from "vue";

export interface ConfirmOptions {
  title?: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: "danger" | "warning" | "info";
}

const visible = ref(false);
const options = ref<ConfirmOptions>({
  title: "确认",
  message: "",
  confirmText: "确定",
  cancelText: "取消",
  type: "info",
});

let resolvePromise: ((value: boolean) => void) | null = null;

const show = (opts: ConfirmOptions): Promise<boolean> => {
  options.value = {
    title: opts.title || "确认",
    message: opts.message,
    confirmText: opts.confirmText || "确定",
    cancelText: opts.cancelText || "取消",
    type: opts.type || "info",
  };
  visible.value = true;

  return new Promise((resolve) => {
    resolvePromise = resolve;
  });
};

const handleConfirm = () => {
  visible.value = false;
  resolvePromise?.(true);
};

const handleCancel = () => {
  visible.value = false;
  resolvePromise?.(false);
};

defineExpose({ show });
</script>

<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div v-if="visible" class="dialog-overlay" @click.self="handleCancel">
        <div class="dialog">
          <div class="dialog-header">
            <span class="dialog-icon" :class="options.type">
              {{ options.type === 'danger' ? '🗑️' : options.type === 'warning' ? '⚠️' : 'ℹ️' }}
            </span>
            <h3>{{ options.title }}</h3>
          </div>
          <p class="dialog-message">{{ options.message }}</p>
          <div class="dialog-actions">
            <button class="btn ghost" @click="handleCancel">{{ options.cancelText }}</button>
            <button :class="['btn', options.type === 'danger' ? 'danger' : 'primary']" @click="handleConfirm">
              {{ options.confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
}

.dialog {
  background: white;
  border-radius: 20px;
  padding: 28px;
  width: 100%;
  max-width: 380px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.dialog-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.dialog-icon {
  font-size: 24px;
}

.dialog-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
}

.dialog-message {
  margin: 0 0 24px;
  color: var(--text-muted);
  font-size: 15px;
  line-height: 1.5;
}

.dialog-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn {
  padding: 10px 20px;
  border: 1px solid var(--card-border);
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s;
}

.btn.ghost {
  background: white;
  color: var(--text-main);
}

.btn.primary {
  background: var(--accent);
  color: var(--btn-text);
  border-color: transparent;
}

.btn.danger {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  border-color: transparent;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.dialog-enter-active,
.dialog-leave-active {
  transition: all 0.25s ease;
}

.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
}

.dialog-enter-from .dialog,
.dialog-leave-to .dialog {
  transform: scale(0.9);
}
</style>
