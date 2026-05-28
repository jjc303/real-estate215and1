<template>
  <div class="houselist-root">
    <div class="title">
        <div class="img-wrap">
            <img src="@/assets/images/csu-logo.png" alt="中南大学logo" class="csu-logo" />
            <img src="@/assets/images/csu-name.png" alt="中南大学logo" class="csu-name" />
        </div>
        <div class="searchBar-wrap">
            <SearchBar/>
        </div>
    </div>
    <div class="filter-area">
        <!--面包屑导航-->
        <div class="breadcrumb-nav">
            <!--自动生成路由层级-->
            <template v-for="(item,idx) in route.matched" :key="item.path">
                <router-link :to="item.path" class="breadcrumb-link">
                    {{ item.meta?.title }}
                </router-link>
                <span v-if="idx < route.matched.length-1" class="breadcrumb-divider">></span>
            </template>
            
            <!--动态追加筛选条件-->
            <template v-if="selectedDistrict&&selectedDistrict!=='不限'">
                <span class="breadcrumb-divider">></span>
                <router-link :to="`/houseList?district=${selectedDistrict}`" class="breadcrumb-link">
                    {{ selectedDistrict }}租房
                </router-link>
            </template>
        </div>
        <div class="filter-wrap">
             
            <!--区域筛选-->
            <div class="filter-row">
                <span class="filter-label">区域</span>
                <div class="filter-option">
                    <span
                        v-for="d in districts"
                        :key="d"
                        :class="{active:selectedDistrict===d}"
                        @click="setFilter('district',d)"
                    >
                        {{ d }}
                    </span>
                </div>
                
            </div>
            
            <!--租金筛选-->
             <div class="filter-row">
                <span class="filter-label">租金</span>
                <div class="filter-option">
                    <span
                        v-for="p in prices"
                        :key="p.value"
                        :class="{active:filter.price.includes(p.value)}"
                        @click="setFilter('price',p.value)"
                    >
                        {{ p.label }}
                    </span>
                    <div class="custom-range">
                        <input v-model.number="customPrice.min" type="number" placeholder="最低" class="range-input" min="0" />
                        <span class="range-separator">-</span>
                        <input v-model.number="customPrice.max" type="number" placeholder="最高" class="range-input" min="0" />
                        <button type="button" class="range-confirm" @click="confirmPriceRange">确定</button>
                    </div>
                </div>
            </div>
            <!--面积筛选-->
             <div class="filter-row">
                <span class="filter-label">面积</span>
                <div class="filter-option">
                    <span
                        v-for="a in areas"
                        :key="a.value"
                        :class="{active:filter.area.includes(a.value)}"
                        @click="setFilter('area',a.value)"
                    >
                        {{ a.label }}
                    </span>
                    <div class="custom-range">
                        <input v-model.number="customArea.min" type="number" placeholder="最低" class="range-input" min="0" />
                        <span class="range-separator">-</span>
                        <input v-model.number="customArea.max" type="number" placeholder="最高" class="range-input" min="0" />
                        <button type="button" class="range-confirm" @click="confirmAreaRange">确定</button>
                    </div>
                </div>
            </div>
            <!--户型筛选-->
             <div class="filter-row">
                <span class="filter-label">户型</span>
                <div class="filter-option">
                    <span
                        v-for="r in rooms"
                        :key="r.value"
                        :class="{active:filter.room.includes(r.value)}"
                        @click="setFilter('room',r.value)"
                    >
                        {{ r.label }}
                    </span>
                </div>
            </div>
            <!--朝向筛选-->
             <div class="filter-row">
                <span class="filter-label">朝向</span>
                <div class="filter-option">
                    <span
                        v-for="o in orientations"
                        :key="o"
                        :class="{active:filter.orientation.includes(o)}"
                        @click="setFilter('orientation',o)"
                    >
                        {{ o }}
                    </span>    
                </div>
            </div>
            <div v-show="showMore">
                <!--租期筛选-->
                <div class="filter-row">
                    <span class="filter-label">租期</span>
                    <div class="filter-option">
                        <span
                            v-for="t in times"
                            :key="t"
                            :class="{active:filter.time.includes(t)}"
                            @click="setFilter('time',t)"
                        >
                            {{ t }}
                        </span>    
                    </div>
                </div>
                <!--楼层筛选-->
                <div class="filter-row">
                    <span class="filter-label">楼层</span>
                    <div class="filter-option">
                        <span
                            v-for="f in floors"
                            :key="f"
                            :class="{active:filter.floor.includes(f)}"
                            @click="setFilter('floor',f)"
                        >
                            {{ f }}
                        </span>    
                    </div>
                </div>
                <!--电梯筛选-->
                <div class="filter-row">
                    <span class="filter-label">电梯</span>
                    <div class="filter-option">
                        <span
                            v-for="e in elevators"
                            :key="e"
                            :class="{active:filter.elevator===e}"
                            @click="setFilter('elevator',e)"
                        >
                            {{ e }}
                        </span>    
                    </div>
                </div>
            </div>
            <div class="more-toggle" @click="showMore = !showMore">
                <span class="line"></span>
                {{ showMore ? '收起' : '更多' }}
                <span class="arrow">{{ showMore ? '∧' : '∨' }}</span>
                <span class="line"></span>
            </div>
        </div>
        <div class="filter-result">
            <div class="result-number">
                已找到 <span class="num">{{ total }}</span> 条房源
            </div>
            <div class="filter-empty-btn" @click="clearAllFilter">
                清空所有筛选条件
            </div>
        </div>
    </div>
    <div class="house-content">
        <div class="sort-bar">
            <span 
                v-for="sort in sortList"
                :key="sort.value"
                :class="{active:filter.sort===sort.value||filter.sort.startsWith(sort.value)}"
                @click="setFilter('sort',sort.value)"
            >
                {{ sort.label }}
                <span v-if="sort.value === 'price' && filter.sort.startsWith('price')">
                    {{ filter.sort === 'price_asc' ? '↑' : '↓' }}
                </span>
                <span v-if="sort.value === 'area' && filter.sort.startsWith('area')">
                    {{ filter.sort === 'area_asc' ? '↑' : '↓' }}
                </span>
            </span>   
            
        </div>
        <div class="house-bar-list">
            <HouseBar 
                v-for="item in houseList"
                :key="item.id"
                :house="item"
                @collect="handleCollect"
            />
        </div>
        <!-- 分页控件 -->
        <Pagination
            :pageNum="pageNum"
            :pageSize="pageSize"
            :total="total"
            @change="handlePageChange"
        />
    </div>
  </div>
