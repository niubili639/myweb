<script setup lang="ts">
import { computed, onMounted, ref, nextTick } from "vue";
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
const imageSize = ref("1328*1328");
const messagesContainer = ref<HTMLElement | null>(null);
const sidebarCollapsed = ref(false);

const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

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
    scrollToBottom();
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
  if (!chatInput.value.trim()) return;
  chatLoading.value = true;
  error.value = "";
  try {
    const res = await chatApi({
      prompt: chatInput.value,
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
  if (!imageInput.value.trim()) return;
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

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
};

onMounted(async () => {
  await loadSessions();
});
</script>

<template>
  <div class="ai-container">
    <!-- 左侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <button class="new-chat-btn" @click="newConversation(mode)">
          <span class="icon">+</span>
          <span class="text">新对话</span>
        </button>
        <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed">
          <span>{{ sidebarCollapsed ? '→' : '←' }}</span>
        </button>
      </div>

      <div class="session-list" v-if="!sidebarCollapsed">
        <div
          v-for="s in sessions"
          :key="s.id"
          :class="['session-item', { active: currentSessionId === s.id }]"
          @click="switchSession(s)"
        >
          <span class="session-icon">{{ s.mode === 'image' ? '🎨' : '💬' }}</span>
          <div class="session-info">
            <span class="session-title">{{ s.title || (s.mode === 'image' ? '图片生成' : '新对话') }}</span>
          </div>
          <div class="session-actions" @click.stop>
            <button class="action-btn" @click="sessionMenuOpen = sessionMenuOpen === s.id ? null : s.id">⋯</button>
            <div v-if="sessionMenuOpen === s.id" class="dropdown-menu">
              <button @click="togglePin(s)">
                {{ s.is_pinned === 1 ? '📌 取消置顶' : '📌 置顶' }}
              </button>
              <button class="danger" @click="handleDelete(s)">🗑️ 删除</button>
            </div>
          </div>
          <span v-if="s.is_pinned === 1" class="pin-badge">📌</span>
        </div>
        <p v-if="!sessions.length" class="empty-hint">暂无会话</p>
      </div>
    </aside>

    <!-- 主聊天区域 -->
    <main class="chat-main">
      <!-- 顶部工具栏 -->
      <header class="chat-header">
        <div class="mode-tabs">
          <button :class="['tab', { active: mode === 'chat' }]" @click="mode = 'chat'; newConversation('chat')">
            💬 对话
          </button>
          <button :class="['tab', { active: mode === 'image' }]" @click="mode = 'image'; newConversation('image')">
            🎨 生图
          </button>
        </div>
        <div class="model-selector">
          <template v-if="mode === 'chat'">
            <select v-model="textModel">
              <option value="qwen-turbo">Qwen Turbo</option>
              <option value="qwen-plus">Qwen Plus</option>
            </select>
          </template>
          <template v-else>
            <select v-model="imageModel">
              <option value="qwen-image-plus">Qwen Image Plus</option>
              <option value="qwen-image">Qwen Image</option>
            </select>
            <select v-model="imageSize">
              <option value="1328*1328">1:1</option>
              <option value="1664*928">16:9</option>
              <option value="928*1664">9:16</option>
            </select>
          </template>
        </div>
      </header>

      <!-- 消息区域 -->
      <div class="messages-wrapper" ref="messagesContainer">
        <div class="messages-container">
          <!-- 空状态 -->
          <div v-if="!formattedMessages.length" class="empty-state">
            <div class="logo-icon">✨</div>
            <h2>有什么可以帮你的？</h2>
            <p>开始一段新对话，或者让我为你生成一张图片</p>
            <div class="quick-actions">
              <button class="quick-btn" @click="chatInput = '给我讲个故事'; sendMessage()">📖 讲个故事</button>
              <button class="quick-btn" @click="chatInput = '今天天气怎么样'; sendMessage()">🌤️ 聊聊天气</button>
              <button class="quick-btn" @click="mode = 'image'; imageInput = '一只可爱的猫咪'; sendMessage()">🐱 画只猫咪</button>
            </div>
          </div>

          <!-- 消息列表 -->
          <template v-else>
            <div
              v-for="msg in formattedMessages"
              :key="msg.id"
              :class="['message', msg.role]"
            >
              <div class="avatar">
                {{ msg.role === 'assistant' ? '🤖' : '👤' }}
              </div>
              <div class="message-content">
                <div class="message-header">
                  <span class="role-name">{{ msg.role === 'assistant' ? 'AI 助手' : '你' }}</span>
                </div>
                <div class="message-body">
                  <template v-if="msg.message_type === 'image'">
                    <div class="image-grid">
                      <img v-for="url in msg.content.split('\n')" :key="url" :src="url" alt="生成的图片" />
                    </div>
                  </template>
                  <p v-else>{{ msg.content }}</p>
                </div>
              </div>
            </div>
          </template>

          <!-- 加载状态 -->
          <div v-if="chatLoading || imageLoading" class="message assistant loading">
            <div class="avatar">🤖</div>
            <div class="message-content">
              <div class="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部输入区 -->
      <div class="input-area">
        <div class="input-container">
          <textarea
            v-if="mode === 'chat'"
            v-model="chatInput"
            placeholder="输入消息..."
            rows="1"
            @keydown="handleKeydown"
            @input="(e: Event) => { const t = e.target as HTMLTextAreaElement; t.style.height = 'auto'; t.style.height = Math.min(t.scrollHeight, 200) + 'px'; }"
          ></textarea>
          <textarea
            v-else
            v-model="imageInput"
            placeholder="描述你想要的图片..."
            rows="1"
            @keydown="handleKeydown"
            @input="(e: Event) => { const t = e.target as HTMLTextAreaElement; t.style.height = 'auto'; t.style.height = Math.min(t.scrollHeight, 200) + 'px'; }"
          ></textarea>
          <button
            class="send-btn"
            :disabled="chatLoading || imageLoading || !(mode === 'chat' ? chatInput.trim() : imageInput.trim())"
            @click="sendMessage"
          >
            <span v-if="chatLoading || imageLoading" class="spinner"></span>
            <span v-else>↑</span>
          </button>
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <p class="disclaimer">AI 生成内容仅供参考</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
.ai-container {
  display: flex;
  height: calc(100vh - 60px);
  overflow: hidden;
}

/* 侧边栏 */
.sidebar {
  width: 260px;
  background: rgba(255, 255, 255, 0.85);
  border-right: 1px solid var(--card-border);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  padding: 12px;
  display: flex;
  gap: 8px;
  border-bottom: 1px solid var(--card-border);
}

.new-chat-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  border: 1px dashed var(--card-border);
  border-radius: 12px;
  background: transparent;
  color: var(--text-main);
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.new-chat-btn:hover {
  background: #fff0f6;
  border-color: #ff9acb;
}

.sidebar.collapsed .new-chat-btn .text {
  display: none;
}

.collapse-btn {
  width: 40px;
  height: 40px;
  border: 1px solid var(--card-border);
  border-radius: 10px;
  background: transparent;
  cursor: pointer;
  color: var(--text-muted);
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}

.session-item:hover {
  background: #fff0f6;
}

.session-item.active {
  background: linear-gradient(135deg, #fff0f6, #ffe9f1);
}

.session-icon {
  font-size: 16px;
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-title {
  display: block;
  font-size: 14px;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-actions {
  position: relative;
}

.action-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 6px;
  color: var(--text-muted);
  opacity: 0;
  transition: opacity 0.2s;
}

.session-item:hover .action-btn {
  opacity: 1;
}

.dropdown-menu {
  position: absolute;
  right: 0;
  top: 100%;
  background: white;
  border: 1px solid var(--card-border);
  border-radius: 10px;
  padding: 4px;
  min-width: 120px;
  box-shadow: var(--card-shadow);
  z-index: 100;
}

.dropdown-menu button {
  display: block;
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: transparent;
  text-align: left;
  cursor: pointer;
  border-radius: 6px;
  font-size: 13px;
}

.dropdown-menu button:hover {
  background: #fff0f6;
}

.dropdown-menu .danger {
  color: #dc2626;
}

.pin-badge {
  font-size: 12px;
}

.empty-hint {
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
  padding: 20px;
}

/* 主聊天区 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-header {
  padding: 12px 20px;
  border-bottom: 1px solid var(--card-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.7);
}

.mode-tabs {
  display: flex;
  gap: 4px;
  background: #fff0f6;
  padding: 4px;
  border-radius: 10px;
}

.tab {
  padding: 8px 16px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  color: var(--text-muted);
  transition: all 0.2s;
}

.tab.active {
  background: white;
  color: var(--text-main);
  box-shadow: 0 2px 8px rgba(235, 64, 120, 0.1);
}

.model-selector {
  display: flex;
  gap: 8px;
}

.model-selector select {
  padding: 8px 12px;
  border: 1px solid var(--card-border);
  border-radius: 8px;
  background: white;
  color: var(--text-main);
  font-size: 13px;
}

/* 消息区域 */
.messages-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.messages-container {
  max-width: 800px;
  margin: 0 auto;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
  text-align: center;
  padding: 40px;
}

.logo-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.empty-state h2 {
  font-size: 24px;
  color: var(--text-main);
  margin: 0 0 8px;
}

.empty-state p {
  color: var(--text-muted);
  margin: 0 0 30px;
}

.quick-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.quick-btn {
  padding: 12px 20px;
  border: 1px solid var(--card-border);
  border-radius: 20px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-main);
  transition: all 0.2s;
}

.quick-btn:hover {
  background: #fff0f6;
  border-color: #ff9acb;
  transform: translateY(-2px);
}

/* 消息样式 */
.message {
  display: flex;
  gap: 16px;
  padding: 24px 0;
  border-bottom: 1px solid rgba(255, 214, 232, 0.5);
}

.message:last-child {
  border-bottom: none;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.message.user .avatar {
  background: linear-gradient(135deg, #ff9acb, #ffd6e8);
}

.message.assistant .avatar {
  background: linear-gradient(135deg, #ffe9f1, #fff6fb);
  border: 1px solid var(--card-border);
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  margin-bottom: 6px;
}

.role-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-main);
}

.message-body p {
  margin: 0;
  line-height: 1.7;
  color: var(--text-main);
  white-space: pre-wrap;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 8px;
}

.image-grid img {
  width: 100%;
  border-radius: 12px;
  border: 1px solid var(--card-border);
}

/* 加载动画 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #ff9acb;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 输入区域 */
.input-area {
  padding: 16px 20px 20px;
  background: linear-gradient(to top, rgba(255, 246, 251, 0.95), transparent);
}

.input-container {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border: 1px solid var(--card-border);
  border-radius: 24px;
  box-shadow: 0 4px 20px rgba(235, 64, 120, 0.08);
}

.input-container textarea {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  font-size: 15px;
  line-height: 1.5;
  color: var(--text-main);
  background: transparent;
  max-height: 200px;
  padding: 4px 0;
}

.input-container textarea::placeholder {
  color: var(--text-muted);
}

.send-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff9acb, #ffd6e8);
  color: var(--btn-text);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(235, 64, 120, 0.3);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top-color: var(--btn-text);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-msg {
  max-width: 800px;
  margin: 8px auto 0;
  color: #dc2626;
  font-size: 13px;
  text-align: center;
}

.disclaimer {
  max-width: 800px;
  margin: 8px auto 0;
  color: var(--text-muted);
  font-size: 12px;
  text-align: center;
}

/* 响应式 */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 60px;
    height: calc(100vh - 60px);
    z-index: 100;
    transform: translateX(-100%);
  }

  .sidebar:not(.collapsed) {
    transform: translateX(0);
  }

  .chat-main {
    width: 100%;
  }

  .mode-tabs {
    display: none;
  }

  .quick-actions {
    flex-direction: column;
  }
}
</style>
