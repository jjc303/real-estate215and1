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
          <!-- 错误提示 -->
          <Transition name="fade">
            <div v-if="showError" class="error-toast">
              <i class="fa-solid fa-circle-exclamation"></i>
              <span>{{ errorMessage }}</span>
            </div>
          </Transition>
          
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
                    <span class="chat-time">{{ formatRelativeTime(item.time) }}</span>
                  </div>
                </div>
                <div v-if="item.unread > 0" class="unread-badge">{{ item.unread }}</div>
              </div>
            </div>
          </div>

          <div class="chat-main">
            <div class="chat-header" v-if="selectedChat">
              <div class="header-info">
                <span class="user-name">{{ selectedChat.userName }}</span>
              </div>
            </div>

            <!-- 空状态 -->
            <div v-if="!selectedChat" class="empty-state">
              <div class="empty-icon">
                <i class="fa-solid fa-comments"></i>
              </div>
              <p class="empty-title">开始沟通房源详情</p>
              <p class="empty-desc">选择一个对话，与租客交流租房事宜</p>
            </div>

            <div ref="messagesContainer" class="chat-messages" v-if="selectedChat">
              <div v-for="(msg, index) in currentMessages" :key="index" class="message-item">
                <div :class="['message-bubble', { 'is-mine': msg.isMine }]">
                  {{ msg.content }}
                </div>
                <span :class="['message-time', { 'is-mine': msg.isMine }]">{{ formatRelativeTime(msg.time) }}</span>
              </div>
            </div>

            <!-- 优化后的输入框区域 -->
            <div class="chat-input-area" v-if="selectedChat">
              <!-- 快捷短语栏 -->
              <div class="quick-phrases">
                <span 
                  v-for="phrase in currentQuickPhrases" 
                  :key="phrase"
                  class="phrase-tag"
                  @click="insertPhrase(phrase)"
                >
                  {{ phrase }}
                </span>
              </div>
              
              <div class="input-wrapper">
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
import { ref, computed, nextTick, watch } from 'vue';
import { 
  getConversationList, 
  getMessageList, 
  sendMessage as sendMessageApi, 
  markAsRead,
  createConversation 
} from '@/api/conversation';

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  houseId: {
    type: Number,
    default: null
  }
});

const emit = defineEmits(['update:visible']);

const searchKeyword = ref('');
const selectedChatId = ref(null);
const messageInput = ref('');
const messagesContainer = ref(null);
const errorMessage = ref('');
const showError = ref(false);
const loading = ref(false);
const messagesLoading = ref(false);

// 当前用户信息（从 localStorage 获取）
const currentUser = ref(null);
try {
  currentUser.value = JSON.parse(localStorage.getItem('userInfo') || 'null');
} catch (e) {
  currentUser.value = null;
}

const formatRelativeTime = (timeStr) => {
  if (!timeStr) return '';
  
  if (timeStr.includes('昨天') || timeStr.includes('前天')) {
    return timeStr;
  }
  
  try {
    const date = new Date(timeStr);
    if (isNaN(date.getTime())) {
      return timeStr;
    }
    
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    
    if (diffMinutes < 1) {
      return '刚刚';
    } else if (diffMinutes < 60) {
      return `${diffMinutes}分钟前`;
    } else if (diffMinutes < 1440) {
      const hoursAgo = Math.floor(diffMinutes / 60);
      return `${hoursAgo}小时前`;
    } else if (diffMinutes < 43200) {
      const daysAgo = Math.floor(diffMinutes / 1440);
      return `${daysAgo}天前`;
    } else {
      return date.toLocaleDateString('zh-CN');
    }
  } catch (e) {
    return timeStr;
  }
};

const showErrorMessage = (msg) => {
  errorMessage.value = msg;
  showError.value = true;
  setTimeout(() => {
    showError.value = false;
  }, 3000);
};

// 房东快捷短语（租客发给房东）
const landlordPhrases = [
  '房源还在',
  '随时可看房',
  '价格可谈',
  '请留下联系方式',
  '押一付三',
  '精装修拎包入住'
];

// 租客快捷短语（房东发给租客）
const tenantPhrases = [
  '请问租金多少',
  '可以押一付一吗',
  '能短租吗',
  '有中介费吗',
  '什么时候能看房',
  '包物业费吗'
];

const currentQuickPhrases = computed(() => {
  if (!selectedChat.value || !currentUser.value) return [];
  
  // 当前用户是租客，发给房东的快捷短语
  if (currentUser.value.role === 'tenant') {
    return landlordPhrases;
  }
  // 当前用户是房东，发给租客的快捷短语
  return tenantPhrases;
});

const chatList = ref([]);
const currentMessages = ref([]);

const filteredChatList = computed(() => {
  if (!searchKeyword.value) return chatList.value;
  return chatList.value.filter(item => 
    item.userName.includes(searchKeyword.value) ||
    (item.lastMessage && item.lastMessage.includes(searchKeyword.value)) ||
    (item.house && item.house.title && item.house.title.includes(searchKeyword.value))
  );
});

const selectedChat = computed(() => {
  return chatList.value.find(item => item.id === selectedChatId.value);
});

