<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { marked } from "marked";
import DOMPurify from "dompurify";
import { fetchMyCouple, addNote, listNotes, updateNote, deleteNote, type Note } from "@/api/couples";
import { uploadImage } from "@/api/imageHost";

const coupleId = ref<number | null>(null);
const notes = ref<Note[]>([]);
const noteForm = ref({ title: "", content_md: "" });
const error = ref("");
const uploading = ref(false);
const uploadStatus = ref("");
const selectedId = ref<number | null>(null);
const editing = ref(false);

const renderMarkdown = (md: string) => DOMPurify.sanitize(marked.parse(md || ""));
const previewHtml = computed(() => renderMarkdown(noteForm.value.content_md));

const loadData = async () => {
  try {
    const couple = await fetchMyCouple();
    coupleId.value = couple?.id ?? null;
    if (coupleId.value) {
      notes.value = await listNotes(coupleId.value);
      if (!selectedId.value && notes.value.length) {
        selectedId.value = notes.value[0].id;
        editing.value = false;
        noteForm.value = { title: notes.value[0].title, content_md: notes.value[0].content_md };
      }
    }
  } catch (err) {
    error.value = (err as Error).message;
  }
};

const submitNote = async () => {
  if (!coupleId.value) return;
  if (!noteForm.value.title || !noteForm.value.content_md) return;
  try {
    if (editing.value && selectedId.value) {
      await updateNote(coupleId.value, selectedId.value, { ...noteForm.value });
    } else {
      const newNote = await addNote(coupleId.value, { ...noteForm.value });
      selectedId.value = newNote.id;
    }
    noteForm.value = { title: "", content_md: "" };
    editing.value = false;
    notes.value = await listNotes(coupleId.value);
  } catch (err) {
    error.value = (err as Error).message;
  }
};

const handleUpload = async (event: Event) => {
  const files = (event.target as HTMLInputElement).files;
  if (!files?.length) return;
  const file = files[0];
  uploading.value = true;
  uploadStatus.value = "上传中...";
  try {
    const resp = await uploadImage(file);
    const url: string | undefined =
      resp?.data?.links?.url || resp?.data?.links?.markdown || resp?.data?.links?.markdown_with_link;
    if (url) {
      noteForm.value.content_md = `${noteForm.value.content_md}\n\n![](${url})`;
      uploadStatus.value = "上传成功，已插入链接";
    } else {
      uploadStatus.value = "上传成功，但未获取到链接";
    }
  } catch (err) {
    uploadStatus.value = (err as Error).message || "上传失败";
  } finally {
    uploading.value = false;
    (event.target as HTMLInputElement).value = "";
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
  if (!coupleId.value) return;
  try {
    await deleteNote(coupleId.value, noteId);
    notes.value = await listNotes(coupleId.value);
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

onMounted(loadData);
</script>

<template>
  <div class="page">
    <div class="layout">
      <aside class="sidebar">
        <button class="btn primary full" @click="startNewNote">
          新建点滴
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
                placeholder="使用 Markdown 写下想说的话，或粘贴上传的图片链接"
              ></textarea>
              <button class="btn primary" @click="submitNote" :disabled="!coupleId">保存</button>
              <p class="muted" v-if="!coupleId">请先在「情侣空间」创建情侣信息</p>
            </div>
            <div class="preview">
              <p class="muted">实时预览</p>
              <div class="note-body" v-html="previewHtml"></div>
            </div>
          </div>
          <p v-if="!notes.length" class="muted center">还没有记录，写一篇吧。</p>
        </template>
      </main>
    </div>

    <p v-if="error" class="error">请求失败：{{ error }}</p>
  </div>
</template>

<style scoped>
.page {
  padding: 32px 16px 60px;
  max-width: 1100px;
  margin: 0 auto;
  color: #111827;
}
.layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 12px;
  height: calc(100vh - 200px);
  align-items: stretch;
}
.sidebar {
  background: #ffffff;
  border: 1px solid #ffd6e8;
  border-radius: 18px;
  padding: 12px;
  box-shadow: 0 10px 28px rgba(235, 64, 120, 0.08);
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
}
.note-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  flex: 1;
}
.note-item {
  padding: 10px;
  border-radius: 12px;
  border: 1px solid #ffe3ef;
  background: #fff;
  cursor: pointer;
  transition: 0.2s ease;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.note-item.active {
  border-color: #ff9acb;
  box-shadow: 0 8px 18px rgba(235, 64, 120, 0.12);
}
.note-item .title {
  margin: 0;
  font-weight: 700;
}
.note-actions {
  display: flex;
  gap: 6px;
}
.btn.tiny {
  padding: 6px 10px;
  border-radius: 10px;
}
.btn.danger {
  background: linear-gradient(135deg, #fecdd3, #fda4af);
  color: #7f1d1d;
}
.main {
  min-height: 480px;
  height: 100%;
}
.layout {
  margin-top: 0;
}
.center {
  text-align: center;
}
.editor-card {
  background: #ffffff;
  border: 1px solid #ffd6e8;
  border-radius: 18px;
  padding: 16px;
  box-shadow: 0 14px 34px rgba(235, 64, 120, 0.08);
  height: 100%;
}
.editor-card.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  height: 100%;
  align-items: stretch;
}
.view-card {
  background: #ffffff;
  border: 1px solid #ffd6e8;
  border-radius: 18px;
  padding: 16px;
  box-shadow: 0 14px 34px rgba(235, 64, 120, 0.08);
  height: 100%;
  overflow-y: auto;
}
.view-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.actions {
  display: flex;
  gap: 8px;
}
.stack {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 0;
}
input,
textarea {
  background: #fff0f6;
  border: 1px solid #ffcfe3;
  border-radius: 12px;
  padding: 10px 12px;
  color: #111827;
}
textarea {
  resize: vertical;
  min-height: 0;
  flex: 1;
  height: 100%;
  overflow: auto;
}
.btn {
  border: 1px solid #ffcfe3;
  border-radius: 999px;
  padding: 10px 16px;
  cursor: pointer;
  background: linear-gradient(135deg, #ff9acb, #ffd6e8);
  color: #5b0f2c;
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
.notes {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.note {
  padding: 12px;
  border-radius: 14px;
  background: #ffffff;
  border: 1px solid #ffd6e8;
  box-shadow: 0 10px 28px rgba(235, 64, 120, 0.08);
}
.note-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.note-body :deep(p) {
  margin: 6px 0;
}
.note-body :deep(pre) {
  background: #f9fbff;
  padding: 10px;
  border-radius: 8px;
  overflow: auto;
}
.preview {
  border-left: 1px solid #ffe3ef;
  padding-left: 12px;
  min-height: 0;
  overflow: auto;
}
.small {
  font-size: 12px;
}
.muted {
  color: #6b7280;
  font-size: 13px;
}
.error {
  margin-top: 8px;
  color: #ef4444;
}
@media (max-width: 900px) {
  .editor-card {
    grid-template-columns: 1fr;
  }
  .preview {
    border-left: none;
    padding-left: 0;
  }
}
</style>
