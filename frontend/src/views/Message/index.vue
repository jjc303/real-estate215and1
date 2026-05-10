<template>
  <div class="message-layout">
    <div class="message-inner">
      <div class="message-sidebar">
        <div class="sidebar-title">消息中心</div>
        <div class="sidebar-menu">
          <div 
            v-for="item in menuItems" 
            :key="item.key"
            :class="['menu-item', { active: activeTab === item.key }]"
            @click="handleMenuClick(item.key)"
          >
            <i :class="item.icon"></i>
            <span>{{ item.label }}</span>
          </div>
        </div>
      </div>
      <div class="message-content">
        <router-view />
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user.js'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const activeTab = ref('chat')

const menuItems = computed(() => {
  return [
    { key: 'chat', label: '留言管理', icon: 'fa-solid fa-comments' },
    { key: 'news', label: userStore.userRole === 'admin' ? '新闻管理' : '新闻查看', icon: 'fa-solid fa-newspaper' }
  ]
})

const handleMenuClick = (key) => {
  router.push(`/message/${key}`)
}

onMounted(() => {
  const path = route.path
  if (path.includes('/news')) {
    activeTab.value = 'news'
  } else if (path.includes('/chat')) {
    activeTab.value = 'chat'
  }
})

watch(() => route.path, (newPath) => {
  if (newPath.includes('/news')) {
    activeTab.value = 'news'
  } else if (newPath.includes('/chat')) {
    activeTab.value = 'chat'
  }
})
</script>
<style scoped>
.message-layout {
  width: 100vw;
  min-height: calc(100vh - 140px);
  background: linear-gradient(180deg, #eceef1 0%, #f5f7fa 100%);
  position: relative;
  left: 50%;
  right: 50%;
  margin-left: -50vw;
  margin-right: -50vw;
}

.message-inner {
  display: flex;
  padding: 20px 12px;
  gap: 20px;
  max-width: 1300px;
  margin: 0 auto;
}

.message-sidebar {
  width: 180px;
  background: white;
  border-radius: 20px;
  padding: 20px 0;
  flex-shrink: 0;
  box-shadow: 0 4px 20px rgba(25, 118, 210, 0.08);
}

.sidebar-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a2e;
  padding: 0 16px 16px;
  border-bottom: 1px solid #f0f0f0;
  margin-bottom: 12px;
}

.sidebar-menu {
  padding: 0 10px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 12px;
  border-radius: 12px;
  color: #555;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
}

.menu-item:hover {
  background: #f5f7fa;
  color: #1976d2;
}

.menu-item.active {
  background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
  color: white;
}

.message-content {
  flex: 1;
  min-width: 0;
}
</style>
