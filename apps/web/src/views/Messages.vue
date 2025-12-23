<script setup lang="ts">
import { onMounted, ref } from "vue";
import { fetchMyCouple, addMessage, listMessages, deleteMessage, type Message } from "@/api/couples";
import { globalToast } from "@/composables/useToast";
import ConfirmDialog from "@/components/common/ConfirmDialog.vue";

const coupleId = ref<number | null>(null);
const partnerAName = ref("TA");
const partnerBName = ref("我");
const messages = ref<Message[]>([]);
const loading = ref(false);

const messageForm = ref({ author: "", content: "" });
const confirmDialog = ref<InstanceType<typeof ConfirmDialog> | null>(null);

const loadData = async () => {
  loading.value = true;
  try {
    const couple = await fetchMyCouple();
    if (couple) {
      coupleId.value = couple.id;
      partnerAName.value = couple.partner_a_name || "TA";
      partnerBName.value = couple.partner_b_name || "我";
      messages.value = await listMessages(couple.id);
    }
  } catch (err) {
    globalToast.error((err as Error).message);
  } finally {
    loading.value = false;
  }
};

const submitMessage = async () => {
  if (!coupleId.value || !messageForm.value.author || !messageForm.value.content) {
    globalToast.warning("请选择留言者并输入内容");
    return;
  }
  try {
    await addMessage(coupleId.value, messageForm.value);
    messageForm.value = { author: "", content: "" };
    messages.value = await listMessages(coupleId.value);
    globalToast.success("留言成功");
  } catch (err) {
    globalToast.error((err as Error).message);
  }
};

const handleDelete = async (id: number) => {
  const confirmed = await confirmDialog.value?.show({
    title: "删除留言",
    message: "确定要删除这条留言吗？",
    type: "danger",
  });
  if (!confirmed || !coupleId.value) return;
  try {
    await deleteMessage(coupleId.value, id);
    messages.value = await listMessages(coupleId.value);
    globalToast.success("已删除");
  } catch (err) {
    globalToast.error((err as Error).message);
  }
};

const formatDate = (dateStr: string) => {
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}月${d.getDate()}日 ${d.getHours()}:${String(d.getMinutes()).padStart(2, "0")}`;
};

onMounted(loadData);
</script>

<template>
  <div class="page">
    <ConfirmDialog ref="confirmDialog" />

    <div class="header">
      <span class="header-icon">💌</span>
      <div>
        <h2>留言板</h2>
        <p class="subtitle">写下想对 TA 说的话</p>
      </div>
    </div>

    <!-- 发留言 -->
    <div class="compose-card">
      <div class="author-select">
        <span class="label">我是：</span>
        <button
          :class="['author-btn', { active: messageForm.author === partnerAName }]"
          @click="messageForm.author = partnerAName"
        >
          {{ partnerAName }}
        </button>
        <button
          :class="['author-btn', { active: messageForm.author === partnerBName }]"
          @click="messageForm.author = partnerBName"
        >
          {{ partnerBName }}
        </button>
      </div>
      <textarea
        v-model="messageForm.content"
        placeholder="写下你想说的话..."
        rows="3"
      ></textarea>
      <button class="btn primary" @click="submitMessage" :disabled="!coupleId">
        发送留言 💕
      </button>
      <p v-if="!coupleId" class="hint">请先在「情侣空间」创建档案</p>
    </div>

    <!-- 留言列表 -->
    <div v-if="loading" class="loading">
      <span class="spinner"></span>
    </div>

    <div v-else-if="messages.length" class="messages-list">
      <div v-for="msg in messages" :key="msg.id" class="message-card">
        <div class="message-header">
          <span class="author">{{ msg.author }}</span>
          <span class="time">{{ formatDate(msg.created_at) }}</span>
        </div>
        <p class="content">{{ msg.content }}</p>
        <button class="delete-btn" @click="handleDelete(msg.id)">🗑️</button>
      </div>
    </div>

    <div v-else class="empty">
      <span class="empty-icon">💬</span>
      <p>还没有留言，写下第一条吧</p>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 24px 20px 60px;
  max-width: 700px;
  margin: 0 auto;
}

.header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
}

.header-icon { font-size: 36px; }

.header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
}

.subtitle {
  margin: 4px 0 0;
  color: var(--text-muted);
  font-size: 14px;
}

/* 发留言卡片 */
.compose-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: var(--card-shadow);
}

.author-select {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.label {
  color: var(--text-muted);
  font-size: 14px;
}

.author-btn {
  padding: 8px 16px;
  border: 1px solid var(--card-border);
  border-radius: 20px;
  background: white;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.author-btn:hover {
  border-color: #ff9acb;
}

.author-btn.active {
  background: var(--accent);
  color: var(--btn-text);
  border-color: transparent;
}

textarea {
  width: 100%;
  padding: 14px;
  border: 1px solid var(--card-border);
  border-radius: 14px;
  background: #fff8fb;
  resize: none;
  font-size: 15px;
  margin-bottom: 14px;
}

textarea:focus {
  outline: none;
  border-color: #ff9acb;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  background: var(--accent);
  color: var(--btn-text);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(235, 64, 120, 0.2);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.hint {
  margin: 10px 0 0;
  color: var(--text-muted);
  font-size: 13px;
}

/* 留言列表 */
.messages-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 16px;
  position: relative;
  box-shadow: var(--card-shadow);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.author {
  font-weight: 600;
  color: #c21b68;
}

.time {
  font-size: 12px;
  color: var(--text-muted);
}

.content {
  margin: 0;
  line-height: 1.6;
  white-space: pre-wrap;
}

.delete-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
  font-size: 14px;
}

.message-card:hover .delete-btn {
  opacity: 0.6;
}

.delete-btn:hover {
  opacity: 1 !important;
}

/* 加载和空状态 */
.loading {
  display: flex;
  justify-content: center;
  padding: 40px;
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

.empty {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}
</style>
