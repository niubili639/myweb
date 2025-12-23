<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  chat as chatApi,
  generateImage,
  listSessions,
  createSession,
  listMessages,
  setSessionPin,
  deleteSession,
  type ChatSession,
  type ChatMessage,
} from "@/api/ai";

type Mode = "chat" | "image";

const sessions = ref<ChatSession[]>([]);
const currentSessionId = ref<number | null>(null);
const mode = ref<Mode>("chat");
const chatInput = ref("");
const imageInput = ref("");
const messages = ref<ChatMessage[]>([]);
const sessionMenuOpen = ref<number | null>(null);
const chatLoading = ref(false);
const imageLoading = ref(false);
const error = ref("");
const textModel = ref("qwen-turbo");
const imageModel = ref("qwen-image-plus");
// 限定为 Qwen 文生图支持的尺寸
const imageSize = ref("1328*1328");

const loadSessions = async () => {
  try {
    sessions.value = await listSessions();
    if (!currentSessionId.value && sessions.value.length) {
      currentSessionId.value = sessions.value[0].id;
      mode.value = (sessions.value[0].mode as Mode) || "chat";
      await loadMessages();
    }
  } catch (err) {
    error.value = (err as Error).message;
  }
};

const loadMessages = async () => {
  if (!currentSessionId.value) return;
  try {
    messages.value = await listMessages(currentSessionId.value);
  } catch (err) {
    error.value = (err as Error).message;
  }
};

const newConversation = async (targetMode: Mode = "chat") => {
  error.value = "";
  try {
    const session = await createSession({
      title: "新会话",
      mode: targetMode,
      model: targetMode === "chat" ? textModel.value : imageModel.value,
    });
    sessions.value.unshift(session);
    currentSessionId.value = session.id;
    mode.value = targetMode;
    messages.value = [];
  } catch (err) {
    error.value = (err as Error).message;
  }
};

const switchSession = async (session: ChatSession) => {
  currentSessionId.value = session.id;
  mode.value = (session.mode as Mode) || "chat";
  await loadMessages();
  sessionMenuOpen.value = null;
};

const sendMessage = async () => {
  if (mode.value === "chat") {
    await submitChat();
  } else {
    await submitImage();
  }
};

const submitChat = async () => {
  if (!chatInput.value) return;
  chatLoading.value = true;
  error.value = "";
  try {
    const res = await chatApi({
      prompt: chatInput.value,
      session_id: currentSessionId.value || undefined,
      model: textModel.value,
    });
    if (res.session_id && res.session_id !== currentSessionId.value) {
      await loadSessions();
      currentSessionId.value = res.session_id;
    } else {
      await loadMessages();
    }
    chatInput.value = "";
  } catch (err) {
    error.value = (err as Error).message;
  } finally {
    chatLoading.value = false;
    await loadMessages();
  }
};

const submitImage = async () => {
  if (!imageInput.value) return;
  imageLoading.value = true;
  error.value = "";
  try {
    const res = await generateImage({
      prompt: imageInput.value,
      session_id: currentSessionId.value || undefined,
      model: imageModel.value,
      size: imageSize.value,
    });
    if (res.session_id && res.session_id !== currentSessionId.value) {
      await loadSessions();
      currentSessionId.value = res.session_id;
    } else {
      await loadMessages();
    }
    imageInput.value = "";
  } catch (err) {
    error.value = (err as Error).message;
  } finally {
    imageLoading.value = false;
    await loadMessages();
  }
};

const formattedMessages = computed(() => messages.value);

const togglePin = async (session: ChatSession) => {
  try {
    await setSessionPin(session.id, !(session.is_pinned === 1));
    await loadSessions();
  } catch (err) {
    error.value = (err as Error).message;
  } finally {
    sessionMenuOpen.value = null;
  }
};

const handleDelete = async (session: ChatSession) => {
  try {
    await deleteSession(session.id);
    if (currentSessionId.value === session.id) {
      currentSessionId.value = null;
      messages.value = [];
    }
    await loadSessions();
  } catch (err) {
    error.value = (err as Error).message;
  } finally {
    sessionMenuOpen.value = null;
  }
};

onMounted(async () => {
  await loadSessions();
});
</script>

