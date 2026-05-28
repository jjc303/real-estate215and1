<template>
  <div class="home-root">
    <div class="page-wrap">
    <!-- 首页主体内容 -->
    <div class="home-container">
        <div class="home-header">
            <img src="@/assets/images/csu-logo.png" alt="中南大学logo" class="csu-logo" />
            <img src="@/assets/images/csu-name.png" alt="中南大学logo" class="csu-name" />
            <div class="home-nav-wrap">
                <NavBar />
            </div>
            <div class="home-user">
              <UserButton />
            </div>
        </div>
        <div class="home-content">
          <div class="title-small">一席定境，一生从容</div>
          <div class="title-large">来中南找房寻找真正的家</div>
          <div class="home-searchBar">
              <SearchBar />
          </div>
        </div>
    </div>
  </div>
  <!-- 分类展区 -->
  <div class="sort-area">
    <div class="sort-item">
      <div class="sort-title-wrap">
        <div class="sort-big-title">户型多多</div>
        <div class="sort-small-title">一屋一形制，一生一归处</div>
      </div>
      <div class="sort-content">
        <!-- 这里可以放一些户型的图片或者介绍 -->
         <HouseCard 
            v-for="house in houseTypes" 
            :key="house.id" 
            :house="house"
            @click="goToDetail(house)"
          />
      </div>
    </div>
    <div class="sort-item">
      <div class="sort-title-wrap">
        <div class="sort-big-title">小区精选</div>
        <div class="sort-small-title">甄选一城佳境，安享一隅清欢</div>
      </div>
      <div class="sort-content">
        <!-- 这里可以放一些户型的图片或者介绍 -->
         <HouseCard 
            v-for="house in houseEstates" 
            :key="house.id" 
            :house="house"
            @click="goToDetail(house)"
          />
      </div>
    </div>
  </div>
  </div>
</template>

<script setup>
import HouseCard from '@/components/HouseCard.vue';
import NavBar from '@/components/NavBar.vue';
import SearchBar from '@/components/SearchBar.vue';
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import UserButton from '@/components/UserButton.vue';
import { useUserStore } from '@/stores/user.js';
import { getHouseList } from '@/api/house.js';
import { getDefaultHouseImage } from '@/utils/tools.js';

const router = useRouter();
const userStore = useUserStore();

// 两个区域的房源数据
const houseTypes = ref([]);
const houseEstates = ref([]);

// 点击跳转详情
const goToDetail = (house) => {
  router.push(`/houseDetail/${house.id}`)
}

// 数据映射函数：将API数据转为卡片格式
const mapHouseToCard = (house, index) => {
  return {
    id: house.id,
    title: house.title || '未知房源',
    image: house.images?.[0] || null,
    spec: `${house.area || 0}㎡ | ${house.house_type || '未知户型'}`,
    price: `¥${house.price || 0}/月`,
    badge: index === 0 ? '精选' : (index === 1 ? '推荐' : (index === 2 ? '热销' : ''))
  }
}

// 加载户型专区房源（按户型分组）
const loadHouseTypes = async () => {
  try {
    // 获取足够多的房源进行分组
    const res = await getHouseList({ 
      page: 1, 
      page_size: 20 
    });
    
    if (res && res.data && res.data.items) {
      const houses = res.data.items;
      
      // 按户型分组，每个户型取1个
      const typeGroups = {};
      houses.forEach(house => {
        const typeMatch = house.house_type?.match(/(\d)室/);
        const type = typeMatch ? `${typeMatch[1]}室` : '其他';
        if (!typeGroups[type]) {
          typeGroups[type] = house;
        }
      });
      
      // 取前4种户型
      const types = Object.keys(typeGroups).slice(0, 4);
      houseTypes.value = types.map((type, index) => {
        const house = typeGroups[type];
        return {
          ...mapHouseToCard(house, index),
          title: type,  // 户型标题如"一室"、"两室"
          spec: `${house.area || 0}㎡ | ${house.house_type || type}`,
          badge: index === 0 ? '热销' : (index === 1 ? '特价' : (index === 2 ? '推荐' : '新上'))
        };
      });
      
      console.log('户型专区数据:', houseTypes.value);
    }
  } catch (error) {
    console.error('加载户型房源失败', error);
  }
}

