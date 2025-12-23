<script setup lang="ts">
import { RouterLink, RouterView, useRouter } from "vue-router";
import { computed } from "vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();
const isAuthed = computed(() => !!auth.token);

const logout = () => {
  auth.clear();
  router.push({ name: "Login" });
};
</script>

<template>
  <div class="shell">
    <header class="topbar">
      <div class="brand" @click="router.push('/')">
        <div class="dot"></div>
        <span>陌上花开</span>
      </div>
      <nav v-if="isAuthed">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/ai">智能体</RouterLink>
        <RouterLink to="/couple">情侣空间</RouterLink>
        <RouterLink to="/album">相册</RouterLink>
        <RouterLink to="/notes">记录</RouterLink>
        <RouterLink v-if="auth.user?.is_admin" to="/settings">设置</RouterLink>
      </nav>
      <div class="auth-actions">
        <span v-if="auth.user" class="user">{{ auth.user.email }}</span>
        <RouterLink v-if="!isAuthed" class="btn small" to="/login">登录</RouterLink>
        <button v-else class="btn small ghost" @click="logout">退出</button>
      </div>
    </header>
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.shell {
  position: relative;
  min-height: 100vh;
  background: radial-gradient(circle at 20% 20%, rgba(255, 192, 203, 0.12), transparent 35%),
    radial-gradient(circle at 80% 0%, rgba(204, 229, 255, 0.12), transparent 35%),
    var(--bg-gradient-bottom);
  color: var(--text-main);
  font-family: "Microsoft YaHei", "PingFang SC", "Inter", system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
}
.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(16px);
  background: rgba(255, 255, 255, 0.75);
  border-bottom: 1px solid var(--card-border);
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  letter-spacing: 0.2px;
  cursor: pointer;
}
.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff9acb, #ffd6e8);
  box-shadow: 0 0 12px rgba(235, 64, 120, 0.4);
}
.topbar nav {
  display: flex;
  gap: 18px;
  font-size: 14px;
}
.topbar a {
  color: #4a0c26;
  font-weight: 700;
  letter-spacing: 0.2px;
  text-decoration: none;
}
.topbar a.router-link-exact-active {
  color: #c21b68;
}
.auth-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}
.user {
  color: #7a103d;
}
.main {
  position: relative;
  z-index: 1;
}
.footer {
  position: relative;
  z-index: 1;
  padding: 16px 24px 32px;
  color: #94a3b8;
  display: flex;
  gap: 16px;
  justify-content: center;
  font-size: 13px;
}
.btn {
  border: 1px solid var(--card-border);
  border-radius: 999px;
  padding: 8px 12px;
  cursor: pointer;
  background: var(--accent);
  color: var(--btn-text);
  transition: 0.2s ease;
  font-weight: 600;
}
.btn.ghost {
  background: #ffffff;
}
.btn.small {
  font-size: 13px;
  padding: 6px 12px;
}
.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 30px rgba(235, 64, 120, 0.15);
}
@media (max-width: 900px) {
  .topbar nav {
    display: none;
  }
}
</style>