<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo">Q</div>
        <button class="pill" @click="newConversation('chat')">+ 新对话</button>
        <button class="pill ghost" @click="newConversation('image')">+ 新图片</button>
      </div>
      <div class="session-list">
        <div
          v-for="s in sessions"
          :key="s.id"
          :class="['session-item', currentSessionId === s.id && 'active']"
          @click="switchSession(s)"
        >
          <div class="title">{{ s.title || (s.mode === 'image' ? '图片' : '对话') }}</div>
          <div class="meta">
            {{ s.mode }} · {{ s.model || "默认" }}
            <span v-if="s.is_pinned === 1" class="tag">置顶</span>
          </div>
          <div class="session-actions" @click.stop="">
            <button class="dots" @click="sessionMenuOpen = sessionMenuOpen === s.id ? null : s.id">⋯</button>
            <div v-if="sessionMenuOpen === s.id" class="menu">
              <button @click="togglePin(s)">{{ s.is_pinned === 1 ? "取消置顶" : "置顶" }}</button>
              <button class="danger" @click="handleDelete(s)">删除</button>
            </div>
          </div>
        </div>
        <p v-if="!sessions.length" class="muted">暂无会话，先新建一个吧。</p>
      </div>
    </aside>

    <main class="main">
      <header class="topbar">
        <div class="mode-switch">
          <button :class="['chip', mode === 'chat' && 'active']" @click="mode = 'chat'">对话</button>
          <button :class="['chip', mode === 'image' && 'active']" @click="mode = 'image'">生成图片</button>
        </div>
        <div class="model-select" v-if="mode === 'chat'">
          <label>模型</label>
          <select v-model="textModel">
            <option value="qwen-turbo">qwen-turbo</option>
            <option value="qwen-plus">qwen-plus</option>
          </select>
        </div>
        <div class="model-select" v-else>
          <label>模型</label>
          <select v-model="imageModel">
            <option value="qwen-image-plus">qwen-image-plus</option>
            <option value="qwen-image">qwen-image</option>
          </select>
          <label>尺寸</label>
          <select v-model="imageSize">
            <option value="1328*1328">1328 × 1328 (默认)</option>
            <option value="1664*928">1664 × 928 (16:9)</option>
            <option value="1472*1140">1472 × 1140 (4:3)</option>
            <option value="1140*1472">1140 × 1472 (3:4)</option>
            <option value="928*1664">928 × 1664 (9:16)</option>
          </select>
        </div>
      </header>

      <section class="conversation" :class="{ hasMessages: formattedMessages.length > 0 }">
        <div class="history" :class="{ emptyState: !formattedMessages.length }">
          <div
            v-for="msg in formattedMessages"
            :key="msg.id"
            :class="['bubble', msg.role === 'assistant' ? 'assistant' : 'user']"
          >
            <div class="bubble-head">{{ msg.role === "assistant" ? "AI" : "我" }}</div>
            <div class="bubble-body">
              <template v-if="msg.message_type === 'image'">
                <div class="image-grid">
                  <img v-for="url in msg.content.split('\n')" :key="url" :src="url" alt="AI 图" />
                </div>
              </template>
              <p v-else>{{ msg.content }}</p>
            </div>
          </div>
          <div v-if="!formattedMessages.length" class="empty">
            <h2>有什么可以帮忙的？</h2>
            <p class="muted">输入问题开始对话，或切换到“生成图片”创作一张图。</p>
          </div>
        </div>

        <div class="input-bar">
          <div class="input-wrap">
            <textarea
              v-if="mode === 'chat'"
              v-model="chatInput"
              rows="2"
              placeholder="输入你的问题..."
              @keydown.enter.prevent="sendMessage"
            ></textarea>
            <textarea
              v-else
              v-model="imageInput"
              rows="2"
              placeholder="描述你想要的画面..."
              @keydown.enter.prevent="sendMessage"
            ></textarea>
            <div class="input-actions">
              <button class="btn send" :disabled="chatLoading || imageLoading" @click="sendMessage">
                {{ chatLoading || imageLoading ? "处理中..." : "发送" }}
              </button>
            </div>
          </div>
        </div>
      </section>

      <p v-if="error" class="error">请求失败：{{ error }}</p>
    </main>
  </div>
</template>

