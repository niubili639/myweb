<script setup lang="ts">
defineProps<{
  leftName: string;
  rightName: string;
  leftEmoji?: string;
  rightEmoji?: string;
  tagline?: string;
  elapsed: { d: number; h: number; m: number; s: number };
}>();
</script>

<template>
  <div class="bubble">
    <div class="pair">
      <div class="avatar">
        <div class="img sun">{{ leftEmoji || "☀️" }}</div>
        <p>{{ leftName }}</p>
      </div>
      <div class="heart">❤️</div>
      <div class="avatar">
        <div class="img photo">{{ rightEmoji || "😊" }}</div>
        <p>{{ rightName }}</p>
      </div>
    </div>
    <p class="footnote">{{ tagline || "这是我们一起走过的" }}</p>
    <div class="count">
      <span class="big">{{ elapsed.d }}天</span>
      <span class="time">{{ elapsed.h }}时 {{ elapsed.m }}分 {{ elapsed.s }}秒</span>
    </div>
  </div>
</template>

<style scoped>
.bubble {
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.08);
  padding: 16px 24px;
  border: 1px solid #ebebeb;
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
  font-size: 28px;
}
.footnote {
  margin: 8px 0 4px;
  color: #7c3aed;
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
  color: #374151;
}
@media (max-width: 900px) {
  .bubble {
    min-width: 0;
    width: 100%;
  }
}
</style>
