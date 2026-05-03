<template>
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
            <!--方式筛选-->
            <div class="filter-row">
                <span class="filter-label">方式</span>
                <div class="filter-option">
                    <span
                        v-for="type in rentTypes"
                        :key="type"
                        :class="{active:filter.type===type}"
                        @click="setFilter('type',type)"
                    >
                        {{ type }}
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
        <div class="pagination">
            <button 
                @click="changePage(1)" 
                :disabled="pageNum === 1"
                class="page-btn"
            >
                首页
            </button>
            <button 
                @click="changePage(pageNum-1)" 
                :disabled="pageNum === 1"
                class="page-btn"
            >
                上一页
            </button>
            <span class="page-info">
                第 {{ pageNum }} 页 / 共 {{ Math.ceil(total/pageSize) }} 页
            </span>
            <button 
                @click="changePage(pageNum+1)" 
                :disabled="pageNum >= Math.ceil(total/pageSize)"
                class="page-btn"
            >
                下一页
            </button>
            <button 
                @click="changePage(Math.ceil(total/pageSize))" 
                :disabled="pageNum >= Math.ceil(total/pageSize)"
                class="page-btn"
            >
                尾页
            </button>
        </div>
    </div>
    <LoginModal/>
</template>
<script setup>

import HouseBar from '@/components/HouseBar.vue';
import SearchBar from '@/components/SearchBar.vue';
import { ref,reactive } from 'vue';
import LoginModal from '@/components/LoginModal.vue';
import { useUserStore } from '@/stores/user.js';
import { useRoute,useRouter} from 'vue-router';
import { watch } from 'vue';
import { onMounted } from 'vue';


const userStore = useUserStore();
const route=useRoute();


// 控制更多筛选显示/隐藏
const showMore = ref(false)
//房源总数
const total = ref(0)//房源总数
const pageNum=ref(1)//当前页数
const pageSize=ref(10)//每页条数
const houseList = ref([])//房源信息
const districts=['不限','雨花','岳麓','天心','开福','芙蓉','望城','宁乡市','浏阳','长沙县'];
const selectedDistrict=ref('');
// 租赁方式
const rentTypes = ['不限', '整租', '合租']
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
  type: 'single',       // 方式 单选
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
  type: '',
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
const mockData = [
  { id: 1, title: "中南大学旁精致单间 拎包入住", district: "岳麓", businessArea: "麓谷", area: 35, room: "一室", orientation: "南北", price: 1800, images: ["https://picsum.photos/id/101/800/600"], tags: ["近地铁"], updateTime: "2026-04-25", isCollect: false },
  { id: 2, title: "岳麓山脚下两室一厅", district: "岳麓", businessArea: "大学城", area: 68, room: "二室", orientation: "南", price: 2600, images: ["https://picsum.photos/id/104/800/600"], tags: ["南北通透"], updateTime: "2026-04-23", isCollect: true },
  { id: 3, title: "雨花区精装合租次卧", district: "雨花", businessArea: "红星", area: 28, room: "一室", orientation: "东", price: 1200, images: ["https://picsum.photos/id/106/800/600"], tags: ["合租"], updateTime: "2026-04-20", isCollect: false },
  { id: 4, title: "天心区大三居 适合整租", district: "天心", businessArea: "省政府", area: 95, room: "三室", orientation: "南北", price: 3800, images: ["https://picsum.photos/id/107/800/600"], tags: ["整租"], updateTime: "2026-04-18", isCollect: false },
  { id: 5, title: "开福区单间公寓 独立卫浴", district: "开福", businessArea: "五一广场", area: 32, room: "一室", orientation: "西", price: 1500, images: ["https://picsum.photos/id/109/800/600"], tags: ["近商圈"], updateTime: "2026-04-15", isCollect: true },
  { id: 6, title: "芙蓉区老式两居 性价比高", district: "芙蓉", businessArea: "芙蓉广场", area: 72, room: "二室", orientation: "北", price: 1900, images: ["https://picsum.photos/id/110/800/600"], tags: ["低楼层"], updateTime: "2026-04-12", isCollect: false },
  { id: 7, title: "望城区湖景单间", district: "望城", businessArea: "滨水新城", area: 40, room: "一室", orientation: "南", price: 1000, images: ["https://picsum.photos/id/111/800/600"], tags: ["安静"], updateTime: "2026-04-10", isCollect: false },
  { id: 8, title: "长沙县精装四室", district: "长沙县", businessArea: "星沙", area: 120, room: "四室以上", orientation: "南北", price: 4800, images: ["https://picsum.photos/id/112/800/600"], tags: ["大户型"], updateTime: "2026-04-08", isCollect: false },
  { id: 9, title: "浏阳市温馨小单间", district: "浏阳", businessArea: "经开区", area: 25, room: "一室", orientation: "东", price: 900, images: ["https://picsum.photos/id/114/800/600"], tags: ["低价"], updateTime: "2026-04-05", isCollect: false },
  { id: 10, title: "宁乡市两室一厅 居家装修", district: "宁乡市", businessArea: "市中心", area: 65, room: "二室", orientation: "西", price: 1700, images: ["https://picsum.photos/id/115/800/600"], tags: ["居家"], updateTime: "2026-04-02", isCollect: true },
  { id: 11, title: "岳麓区高校旁合租单间", district: "岳麓", businessArea: "大学城", area: 30, room: "一室", orientation: "南", price: 1350, images: ["https://picsum.photos/id/116/800/600"], tags: ["近学校"], updateTime: "2026-03-30", isCollect: false },
  { id: 12, title: "雨花区高端公寓", district: "雨花", businessArea: "德思勤", area: 45, room: "一室", orientation: "北", price: 2200, images: ["https://picsum.photos/id/117/800/600"], tags: ["高端"], updateTime: "2026-03-28", isCollect: false },
  { id: 13, title: "开福区江景大三室", district: "开福", businessArea: "滨江路", area: 110, room: "三室", orientation: "南北", price: 5200, images: ["https://picsum.photos/id/118/800/600"], tags: ["江景"], updateTime: "2026-03-25", isCollect: false },
  { id: 14, title: "芙蓉区平价单间", district: "芙蓉", businessArea: "火车站", area: 26, room: "一室", orientation: "东", price: 950, images: ["https://picsum.photos/id/119/800/600"], tags: ["便利"], updateTime: "2026-03-22", isCollect: false },
  { id: 15, title: "望城区刚需两居", district: "望城", businessArea: "金星北", area: 62, room: "二室", orientation: "西", price: 1650, images: ["https://picsum.photos/id/120/800/600"], tags: ["实惠"], updateTime: "2026-03-20", isCollect: false },
];
const setFilter=(key,value)=>{
    if(key=='sort'){
        if(value === 'price'){
            filter.sort = filter.sort === 'price_asc' ? 'price_desc' : 'price_asc'
        } else if(value === 'area'){
            filter.sort = filter.sort === 'area_asc' ? 'area_desc' : 'area_asc'
         } else {
            filter.sort = value
        }
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
    //接入接口 调用搜索函数

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
    alert('最低价格不能大于最高价格')
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
    alert('最小面积不能大于最大面积')
    return
  }
  
  pageNum.value = 1
  fetchHouseList()
}

