<script setup lang="ts">
import { onMounted, ref, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { marked } from "marked";
import DOMPurify from "dompurify";
import { fetchMyCouple, addNote, listNotes, updateNote, deleteNote, type Note } from "@/api/couples";

// 空间类型定义
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

// 当前空间类型
const currentSpace = ref<SpaceType>("couple");

// 数据
const spaceId = ref<number | null>(null);
const notes = ref<Note[]>([]);
const noteForm = ref({ title: "", content_md: "" });
const error = ref("");
const uploading = ref(false);
const uploadStatus = ref("");
const selectedId = ref<number | null>(null);
const editing = ref(false);
const loading = ref(false);

const currentSpaceConfig = computed(() => 
  spaceConfigs.find(s => s.key === currentSpace.value) || spaceConfigs[0]
);

const renderMarkdown = (md: string) => DOMPurify.sanitize(marked.parse(md || "") as string);
const previewHtml = computed(() => renderMarkdown(noteForm.value.content_md));

// 切换空间
const switchSpace = (space: SpaceType) => {
  router.push(`/notes/${space}`);
};

// 加载空间数据
const loadSpaceData = async () => {
  loading.value = true;
  error.value = "";
  spaceId.value = null;
  notes.value = [];
  selectedId.value = null;
  noteForm.value = { title: "", content_md: "" };

  try {
    if (currentSpace.value === "couple") {
      const couple = await fetchMyCouple();
      spaceId.value = couple?.id ?? null;
      if (spaceId.value) {
        notes.value = await listNotes(spaceId.value);
        if (notes.value.length) {
          selectedId.value = notes.value[0].id;
          editing.value = false;
          noteForm.value = { title: notes.value[0].title, content_md: notes.value[0].content_md };
        }
      }
    } else {
      // 其他空间类型暂未实现，显示提示
      error.value = `${currentSpaceConfig.value.label}功能即将上线，敬请期待！`;
    }
  } catch (err) {
    error.value = (err as Error).message;
  } finally {
    loading.value = false;
  }
};

const submitNote = async () => {
  if (!spaceId.value) return;
  if (!noteForm.value.title || !noteForm.value.content_md) return;
  try {
    if (editing.value && selectedId.value) {
      await updateNote(spaceId.value, selectedId.value, { ...noteForm.value });
    } else {
      const newNote = await addNote(spaceId.value, { ...noteForm.value });
      selectedId.value = newNote.id;
    }
    noteForm.value = { title: "", content_md: "" };
    editing.value = false;
    notes.value = await listNotes(spaceId.value);
  } catch (err) {
    error.value = (err as Error).message;
  }
};

const startNewNote = () => {
  noteForm.value = { title: "", content_md: "" };
  selectedId.value = null;
  editing.value = true;
};

const openNote = (n: Note) => {
  selectedId.value = n.id;
  editing.value = false;
  noteForm.value = { title: n.title, content_md: n.content_md };
};

const removeNote = async (noteId: number) => {
  if (!spaceId.value) return;
  try {
    await deleteNote(spaceId.value, noteId);
    notes.value = await listNotes(spaceId.value);
    if (selectedId.value === noteId) {
      if (notes.value.length) {
        selectedId.value = notes.value[0].id;
        editing.value = false;
        noteForm.value = { title: notes.value[0].title, content_md: notes.value[0].content_md };
      } else {
        selectedId.value = null;
        editing.value = true;
        noteForm.value = { title: "", content_md: "" };
      }
    }
  } catch (err) {
    error.value = (err as Error).message;
  }
};

// 监听路由参数变化
watch(
  () => route.params.spaceType,
  (newType) => {
    const type = (newType as SpaceType) || "couple";
    if (spaceConfigs.some(s => s.key === type)) {
      currentSpace.value = type;
      loadSpaceData();
    } else {
      router.replace("/notes/couple");
    }
  },
  { immediate: true }
);

onMounted(() => {
  // 如果没有空间类型参数，默认跳转到 couple
  if (!route.params.spaceType) {
    router.replace("/notes/couple");
  }
});
</script>

<template>
  <div class="page">
    <!-- 空间切换 Tab -->
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

    <!-- 当前空间标题 -->
    <div class="space-header">
      <span class="space-icon">{{ currentSpaceConfig.icon }}</span>
      <h2>{{ currentSpaceConfig.label }}的记录</h2>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <span class="spinner"></span>
      <p>加载中...</p>
    </div>

    <!-- 空间未开通提示 -->
    <div v-else-if="currentSpace !== 'couple'" class="coming-soon">
      <span class="big-icon">{{ currentSpaceConfig.icon }}</span>
      <h3>{{ currentSpaceConfig.label }}功能即将上线</h3>
      <p class="muted">敬请期待，我们正在努力开发中...</p>
      <button class="btn ghost" @click="switchSpace('couple')">返回情侣空间</button>
    </div>

    <!-- 主内容区 -->
    <div v-else class="layout">
      <aside class="sidebar">
        <button class="btn primary full" @click="startNewNote">
          ✏️ 新建记录
        </button>
        <div class="note-list">
          <div
            v-for="n in notes"
            :key="n.id"
            :class="['note-item', selectedId === n.id && 'active']"
          >
            <div class="note-head-item" @click="openNote(n)">
              <p class="title">{{ n.title }}</p>
              <p class="muted small">{{ n.created_at }}</p>
            </div>
            <div class="note-actions">
              <button class="btn ghost tiny" @click.stop="openNote(n)">查看</button>
              <button class="btn danger tiny" @click.stop="removeNote(n.id)">删除</button>
            </div>
          </div>
          <p v-if="!notes.length && spaceId" class="empty-hint">还没有记录，写一篇吧 ✨</p>
          <p v-if="!spaceId" class="empty-hint">请先在「{{ currentSpaceConfig.label }}」创建空间信息</p>
        </div>
      </aside>

      <main class="main">
        <template v-if="selectedId !== null && !editing">
          <div class="view-card">
            <div class="view-head">
              <div>
                <p class="muted small">创建时间：{{ notes.find((x) => x.id === selectedId)?.created_at }}</p>
                <h3>{{ notes.find((x) => x.id === selectedId)?.title }}</h3>
              </div>
              <div class="actions">
                <button class="btn ghost" @click="editing = true">编辑</button>
              </div>
            </div>
            <div class="note-body" v-html="renderMarkdown(notes.find((x) => x.id === selectedId)?.content_md || '')"></div>
          </div>
        </template>

        <template v-else>
          <div class="editor-card two-col">
            <div class="stack">
              <input v-model="noteForm.title" type="text" placeholder="标题" />
              <textarea
                v-model="noteForm.content_md"
                rows="10"
                placeholder="使用 Markdown 写下想说的话..."
              ></textarea>
              <button class="btn primary" @click="submitNote" :disabled="!spaceId">保存</button>
            </div>
            <div class="preview">
              <p class="muted">实时预览</p>
              <div class="note-body" v-html="previewHtml"></div>
            </div>
          </div>
        </template>
      </main>
    </div>

    <p v-if="error && currentSpace === 'couple'" class="error">请求失败：{{ error }}</p>
  </div>
</template>

<style scoped>
.page {
  padding: 24px 20px 60px;
  max-width: 1100px;
  margin: 0 auto;
  color: var(--text-main);
}

/* 空间切换 Tab */
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
  transition: all 0.2s ease;
}

