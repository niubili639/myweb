<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

// 实时时钟
const now = ref(new Date());
let timer: number | null = null;

const timeStr = computed(() => {
  const h = now.value.getHours().toString().padStart(2, "0");
  const m = now.value.getMinutes().toString().padStart(2, "0");
  const s = now.value.getSeconds().toString().padStart(2, "0");
  return `${h}:${m}:${s}`;
});

const dateStr = computed(() => {
  const year = now.value.getFullYear();
  const month = (now.value.getMonth() + 1).toString().padStart(2, "0");
  const day = now.value.getDate().toString().padStart(2, "0");
  const weekdays = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];
  const weekday = weekdays[now.value.getDay()];
  return `${year}年${month}月${day}日 ${weekday}`;
});

// 问候语
const greeting = computed(() => {
  const hour = now.value.getHours();
  if (hour < 6) return "夜深了 🌙";
  if (hour < 9) return "早上好 ☀️";
  if (hour < 12) return "上午好 🌤️";
  if (hour < 14) return "中午好 🌞";
  if (hour < 18) return "下午好 ☕";
  if (hour < 22) return "晚上好 🌆";
  return "夜深了 🌙";
});

// 快捷入口
const quickLinks = [
  { icon: "💬", title: "AI 对话", desc: "和智能助手聊天", route: "/ai" },
  { icon: "💕", title: "情侣空间", desc: "记录甜蜜时光", route: "/couple" },
  { icon: "📸", title: "相册", desc: "珍藏美好回忆", route: "/album" },
  { icon: "📝", title: "记录", desc: "写下心情日记", route: "/notes" },
];

// 每日一言（可以后续接入 API）
const dailyQuotes = [
  "生活不止眼前的苟且，还有诗和远方。",
  "愿你眼里有光，心中有爱。",
  "每一天都是新的开始。",
  "保持热爱，奔赴山海。",
  "慢慢来，比较快。",
  "今天也要元气满满！",
  "你笑起来真好看。",
  "陪伴是最长情的告白。",
];
const dailyQuote = ref("");

onMounted(() => {
  timer = window.setInterval(() => {
    now.value = new Date();
  }, 1000);
  // 随机选一句
  dailyQuote.value = dailyQuotes[Math.floor(Math.random() * dailyQuotes.length)];
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>

<template>
  <div class="home">
    <!-- 顶部欢迎区 -->
    <section class="welcome">
      <div class="greeting-area">
        <p class="greeting">{{ greeting }}</p>
        <h1 class="username">{{ authStore.user?.email?.split("@")[0] || "朋友" }}</h1>
        <p class="quote">「{{ dailyQuote }}」</p>
      </div>
      <div class="clock-area">
        <div class="clock">
          <span class="time">{{ timeStr }}</span>
          <span class="date">{{ dateStr }}</span>
        </div>
      </div>
    </section>

    <!-- 快捷入口 -->
    <section class="quick-section">
      <h2 class="section-title">快捷入口</h2>
      <div class="quick-grid">
        <div
          v-for="link in quickLinks"
          :key="link.route"
          class="quick-card"
          @click="router.push(link.route)"
        >
          <span class="quick-icon">{{ link.icon }}</span>
          <div class="quick-info">
            <span class="quick-title">{{ link.title }}</span>
            <span class="quick-desc">{{ link.desc }}</span>
          </div>
          <span class="arrow">→</span>
        </div>
      </div>
    </section>

    <!-- 统计卡片 -->
    <section class="stats-section">
      <h2 class="section-title">今日概览</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-icon">💬</span>
          <div class="stat-info">
            <span class="stat-value">--</span>
            <span class="stat-label">AI 对话</span>
          </div>
        </div>
        <div class="stat-card">
          <span class="stat-icon">📝</span>
          <div class="stat-info">
            <span class="stat-value">--</span>
            <span class="stat-label">日记记录</span>
          </div>
        </div>
        <div class="stat-card">
          <span class="stat-icon">📸</span>
          <div class="stat-info">
            <span class="stat-value">--</span>
            <span class="stat-label">照片上传</span>
          </div>
        </div>
        <div class="stat-card">
          <span class="stat-icon">❤️</span>
          <div class="stat-info">
            <span class="stat-value">--</span>
            <span class="stat-label">在一起</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home {
  padding: 32px 20px 60px;
  max-width: 1000px;
  margin: 0 auto;
}

/* 欢迎区 */
.welcome {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.greeting-area {
  flex: 1;
  min-width: 280px;
}

.greeting {
  font-size: 16px;
  color: var(--text-muted);
  margin: 0 0 4px;
}

.username {
  font-size: 36px;
  font-weight: 800;
  color: var(--text-main);
  margin: 0 0 12px;
}

.quote {
  font-size: 14px;
  color: var(--text-muted);
  font-style: italic;
  margin: 0;
}

.clock-area {
  flex-shrink: 0;
}

.clock {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 20px;
  padding: 20px 32px;
  text-align: center;
  box-shadow: var(--card-shadow);
}

.time {
  display: block;
  font-size: 48px;
  font-weight: 700;
  color: var(--text-main);
  font-variant-numeric: tabular-nums;
  letter-spacing: 2px;
  background: linear-gradient(135deg, #ff9acb, #c21b68);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.date {
  display: block;
  font-size: 14px;
  color: var(--text-muted);
  margin-top: 4px;
}

/* 快捷入口 */
.section-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 16px;
}

.quick-section {
  margin-bottom: 40px;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.quick-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 18px;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: var(--card-shadow);
}

.quick-card:hover {
  transform: translateY(-4px);
  border-color: #ff9acb;
  box-shadow: 0 12px 32px rgba(235, 64, 120, 0.15);
}

.quick-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.quick-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.quick-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
}

.quick-desc {
  font-size: 13px;
  color: var(--text-muted);
}

.arrow {
  font-size: 18px;
  color: var(--text-muted);
  transition: transform 0.2s;
}

.quick-card:hover .arrow {
  transform: translateX(4px);
  color: #ff9acb;
}

/* 统计卡片 */
.stats-section {
  margin-bottom: 40px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 18px;
  box-shadow: var(--card-shadow);
}

.stat-icon {
  font-size: 28px;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fff0f6, #ffe9f1);
  border-radius: 12px;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-main);
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
}

/* 响应式 */
@media (max-width: 600px) {
  .welcome {
    flex-direction: column;
    text-align: center;
  }

  .clock {
    width: 100%;
  }

  .username {
    font-size: 28px;
  }

  .time {
    font-size: 40px;
  }
}
</style>
