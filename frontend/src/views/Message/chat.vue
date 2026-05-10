<template>
  <div class="message-chat-page">
    <div class="page-header">
      <h1>留言管理</h1>
      <p class="subtitle">查看和处理用户留言消息</p>
    </div>

    <div class="chat-container">
      <div class="chat-sidebar">
        <div class="search-box">
          <el-input v-model="searchKeyword" placeholder="搜索留言..." clearable>
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
            <div class="chat-avatar">{{ item.avatar || 'U' }}</div>
            <div class="chat-info">
              <div class="chat-top">
                <span class="chat-name">{{ item.userName }}</span>
                <span class="chat-time">{{ item.time }}</span>
              </div>
              <div class="chat-preview">{{ item.lastMessage }}</div>
            </div>
            <div v-if="item.unread > 0" class="unread-badge">{{ item.unread }}</div>
          </div>
        </div>
      </div>

      <div class="chat-main">
        <div class="chat-header">
          <span v-if="selectedChat">{{ selectedChat.userName }}</span>
          <span v-else class="placeholder-text">选择一个对话开始查看</span>
        </div>

        <div class="chat-messages" v-if="selectedChat">
          <div v-for="msg in currentMessages" :key="msg.id" :class="['message-item', msg.type]">
            <div class="message-avatar">{{ msg.type === 'other' ? selectedChat.avatar || 'U' : '我' }}</div>
            <div class="message-content">
              <p>{{ msg.content }}</p>
              <span class="message-time">{{ msg.time }}</span>
            </div>
          </div>
        </div>

        <div v-if="selectedChat" class="chat-input-area">
          <el-input 
            v-model="newMessage" 
            type="textarea" 
            :rows="3" 
            placeholder="输入回复消息..."
          ></el-input>
          <div class="send-btn-wrap">
            <el-button type="primary" @click="sendMessage">
              <i class="fa-solid fa-paper-plane"></i> 发送
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const searchKeyword = ref('')
const selectedChatId = ref(null)
const selectedChat = ref(null)
const newMessage = ref('')

const chatList = ref([
  {
    id: 1,
    userName: '张三',
    avatar: '张',
    lastMessage: '您好，请问这套房源还在吗？',
    time: '10:30',
    unread: 2,
    messages: [
      { id: 101, type: 'other', content: '您好，请问这套房源还在吗？', time: '10:25' },
      { id: 102, type: 'me', content: '您好，房源还在的，随时可以预约看房~', time: '10:27' },
      { id: 103, type: 'other', content: '好的，那我明天上午过去看看可以吗？', time: '10:30' }
    ]
  },
  {
    id: 2,
    userName: '李四',
    avatar: '李',
    lastMessage: '预约看房时间可以改到下午3点吗？',
    time: '昨天',
    unread: 0,
    messages: [
      { id: 201, type: 'other', content: '你好，昨天和您约的上午10点看房', time: '昨天 09:30' },
      { id: 202, type: 'me', content: '没问题，房源我已经准备好了', time: '昨天 09:35' },
      { id: 203, type: 'other', content: '不好意思，临时有点事，可以改到下午3点吗？', time: '昨天 10:00' }
    ]
  },
  {
    id: 3,
    userName: '王五',
    avatar: '王',
    lastMessage: '合同相关问题咨询',
    time: '3天前',
    unread: 1,
    messages: [
      { id: 301, type: 'other', content: '你好，我在合同里看到第6条有点疑问', time: '3天前 14:20' },
      { id: 302, type: 'me', content: '您好，请问是哪一条不理解呢？', time: '3天前 14:25' },
      { id: 303, type: 'other', content: '关于租金支付的时间节点，想确认一下', time: '3天前 14:30' }
    ]
  }
])

const currentMessages = ref([])

const selectChat = (item) => {
  selectedChatId.value = item.id
  selectedChat.value = item
  currentMessages.value = item.messages
  item.unread = 0
}