.space-tab:hover {
  background: #fff0f6;
}

.space-tab.active {
  background: linear-gradient(135deg, var(--tab-color, #ff9acb), rgba(255, 214, 232, 0.8));
  color: #5b0f2c;
  box-shadow: 0 4px 12px rgba(235, 64, 120, 0.15);
}

.tab-icon {
  font-size: 18px;
}

.tab-label {
  font-size: 14px;
}

/* 空间标题 */
.space-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.space-icon {
  font-size: 28px;
}

.space-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
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

/* 即将上线 */
.coming-soon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.big-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.coming-soon h3 {
  margin: 0 0 8px;
  font-size: 24px;
  color: var(--text-main);
}

.coming-soon .muted {
  margin: 0 0 24px;
}

/* 主布局 */
.layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 16px;
  height: calc(100vh - 260px);
  min-height: 500px;
}

.sidebar {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 18px;
  padding: 14px;
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
  overflow: hidden;
}

.note-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  flex: 1;
}

.note-item {
  padding: 12px;
  border-radius: 12px;
  border: 1px solid var(--card-border);
  background: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.note-item:hover {
  border-color: #ff9acb;
}

.note-item.active {
  border-color: #ff9acb;
  background: #fff8fb;
  box-shadow: 0 4px 12px rgba(235, 64, 120, 0.1);
}

.note-item .title {
  margin: 0 0 4px;
  font-weight: 600;
  font-size: 14px;
}

.note-actions {
  display: flex;
  gap: 6px;
  margin-top: 8px;
}

.empty-hint {
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
  padding: 20px 10px;
}

/* 主内容区 */
.main {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.view-card,
.editor-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 18px;
  padding: 20px;
  box-shadow: var(--card-shadow);
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.view-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--card-border);
  flex-shrink: 0;
}

.view-head h3 {
  margin: 4px 0 0;
  font-size: 20px;
}

.view-card .note-body {
  flex: 1;
  overflow-y: auto;
}

.editor-card.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
  overflow: hidden;
}

.preview {
  border-left: 1px solid var(--card-border);
  padding-left: 20px;
  overflow-y: auto;
  height: 100%;
}

input,
textarea {
  background: #fff0f6;
  border: 1px solid #ffcfe3;
  border-radius: 12px;
  padding: 12px 14px;
  color: var(--text-main);
  font-size: 14px;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: #ff9acb;
}

textarea {
  resize: none;
  min-height: 150px;
  flex: 1;
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
}

.btn.primary {
  border-color: transparent;
}

.btn.ghost {
  background: #fff;
}

.btn.full {
  width: 100%;
}

.btn.tiny {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 8px;
}

.btn.danger {
  background: linear-gradient(135deg, #fecdd3, #fda4af);
  color: #7f1d1d;
}

.btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(235, 64, 120, 0.15);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Markdown 内容 */
.note-body :deep(p) {
  margin: 8px 0;
  line-height: 1.7;
}

.note-body :deep(h1),
.note-body :deep(h2),
.note-body :deep(h3) {
  margin: 16px 0 8px;
}

.note-body :deep(pre) {
  background: #f8fafc;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
}

.note-body :deep(code) {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}

.note-body :deep(img) {
  max-width: 100%;
  border-radius: 8px;
}

/* 辅助样式 */
.muted {
  color: var(--text-muted);
  font-size: 13px;
}

.small {
  font-size: 12px;
}

.error {
  margin-top: 16px;
  padding: 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  color: #dc2626;
  text-align: center;
}

/* 响应式 */
@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
    height: auto;
  }

  .sidebar {
    height: auto;
    max-height: 300px;
  }

  .main {
    min-height: 400px;
  }

  .editor-card.two-col {
    grid-template-columns: 1fr;
  }

  .preview {
    border-left: none;
    border-top: 1px solid var(--card-border);
    padding-left: 0;
    padding-top: 16px;
    max-height: 300px;
  }

  .space-tabs {
    width: 100%;
    overflow-x: auto;
  }
}
</style>
