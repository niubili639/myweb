<script setup lang="ts">
import { onMounted, ref, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { uploadImage } from "@/api/imageHost";
import { createPhoto, getPhotos, deletePhoto, type Photo } from "@/api/media";
import { globalToast } from "@/composables/useToast";
import ConfirmDialog from "@/components/common/ConfirmDialog.vue";

// 空间类型
type SpaceType = "couple" | "family" | "friends";

interface SpaceConfig {
  key: SpaceType;
  label: string;
  icon: string;
  color: string;
}

const spaceConfigs: SpaceConfig[] = [
  { key: "couple", label: "情侣空间", icon: "💕", color: "#ff9acb" },
  { key: "family", label: "家人空间", icon: "🏠", color: "#60a5fa" },
  { key: "friends", label: "朋友空间", icon: "👫", color: "#34d399" },
];

const route = useRoute();
const router = useRouter();
const confirmDialog = ref<InstanceType<typeof ConfirmDialog> | null>(null);

const currentSpace = ref<SpaceType>("couple");
const photos = ref<Photo[]>([]);
const loading = ref(false);
const uploading = ref(false);

// 选中的图片
const selectedPhoto = ref<Photo | null>(null);
const showModal = ref(false);

// 拖拽上传状态
const isDragging = ref(false);

const currentSpaceConfig = computed(() =>
  spaceConfigs.find((s) => s.key === currentSpace.value) || spaceConfigs[0]
);

// 切换空间
const switchSpace = (space: SpaceType) => {
  router.push(`/album/${space}`);
};

// 加载照片列表
const loadPhotos = async () => {
  loading.value = true;
  try {
    photos.value = await getPhotos(currentSpace.value);
  } catch (err) {
    globalToast.error((err as Error).message);
  } finally {
    loading.value = false;
  }
};

// 上传图片
const handleUpload = async (files: FileList | null) => {
  if (!files?.length) return;
  uploading.value = true;

  let successCount = 0;
  let failCount = 0;

  for (const file of Array.from(files)) {
    try {
      const res = await uploadImage(file);
      if (res.status && res.data) {
        await createPhoto({
          url: res.data.links.url,
          thumbnail_url: res.data.links.thumbnail_url,
          image_key: res.data.key,
          space_type: currentSpace.value,
        });
        successCount++;
      } else {
        failCount++;
      }
    } catch (err) {
      console.error("Upload error:", err);
      failCount++;
    }
  }

  uploading.value = false;

  if (successCount > 0) {
    globalToast.success(`成功上传 ${successCount} 张图片`);
    await loadPhotos();
  }
  if (failCount > 0) {
    globalToast.error(`${failCount} 张图片上传失败`);
  }
};

// 文件选择
const fileInput = ref<HTMLInputElement | null>(null);
const triggerUpload = () => {
  fileInput.value?.click();
};

const onFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement;
  handleUpload(target.files);
  target.value = "";
};

// 拖拽上传（整个页面）
let dragCounter = 0;

const onPageDragOver = (e: DragEvent) => {
  e.preventDefault();
};

const onPageDragEnter = (e: DragEvent) => {
  e.preventDefault();
  dragCounter++;
  if (e.dataTransfer?.types.includes("Files")) {
    isDragging.value = true;
  }
};

const onPageDragLeave = (e: DragEvent) => {
  e.preventDefault();
  dragCounter--;
  if (dragCounter === 0) {
    isDragging.value = false;
  }
};

const onPageDrop = (e: DragEvent) => {
  e.preventDefault();
  dragCounter = 0;
  isDragging.value = false;
  handleUpload(e.dataTransfer?.files || null);
};

// 打开图片详情
const openPhoto = (photo: Photo) => {
  selectedPhoto.value = photo;
  showModal.value = true;
};

// 关闭弹窗
const closeModal = () => {
  showModal.value = false;
  selectedPhoto.value = null;
};

// 复制链接
const copyLink = async (url: string) => {
  try {
    await navigator.clipboard.writeText(url);
    globalToast.success("链接已复制到剪贴板");
  } catch {
    globalToast.error("复制失败");
  }
};

// 删除图片
const handleDelete = async (photoId: number) => {
  const confirmed = await confirmDialog.value?.show({
    title: "删除照片",
    message: "确定要删除这张照片吗？此操作无法撤销。",
    confirmText: "删除",
    cancelText: "取消",
    type: "danger",
  });

  if (!confirmed) return;

  try {
    await deletePhoto(photoId);
    globalToast.success("删除成功");
    closeModal();
    await loadPhotos();
  } catch (err) {
    globalToast.error((err as Error).message);
  }
};

