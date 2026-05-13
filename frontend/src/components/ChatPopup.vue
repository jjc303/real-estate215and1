<template>
  <Teleport to="body">
    <div v-if="visible" class="chat-popup-overlay" @click.self="close">
      <div class="chat-popup">
        <div class="chat-popup-header">
          <h3 class="popup-title">消息中心</h3>
          <button class="close-btn" @click="close">
            <i class="fa-solid fa-x"></i>
          </button>
        </div>
        
        <div class="chat-popup-body">
          <div class="chat-sidebar">
            <div class="search-box">
              <el-input v-model="searchKeyword" placeholder="搜索租客或房源..." clearable size="small">
                <template #prefix>
                  <i class="fa-solid fa-magnifying-glass"></i>
                </template>
              </el-input>
            </div>
            <div class="chat-list">
              <div 
                v-for="item in chatList" 
                :key="item.id"
                :class="['chat-item', { active: selectedChatId === item.id }]"
                @click="selectChat(item)"
              >
                <div class="chat-avatar">
                  <i class="fa-solid fa-user"></i>
                </div>
                <div class="chat-info">
                  <div class="chat-top">
                    <span class="chat-name">{{ item.userName }}</span>
                  </div>
                  <div class="chat-preview">{{ item.lastMessage }}</div>
                  <div class="chat-bottom">
                    <span class="chat-time">{{ item.time }}</span>
                  </div>
                </div>
                <div v-if="item.unread > 0" class="unread-badge">{{ item.unread }}</div>
              </div>
            </div>
          </div>

          <div class="chat-main">
            <div class="chat-header">
              <template v-if="selectedChat">
                <div class="header-info">
                  <span class="user-name">{{ selectedChat.userName }}</span>
                </div>
              </template>
              <template v-else>
                <div class="empty-header">
                  <div class="empty-icon">
                    <i class="fa-solid fa-comments"></i>
                  </div>
                  <p class="empty-title">开始沟通房源详情</p>
                  <p class="empty-desc">选择一个对话，与租客交流租房事宜</p>
                </div>
              </template>
            </div>

            <div ref="messagesContainer" class="chat-messages" v-if="selectedChat">
              <div v-for="(msg, index) in currentMessages" :key="index" class="message-item">
                <div :class="['message-bubble', { 'is-mine': msg.isMine }]">
                  {{ msg.content }}
                </div>
                <span :class="['message-time', { 'is-mine': msg.isMine }]">{{ msg.time }}</span>
              </div>
            </div>

            <!-- 优化后的输入框区域 -->
            <div class="chat-input-area" v-if="selectedChat">
              <!-- 快捷短语栏 -->
              <div class="quick-phrases">
                <span 
                  v-for="phrase in quickPhrases" 
                  :key="phrase"
                  class="phrase-tag"
                  @click="insertPhrase(phrase)"
                >
                  {{ phrase }}
                </span>
              </div>
              
              <div class="input-wrapper">
                <div class="input-actions">
                  <button class="action-btn" title="表情">
                    <i class="fa-regular fa-face-smile"></i>
                  </button>
                  <button class="action-btn" title="图片">
                    <i class="fa-regular fa-image"></i>
                  </button>
                </div>
                
                <div class="input-box">
                  <textarea
                    v-model="messageInput"
                    placeholder="输入消息..."
                    rows="1"
                    @input="autoResize"
                    @keydown.enter.prevent="handleEnter"
                  ></textarea>
                </div>
                
                <button 
                  class="send-btn" 
                  :class="{ 'can-send': messageInput.trim() }"
                  @click="sendMessage"
                >
                  <i class="fa-solid fa-paper-plane"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue';

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:visible']);

const searchKeyword = ref('');
const selectedChatId = ref(null);
const messageInput = ref('');
const messagesContainer = ref(null);

// 快捷短语
const quickPhrases = ref([
  '房源还在',
  '随时可看房',
  '价格可谈',
  '请留下联系方式'
]);

const chatList = ref([
  { id: 1, userName: '张三', lastMessage: '您好，请问房子还在吗？', time: '10:30', unread: 2 },
  { id: 2, userName: '李四', lastMessage: '我想预约看房', time: '昨天', unread: 0 },
  { id: 3, userName: '王五', lastMessage: '租金可以便宜点吗？', time: '09:15', unread: 1 },
]);

const currentMessages = ref([
  { id: 1, content: '您好，请问房子还在吗？', time: '10:25', isMine: false },
  { id: 2, content: '在的，您什么时候方便看房？', time: '10:26', isMine: true },
  { id: 3, content: '周末可以吗？', time: '10:28', isMine: false },
  { id: 4, content: '可以的，周六下午2点怎么样？', time: '10:30', isMine: true },
]);

const filteredChatList = computed(() => {
  if (!searchKeyword.value) return chatList.value;
  return chatList.value.filter(item => 
    item.userName.includes(searchKeyword.value) ||
    item.lastMessage.includes(searchKeyword.value)
  );
});

const selectedChat = computed(() => {
  return chatList.value.find(item => item.id === selectedChatId.value);
});

