<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { register, login, type LoginResponse } from "@/api/auth";
import { useAuthStore } from "@/stores/auth";

const form = ref({ email: "", password: "", invite_code: "" });
const loading = ref(false);
const error = ref("");
const router = useRouter();
const auth = useAuthStore();

const submit = async () => {
  loading.value = true;
  error.value = "";
  try {
    await register({
      email: form.value.email,
      password: form.value.password,
      invite_code: form.value.invite_code,
    });
    const res: LoginResponse = await login({
      username: form.value.email,
      password: form.value.password,
    });
    auth.setSession(res);
    router.push({ name: "Home" });
  } catch (err) {
    error.value = (err as Error).message;
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="page">
    <div class="card">
      <p class="label">注册</p>
      <h2>创建你的情侣空间账号</h2>
      <div class="stack">
        <input v-model="form.email" type="email" placeholder="邮箱" />
        <input v-model="form.password" type="password" placeholder="密码" />
        <input v-model="form.invite_code" type="text" placeholder="邀请码（管理员每日更新）" />
        <button class="btn primary" :disabled="loading" @click="submit">
          {{ loading ? "注册中..." : "注册并登录" }}
        </button>
        <p class="muted">
          已有账号？
          <RouterLink to="/login">去登录</RouterLink>
        </p>
        <p v-if="error" class="error">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: calc(100vh - 120px);
  display: grid;
  place-items: center;
  padding: 32px 16px;
}
.card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 20px;
  color: #e2e8f0;
  width: min(420px, 100%);
  box-shadow: 0 10px 50px rgba(0, 0, 0, 0.25);
}
.label {
  color: #94a3b8;
  font-size: 13px;
}
.stack {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 12px;
}
input {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 10px 12px;
  color: #e5e7eb;
}
.btn {
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  padding: 10px 16px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.04);
  color: #e2e8f0;
  transition: 0.2s ease;
  font-weight: 600;
}
.btn.primary {
  background: linear-gradient(135deg, #6366f1, #a855f7);
  border-color: transparent;
}
.btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 10px 30px rgba(99, 102, 241, 0.25);
}
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.muted {
  color: #94a3b8;
  font-size: 13px;
}
.error {
  color: #fca5a5;
  font-size: 13px;
}
</style>
