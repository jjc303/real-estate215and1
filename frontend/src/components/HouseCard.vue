<template>
  <div class="house-card" @click="$emit('click',house)">
    <div class="house-img">
        <img :src="house.image || getHouseImage(house.images, 0, house.id)" :alt="house.title" @error="$event.target.src = getDefaultHouseImage(house.id)"/>
        <div class="badge" v-if="house.badge">{{ house.badge }}</div>
    </div>
    <div class="house-info">
      <h3 class="house-title">{{ house.title }}</h3>
      <div class="house-details">
        <span class="house-spec">{{ house.spec }}</span>
        <span class="house-price">{{ house.price }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { getHouseImage, getDefaultHouseImage } from '@/utils/tools.js'

defineProps({
  house: {
    type: Object,
    required: true,
  }
})
defineEmits(['click'])
</script>   
<style scoped>
.house-card {
  cursor: pointer;
  flex: 1;
}
.house-img {
  position: relative;
  width: 100%;
  height: 240px;
  border-radius:8px;
  overflow: hidden;
}
.house-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.badge {
  position: absolute;
  top: 12px;
  left: 0px;
  background-color:#e73a3a;
  color: #fff;
  padding: 4px 12px;
  border-radius:0 4px  4px 0;
  font-size: 14px;
}
.house-info {
  margin-top: 12px;
}
.house-title {
  font-size: 20px;
  font-weight: bold;
  color:#111;
  line-height: 1.4;
  margin:0 0 8px;
}
.house-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
}
.house-spec {
  font-size: 16px;
  color:#666;
}
.house-price {
  font-size: 22px;
  color:#ff5a5f;
  font-weight: 700;
}
</style>