const selectChat = (item) => {
  selectedChatId.value = item.id;
  item.unread = 0;
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

const insertPhrase = (phrase) => {
  messageInput.value = phrase;
};

const autoResize = (e) => {
  const textarea = e.target;
  textarea.style.height = 'auto';
  textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
};

const handleEnter = (e) => {
  if (!e.shiftKey) {
    sendMessage();
  }
};

const sendMessage = () => {
  if (!messageInput.value.trim() || !selectedChat.value) return;
  
  currentMessages.value.push({
    id: Date.now(),
    content: messageInput.value,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    isMine: true
  });
  
  messageInput.value = '';
  
  // 重置textarea高度
  nextTick(() => {
    const textarea = document.querySelector('.input-box textarea');
    if (textarea) textarea.style.height = 'auto';
    
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

const close = () => {
  emit('update:visible', false);
};
</script>

<style scoped>
.chat-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.chat-popup {
  width: 90%;
  max-width: 900px;
  height: 75vh;
  background: #ffffff;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.18), 0 10px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

.chat-popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
  box-shadow: 0 2px 10px rgba(56, 189, 248, 0.3);
}

.popup-title {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.popup-title::before {
  content: '';
  width: 4px;
  height: 18px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 2px;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #ffffff;
  transition: all 0.25s ease;
  font-size: 16px;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.35);
  transform: scale(1.05);
}

.chat-popup-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.chat-sidebar {
  width: 300px;
  background: #f8fafc;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
}

.search-box {
  padding: 16px;
}

.search-box :deep(.el-input__wrapper) {
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  transition: all 0.2s ease;
}

.search-box :deep(.el-input__wrapper:hover) {
  border-color: #38bdf8;
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.1);
}

.search-box :deep(.el-input__wrapper.is-focus) {
  border-color: #38bdf8;
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15);
}

.chat-list {
  flex: 1;
  overflow-y: auto;
}

.chat-list::-webkit-scrollbar {
  width: 6px;
}

.chat-list::-webkit-scrollbar-track {
  background: transparent;
}

.chat-list::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.chat-list::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.chat-item {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid #e2e8f0;
  position: relative;
}

.chat-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: transparent;
  transition: background 0.2s ease;
}

.chat-item:hover {
  background: #f1f5f9;
  transform: translateX(2px);
}

.chat-item.active {
  background: #ffffff;
  box-shadow: inset 3px 0 0 #38bdf8;
}

.chat-item.active::before {
  background: #38bdf8;
}

.chat-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7dd3fc 0%, #38bdf8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 14px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(56, 189, 248, 0.3);
}

.chat-avatar i {
  color: #ffffff;
  font-size: 18px;
}

.chat-info {
  flex: 1;
  overflow: hidden;
  min-width: 0;
}

.chat-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-name {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.chat-preview {
  font-size: 13px;
  color: #64748b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 4px;
  line-height: 1.4;
}

.chat-bottom {
  margin-top: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-time {
  font-size: 12px;
  color: #94a3b8;
}

.unread-badge {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: #ffffff;
  font-size: 11px;
  font-weight: 600;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.35);
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #ffffff;
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.empty-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  flex: 1;
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  box-shadow: 0 4px 20px rgba(56, 189, 248, 0.2);
}

.empty-icon i {
  font-size: 36px;
  color: #38bdf8;
}

.empty-title {
  font-size: 18px;
  color: #475569;
  margin: 0 0 8px 0;
  font-weight: 500;
}

.empty-desc {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  background: #f8fafc;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.message-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.message-bubble {
  max-width: 65%;
  padding: 12px 16px;
  border-radius: 20px;
  font-size: 14px;
  line-height: 1.6;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  align-self: flex-start;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.message-bubble:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.message-bubble.is-mine {
  background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
  color: #ffffff;
  border-color: transparent;
  align-self: flex-end;
  box-shadow: 0 2px 12px rgba(56, 189, 248, 0.35);
}

.message-time {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 6px;
  align-self: flex-start;
  padding-left: 8px;
}

.message-time.is-mine {
  align-self: flex-end;
  padding-right: 8px;
  color: rgba(255, 255, 255, 0.7);
}

/* ==================== 优化后的输入框区域 ==================== */
.chat-input-area {
  padding: 12px 20px 16px;
  border-top: 1px solid #e2e8f0;
  background: #ffffff;
}

/* 快捷短语栏 */
.quick-phrases {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.phrase-tag {
  padding: 4px 12px;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 12px;
  font-size: 12px;
  color: #0284c7;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.phrase-tag:hover {
  background: #e0f2fe;
  border-color: #38bdf8;
  color: #0ea5e9;
  transform: translateY(-1px);
}

/* 输入框包装器 */
.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 8px 12px;
  transition: all 0.2s ease;
}

.input-wrapper:focus-within {
  border-color: #38bdf8;
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.12);
  background: #ffffff;
}

/* 左侧操作按钮 */
.input-actions {
  display: flex;
  gap: 6px;
  padding-bottom: 2px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #94a3b8;
  transition: all 0.2s ease;
  font-size: 16px;
}

.action-btn:hover {
  background: #e0f2fe;
  color: #38bdf8;
}

/* 输入框 */
.input-box {
  flex: 1;
}

.input-box textarea {
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  line-height: 1.5;
  color: #1e293b;
  resize: none;
  max-height: 120px;
  padding: 6px 0;
  font-family: inherit;
}

.input-box textarea::placeholder {
  color: #94a3b8;
}

/* 发送按钮 */
.send-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  background: #cbd5e1;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #ffffff;
  transition: all 0.25s ease;
  font-size: 15px;
  flex-shrink: 0;
  margin-bottom: 2px;
}

.send-btn.can-send {
  background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
  box-shadow: 0 2px 8px rgba(56, 189, 248, 0.3);
}

.send-btn.can-send:hover {
  transform: scale(1.08);
  box-shadow: 0 4px 12px rgba(56, 189, 248, 0.4);
}

.send-btn:active {
  transform: scale(0.95);
}
</style>