<style scoped>
.layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: calc(100vh - 140px);
  gap: 16px;
  padding: 16px 18px;
  color: var(--text-main);
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
}
.sidebar {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 18px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: var(--card-shadow);
}
.sidebar-header {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.logo {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: var(--accent);
  color: var(--btn-text);
  display: grid;
  place-items: center;
  font-weight: 700;
}
.pill {
  border: 1px solid var(--card-border);
  border-radius: 999px;
  background: #fff8fb;
  padding: 9px 12px;
  cursor: pointer;
  color: var(--text-main);
  transition: 0.2s ease;
}
.pill:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 18px rgba(235, 64, 120, 0.12);
}
.pill.ghost {
  background: #fff;
}
.session-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.session-item {
  border: 1px solid var(--card-border);
  border-radius: 14px;
  padding: 10px;
  background: #fff;
  cursor: pointer;
  transition: 0.2s ease;
}
.session-item:hover {
  border-color: #ff9acb;
  box-shadow: 0 10px 24px rgba(235, 64, 120, 0.12);
}
.session-item.active {
  border-color: #ff9acb;
  box-shadow: 0 10px 24px rgba(235, 64, 120, 0.16);
}
.session-item .title {
  margin: 0;
  font-weight: 600;
  color: var(--text-main);
}
.session-item .meta {
  margin: 0;
  color: var(--text-muted);
  font-size: 12px;
}
.meta .tag {
  margin-left: 6px;
  padding: 2px 6px;
  border-radius: 999px;
  background: #ffe3ef;
  color: #7a103d;
}
.session-actions {
  position: relative;
  margin-top: 6px;
  display: flex;
  justify-content: flex-end;
}
.dots {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 16px;
  padding: 2px 6px;
}
.dots:hover {
  color: var(--text-main);
}
.menu {
  position: absolute;
  right: 0;
  top: 24px;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 10px;
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 120px;
  z-index: 5;
  box-shadow: var(--card-shadow);
}
.menu button {
  background: transparent;
  border: none;
  color: var(--text-main);
  text-align: left;
  padding: 6px 8px;
  border-radius: 8px;
  cursor: pointer;
}
.menu button:hover {
  background: #fff4f9;
}
.menu .danger {
  color: #fca5a5;
}
.main {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 18px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: calc(100vh - 180px);
  box-shadow: var(--card-shadow);
}
.topbar {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: flex-start;
  flex-wrap: wrap;
}
.mode-switch {
  display: flex;
  gap: 8px;
}
.topbar .chip {
  border: 1px solid var(--card-border);
  border-radius: 999px;
  background: #fff8fb;
  padding: 8px 12px;
  color: var(--text-main);
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s ease;
}
.topbar .chip.active {
  background: var(--accent);
  border-color: transparent;
  color: var(--btn-text);
  box-shadow: 0 10px 24px rgba(235, 64, 120, 0.16);
}
.model-select {
  display: flex;
  align-items: center;
  gap: 8px;
}
.model-select label {
  color: var(--text-muted);
  font-size: 13px;
}
.model-select select {
  background: #fff;
  border: 1px solid var(--card-border);
  border-radius: 10px;
  padding: 8px 10px;
  color: var(--text-main);
}
.conversation {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
}
.conversation.hasMessages {
  padding-top: 24px;
}
.history {
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 12px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #fff;
  max-width: 920px;
  width: 100%;
  max-height: 70vh;
  justify-content: flex-start;
  box-shadow: var(--card-shadow);
}
.history.emptyState {
  justify-content: center;
  min-height: 320px;
  padding-top: 0;
}
.bubble {
  border: 1px solid var(--card-border);
  border-radius: 14px;
  padding: 10px;
  background: #fff8fb;
}
.bubble.assistant {
  background: linear-gradient(135deg, #fff2f8, #fef6ff);
}
.bubble-head {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 4px;
}
.bubble-body p {
  margin: 0;
  color: var(--text-main);
}
.empty {
  text-align: center;
  color: var(--text-main);
  margin-top: 0;
}
.input-bar {
  border: 1px solid var(--card-border);
  border-radius: 18px;
  padding: 10px;
  background: #fff;
  max-width: 820px;
  margin: 14px auto 0;
  width: 100%;
  box-shadow: var(--card-shadow);
}
.input-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: stretch;
  position: relative;
}
.input-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}
.input-actions .btn.send {
  align-self: flex-end;
}
textarea {
  border: 1px solid #ffcfe3;
  border-radius: 12px;
  padding: 10px;
  resize: none;
  color: var(--text-main);
  background: #fff0f6;
}
.btn {
  border: 1px solid var(--card-border);
  border-radius: 999px;
  padding: 10px 16px;
  cursor: pointer;
  background: #fff;
  color: var(--text-main);
  transition: 0.2s ease;
  font-weight: 600;
}
.btn.plain {
  background: #fff;
  color: var(--text-main);
}
.btn.send {
  background: var(--accent);
  color: var(--btn-text);
  border-color: transparent;
  box-shadow: 0 10px 24px rgba(235, 64, 120, 0.14);
}
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.image-grid {
  margin-top: 8px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
}
.image-grid img {
  width: 100%;
  border-radius: 10px;
  border: 1px solid var(--card-border);
  object-fit: cover;
}
.muted {
  color: var(--text-muted);
  font-size: 13px;
}
.error {
  color: #fca5a5;
}
@media (max-width: 1080px) {
  .layout {
    grid-template-columns: 1fr;
    min-height: auto;
  }
  .sidebar {
    order: 2;
  }
  .main {
    order: 1;
  }
}
</style>
