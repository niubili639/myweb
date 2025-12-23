<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import dayjs from "dayjs";
import { useAuthStore } from "@/stores/auth";
import { useAppStore } from "@/stores/app";
import { getApiKey, setApiKey } from "@/api/auth";
import { fetchHealth, type HealthResponse } from "@/api/health";
import { globalToast } from "@/composables/useToast";
import http from "@/api/http";

interface UserRow {
  id: number;
  email: string;
  role?: string;
  allowed_spaces?: string;
  is_admin: boolean;
}

const auth = useAuthStore();
const appStore = useAppStore();
const apiKeyInput = ref("");
const users = ref<UserRow[]>([]);
const error = ref("");
const saving = ref(false);

// 健康检查
const health = ref<HealthResponse | null>(null);
const loadingHealth = ref(false);

const formattedTime = computed(() => {
  const raw = health.value?.data?.time;
  if (!raw) return "-";
  const normalized = raw.replace(/(\.\d{3})\d+/, "$1");
  const parsed = dayjs(normalized);
  if (!parsed.isValid()) return health.value?.data.time || "-";
  return parsed.format("YYYY-MM-DD HH:mm:ss");
});

const loadHealth = async () => {
  loadingHealth.value = true;
  try {
    health.value = await fetchHealth();
  } catch (err) {
    error.value = (err as Error).message;
  } finally {
    loadingHealth.value = false;
  }
};

const amapKeyInput = ref("");
const amapSafeKeyInput = ref("");

const loadApiKey = async () => {
  try {
    const key = await getApiKey("qwen");
    apiKeyInput.value = key.key;
  } catch {
    /* ignore missing */
  }
  try {
    const key = await getApiKey("amap_web_key");
    amapKeyInput.value = key.key;
  } catch {
    /* ignore missing */
  }
  try {
    const key = await getApiKey("amap_web_safe_key");
    amapSafeKeyInput.value = key.key;
  } catch {
    /* ignore missing */
  }
};

const saveApiKey = async () => {
  saving.value = true;
  error.value = "";
  try {
    await setApiKey({ key: apiKeyInput.value, provider: "qwen" });
  } catch (err) {
    error.value = (err as Error).message;
  } finally {
    saving.value = false;
  }
};

const saveAmapKey = async () => {
  saving.value = true;
  error.value = "";
  try {
    await setApiKey({ key: amapKeyInput.value, provider: "amap_web_key" });
    await setApiKey({ key: amapSafeKeyInput.value, provider: "amap_web_safe_key" });
    globalToast.success("保存成功");
  } catch (err) {
    error.value = (err as Error).message;
  } finally {
    saving.value = false;
  }
};

const loadUsers = async () => {
  try {
    const { data } = await http.get<UserRow[]>("/api/v1/auth/users");
    users.value = data;
  } catch (err) {
    error.value = (err as Error).message;
  }
};

const updateUser = async (user: UserRow) => {
  saving.value = true;
  error.value = "";
  try {
    await http.patch(`/api/v1/auth/users/${user.id}`, {
      role: user.role,
      allowed_spaces: user.allowed_spaces,
    });
    await loadUsers();
  } catch (err) {
    error.value = (err as Error).message;
  } finally {
    saving.value = false;
  }
};

onMounted(async () => {
  await Promise.all([loadApiKey(), loadUsers(), loadHealth()]);
});
</script>

