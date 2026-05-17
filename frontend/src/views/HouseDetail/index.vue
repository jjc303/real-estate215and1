<template>
    <div class="house-detail">
        <!-- 标题区域（放在最上方） -->
        <div class="title-section">
            <h1 class="house-title">{{ house.title }}</h1>
        </div>

        <!-- 主内容区：左侧图片，右侧信息 -->
        <div class="main-section">
            <!-- 左侧图片区 -->
            <div class="gallery-section">
                <div class="gallery-main">
                    <img 
                        :src="house.images?.length ? house.images[currentImgIndex] : defaultImg" 
                        alt="房源主图"
                        @error="$event.target.src = defaultImg"
                    />
                </div>
                <div class="gallery-thumbs">
                    <div 
                        v-for="(img, index) in (house.images || [])" 
                        :key="index"
                        class="thumb-item"
                        :class="{ active: currentImgIndex === index }"
                        @click="currentImgIndex = index"
                    >
                        <img :src="img" :alt="`图片${index + 1}`" />
                    </div>
                </div>
            </div>

            <!-- 右侧信息区 -->
            <div class="info-section">
                <div class="house-price">
                    <span class="price-value">{{ house.price }}</span>
                    <span class="price-unit">元/月</span>
                </div>
                <div class="house-meta">
                    <div class="meta-item">
                        <span class="meta-label">位置</span>
                        <span class="meta-value">{{ house.district }} · {{ house.businessArea }}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">户型</span>
                        <span class="meta-value">{{ house.room }}{{ house.hall }}厅 · {{ house.area }}㎡</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">朝向</span>
                        <span class="meta-value">{{ house.orientation }}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">楼层</span>
                        <span class="meta-value">{{ house.floor }}层 / 共{{ house.totalFloor }}层</span>
                    </div>
                </div>
                <div class="house-tags">
                    <span v-for="tag in (house.tags || [])" :key="tag" class="tag">{{ tag }}</span>
                </div>
                <div class="info-actions">
                    <button class="btn btn-primary chat-btn" @click="openChat">
                        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        </svg>
                        联系房东
                    </button>
                    <button 
                        class="btn btn-outline collect-btn" 
                        :class="{ active: house.isCollect }"
                        @click="handleCollect"
                    >
                        {{ house.isCollect ? '★ 已收藏' : '☆ 收藏' }}
                    </button>
                </div>
            </div>
        </div>

        <!-- 房源详情描述 -->
        <div class="detail-section">
            <h2 class="section-title">房源描述</h2>
            <div class="detail-content">
                {{ house.description || '暂无详细描述' }}
            </div>
        </div>

        <!-- 房源参数 -->
        <div class="params-section">
            <h2 class="section-title">房源参数</h2>
            <div class="params-grid">
                <div class="param-item">
                    <span class="param-label">建筑面积</span>
                    <span class="param-value">{{ house.area }}㎡</span>
                </div>
                <div class="param-item">
                    <span class="param-label">户型</span>
                    <span class="param-value">{{ house.room }}室{{ house.hall }}厅{{ house.toilet }}卫</span>
                </div>
                <div class="param-item">
                    <span class="param-label">朝向</span>
                    <span class="param-value">{{ house.orientation }}</span>
                </div>
                <div class="param-item">
                    <span class="param-label">楼层</span>
                    <span class="param-value">{{ house.floor }}层 / 共{{ house.totalFloor }}层</span>
                </div>
                <div class="param-item">
                    <span class="param-label">装修</span>
                    <span class="param-value">{{ house.decoration }}</span>
                </div>
                <div class="param-item">
                    <span class="param-label">电梯</span>
                    <span class="param-value">{{ house.elevator ? '有' : '无' }}</span>
                </div>
                <div class="param-item">
                    <span class="param-label">租金</span>
                    <span class="param-value">{{ house.price }}元/月</span>
                </div>
                <div class="param-item">
                    <span class="param-label">付款方式</span>
                    <span class="param-value">{{ house.payment }}</span>
                </div>
            </div>
        </div>

        <!-- 聊天弹窗 -->
        <ChatPopup 
            :visible="showChat" 
            :house-id="house.id"
            @update:visible="showChat = $event" 
        />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user.js';
import { ElMessage } from 'element-plus';
import ChatPopup from '@/components/ChatPopup.vue';
import defaultImg from '@/assets/images/default-house.png';
import { mockHouses } from '@/mock/houseList';

const route = useRoute();
const userStore = useUserStore();

const house = ref({});
const currentImgIndex = ref(0);
const showChat = ref(false);

const handleCollect = () => {
    if (!userStore.token) {
        ElMessage.warning('请先登录');
        return;
    }
    house.value.isCollect = !house.value.isCollect;
    // 后续接入收藏接口
};

