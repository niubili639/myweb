import { ref } from "vue";

export interface ToastItem {
  id: number;
  message: string;
  type: "success" | "error" | "info" | "warning";
}

const toasts = ref<ToastItem[]>([]);
let idCounter = 0;

export function useToast() {
  const show = (
    message: string,
    type: "success" | "error" | "info" | "warning" = "info",
    duration = 3000
  ) => {
    const id = ++idCounter;
    toasts.value.push({ id, message, type });

    if (duration > 0) {
      setTimeout(() => {
        remove(id);
      }, duration);
    }

    return id;
  };

  const remove = (id: number) => {
    toasts.value = toasts.value.filter((t) => t.id !== id);
  };

  return {
    toasts,
    show,
    remove,
    success: (msg: string, duration?: number) => show(msg, "success", duration),
    error: (msg: string, duration?: number) => show(msg, "error", duration),
    info: (msg: string, duration?: number) => show(msg, "info", duration),
    warning: (msg: string, duration?: number) => show(msg, "warning", duration),
  };
}

// 单例，全局共享
export const globalToast = useToast();