<template>
  <div class="page">
    <div class="header">
      <div>
        <p class="muted">管理后台</p>
        <h2>系统设置</h2>
        <p class="muted">仅管理员可见。配置 API Key、查看系统状态、管理用户。</p>
      </div>
    </div>

    <!-- 系统状态 -->
    <section class="card">
      <div class="card-header">
        <h3>🖥️ 系统状态</h3>
        <button class="btn ghost small" @click="loadHealth" :disabled="loadingHealth">
          {{ loadingHealth ? "刷新中..." : "刷新" }}
        </button>
      </div>
      <div class="status-grid">
        <div class="status-item">
          <span class="status-label">状态</span>
          <span class="status-value">
            <span class="dot" :class="health?.status === 'ok' ? 'green' : 'yellow'"></span>
            {{ health?.status ?? "loading" }}
          </span>
        </div>
        <div class="status-item">
          <span class="status-label">服务</span>
          <span class="status-value">{{ health?.data?.service || "..." }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">版本</span>
          <span class="status-value">{{ health?.data?.version || "-" }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">服务器时间</span>
          <span class="status-value">{{ formattedTime }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">API 地址</span>
          <span class="status-value">{{ appStore.apiBaseUrl }}</span>
        </div>
        <div class="status-item">
          <span class="status-label">当前用户</span>
          <span class="status-value">{{ auth.user?.email || "-" }}</span>
        </div>
      </div>
    </section>

    <!-- API Key 配置 -->
    <section class="card">
      <h3>🔑 千问 API Key</h3>
      <p class="hint">配置后用户可使用 AI 对话和图片生成功能</p>
      <div class="input-row">
        <input v-model="apiKeyInput" type="password" placeholder="sk-..." />
        <button class="btn primary" :disabled="saving" @click="saveApiKey">
          {{ saving ? "保存中..." : "保存" }}
        </button>
      </div>
    </section>

    <!-- 高德地图 Key -->
    <section class="card">
      <h3>🗺️ 高德地图 API（Web端）</h3>
      <p class="hint">配置后可在情侣空间显示双方位置和距离</p>
      <div class="input-group">
        <label class="input-label">Web Key</label>
        <input v-model="amapKeyInput" type="password" placeholder="高德 Web JS API Key" />
      </div>
      <div class="input-group">
        <label class="input-label">安全密钥 (jscode)</label>
        <input v-model="amapSafeKeyInput" type="password" placeholder="高德安全密钥" />
      </div>
      <button class="btn primary" :disabled="saving" @click="saveAmapKey">
        {{ saving ? "保存中..." : "保存" }}
      </button>
    </section>

    <!-- 用户管理 -->
    <section class="card">
      <h3>👥 用户管理</h3>
      <div class="users" v-if="users.length">
        <div class="user-row header">
          <span>ID</span>
          <span>邮箱</span>
          <span>角色</span>
          <span>可访问空间</span>
          <span>操作</span>
        </div>
        <div class="user-row" v-for="u in users" :key="u.id">
          <span class="user-id">{{ u.id }}</span>
          <span class="user-email">{{ u.email }}</span>
          <input v-model="u.role" class="input" placeholder="角色" />
          <input v-model="u.allowed_spaces" class="input" placeholder="空间" />
          <button class="btn ghost small" :disabled="saving" @click="updateUser(u)">更新</button>
        </div>
      </div>
      <p v-else class="muted">暂无用户数据。</p>
    </section>

    <p v-if="error" class="error">请求失败：{{ error }}</p>
  </div>
</template>

<style scoped>
.page {
  padding: 32px 20px 60px;
  max-width: 1000px;
  margin: 0 auto;
  color: var(--text-main);
}

.header {
  margin-bottom: 24px;
}

.header h2 {
  margin: 4px 0 8px;
  font-size: 28px;
  font-weight: 800;
}

.card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 20px;
  color: var(--text-main);
  box-shadow: var(--card-shadow);
  margin-bottom: 20px;
}

.card h3 {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 700;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
}

.hint {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0 0 12px;
}

/* 状态网格 */
.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.status-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.status-label {
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 8px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.green {
  background: #34d399;
  box-shadow: 0 0 8px rgba(52, 211, 153, 0.6);
}

.dot.yellow {
  background: #fbbf24;
  box-shadow: 0 0 8px rgba(251, 191, 36, 0.6);
}

/* 输入行 */
.input-row {
  display: flex;
  gap: 12px;
}

.input-group {
  margin-bottom: 12px;
}

.input-label {
  display: block;
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 6px;
}

input,
.input {
  flex: 1;
  width: 100%;
  background: #fff0f6;
  border: 1px solid #ffcfe3;
  border-radius: 10px;
  padding: 10px 14px;
  color: var(--text-main);
  font-size: 14px;
  box-sizing: border-box;
}

input:focus,
.input:focus {
  outline: none;
  border-color: #ff9acb;
}

/* 按钮 */
.btn {
  border: 1px solid var(--card-border);
  border-radius: 10px;
  padding: 10px 18px;
  cursor: pointer;
  background: var(--accent);
  color: var(--btn-text);
  transition: all 0.2s ease;
  font-weight: 600;
  font-size: 14px;
  white-space: nowrap;
}

.btn.primary {
  border-color: transparent;
}

.btn.ghost {
  background: #fff;
}

.btn.small {
  padding: 8px 14px;
  font-size: 13px;
}

.btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(235, 64, 120, 0.15);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 用户列表 */
.users {
  margin-top: 12px;
  overflow-x: auto;
}

.user-row {
  display: grid;
  grid-template-columns: 50px 1fr 120px 1fr 80px;
  gap: 12px;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--card-border);
  min-width: 600px;
}

.user-row.header {
  font-weight: 600;
  font-size: 13px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.user-row:last-child {
  border-bottom: none;
}

.user-id {
  font-weight: 600;
  color: var(--text-muted);
}

.user-email {
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.muted {
  color: var(--text-muted);
  font-size: 14px;
}

.error {
  margin-top: 16px;
  padding: 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  color: #dc2626;
  font-size: 14px;
}

/* 响应式 */
@media (max-width: 600px) {
  .input-row {
    flex-direction: column;
  }

  .status-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