// 监听路由
watch(
  () => route.params.spaceType,
  (newType) => {
    const type = (newType as SpaceType) || "couple";
    if (spaceConfigs.some((s) => s.key === type)) {
      currentSpace.value = type;
      loadPhotos();
    } else {
      router.replace("/album/couple");
    }
  },
  { immediate: true }
);

onMounted(() => {
  if (!route.params.spaceType) {
    router.replace("/album/couple");
  }
});
</script>

<template>
  <div
    class="page"
    @dragover="onPageDragOver"
    @dragenter="onPageDragEnter"
    @dragleave="onPageDragLeave"
    @drop="onPageDrop"
  >
    <ConfirmDialog ref="confirmDialog" />

    <!-- 全屏拖拽遮罩 -->
    <Transition name="fade">
      <div v-if="isDragging" class="drag-overlay">
        <div class="drag-content">
          <span class="drag-icon">📤</span>
          <p>松开鼠标上传图片</p>
        </div>
      </div>
    </Transition>

    <!-- 空间切换 -->
    <div class="space-tabs">
      <button
        v-for="space in spaceConfigs"
        :key="space.key"
        :class="['space-tab', { active: currentSpace === space.key }]"
        :style="currentSpace === space.key ? { '--tab-color': space.color } : {}"
        @click="switchSpace(space.key)"
      >
        <span class="tab-icon">{{ space.icon }}</span>
        <span class="tab-label">{{ space.label }}</span>
      </button>
    </div>

    <!-- 标题和上传按钮 -->
    <div class="header">
      <div class="header-left">
        <span class="header-icon">{{ currentSpaceConfig.icon }}</span>
        <div>
          <h2>{{ currentSpaceConfig.label }}相册</h2>
          <p class="stats">共 {{ photos.length }} 张照片</p>
        </div>
      </div>
      <button class="upload-btn" :disabled="uploading" @click="triggerUpload">
        <span v-if="uploading" class="btn-spinner"></span>
        <span v-else>📤</span>
        <span>{{ uploading ? "上传中..." : "上传照片" }}</span>
      </button>
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        multiple
        hidden
        @change="onFileChange"
      />
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <span class="spinner"></span>
      <p>加载中...</p>
    </div>

    <!-- 图片网格 -->
    <div v-else-if="photos.length" class="gallery">
      <div
        v-for="photo in photos"
        :key="photo.id"
        class="gallery-item"
        @click="openPhoto(photo)"
      >
        <img :src="photo.thumbnail_url || photo.url" :alt="photo.caption || '照片'" loading="lazy" />
        <div class="item-actions">
          <button class="item-btn share" @click.stop="copyLink(photo.url)" title="复制链接">
            🔗
          </button>
          <button class="item-btn delete" @click.stop="handleDelete(photo.id)" title="删除">
            🗑️
          </button>
        </div>
        <div class="overlay">
          <span class="img-date">{{ photo.created_at?.split('T')[0] }}</span>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty">
      <span class="empty-icon">📸</span>
      <h3>还没有照片</h3>
      <p>拖拽图片到页面或点击上传按钮</p>
    </div>

    <!-- 图片详情弹窗 -->
    <Transition name="modal">
      <div v-if="showModal && selectedPhoto" class="modal-overlay" @click.self="closeModal">
        <div class="modal">
          <button class="modal-close" @click="closeModal">×</button>
          <div class="modal-image">
            <img :src="selectedPhoto.url" :alt="selectedPhoto.caption || '照片'" />
          </div>
          <div class="modal-info">
            <p class="modal-date">{{ selectedPhoto.created_at?.split('T')[0] }}</p>
            <p v-if="selectedPhoto.caption" class="modal-caption">{{ selectedPhoto.caption }}</p>
            <div class="modal-actions">
              <button class="action-btn" @click="copyLink(selectedPhoto.url)">
                <span class="action-icon">📋</span>
                <span>复制链接</span>
              </button>
              <button class="action-btn danger" @click="handleDelete(selectedPhoto.id)">
                <span class="action-icon">🗑️</span>
                <span>删除</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.page {
  padding: 24px 20px 60px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: calc(100vh - 100px);
  position: relative;
}