const openChat = () => {
    if (!userStore.token) {
        ElMessage.warning('请先登录');
        return;
    }
    showChat.value = true;
};

const fetchHouseDetail = async () => {
    const houseId = parseInt(route.params.id);
    // 模拟获取房源详情
    const foundHouse = mockHouses.find(h => h.id === houseId);
    if (foundHouse) {
        house.value = {
            ...foundHouse,
            // 保留原始图片数据，不覆盖
            isCollect: false,
            hall: 1,
            toilet: 1,
            totalFloor: 28,
            decoration: '精装修',
            payment: '押一付三'
        };
    } else {
        house.value = {
            id: houseId,
            title: '房源不存在',
            price: 0,
            district: '',
            businessArea: '',
            area: 0,
            room: 0,
            orientation: '',
            floor: 0,
            description: '',
            images: [],
            tags: []
        };
    }
};

onMounted(() => {
    fetchHouseDetail();
});
</script>

<style scoped>
.house-detail {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* 标题区域 */
.title-section {
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid #eee;
}

.house-title {
    font-size: 24px;
    font-weight: 600;
    color: #333;
    line-height: 1.4;
    margin: 0;
}

/* 主内容区 - 左右布局 */
.main-section {
    display: flex;
    gap: 30px;
    margin-bottom: 30px;
}

/* 左侧图片区 */
.gallery-section {
    width: 500px;
    flex-shrink: 0;
}

.gallery-main {
    width: 100%;
    height: 320px;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.gallery-main img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.gallery-thumbs {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding-bottom: 4px;
}

.gallery-thumbs::-webkit-scrollbar {
    height: 4px;
}

.gallery-thumbs::-webkit-scrollbar-thumb {
    background: #ddd;
    border-radius: 2px;
}

.thumb-item {
    width: 70px;
    height: 52px;
    border-radius: 6px;
    overflow: hidden;
    cursor: pointer;
    border: 2px solid transparent;
    transition: all 0.2s;
    flex-shrink: 0;
}

.thumb-item.active {
    border-color: #006cd8;
}

.thumb-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.thumb-item:hover {
    border-color: #006cd8;
}

/* 右侧信息区 */
.info-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 30px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.house-price {
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid #eee;
}

.price-value {
    font-size: 32px;
    font-weight: 700;
    color: #f56c6c;
}

.price-unit {
    font-size: 14px;
    color: #f56c6c;
    margin-left: 4px;
}

.house-meta {
    margin-bottom: 12px;
}

.meta-item {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
}

.meta-label {
    width: 50px;
    font-size: 13px;
    color: #999;
    flex-shrink: 0;
}

.meta-value {
    font-size: 13px;
    color: #333;
}

.house-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 16px;
}

.tag {
    padding: 3px 10px;
    background: #e8f4fd;
    color: #006cd8;
    border-radius: 4px;
    font-size: 12px;
}

.info-actions {
    display: flex;
    gap: 10px;
    margin-top: auto;
    padding-top: 16px;
}

.btn {
    padding: 10px 24px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 6px;
    border: none;
}

.btn-primary {
    background: linear-gradient(135deg, #006cd8 0%, #0088ff 100%);
    color: #fff;
}

.btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 10px rgba(0, 108, 216, 0.3);
}

.btn-outline {
    background: #fff;
    color: #666;
    border: 1px solid #ddd;
}

.btn-outline:hover {
    border-color: #006cd8;
    color: #006cd8;
}

.btn-outline.active {
    background: #006cd8;
    color: #fff;
    border-color: #006cd8;
}

.btn-icon {
    width: 20px;
    height: 20px;
}

/* 详情描述 */
.detail-section,
.params-section {
    background: #fff;
    border-radius: 12px;
    padding: 30px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    margin-bottom: 30px;
}

.section-title {
    font-size: 20px;
    font-weight: 600;
    color: #333;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid #f0f0f0;
}

.detail-content {
    font-size: 15px;
    line-height: 1.8;
    color: #666;
}

/* 参数网格 */
.params-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
}

.param-item {
    display: flex;
    flex-direction: column;
    padding: 15px;
    background: #fafafa;
    border-radius: 8px;
}

.param-label {
    font-size: 13px;
    color: #999;
    margin-bottom: 8px;
}

.param-value {
    font-size: 15px;
    font-weight: 500;
    color: #333;
}

@media (max-width: 768px) {
    .info-section {
        flex-direction: column;
        gap: 20px;
    }

    .info-actions {
        align-items: stretch;
    }

    .params-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .gallery-main {
        height: 280px;
    }
}
</style>