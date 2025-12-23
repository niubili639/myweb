<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import dayjs from "dayjs";
import { fetchHealth, type HealthResponse } from "@/api/health";
import { useAppStore } from "@/stores/app";
import { useAuthStore } from "@/stores/auth";

const appStore = useAppStore();
const authStore = useAuthStore();

const health = ref<HealthResponse | null>(null);
const loadingHealth = ref(false);
const error = ref("");

const formattedTime = computed(() => {
  const raw = health.value?.data?.time;
  if (!raw) return "-";
  // JS Date 只支持毫秒；后端可能返回微秒，先截断到 3 位小数再解析
  const normalized = raw.replace(/(\.\d{3})\d+/, "$1");
  const parsed = dayjs(normalized);
  if (!parsed.isValid()) return health.value.data.time;
  // dayjs 默认会按本地时区展示 Date 对象（ISO 字符串带时区偏移也会正确转换）
  return parsed.format("YYYY-MM-DD HH:mm:ss");
});

const loadHealth = async () => {
  loadingHealth.value = true;
  error.value = "";
  try {
    health.value = await fetchHealth();
  } catch (err) {
    error.value = (err as Error).message;
  } finally {
    loadingHealth.value = false;
  }
};

onMounted(loadHealth);
</script>

<template>
  <div class="page">
    <section class="hero">
      <div class="hero-text">
        <p class="pill">欢迎回来</p>
        <h1>情侣空间 · AI 助理</h1>
        <p class="sub">在右上角切换“智能体 / 情侣空间 / 相册 / 记录”模块。</p>
        <div class="badges">
          <span>已登录：{{ authStore.user?.email }}</span>
          <span>API Base: {{ appStore.apiBaseUrl }}</span>
        </div>
      </div>
      <div class="hero-card">
        <p class="label">后端健康</p>
        <div class="metric">
          <span class="dot green"></span>
          <span>{{ health?.status ?? "loading" }}</span>
        </div>
        <div class="mini-grid">
          <div>
            <p>服务</p>
            <strong>{{ health?.data.service || "..." }}</strong>
          </div>
          <div>
            <p>版本</p>
            <strong>{{ health?.data.version || "-" }}</strong>
          </div>
          <div>
            <p>时间</p>
            <strong>{{ formattedTime }}</strong>
          </div>
          <div>
            <p>API</p>
            <strong>{{ appStore.apiBaseUrl }}</strong>
          </div>
        </div>
        <button class="btn ghost full" @click="loadHealth" :disabled="loadingHealth">
          {{ loadingHealth ? "刷新中..." : "刷新健康检查" }}
        </button>
      </div>
    </section>

    <p v-if="error" class="error">请求失败：{{ error }}</p>
  </div>
</template>

<style scoped>
.page {
  position: relative;
  z-index: 1;
  padding: 48px 16px 80px;
  max-width: 1100px;
  margin: 0 auto;
  color: var(--text-main);
}
.hero {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  align-items: center;
  margin-bottom: 28px;
}
.hero-text h1 {
  margin: 8px 0 4px;
  font-size: 32px;
  color: var(--text-main);
  font-weight: 800;
}
.sub {
  color: var(--text-muted);
  margin-bottom: 14px;
  max-width: 520px;
  font-weight: 600;
}
.pill {
  display: inline-flex;
  background: #ffe9f1;
  color: #4a0c26;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  letter-spacing: 0.1px;
  font-weight: 700;
}
.badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  color: var(--text-muted);
  font-size: 12px;
}
.badges span {
  padding: 6px 10px;
  border: 1px solid var(--card-border);
  border-radius: 8px;
  background: #fff;
}
.hero-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 18px;
  padding: 18px;
  box-shadow: var(--card-shadow);
}
.label {
  color: var(--text-main);
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 4px;
}
.metric {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0 12px;
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.dot.green {
  background: #34d399;
  box-shadow: 0 0 12px rgba(52, 211, 153, 0.9);
}
.mini-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}
.mini-grid strong {
  color: var(--text-main);
  font-weight: 800;
}
.btn {
  border: 1px solid var(--card-border);
  border-radius: 999px;
  padding: 10px 16px;
  cursor: pointer;
  background: var(--accent);
  color: var(--btn-text);
  transition: 0.2s ease;
  font-weight: 700;
}
.btn.ghost {
  background: #fff;
}
.btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 10px 30px rgba(235, 64, 120, 0.18);
}
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.btn.full {
  width: 100%;
  justify-content: center;
}
.error {
  margin-top: 16px;
  color: #fca5a5;
  text-align: center;
}
</style>