</template>
<script setup>
import HouseBar from '@/components/HouseBar.vue';
import SearchBar from '@/components/SearchBar.vue';
import { ref,reactive } from 'vue';
import { useUserStore } from '@/stores/user.js';
import { useRoute,useRouter} from 'vue-router';
import { watch } from 'vue';
import { onMounted } from 'vue';
import Pagination from '@/components/Pagination.vue';
import { getHouseList } from '@/api/house.js';
import { getFavoriteList } from '@/api/favorite.js';
import { ElMessage } from 'element-plus';
const userStore = useUserStore();
const route=useRoute();


// 控制更多筛选显示/隐藏
const showMore = ref(false)
//房源总数
const total = ref(0)//房源总数
const pageNum=ref(1)//当前页数
const pageSize=ref(10)//每页条数
const houseList = ref([])//房源信息
const collectedHouseIds = ref(new Set()) // 收藏的房源ID集合
const districts=['不限','雨花区','岳麓区','天心区','开福区','芙蓉区','望城区','宁乡市','浏阳区','长沙县'];
const selectedDistrict=ref('');

const prices = ref([
  { label: '1000以下', value: '1000' },
  { label: '1000-2000', value: '1000-2000' },
  { label: '2000-3000', value: '2000-3000' },
  { label: '5000以上', value: '5000' },
])