/* 全屏拖拽遮罩 */
.drag-overlay {
  position: fixed;
  inset: 0;
  background: rgba(255, 154, 203, 0.9);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.drag-content {
  text-align: center;
  color: white;
}

.drag-icon {
  font-size: 64px;
  display: block;
  margin-bottom: 16px;
  animation: bounce 0.6s ease infinite alternate;
}

.drag-content p {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

@keyframes bounce {
  from { transform: translateY(0); }
  to { transform: translateY(-10px); }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 空间切换 */
.space-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  padding: 6px;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  width: fit-content;
}

.space-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border: none;
  border-radius: 12px;
  background: transparent;
  cursor: pointer;
  font-weight: 600;
  color: var(--text-muted);
  transition: all 0.2s;
}

.space-tab:hover { background: #fff0f6; }

.space-tab.active {
  background: linear-gradient(135deg, var(--tab-color, #ff9acb), rgba(255, 214, 232, 0.8));
  color: #5b0f2c;
  box-shadow: 0 4px 12px rgba(235, 64, 120, 0.15);
}

.tab-icon { font-size: 18px; }
.tab-label { font-size: 14px; }

/* 头部 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-icon { font-size: 36px; }

.header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
}

.stats {
  margin: 4px 0 0;
  color: var(--text-muted);
  font-size: 14px;
}

/* 上传按钮 */
.upload-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  background: var(--accent);
  color: var(--btn-text);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s;
}

.upload-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(235, 64, 120, 0.25);
}

.upload-btn:disabled {
  opacity: 0.7;
  cursor: wait;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(91, 15, 44, 0.3);
  border-top-color: var(--btn-text);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* 加载 */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px;
  color: var(--text-muted);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--card-border);
  border-top-color: #ff9acb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 图片网格 */
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.gallery-item {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  aspect-ratio: 1;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  transition: all 0.3s;
}

.gallery-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(235, 64, 120, 0.15);
}

.gallery-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.gallery-item:hover img {
  transform: scale(1.05);
}

/* 图片操作按钮 */
.item-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 6px;
  opacity: 0;
  transition: opacity 0.2s;
  z-index: 5;
}

.gallery-item:hover .item-actions {
  opacity: 1;
}

.item-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  backdrop-filter: blur(8px);
}

.item-btn.share {
  background: rgba(255, 255, 255, 0.9);
}

.item-btn.share:hover {
  background: white;
  transform: scale(1.1);
}

.item-btn.delete {
  background: rgba(254, 226, 226, 0.9);
}

.item-btn.delete:hover {
  background: #fee2e2;
  transform: scale(1.1);
}

/* 上传卡片 */
.upload-card {
  border: 2px dashed var(--card-border);
  background: rgba(255, 248, 251, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-card:hover {
  border-color: #ff9acb;
  background: #fff0f6;
}

.upload-card.dragging {
  border-color: #ff9acb;
  background: #ffe9f1;
  transform: scale(1.02);
}

.upload-card.uploading {
  opacity: 0.7;
  cursor: wait;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--text-muted);
}

.upload-icon {
  font-size: 32px;
  opacity: 0.6;
}

.upload-text {
  font-size: 13px;
  font-weight: 500;
}

.upload-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid var(--card-border);
  border-top-color: #ff9acb;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 10px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.6));
  color: white;
  opacity: 0;
  transition: opacity 0.3s;
}

.gallery-item:hover .overlay { opacity: 1; }

.img-date { font-size: 12px; }

/* 空状态 */
.empty {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 64px;
  display: block;
  margin-bottom: 16px;
}

.empty h3 {
  margin: 0 0 8px;
  color: var(--text-main);
}

.empty p { margin: 0; }

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  background: white;
  border-radius: 20px;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  position: relative;
}

.modal-close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  border-radius: 50%;
  font-size: 24px;
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.modal-close:hover { background: rgba(0, 0, 0, 0.7); }

.modal-image {
  max-height: 65vh;
  overflow: hidden;
  background: #f8f8f8;
}

.modal-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.modal-info { padding: 20px; }

.modal-date {
  margin: 0 0 8px;
  color: var(--text-muted);
  font-size: 14px;
}

.modal-caption {
  margin: 0 0 16px;
  font-size: 16px;
}

.modal-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: 1px solid var(--card-border);
  border-radius: 12px;
  background: white;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #fff0f6;
  border-color: #ff9acb;
  transform: translateY(-1px);
}

.action-btn.danger {
  color: #dc2626;
  border-color: #fecaca;
}

.action-btn.danger:hover {
  background: #fef2f2;
  border-color: #f87171;
}

.action-icon { font-size: 16px; }

/* 弹窗动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal,
.modal-leave-to .modal {
  transform: scale(0.9);
}

/* 响应式 */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .gallery {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .modal-actions {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
    justify-content: center;
  }

  .space-tabs {
    width: 100%;
    overflow-x: auto;
  }
}
</style>