// 清空所有筛选
const clearAllFilter = () => {
  filter.district = ''
  filter.type = ''
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
  fetchHouseList()
}

const handleCollect=async(house)=>{
    //登录才能收藏
    if (!userStore.token) {
        alert('请先登录')
        return
    }
    //接入收藏处理接口
    house.isCollect = !house.isCollect
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

// 只做分页，不做任何模拟筛选
const fetchHouseList=async()=>{
    // 模拟后端返回
    const start = (pageNum.value - 1) * pageSize.value;
    const end = start + pageSize.value;

    const res = {
        code: 200,
        data: {
            list: mockData.slice(start, end),
            total: mockData.length
        }
    }

    houseList.value = res.data.list
    total.value = res.data.total
}
// 页码改变触发
const changePage = (num) => {
  pageNum.value = num
  fetchHouseList()
}
watch(()=>filter.district,(val)=>{
    selectedDistrict.value=val||'不限'
},{immediate:true})
watch(filter, () => {
  // fetchHouseList()
}, { deep: true })

onMounted(() => {
  fetchHouseList()
})

</script>

<style>
*{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
</style>
<style scoped>

.title{
    background: linear-gradient(to right, rgba(140,140,140,0.4), rgba(180,180,180,0.15));
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
.pagination {
  text-align: center;
  margin: 40px 0;
}
.page-btn {
  padding: 6px 16px;
  margin: 0 5px;
  border: 1px solid #ccc;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: #333;
}
.page-btn:hover:not(:disabled) {
  border-color: #006cd8;
  color: #006cd8;
}
.page-btn:disabled {
  background: #f5f5f5;
  color: #bbb;
  cursor: not-allowed;
  border-color: #eee;
}
.page-info {
  margin: 0 12px;
  font-size: 14px;
  color: #666;
}
</style>