const areas = ref([
  { label: '30㎡以下', value: '30' },
  { label: '30-50㎡', value: '30-50' },
  { label: '50-80㎡', value: '50-80' },
  { label: '80-100㎡', value: '80-100' },
  { label: '100㎡以上', value: '100' },
])

// 自定义价格范围
const customPrice = reactive({
  min: null,
  max: null
})

// 自定义面积范围
const customArea = reactive({
  min: null,
  max: null
})

const rooms = ref([
  { label: '一室', value: '1' },
  { label: '二室', value: '2' },
  { label: '三室', value: '3' },
  { label: '四室以上', value: '4+' },
])
const orientations = ref([ '东', '南', '西', '北', '南北'])
const times=ref(['月租','年租'])
const floors=ref(['低楼层','中楼层','高楼层'])
const elevators=ref(['有电梯','无电梯'])
const sortList=ref([
    { label: '综合排序', value: 'default' },
    { label: '价格', value: 'price' },
    { label: '面积', value: 'area' }
])
const filterConfig = {
  district: 'single',       // 区域 单选
  price: 'multiple',    // 租金 多选
  area: 'multiple',     // 面积 多选
  room: 'multiple',     // 户型 多选
  orientation: 'multiple', // 朝向 多选
  time:'multiple',//租期多选
  floor:'multiple',//楼层多选
  elevator:'single',//电梯单选
  sort: 'single' //
}
const filter = reactive({
  district: '',
  elevator:'',
  price: [],
  area: [],
  room: [],
  orientation: [],
  time:[],
  floor:[],
  sort: 'default', //排序方式
  min_rent: null,
  max_rent: null,
  min_area: null,
  max_area: null
})

const setFilter=(key,value)=>{
    if(key=='sort'){
        if(value === 'price'){
            filter.sort = filter.sort === 'price_asc' ? 'price_desc' : 'price_asc'
        } else if(value === 'area'){
            filter.sort = filter.sort === 'area_asc' ? 'area_desc' : 'area_asc'
         } else {
            filter.sort = value
        }
        // 排序改变后重新获取数据并排序
        fetchHouseList()
        return
    }
    const type = filterConfig[key]
    if(type==='single'){
         filter[key] = filter[key] === value ? '' : value
    }
    else if(type==='multiple'){
        let arr=filter[key]
        if(arr.includes(value)){
            filter[key]=arr.filter(i=>i!==value)//取消
        }else{
            filter[key].push(value)//选中
        }
    }
    
    // 筛选条件改变，重置到第一页
    pageNum.value = 1
    fetchHouseList()
}

// 确认自定义价格范围
const confirmPriceRange = () => {
  if (customPrice.min !== null && customPrice.min !== '') {
    filter.min_rent = customPrice.min
  } else {
    filter.min_rent = null
  }
  if (customPrice.max !== null && customPrice.max !== '') {
    filter.max_rent = customPrice.max
  } else {
    filter.max_rent = null
  }
  
  if (filter.min_rent !== null && filter.max_rent !== null && filter.min_rent > filter.max_rent) {
    ElMessage.warning('最低价格不能大于最高价格')
    return
  }
  
  pageNum.value = 1
  fetchHouseList()
}

// 确认自定义面积范围
const confirmAreaRange = () => {
  if (customArea.min !== null && customArea.min !== '') {
    filter.min_area = customArea.min
  } else {
    filter.min_area = null
  }
  if (customArea.max !== null && customArea.max !== '') {
    filter.max_area = customArea.max
  } else {
    filter.max_area = null
  }
  
  if (filter.min_area !== null && filter.max_area !== null && filter.min_area > filter.max_area) {
    ElMessage.warning('最小面积不能大于最大面积')
    return
  }
  
  pageNum.value = 1
  fetchHouseList()
}

