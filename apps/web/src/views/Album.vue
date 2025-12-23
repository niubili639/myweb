<script setup lang="ts">
import { onMounted, ref } from "vue";
import { addPhoto, listPhotos, type Photo } from "@/api/media";
import { fetchMyCouple } from "@/api/couples";

const coupleId = ref<number | null>(null);
const photos = ref<Photo[]>([]);
const photoForm = ref({ url: "", caption: "" });
const error = ref("");

const loadCoupleAndPhotos = async () => {
  try {
    const couple = await fetchMyCouple();
    coupleId.value = couple?.id ?? null;
    if (coupleId.value) {
      photos.value = await listPhotos(coupleId.value);
    }
  } catch (err) {
    error.value = (err as Error).message;
  }
};

const submitPhoto = async () => {
  if (!coupleId.value || !photoForm.value.url) return;
  try {
    await addPhoto(coupleId.value, { ...photoForm.value });
    photoForm.value = { url: "", caption: "" };
    photos.value = await listPhotos(coupleId.value);
  } catch (err) {
    error.value = (err as Error).message;
  }
};

onMounted(loadCoupleAndPhotos);
</script>

<template>
  <div class="page">
    <div class="header">
      <div>
        <p class="muted">情侣相册</p>
        <h2>收藏我们的每一张照片</h2>
      </div>
    </div>
    <div class="card">
      <div class="stack">
        <input v-model="photoForm.url" type="url" placeholder="图片 URL" />
        <input v-model="photoForm.caption" type="text" placeholder="描述（可选）" />
        <button class="btn primary" @click="submitPhoto" :disabled="!coupleId">添加</button>
        <p class="muted" v-if="!coupleId">请先在“情侣空间”创建情侣信息。</p>
      </div>
      <div class="image-grid" v-if="photos.length">
        <div class="image-card" v-for="p in photos" :key="p.id">
          <img :src="p.url" :alt="p.caption || 'photo'" />
          <p class="muted">{{ p.caption }}</p>
        </div>
      </div>
      <p v-else class="muted">暂无照片，粘贴一个图片链接吧。</p>
      <p v-if="error" class="error">请求失败：{{ error }}</p>
    </div>
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
}
.stack {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
}
input {
  background: #fff0f6;
  border: 1px solid #ffcfe3;
  border-radius: 10px;
  padding: 10px 12px;
  color: var(--text-main);
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
.btn.primary {
  border-color: transparent;
}
.btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 10px 30px rgba(235, 64, 120, 0.18);
}
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.muted {
  color: var(--text-muted);
  font-size: 13px;
}
.image-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
}
.image-grid img {
  width: 100%;
  border-radius: 12px;
  object-fit: cover;
  border: 1px solid var(--card-border);
}
.image-card {
  background: #fff;
  padding: 8px;
  border-radius: 10px;
  border: 1px solid var(--card-border);
}
.error {
  margin-top: 8px;
  color: #ef4444;
}
</style>