// 加载小区精选房源（按区域分组）
const loadHouseEstates = async () => {
  try {
    // 获取足够多的房源进行分组
    const res = await getHouseList({ 
      page: 1, 
      page_size: 20 
    });
    
    if (res && res.data && res.data.items) {
      const houses = res.data.items;
      
      // 按区域分组，每个区域取1个
      const regionGroups = {};
      houses.forEach(house => {
        const region = house.region || house.district || '其他';
        if (!regionGroups[region]) {
          regionGroups[region] = house;
        }
      });
      
      // 取前4个区域
      const regions = Object.keys(regionGroups).slice(0, 4);
      houseEstates.value = regions.map((region, index) => {
        const house = regionGroups[region];
        return {
          ...mapHouseToCard(house, index),
          title: house.title || region,
          spec: region  // 显示区域名
        };
      });
      
      console.log('小区精选数据:', houseEstates.value);
    }
  } catch (error) {
    console.error('加载小区房源失败', error);
  }
}

// 统一加载所有数据
const loadAllHouses = async () => {
  await Promise.all([
    loadHouseTypes(),
    loadHouseEstates()
  ]);
}

// 页面加载时获取数据
onMounted(() => {
  loadAllHouses();
});
</script>

<style>
/* 全局清除浏览器默认白边 */
* {
  margin: 0 ;
  padding: 0 ;
  box-sizing: border-box;
}
</style>
<style scoped>

.home-container {
  width: 1488px;
  height: 600px;
  margin: 0;
  padding: 0;
  background-image: url('@/assets/images/home.jpg');
  background-size: cover;
  background-position: 50% 68%;
  background-repeat: no-repeat;
  position: relative;
}

.csu-logo {
  position: absolute;
  top: 32px;
  left: 230px;
  height: 80px;
  object-fit: contain;
}

.csu-name {
  position: absolute;
  top: 44px;
  left: 310px;
  height: 50px;
  background: transparent;
  object-fit: contain;
}
.home-header {
  position: relative;
  height: 120px;
}
.home-nav-wrap {
  position: absolute;
  top: 40px;       /* 上下位置 */
  left: 460px;     /* 左右位置 */
  z-index: 100;    /* 保证在最上面 */

}
.home-user {
  position: absolute;
  top: 45px;
  right: 40px;
  display: flex;
  gap: 0px;
  align-items: center;
}
.home-content {
  position: absolute;
  top: 50%;
  left: 70%;
  transform: translate(-50%, -50%);
  text-align: left;
  color: #fff;
  width: 600px;
}
.title-small {
  font-size: 32px;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 400;
  letter-spacing: 2px;
  font-family: "Helvetica Neue", "PingFang SC", sans-serif;
  text-transform: uppercase; /* 可选，让文字更规整 */
}

.title-large {
  font-size: 52px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 3px;
  font-family: "Helvetica Neue", "PingFang SC", sans-serif;
  text-shadow: 0 3px 12px rgba(0, 0, 0, 0.25);
  line-height: 1.2;
  white-space: nowrap;
}
.home-searchBar {
  margin-top: 30px;
}

.sort-area {
  display: flex;
  width:1272px;
  flex-direction:column;
  gap: 90px;
  margin:90px  100px;
}
.sort-item {
  height: 400px;
  border-radius: 10px;
}
.sort-big-title {
  font-size: 40px;
  font-weight: 600;
  color: #333;
  text-align: left;
}
.sort-small-title {
  font-size: 18px;
  color: rgba(51, 51, 51, 0.7);
  text-align: left;
}
.sort-content {
  margin-top: 30px;
  display: flex;
  gap: 20px;
  align-items: stretch;
}
</style>