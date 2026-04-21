<template>
  <nav class="nav-bar">
    <div class="nav-menu">
      <router-link 
        v-for="item in items" 
        :key="item.path || item.name"
        :to="item.path"
        class="nav-item"
        active-class="nav-item-active"
      >
        {{ item.name }}
      </router-link>
    </div>
  </nav>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => [
      { name: '首页', path: '/' },
      { name: '房源列表', path: '/houses' },
      { name: '我要租房', path: '/rent' },
      { name: '消息', path: '/messages' },
      { name: '投诉维修', path: '/complaints' },
      { name: '关于我们', path: '/about' }
    ]
  }
})
</script>

<style scoped>
.nav-menu {
  display: flex;
  gap: 10px;
}

.nav-item {
  padding: 8px 18px;
  color: white;
  text-decoration: none;
  font-size: 22px;
  font-weight: 500;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.nav-item:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.15);
}

.nav-item-active {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.25);
  font-weight: 500;
}
</style>