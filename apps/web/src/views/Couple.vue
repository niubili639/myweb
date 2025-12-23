<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from "vue";
import dayjs from "dayjs";
import duration from "dayjs/plugin/duration";
import { createCouple, fetchMyCouple, type Couple } from "@/api/couples";
import HeroCard from "@/components/couple/HeroCard.vue";
import QuickActions from "@/components/couple/QuickActions.vue";
import { useRouter } from "vue-router";

dayjs.extend(duration);

const couple = ref<Couple | null>(null);
const coupleForm = ref({
  name: "我们的故事",
  partner_a_name: "李牛逼",
  partner_b_name: "荆宝宝",
  start_date: dayjs().format("YYYY-MM-DD"),
});
const error = ref("");
let timer: number | undefined;
const heartbeat = ref(0);
const router = useRouter();

const elapsed = computed(() => {
  // heartbeat 只是用于触发每秒重算
  heartbeat.value;
  if (!couple.value?.start_date) return { d: 0, h: 0, m: 0, s: 0 };
  const diff = dayjs.duration(dayjs().diff(dayjs(couple.value.start_date)));
  return {
    d: Math.floor(diff.asDays()),
    h: diff.hours(),
    m: diff.minutes(),
    s: diff.seconds(),
  };
});

const daysTogether = computed(() => {
  if (!couple.value?.start_date) return 0;
  return dayjs().diff(dayjs(couple.value.start_date), "day");
});

const countdowns = computed(() => {
  const start = couple.value?.start_date ? dayjs(couple.value.start_date) : null;
  if (!start) return [];
  const targets = [
    { label: "恋爱一周年纪念日", date: start.add(1, "year") },
    { label: "恋爱二周年纪念日", date: start.add(2, "year") },
    { label: "520 纪念日", date: dayjs().year(dayjs().year()).month(4).date(20) },
  ];
  return targets.map((t) => ({
    label: t.label,
    days: Math.max(0, t.date.diff(dayjs(), "day")),
    date: t.date.format("YYYY-MM-DD"),
  }));
});

const wishList = ref([
  { text: "去大理旅行", progress: 50 },
  { text: "写一封小小情书", progress: 80 },
  { text: "一起完成 10 次夜跑", progress: 20 },
]);

const loadCouple = async () => {
  try {
    couple.value = await fetchMyCouple();
    if (couple.value?.start_date) {
      coupleForm.value.start_date = couple.value.start_date;
      if (couple.value.name) coupleForm.value.name = couple.value.name;
      if (couple.value.partner_a_name) coupleForm.value.partner_a_name = couple.value.partner_a_name;
      if (couple.value.partner_b_name) coupleForm.value.partner_b_name = couple.value.partner_b_name;
    }
  } catch (err) {
    error.value = (err as Error).message;
  }
};

const submitCouple = async () => {
  try {
    couple.value = await createCouple({
      name: coupleForm.value.name,
      partner_a_name: coupleForm.value.partner_a_name,
      partner_b_name: coupleForm.value.partner_b_name,
      start_date: coupleForm.value.start_date,
    });
  } catch (err) {
    error.value = (err as Error).message;
  }
};

onMounted(() => {
  loadCouple();
  timer = window.setInterval(() => {
    heartbeat.value += 1;
  }, 1000);
});

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer);
});
</script>