const sendMessage = () => {
  if (!newMessage.value.trim()) {
    ElMessage.warning('请输入消息内容')
    return
  }
  if (!selectedChat.value) return
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
  const newMsg = {
    id: Date.now(),
    type: 'me',
    content: newMessage.value,
    time: time
  }
  currentMessages.value.push(newMsg)
  selectedChat.value.lastMessage = newMessage.value
  newMessage.value = ''
  ElMessage.success('消息已发送')
}

onMounted(() => {
  if (chatList.value.length > 0) {
    selectChat(chatList.value[0])
  }
})
</script>

<style scoped>
.message-chat-page {
  width: 100%;
  height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
}

.page-header {
  margin: 0 0 16px;
  padding: 0;
  display: flex;
  justify-content: space-between;
  align-items:end;
  flex-shrink: 0;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 6px;
}

.subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.chat-container {
  width: 100%;
  flex: 1;
  display: flex;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(25, 118, 210, 0.08);
  overflow: hidden;
}

.chat-sidebar {
  width: 260px;
  border-right: 1px solid #f0f2f5;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.search-box {
  padding: 14px;
  border-bottom: 1px solid #f0f2f5;
  flex-shrink: 0;
}

.search-box :deep(.el-input__wrapper) {
  border-radius: 24px;
  background: #f7f8fa;
  box-shadow: none;
}

.chat-list {
  overflow-y: auto;
  flex: 1;
}

.chat-list::-webkit-scrollbar {
  width: 6px;
}

.chat-list::-webkit-scrollbar-thumb {
  background: #e0e0e0;
  border-radius: 3px;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.chat-item:hover {
  background: #f7f8fa;
}

.chat-item.active {
  background: linear-gradient(90deg, #e8f0fe 0%, #f7f8fa 100%);
  border-left: 3px solid #1976d2;
}

.chat-avatar {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  background: linear-gradient(135deg, #1976d2 0%, #64b5f6 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 17px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(25, 118, 210, 0.15);
}

.chat-info {
  flex: 1;
  min-width: 0;
}

.chat-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.chat-name {
  font-weight: 600;
  font-size: 15px;
  color: #1a1a2e;
}

.chat-time {
  font-size: 12px;
  color: #a0a0a0;
}

.chat-preview {
  font-size: 13px;
  color: #888;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
}

.unread-badge {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  background: linear-gradient(135deg, #f44336 0%, #ff6b6b 100%);
  color: white;
  font-size: 11px;
  font-weight: 700;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #fafbfc;
}

.chat-header {
  padding: 18px 28px;
  border-bottom: 1px solid #f0f2f5;
  font-weight: 700;
  font-size: 16px;
  color: #1a1a2e;
  background: white;
}

.placeholder-text {
  color: #999;
  font-weight: 400;
}

.chat-messages {
  flex: 1;
  padding: 24px 28px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
  background: #fafbfc;
}

.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #e0e0e0;
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.message-item {
  display: flex;
  gap: 12px;
}

.message-item.other {
  justify-content: flex-start;
}

.message-item.me {
  justify-content: flex-end;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: white;
}

.message-item.other .message-avatar {
  background: linear-gradient(135deg, #90a4ae 0%, #78909c 100%);
}

.message-item.me .message-avatar {
  display: none;
}

.message-content {
  max-width: 60%;
  padding: 14px 18px;
  border-radius: 18px;
  position: relative;
  word-break: break-word;
}

.message-item.other .message-content {
  background: white;
  color: #2c3e50;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.message-item.me .message-content {
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
  color: white;
  border-bottom-right-radius: 4px;
  box-shadow: 0 2px 10px rgba(25, 118, 210, 0.25);
}

.message-content p {
  margin: 0;
  line-height: 1.65;
  font-size: 15px;
}

.message-time {
  font-size: 11px;
  opacity: 0.75;
  display: block;
  text-align: right;
  margin-top: 6px;
}

.chat-input-area {
  padding: 18px 28px;
  border-top: 1px solid #f0f2f5;
  background: white;
}

.send-btn-wrap {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.send-btn-wrap .el-button {
  border-radius: 24px;
  padding-left: 28px;
  padding-right: 28px;
  height: 40px;
  font-weight: 600;
}
</style>