// 清空所有筛选
const clearAllFilter = () => {
  filter.district = ''
  filter.elevator = ''
  filter.price = []
  filter.area = []
  filter.room = []
  filter.orientation = []
  filter.time = []
  filter.floor = []
  filter.sort='default'
  filter.min_rent = null
  filter.max_rent = null
  filter.min_area = null
  filter.max_area = null
  customPrice.min = null
  customPrice.max = null
  customArea.min = null
  customArea.max = null

  pageNum.value = 1
  // 保留搜索关键词，只清空筛选条件
  fetchHouseList()
}

const handleCollect=async(house)=>{
    //登录才能收藏
    if (!userStore.token) {
        userStore.openLoginModal()
        return
    }
    
    try {
        // 导入收藏 API
        const { addFavorite, removeFavorite } = await import('@/api/favorite')
        const houseIdStr = String(house.id)
        
        if (house.isCollect) {
            // 取消收藏
            const res = await removeFavorite(house.id)
            if (res.code === 0) {
                house.isCollect = false
                collectedHouseIds.value.delete(houseIdStr)
                ElMessage.success('已取消收藏')
            } else {
                ElMessage.error(res.message || '取消收藏失败')
            }
        } else {
            // 添加收藏
            const res = await addFavorite(house.id)
            if (res.code === 0) {
                house.isCollect = true
                collectedHouseIds.value.add(houseIdStr)
                ElMessage.success('收藏成功')
            } else {
                ElMessage.error(res.message || '收藏失败')
            }
        }
    } catch (error) {
        console.error('收藏操作失败:', error)
        ElMessage.error('收藏失败，请重试')
    }
}

// 加载用户收藏列表
const loadCollectedHouses = async () => {
    if (!userStore.token) {
        collectedHouseIds.value.clear()
        return
    }
    try {
        const res = await getFavoriteList()
        if (res && res.data) {
            // 确保 res.data 是数组
            const dataArray = Array.isArray(res.data) ? res.data : (res.data.list || res.data.items || [])
            // 使用字符串类型确保一致性，将house_id或id转为字符串
            collectedHouseIds.value = new Set(dataArray.map(item => String(item.house_id || item.id)))
        }
    } catch (error) {
        console.error('加载收藏列表失败:', error)
    }
}

/*const fetchHouseList=async()=>{
    const params={
        ...filter,//平铺filter
        pageNum:pageNum.value,
        pageSize:pageSize.value
    }

    //后端请求
    //axios.get

    // 模拟后端返回格式
    const res = {
        code: 200,
        data: {
        list: [],     // 当前页房源
        total: 0      // 数据总条数
        }
    }
    // 赋值
    houseList.value = res.data.list
    total.value = res.data.total
}*/

