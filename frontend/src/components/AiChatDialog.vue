<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    width="520px"
    top="8vh"
    :close-on-click-modal="true"
    destroy-on-close
    class="ai-chat-dialog"
  >
    <template #header>
      <div class="ai-chat-header">
        <div class="ai-avatar">
          <i class="fa-solid fa-robot"></i>
        </div>
        <div class="ai-info">
          <span class="ai-title">AI 智能助手</span>
          <span class="ai-status">{{ houseId ? '正在了解此房源' : '随时为您解答' }}</span>
        </div>
      </div>
    </template>

    <div class="ai-chat-body" ref="chatBodyRef">
      <div v-if="messages.length === 0" class="ai-welcome">
        <div class="welcome-icon">
          <i class="fa-solid fa-comments"></i>
        </div>
        <p class="welcome-text">
          {{ houseId ? '关于这套房源，您想了解什么？' : '有什么可以帮您的？' }}
        </p>
        <div class="quick-questions">
          <button
            v-for="q in quickQuestions"
            :key="q"
            class="quick-btn"
            @click="sendMessage(q)"
          >
            {{ q }}
          </button>
        </div>
      </div>

      <div v-else class="message-list">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message-item', msg.role]"
        >
          <div class="message-avatar">
            <i v-if="msg.role === 'user'" class="fa-solid fa-user"></i>
            <i v-else class="fa-solid fa-robot"></i>
          </div>
          <div class="message-content">
            <div class="message-text">{{ msg.content }}</div>
            <div class="message-time">{{ msg.time }}</div>
          </div>
        </div>

        <div v-if="loading" class="message-item assistant loading">
          <div class="message-avatar">
            <i class="fa-solid fa-robot"></i>
          </div>
          <div class="message-content">
            <div class="message-text">
              <i class="fa-solid fa-spinner fa-spin"></i> AI 思考中...
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="ai-chat-input">
      <div class="input-wrapper">
        <el-input
          v-model="inputText"
          :placeholder="houseId ? '问问AI关于这套房源的问题...' : '输入您的问题...'"
          @keyup.enter="handleSend"
          :disabled="loading"
        />
        <button 
          class="send-btn" 
          @click="handleSend" 
          :disabled="loading || !inputText.trim()"
        >
          <i class="fa-solid fa-paper-plane"></i>
        </button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { houseChat, chat } from '@/api/ai.js'

const props = defineProps({
  visible: Boolean,
  houseId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['update:visible'])

const inputText = ref('')
const loading = ref(false)
const messages = ref([])
const chatBodyRef = ref(null)
const sessionId = ref(null)

const quickQuestions = computed(() => {
  if (props.houseId) {
    // 房源专属助手
    return [
      '这套房源的详细信息',
      '租金可以优惠吗',
      '周边配套怎么样',
      '最短租期多久'
    ]
  } else {
    // 通用租房助手
    return [
      '如何发布房源',
      '租房流程是什么',
      '押金如何计算',
      '合同怎么签'
    ]
  }
})

const formatTime = (date) => {
  const h = date.getHours().toString().padStart(2, '0')
  const m = date.getMinutes().toString().padStart(2, '0')
  return `${h}:${m}`
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatBodyRef.value) {
      chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
    }
  })
}

const sendMessage = async (text) => {
  if (!text.trim() || loading.value) return

  inputText.value = text
  loading.value = true

  messages.value.push({
    role: 'user',
    content: text,
    time: formatTime(new Date())
  })
  scrollToBottom()

  try {
    const payload = {
      message: text,
      session_id: sessionId.value
    }

    let res
    if (props.houseId) {
      payload.house_id = props.houseId
      res = await houseChat(payload)
    } else {
      res = await chat(payload)
    }

    if (res.code === 0) {
      sessionId.value = res.data.session_id
      messages.value.push({
        role: 'assistant',
        content: res.data.answer,
        time: formatTime(new Date())
      })
    } else {
      ElMessage.error(res.message || 'AI 回复失败')
    }
  } catch (e) {
    ElMessage.error('AI 服务暂时不可用')
  } finally {
    loading.value = false
    inputText.value = ''
    scrollToBottom()
  }
}

const handleSend = () => {
  sendMessage(inputText.value)
}

watch(() => props.visible, (val) => {
  if (!val) {
    inputText.value = ''
    loading.value = false
  }
})
</script>

<style scoped>
.ai-chat-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
}

.ai-info {
  display: flex;
  flex-direction: column;
}

.ai-title {
  font-weight: 600;
  font-size: 16px;
}

.ai-status {
  font-size: 12px;
  color: #999;
}

.ai-chat-body {
  height: 400px;
  overflow-y: auto;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 16px;
}

.ai-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.welcome-icon {
  font-size: 48px;
  color: #667eea;
  margin-bottom: 16px;
}

.welcome-text {
  color: #666;
  margin-bottom: 20px;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.quick-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 20px;
  background: #fff;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  gap: 10px;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}

.message-item.user .message-avatar {
  background: #667eea;
  color: #fff;
}

.message-item.assistant .message-avatar {
  background: #f0f0f0;
  color: #667eea;
}

.message-content {
  max-width: 75%;
}

.message-text {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
}

.message-item.user .message-text {
  background: #667eea;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.message-item.assistant .message-text {
  background: #fff;
  color: #333;
  border-bottom-left-radius: 4px;
}

.message-time {
  font-size: 11px;
  color: #aaa;
  margin-top: 4px;
  padding: 0 4px;
}

.message-item.user .message-time {
  text-align: right;
}

.ai-chat-input {
  position: relative;
}

.ai-chat-input .input-wrapper {
  position: relative;
}

.ai-chat-input :deep(.el-input__wrapper) {
  border-radius: 24px !important;
  border: 1px solid #e0e0e0;
  box-shadow: none;
  transition: all 0.2s;
  padding-right: 56px !important;
}

.ai-chat-input :deep(.el-input__wrapper:hover) {
  border-color: #667eea;
}

.ai-chat-input :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.ai-chat-input .send-btn {
  position: absolute;
  right: 4px;
  top: 50%;
  transform: translateY(-50%);
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.ai-chat-input .send-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a6fd6 0%, #6b4190 100%);
  transform: translateY(-50%) scale(1.05);
}

.ai-chat-input .send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  opacity: 0.5;
}

.ai-chat-input .send-btn i {
  margin-left: 1px;
}
</style>
