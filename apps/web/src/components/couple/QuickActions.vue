<script setup lang="ts">
type Action = {
  title: string;
  desc: string;
  icon: string;
  tone: "green" | "blue";
  to?: string;
};
const props = defineProps<{ actions: Action[] }>();
const emit = defineEmits<{
  (e: "select", action: Action): void;
}>();

const handleClick = (a: Action) => {
  emit("select", a);
};
</script>

<template>
  <section class="quick">
    <div v-for="a in props.actions" :key="a.title" class="pill-card" @click="handleClick(a)">
      <div class="icon" :class="a.tone">{{ a.icon }}</div>
      <div>
        <p class="title">{{ a.title }}</p>
        <p class="muted">{{ a.desc }}</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
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
  border: 1px solid #e6f0ff;
  background: #ffffff;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.06);
}
.icon {
  width: 38px;
  height: 38px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  font-size: 18px;
}
.icon.green {
  background: #e7f8ee;
}
.icon.blue {
  background: #e6f1ff;
}
.title {
  margin: 0;
  font-weight: 700;
  color: #111827;
}
.muted {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
}
</style>