const fetchHouseList=async()=>{
    try {
        // 从 URL 查询参数中获取搜索关键词
        const searchKeyword = route.query.keyword || '';
        
        // 处理租金范围 - 支持多选
        let minRent = filter.min_rent;
        let maxRent = filter.max_rent;
        
        // 处理选中的租金区间（支持多选）
        if (filter.price.length > 0) {
            let minValues = [];
            let maxValues = [];
            
            filter.price.forEach(priceRange => {
                if (priceRange === '1000') {
                    minValues.push(0);
                    maxValues.push(1000);
                } else if (priceRange === '1000-2000') {
                    minValues.push(1000);
                    maxValues.push(2000);
                } else if (priceRange === '2000-3000') {
                    minValues.push(2000);
                    maxValues.push(3000);
                } else if (priceRange === '5000') {
                    minValues.push(5000);
                    maxValues.push(null); // 无上限
                }
            });
            
            // 取所有区间的最小值和最大值
            minRent = Math.min(...minValues);
            // 如果有 null（表示无上限），则 maxRent 为 null，否则取最大值
            maxRent = maxValues.includes(null) ? null : Math.max(...maxValues);
        }
        
        // 处理面积范围 - 支持多选
        let minArea = filter.min_area;
        let maxArea = filter.max_area;
        
        // 处理选中的面积区间（支持多选）
        if (filter.area.length > 0) {
            let minValues = [];
            let maxValues = [];
            
            filter.area.forEach(areaRange => {
                if (areaRange === '30') {
                    minValues.push(0);
                    maxValues.push(30);
                } else if (areaRange === '30-50') {
                    minValues.push(30);
                    maxValues.push(50);
                } else if (areaRange === '50-80') {
                    minValues.push(50);
                    maxValues.push(80);
                } else if (areaRange === '80-100') {
                    minValues.push(80);
                    maxValues.push(100);
                } else if (areaRange === '100') {
                    minValues.push(100);
                    maxValues.push(null); // 无上限
                }
            });
            
            // 取所有区间的最小值和最大值
            minArea = Math.min(...minValues);
            // 如果有 null（表示无上限），则 maxArea 为 null，否则取最大值
            maxArea = maxValues.includes(null) ? null : Math.max(...maxValues);
        }
        
        // 处理户型
        let houseType = undefined;
        if (filter.room.length > 0) {
            // 将选中的户型合并，如"1,2,3"
            houseType = filter.room.map(r => {
                if (r === '1') return '一室';
                if (r === '2') return '二室';
                if (r === '3') return '三室';
                if (r === '4+') return '四室';
                return r;
            }).join(',');
        }
        
        const params = {
            page: pageNum.value,
            page_size: pageSize.value,
            region: filter.district || undefined,
            house_type: houseType,
            min_rent: minRent,
            max_rent: maxRent,
            min_area: minArea,
            max_area: maxArea,
            keyword: searchKeyword || undefined
        }
        
        // 移除 undefined 值
        Object.keys(params).forEach(key => {
            if (params[key] === undefined || params[key] === null || params[key] === '') {
                delete params[key];
            }
        });
        
        console.log('===== 房源列表请求参数 =====');
        console.log('请求参数:', params);
        console.log('搜索关键词:', searchKeyword);
        console.log('URL query:', route.query);
        console.log('区域:', filter.district);
        console.log('租金区间:', filter.price);
        console.log('面积区间:', filter.area);
        console.log('户型:', filter.room);
        console.log('min_rent:', minRent, 'max_rent:', maxRent);
        console.log('min_area:', minArea, 'max_area:', maxArea);
        console.log('自定义价格:', customPrice);
        console.log('自定义面积:', customArea);
        
        const res = await getHouseList(params)
        
        console.log('===== 房源列表响应 =====');
        console.log('响应数据:', res);
        console.log('房源数量:', res.data?.list?.length);
        console.log('总条数:', res.data?.total);
        
        if (res.code === 0) {
            console.log('===== 房源数据详情 =====');
            if (res.data.list && res.data.list.length > 0) {
                console.log('第一条房源数据:', res.data.list[0]);
                console.log('第一条房源 region:', res.data.list[0].region);
            }
            
            // 先映射数据
            let mappedList = res.data.list.map(house => ({
                id: house.id,
                title: house.title || '无',
                district: house.region || '无',
                businessArea: house.community || '无',
                area: parseFloat(house.area) || 0,
                room: house.house_type || '无',
                orientation: house.orientation || '无',
                price: parseFloat(house.rent) || 0,
                deposit: parseFloat(house.deposit) || 0,
                images: house.images || [],
                cover_image_url: house.cover_image_url || null,
                tags: [],
                updateTime: house.updated_at || '',
                isCollect: collectedHouseIds.value.has(String(house.id)),
                floor: house.floor || '无',
                decoration: house.decoration || '无',
                description: house.description || '无',
                status: house.status || '无',
                address: house.address || '无'
            }))
            
            // 前端排序
            if (filter.sort === 'price_asc') {
                mappedList.sort((a, b) => a.price - b.price)
            } else if (filter.sort === 'price_desc') {
                mappedList.sort((a, b) => b.price - a.price)
            } else if (filter.sort === 'area_asc') {
                mappedList.sort((a, b) => a.area - b.area)
            } else if (filter.sort === 'area_desc') {
                mappedList.sort((a, b) => b.area - a.area)
            }
            
            houseList.value = mappedList
            total.value = res.data.total
        } else {
            ElMessage.error(res.message || '获取房源列表失败')
        }
    } catch (error) {
        ElMessage.error('获取房源列表失败')
        console.error(error)
    }
}
// 翻页
const handlePageChange = (page) => {
  pageNum.value = page
  fetchHouseList()
}