// 获取会话列表
const loadConversationList = async () => {
  loading.value = true;
  try {
    const res = await getConversationList();
    if (res.code === 0 && res.data) {
      const list = res.data.list || [];
      chatList.value = list.map(item => ({
        id: item.id,
        userName: getOtherPartyName(item),
        lastMessage: item.last_message ? item.last_message.content : '',
        time: item.last_message_at,
        unread: item.unread_count || 0,
        tenantId: item.tenant_id,
        landlordId: item.landlord_id,
        houseId: item.house_id,
        house: item.house
      }));
      
      // 如果有传入 houseId，自动找到或创建对应的会话
      if (props.houseId && chatList.value.length > 0) {
        const existingChat = chatList.value.find(c => c.houseId === props.houseId);
        if (existingChat) {
          selectChat(existingChat);
        }
      }
    } else {
      showErrorMessage(res.message || '获取会话列表失败');
    }
  } catch (error) {
    console.error('获取会话列表失败:', error);
    showErrorMessage('网络异常，无法获取会话列表');
  } finally {
    loading.value = false;
  }
};

// 获取对方名称
const getOtherPartyName = (conversation) => {
  if (!currentUser.value) return '未知用户';
  
  if (currentUser.value.role === 'tenant') {
    // 当前用户是租客，显示房东信息
    return conversation.landlord_name || conversation.house?.landlord_name || '房东';
  } else {
    // 当前用户是房东，显示租客信息
    return conversation.tenant_name || '租客';
  }
};

// 获取消息列表
const loadMessages = async (conversationId) => {
  messagesLoading.value = true;
  try {
    const res = await getMessageList(conversationId);
    if (res.code === 0 && res.data) {
      const list = res.data.list || [];
      currentMessages.value = list.map(msg => ({
        id: msg.id,
        content: msg.content,
        time: msg.created_at,
        isMine: msg.sender_id === currentUser.value?.id
      }));
      
      // 标记已读
      await markAsRead(conversationId);
      
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
        }
      });
    } else {
      showErrorMessage(res.message || '获取消息失败');
    }
  } catch (error) {
    console.error('获取消息失败:', error);
    showErrorMessage('网络异常，无法获取消息');
  } finally {
    messagesLoading.value = false;
  }
};

// 选择会话
const selectChat = async (item) => {
  selectedChatId.value = item.id;
  
  // 更新本地未读计数
  item.unread = 0;
  
  // 加载消息
  await loadMessages(item.id);
};

// 创建会话并选择
const createAndSelectChat = async (houseId) => {
  loading.value = true;
  try {
    console.log('创建会话 - houseId:', houseId);
    console.log('创建会话 - token:', localStorage.getItem('token')?.substring(0, 20) + '...');
    
    const res = await createConversation(houseId);
    console.log('创建会话 - 响应:', res);
    
    if (res.code === 0 && res.data) {
      // 重新加载会话列表
      await loadConversationList();
    } else {
      showErrorMessage(res.message || '创建会话失败');
    }
  } catch (error) {
    console.error('创建会话失败 - 错误详情:', error);
    console.error('创建会话失败 - 响应数据:', error.response?.data);
    console.error('创建会话失败 - HTTP状态:', error.response?.status);
    
    const errorMsg = error.response?.data?.message || 
                     error.response?.data?.msg ||
                     error.message || 
                     '网络异常，无法创建会话';
    showErrorMessage(errorMsg);
  } finally {
    loading.value = false;
  }
};

// 插入快捷短语
const insertPhrase = (phrase) => {
  messageInput.value = phrase;
};

// 自动调整textarea高度
const autoResize = (e) => {
  const textarea = e.target;
  textarea.style.height = 'auto';
  textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
};

// 处理回车
const handleEnter = (e) => {
  if (!e.shiftKey) {
    sendMessage();
  }
};

// 发送消息
const sendMessage = async () => {
  if (!selectedChat.value) {
    showErrorMessage('请先选择一个对话');
    return;
  }
  
  const trimmedMessage = messageInput.value.trim();
  
  if (!trimmedMessage) {
    showErrorMessage('消息内容不能为空');
    return;
  }
  
  if (trimmedMessage.length > 1000) {
    showErrorMessage('消息内容不能超过1000个字符');
    return;
  }
  
  loading.value = true;
  try {
    const res = await sendMessageApi(selectedChat.value.id, trimmedMessage);
    if (res.code === 0 && res.data) {
      // 添加到本地消息列表
      currentMessages.value.push({
        id: res.data.id,
        content: trimmedMessage,
        time: res.data.created_at,
        isMine: true
      });
      
      messageInput.value = '';
      
      // 更新会话列表中的最后消息
      const chatIndex = chatList.value.findIndex(c => c.id === selectedChat.value.id);
      if (chatIndex !== -1) {
        chatList.value[chatIndex].lastMessage = trimmedMessage;
        chatList.value[chatIndex].time = res.data.created_at;
      }
      
      nextTick(() => {
        const textarea = document.querySelector('.input-box textarea');
        if (textarea) textarea.style.height = 'auto';
        
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
        }
      });
    } else {
      showErrorMessage(res.message || '发送消息失败');
    }
  } catch (error) {
    console.error('发送消息失败:', error);
    showErrorMessage('网络异常，无法发送消息');
  } finally {
    loading.value = false;
  }
};

// 关闭弹窗
const close = () => {
  emit('update:visible', false);
};

// 监听 visible 变化，加载会话列表
watch(() => props.visible, async (val) => {
  if (val) {
    await loadConversationList();
    
    // 如果传入了 houseId 且没有找到现有会话，创建新会话
    if (props.houseId) {
      const existingChat = chatList.value.find(c => c.houseId === props.houseId);
      if (!existingChat) {
        await createAndSelectChat(props.houseId);
      }
    }
  }
});
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
  width: 80%;
  max-width: 750px;
  height: 85vh;
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
  position: relative;
}

/* 错误提示 */
.error-toast {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: #ffffff;
  padding: 12px 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4);
  z-index: 100;
  animation: slideDown 0.3s ease;
}

.error-toast i {
  font-size: 16px;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
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

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
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