<template>
  <div class="page">
    <div class="paper header-paper">
      <div class="hero-container">
        <HeroCard
          :left-name="coupleForm.partner_a_name || '李牛逼'"
          :right-name="coupleForm.partner_b_name || '荆宝宝'"
          :elapsed="elapsed"
        />
      </div>
    </div>

    <div class="paper main-paper">
      <div class="content">
        <QuickActions
          :actions="[
            { title: '点点滴滴', desc: '记录你我生活', icon: '📘', tone: 'green', to: '/notes' },
            { title: '留言板', desc: '写下留言祝福', icon: '💌', tone: 'blue' },
            { title: '关于我们', desc: '我们的经历', icon: '🧭', tone: 'green' },
          ]"
          @select="(a) => { if (a.to) router.push(a.to); }"
        />

        <section class="cards">
          <div class="card map">
            <header>
              <p class="muted">爱情地图</p>
              <h3>我们的足迹记录在这里</h3>
            </header>
            <div class="map-illust">
              <div class="pin left">{{ coupleForm.partner_a_name }}</div>
              <div class="pin right">{{ coupleForm.partner_b_name }}</div>
              <div class="line"></div>
            </div>
          </div>

          <div class="card wishlist">
            <header>
              <p class="muted">共同愿望清单</p>
              <h3>一起实现的梦想</h3>
            </header>
            <ul class="list">
              <li v-for="item in wishList" :key="item.text">
                <label class="row">
                  <input type="checkbox" :checked="item.progress === 100" />
                  <span>{{ item.text }}</span>
                  <span class="muted">{{ item.progress }}%</span>
                </label>
                <div class="bar">
                  <div class="fill" :style="{ width: item.progress + '%' }"></div>
                </div>
              </li>
            </ul>
          </div>

          <div class="card countdown">
            <header>
              <p class="muted">纪念日倒计时</p>
              <h3>期待每一个重要时刻</h3>
            </header>
            <ul class="list">
              <li v-for="cd in countdowns" :key="cd.label">
                <div class="row">
                  <span>{{ cd.label }}</span>
                  <span class="muted">{{ cd.date }}</span>
                </div>
                <p class="muted">还剩 {{ cd.days }} 天</p>
                <div class="bar slim">
                  <div class="fill green" :style="{ width: Math.min(100, (cd.days / 365) * 100) + '%' }"></div>
                </div>
              </li>
            </ul>
          </div>
        </section>

        <section class="manage">
          <div class="card form">
            <header>
              <p class="muted">基础信息</p>
              <h3>创建 / 更新情侣档案</h3>
            </header>
            <div class="form-grid">
              <label class="field">
                <span>情侣标题</span>
                <input v-model="coupleForm.name" type="text" placeholder="我们的故事" />
              </label>
              <label class="field">
                <span>左侧昵称</span>
                <input v-model="coupleForm.partner_a_name" type="text" placeholder="李牛逼" />
              </label>
              <label class="field">
                <span>右侧昵称</span>
                <input v-model="coupleForm.partner_b_name" type="text" placeholder="荆宝宝" />
              </label>
              <label class="field">
                <span>在一起的日期</span>
                <input v-model="coupleForm.start_date" type="date" />
              </label>
              <button class="btn primary" @click="submitCouple">保存</button>
              <div v-if="couple" class="muted info">
                已记录：{{ couple.name }} · 共 {{ daysTogether }} 天
              </div>
            </div>
          </div>
        </section>

        <p v-if="error" class="error">请求失败：{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
}
.paper {
  width: 100%;
  display: flex;
  justify-content: center;
}
.header-paper {
  background: #ffe9f1;
  background-image: linear-gradient(#ffd6e8 1px, transparent 1px),
    linear-gradient(90deg, #ffd6e8 1px, transparent 1px);
  background-size: 18px 18px;
  padding: 32px 0 16px;
}
.main-paper {
  background: #fff6fb;
  background-image: linear-gradient(#ffddee 1px, transparent 1px),
    linear-gradient(90deg, #ffddee 1px, transparent 1px);
  background-size: 22px 22px;
  padding: 16px 0 48px;
}
.hero-container {
  width: 1200px;
  display: flex;
  justify-content: center;
}
.bubble {
  background: linear-gradient(145deg, #fff, #ffe9f5);
  border-radius: 22px;
  box-shadow: 0 16px 38px rgba(235, 64, 120, 0.12);
  padding: 18px 26px;
  border: 1px solid #ffd6e8;
  text-align: center;
  min-width: 780px;
}
.pair {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40px;
  margin-bottom: 6px;
}
.avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.avatar .img {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 30px;
  border: 4px solid #fff;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}
.avatar .img.sun {
  background: #fff5d6;
}
.avatar .img.photo {
  background: #dbeafe;
}
.heart {
  font-size: 30px;
}
.footnote {
  margin: 8px 0 4px;
  color: #d946ef;
  font-weight: 600;
}
.count {
  display: flex;
  align-items: baseline;
  gap: 10px;
  justify-content: center;
  color: #111827;
}
.count .big {
  font-size: 30px;
  font-weight: 800;
}
.count .time {
  font-size: 16px;
  color: #4b5563;
}
.content {
  width: 1200px;
  margin: 0 auto;
  padding: 10px 14px;
}
.quick {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
  margin: 12px 0 20px;
}
.pill-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid #ffd6e8;
  background: #ffffff;
  box-shadow: 0 12px 32px rgba(235, 64, 120, 0.08);
}
.pill-card .icon {
  width: 38px;
  height: 38px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  font-size: 18px;
}
.icon.green {
  background: #e9fdf3;
}
.icon.blue {
  background: #e8f3ff;
}
.pill-card .title {
  margin: 0;
  font-weight: 700;
  color: #111827;
}
.pill-card .muted {
  margin: 0;
}
.cards {
  display: grid;
  grid-template-columns: 1.2fr 1fr 1fr;
  gap: 16px;
}
.card {
  background: #ffffff;
  border: 1px solid #ffd6e8;
  border-radius: 20px;
  padding: 16px;
  box-shadow: 0 14px 34px rgba(235, 64, 120, 0.08);
}
.card h3 {
  margin: 0;
}
.card .muted {
  margin: 0 0 4px;
}
.map {
  grid-column: span 3;
}
.map-illust {
  position: relative;
  height: 240px;
  border-radius: 18px;
  background: linear-gradient(135deg, #ffe0e6, #e0f2fe);
  overflow: hidden;
  margin-top: 8px;
}
.map-illust .line {
  position: absolute;
  height: 4px;
  background: linear-gradient(90deg, #60a5fa, #ef4444);
  width: 60%;
  left: 20%;
  top: 60%;
  transform: rotate(-8deg);
  border-radius: 999px;
}
.map-illust .pin {
  position: absolute;
  top: 30%;
  padding: 8px 12px;
  background: #fff;
  border-radius: 999px;
  border: 1px solid #e6f0ff;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  font-weight: 700;
  color: #111827;
}
.map-illust .pin.left {
  left: 12%;
}
.map-illust .pin.right {
  right: 12%;
  top: 65%;
}
.list {
  list-style: none;
  padding: 0;
  margin: 10px 0 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.bar {
  height: 8px;
  border-radius: 999px;
  background: #ffe3ef;
  overflow: hidden;
}
.bar.slim {
  height: 6px;
}
.fill {
  height: 100%;
  background: linear-gradient(90deg, #fda4af, #fb7185);
}
.fill.green {
  background: linear-gradient(90deg, #a5f3fc, #34d399);
}
.countdown .list p {
  margin: 2px 0;
}
.wishlist input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #22c55e;
}
.manage {
  margin-top: 20px;
}
.form {
  background: #ffffff;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
  align-items: end;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: #374151;
  font-weight: 600;
}
input {
  background: #fff0f6;
  border: 1px solid #ffcfe3;
  border-radius: 12px;
  padding: 10px 12px;
  color: #111827;
}
.btn {
  border: 1px solid #ffcfe3;
  border-radius: 999px;
  padding: 10px 18px;
  cursor: pointer;
  background: linear-gradient(135deg, #ff9acb, #ffd6e8);
  color: #5b0f2c;
  transition: 0.2s ease;
  font-weight: 700;
  width: fit-content;
}
.btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 10px 30px rgba(235, 64, 120, 0.18);
}
.muted {
  color: #6b7280;
  font-size: 13px;
}
.error {
  margin-top: 16px;
  color: #ef4444;
  text-align: center;
}
@media (max-width: 1024px) {
  .content,
  .hero-container {
    width: 100%;
    padding: 0 12px;
  }
  .bubble {
    min-width: 0;
    width: 100%;
  }
  .cards {
    grid-template-columns: 1fr;
  }
  .map {
    grid-column: span 1;
  }
}
</style>