watch(()=>filter.district,(val)=>{
    selectedDistrict.value=val||'不限'
},{immediate:true})
watch(filter, () => {
  // fetchHouseList()
}, { deep: true })

// 监听 URL 搜索关键词变化
watch(() => route.query.keyword, () => {
  pageNum.value = 1
  fetchHouseList()
})

onMounted(async () => {
  await loadCollectedHouses()
  fetchHouseList()
})

</script>

<style scoped>
.title{
    background: linear-gradient(160deg, #1e293b 0%, #334155 60%, #475569 100%);
    display: flex;
    height: 170px;
    flex-direction: column;
    padding:0 140px;
}
.csu-logo {
    height: 60px;
    object-fit: contain;
}
.csu-name {
    height: 40px;
    background: transparent;
    object-fit: contain;
}
.img-wrap{
    flex:1;
    display: flex;
    align-items: center;
    margin-top: 20px;
}
.searchBar-wrap{
    flex: 1;
    display: flex;
    align-items: center;
    margin-bottom:20px;
}
.filter-area{
    padding:0 140px;
    background: #ffffff;
    border-radius: 12px 12px 0 0;
    margin: -12px 140px 0 140px;
    padding: 20px 24px;
    box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.04);
}
.breadcrumb-nav{
    display: flex;
    align-items: center;
    font-size: 14px;
    color: #666;
    margin: 16px 0;
    gap: 6px;
}
.breadcrumb-link{
    color: #666;
    text-decoration: none;
}
.breadcrumb-link:hover {
    color: #006cd8;
}
.breadcrumb-divider{
    color:#999;
}
.filter-area{
    display: flex;
    flex-direction: column;
    justify-content: left;
}
.filter-row{
    display: flex;
    gap:20px;
    align-items: center;
    margin-bottom: 12px;
}
.filter-label{
    width: 50px;
    font-size: 16px;
    font-weight: 700;
    color: #333;
}
.filter-label:hover{
    color: #006cd8;
}
.filter-option{
    display: flex;
    flex-wrap: wrap;
    gap: 30px;
}
.filter-option span {
  cursor: pointer;
  color: #666;
}
.filter-option span.active {
  color: #006cd8;
  font-weight: bold;
}
.custom-range {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 10px;
}
.range-input {
  width: 70px;
  height: 28px;
  padding: 0 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
}
.range-input:focus {
  border-color: #006cd8;
}
.range-separator {
  color: #999;
}
.range-confirm {
  height: 28px;
  padding: 0 12px;
  border: none;
  border-radius: 4px;
  background-color: #006cd8;
  color: white;
  font-size: 14px;
  cursor: pointer;
}
.range-confirm:hover {
  background-color: #0056b3;
}
.more-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 16px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
}

.more-toggle:hover {
  color: #006cd8;
}

.more-toggle .line {
  flex: 1;
  height: 1px;
  background-color: #eee;
}

.more-toggle .text {
  white-space: nowrap;
}

.more-toggle .arrow {
  font-size: 12px;
}
.filter-result {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
  
}
.result-number {
  font-size: 18px;
  font-weight: 700;
  
}
.result-number .num {
  color: #006cd8;
  font-weight: bold;
  margin: 0 4px;
}
.filter-empty-btn {
  padding: 6px 14px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}
.filter-empty-btn:hover {
  border-color: #006cd8;
  color: #006cd8;
}
.house-content{
    padding:0 140px;
    margin-top: 20px;
}
.sort-bar {
  display: flex;
  gap: 50px;
  border-bottom: 1px solid #eee;
}
.sort-bar span {
  cursor: pointer;
  color: #666;
  padding:10px 0;
  gap:0px;
}
.sort-bar span.active {
  color: #006cd8;
  font-weight: bold;
  border-bottom: 2px solid #006cd8;
}

</style>