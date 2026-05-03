<template>
  <nav class="nav-bar">
    <div class="nav-menu">
      <!--一级菜单-->
      <template v-for="item in userStore.currentMenus" :key="item.path||item.name">
        <!--无子菜单-->
        <router-link 
          v-if="!item.children" 
          :to="item.path"
          class="nav-item"
          active-class="nav-item-active"
        >
          {{ item.name }}
        </router-link>
        <!--有子菜单-->
        <div v-else class="nav-dropdown">
          <span class="nav-item" :class="{'nav-item-active':isActive(item)}">
            {{ item.name }}
            <svg class="arrow" viewBox="0 0 24 24" width="14" height="14">
              <path d="M7 10l5 5 5-5" fill="none" stroke="currentColor" stroke-width="2"/>
            </svg>
          </span>
          <div class="dropdown-menu">
            <router-link
              v-for="child in item.children"
              :key="child.path"
              :to="child.path"
              class="dropdown-item"
            >
              {{ child.name }}
            </router-link>
          </div>
        </div>
      </template>
      
    </div>
  </nav>
</template>

<script setup>
import { useUserStore } from '@/stores/user';
import { useRoute } from 'vue-router';
const userStore=useUserStore()
const route=useRoute()
const isActive = (item) => {
  if (!item.children) return false
  return item.children.some(child => route.path === child.path)
}
</script>

<style scoped>
.nav-menu {
  display: flex;
  gap: 4px;
  align-items: center;
}

.nav-item {
  padding: 10px 12px;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  font-size: 22px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.25s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  line-height: normal;
  position: relative;
}

.nav-item:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.12);
}

.nav-item-active {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.2);
  font-weight: 600;
}

/* 下拉箭头 */
.arrow {
  transition: transform 0.25s ease;
  opacity: 0.7;
}

.nav-dropdown:hover .arrow {
  transform: rotate(180deg);
  opacity: 1;
}

/* 下拉菜单容器 */
.nav-dropdown {
  position: relative;
}

/* 下拉菜单 */
.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%) scale(0.95);
  transform-origin: top center;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12), 0 2px 6px rgba(0, 0, 0, 0.08);
  min-width: 160px;
  padding: 8px;
  z-index: 200;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 小三角指示器 */
.dropdown-menu::before {
  content: '';
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-bottom: 6px solid #ffffff;
}

.nav-dropdown:hover .dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) scale(1);
}

/* 下拉项 */
.dropdown-item {
  display: block;
  padding: 10px 16px;
  color: #333;
  text-decoration: none;
  font-size: 15px;
  font-weight: 400;
  border-radius: 8px;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.dropdown-item:hover {
  background: #f0f5ff;
  color: #2a6aff;
}

.dropdown-item.router-link-active {
  background: #e8f0fe;
  color: #1a73e8;
  font-weight: 500;
}

</style>