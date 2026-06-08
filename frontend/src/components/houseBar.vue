<template>
    <div class="house-bar-wrap" @click="goToDetail">
        <!-- 左侧房源图片 -->
        <div class="house-img">
            <img 
              :src="house.cover_image_url || getHouseImage(house.images, 0, house.id)" 
              alt="房源封面" 
              @error="$event.target.src = getDefaultHouseImage(house.id)"
            />
        </div>
        <!-- 中间：房源信息 -->
        <div class="house-info">
            <div class="house-title">{{ house.title }}</div>
            <div class="house-desc">
                {{ house.district }} · {{ house.businessArea }} · {{ house.area }}㎡
                · {{ house.room }} · {{ house.orientation }}
            </div>
            <div class="house-tags">
                <span v-for="tag in house.tags" :key="tag" class="tag">{{ tag }}</span>
                <span v-if="house.status" class="tag status-tag" :class="house.status">{{ statusText(house.status) }}</span>
            </div>
            <div class="house-time">
                {{ house.updateTime }}
            </div>
        </div>
        <!-- 右侧：价格 + 收藏 -->
        <div class="house-right">
            <div class="house-price">
                <span class="price-text">{{ house.price }}</span>
                <span class="unit">元/月</span>
            </div>
            <!-- 收藏按钮 星星样式 -->
            <div
                class="collect-btn"
                :class="{ active: house.isCollect }"
                @click.stop="$emit('collect', house)"
            >
                {{ house.isCollect ? '★ 已收藏' : '☆ 收藏' }}
            </div>
        </div>
    </div>
</template>
<script setup>
import { useRouter } from 'vue-router'
import { getHouseImage, getDefaultHouseImage } from '@/utils/tools.js'

const router = useRouter()

const props = defineProps({
    house:{
        type:Object,
        required:true,
        default:()=>({})
    }
})

defineEmits(['collect'])

const statusText = (status) => {
    const map = {
        draft: '草稿',
        listed: '已上架',
        rented: '已出租',
        offline: '已下架',
        maintenance: '维修中'
    }
    return map[status] || status
}

const goToDetail = () => {
    router.push(`/houseDetail/${props.house.id}`)
}
</script>

<style scoped>
.house-bar-wrap {
  display: flex;
  align-items: stretch;
  gap: 18px;
  padding: 20px 0;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}
.house-bar-wrap:hover {
  background-color: #fafafa;
}

/* 左侧图片 */
.house-img {
  width: 200px;
  height: 140px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}
.house-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 中间信息 */
.house-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 4px 0;
}
.house-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}
.house-desc {
  font-size: 14px;
  color: #666;
  margin: 8px 0;
}
.house-tags {
  display: flex;
  gap: 10px;
}
.tag {
  padding: 2px 10px;
  background: #f5f7fa;
  color: #666;
  border-radius: 4px;
  font-size: 12px;
}
.house-time {
  font-size: 12px;
  color: #999;
}

/* 状态标签 */
.status-tag {
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 3px;
  border: 1px solid;
}
.status-tag.listed {
  color: #52c41a;
  border-color: #52c41a;
  background: #f6ffed;
}
.status-tag.draft {
  color: #faad14;
  border-color: #faad14;
  background: #fffbe6;
}
.status-tag.offline {
  color: #999;
  border-color: #d9d9d9;
  background: #fafafa;
}
.status-tag.rented {
  color: #1890ff;
  border-color: #1890ff;
  background: #e6f7ff;
}
.status-tag.maintenance {
  color: #ff7a45;
  border-color: #ff7a45;
  background: #fff7e6;
}

/* 右侧价格+收藏 */
.house-right {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
  min-width: 110px;
}
.house-price .price-text {
  font-size: 24px;
  color: #f56c6c;
  font-weight: bold;
}
.house-price .unit {
  font-size: 14px;
  color: #f56c6c;
  margin-left: 2px;
}

/* 收藏按钮 */
.collect-btn {
  padding: 3px 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 13px;
  color: #666;
  white-space: nowrap;
  transition: all 0.2s;
}
.collect-btn.active {
  border-color: #006cd8;
  background-color: #006cd8;
  color: #fff;
}
.collect-btn:hover:not(.active) {
  border-color: #006cd8;
  color: #006cd8;
}
</style>
