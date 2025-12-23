<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useAuthStore } from "@/stores/auth";
import { getApiKey, setApiKey, type ApiKey } from "@/api/auth";
import http from "@/api/http";

interface UserRow {
  id: number;
  email: string;
  role?: string;
  allowed_spaces?: string;
  is_admin: boolean;
}

const auth = useAuthStore();
const apiKeyInput = ref("");
const users = ref<UserRow[]>([]);
const error = ref("");
const saving = ref(false);

const loadApiKey = async () => {
  try {
    const key = await getApiKey("qwen");
    apiKeyInput.value = key.key;
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
  await loadApiKey();
  await loadUsers();
});
</script>

<template>
  <div class="page">
    <div class="header">
      <div>
        <p class="muted">设置</p>
        <h2>统一管理 API Key 与用户</h2>
        <p class="muted">仅管理员可见。可配置千问 API Key、管理用户角色与权限。</p>
      </div>
    </div>

    <section class="card">
      <h3>千问 API Key</h3>
      <div class="stack">
        <input v-model="apiKeyInput" type="password" placeholder="sk-..." />
        <button class="btn primary" :disabled="saving" @click="saveApiKey">
          {{ saving ? "保存中..." : "保存" }}
        </button>
      </div>
    </section>

    <section class="card">
      <h3>用户管理</h3>
      <div class="users" v-if="users.length">
        <div class="user-row header">
          <span>ID</span><span>邮箱</span><span>角色</span><span>可访问空间</span><span>操作</span>
        </div>
        <div class="user-row" v-for="u in users" :key="u.id">
          <span>{{ u.id }}</span>
          <span>{{ u.email }}</span>
          <input v-model="u.role" class="input" />
          <input v-model="u.allowed_spaces" class="input" />
          <button class="btn ghost" :disabled="saving" @click="updateUser(u)">更新</button>
        </div>
      </div>
      <p v-else class="muted">暂无用户数据。</p>
    </section>

    <p v-if="error" class="error">请求失败：{{ error }}</p>
  </div>
</template>

<style scoped>
.page {
  padding: 32px 16px 60px;
  max-width: 1100px;
  margin: 0 auto;
  color: var(--text-main);
}
.header {
  margin-bottom: 12px;
}
.card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 16px;
  color: var(--text-main);
  box-shadow: var(--card-shadow);
  margin-top: 16px;
}
.stack {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 8px;
}
input,
.input {
  background: #fff0f6;
  border: 1px solid #ffcfe3;
  border-radius: 10px;
  padding: 8px 10px;
  color: var(--text-main);
}
.btn {
  border: 1px solid var(--card-border);
  border-radius: 999px;
  padding: 8px 14px;
  cursor: pointer;
  background: var(--accent);
  color: var(--btn-text);
  transition: 0.2s ease;
  font-weight: 700;
}
.btn.primary {
  border-color: transparent;
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
.users {
  margin-top: 12px;
}
.user-row {
  display: grid;
  grid-template-columns: 60px 1fr 120px 1fr 100px;
  gap: 8px;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--card-border);
}
.user-row.header {
  font-weight: 600;
  color: var(--text-main);
  border-bottom: 1px solid var(--card-border);
}
.error {
  margin-top: 16px;
  color: #ef4444;
}
</style>
