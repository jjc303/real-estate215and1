<template>
  <div class="help-page">
    <ParticlesBg />
    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="main-title">
          <span class="help-title-char" v-for="(char, idx) in helpTitleChars" :key="idx" :style="{ '--delay': `${idx * 0.15}s` }">
            {{ char }}
          </span>
        </h1>
        <p class="sub-title">中南找房 · 完整使用教程</p>
      </div>

      <!-- ========== 平台简介 ========== -->
      <div class="intro-section fade-in-section">
        <div class="intro-card">
          <div class="intro-icon-wrapper">
            <i class="fa-solid fa-building"></i>
          </div>
          <div class="intro-text">
            <h2>欢迎来到中南找房</h2>
            <p>
              中南找房是一个面向<strong>房东、租客、管理员</strong>三类用户的房屋租赁平台，
              将找房、沟通、预约看房、签约、缴租、报修、投诉等租房全流程搬到线上，
              并集成 AI 智能问答助手，让租房更高效、更透明。
            </p>
            <div class="intro-meta">
              <span><i class="fa-regular fa-circle-check"></i> 已实现 18+ 功能模块</span>
              <span><i class="fa-regular fa-user"></i> 三类角色权限体系</span>
              <span><i class="fa-regular fa-message"></i> AI 智能问答</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ========== 游客快速指南 ========== -->
      <div class="section-block fade-in-section">
        <h2 class="section-title">👀 游客快速指南</h2>
        <p class="section-desc">无需登录即可浏览以下内容，体验平台基础功能</p>
        <div class="feature-grid">
          <div class="feature-card" v-for="(item, idx) in guestFeatures" :key="idx">
            <div class="feature-icon" :style="{ background: item.color }">
              <i :class="item.icon"></i>
            </div>
            <div class="feature-info">
              <h4>{{ item.title }}</h4>
              <p>{{ item.desc }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ========== 注册与登录 ========== -->
      <div class="section-block fade-in-section">
        <h2 class="section-title">📝 注册与登录</h2>
        <div class="step-list">
          <div class="step-item" v-for="(step, idx) in authSteps" :key="idx">
            <div class="step-badge">{{ idx + 1 }}</div>
            <div class="step-body">
              <h4>{{ step.title }}</h4>
              <p>{{ step.desc }}</p>
              <div class="step-tags" v-if="step.tags">
                <span v-for="tag in step.tags" :key="tag">{{ tag }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ========== 功能导览（按角色） ========== -->
      <div class="section-block fade-in-section">
        <h2 class="section-title">🧭 功能导览</h2>

        <!-- 租客 -->
        <div class="role-guide-card role-guide-tenant">
          <div class="role-guide-header">
            <span class="role-guide-badge tenant-badge">租客</span>
            <span class="role-guide-sub">浏览房源 → 预约看房 → 签约 → 入住</span>
          </div>
          <div class="role-guide-body">
            <div class="guide-module" v-for="(mod, idx) in tenantGuide" :key="idx">
              <div class="module-icon"><i :class="mod.icon"></i></div>
              <div class="module-info">
                <h4>{{ mod.title }}</h4>
                <p>{{ mod.desc }}</p>
                <div class="module-path" v-if="mod.path">
                  <i class="fa-regular fa-location-dot"></i> 路径：<code>{{ mod.path }}</code>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 房东 -->
        <div class="role-guide-card role-guide-landlord">
          <div class="role-guide-header">
            <span class="role-guide-badge landlord-badge">房东</span>
            <span class="role-guide-sub">发布房源 → 管理租赁 → 处理报修</span>
          </div>
          <div class="role-guide-body">
            <div class="guide-module" v-for="(mod, idx) in landlordGuide" :key="idx">
              <div class="module-icon"><i :class="mod.icon"></i></div>
              <div class="module-info">
                <h4>{{ mod.title }}</h4>
                <p>{{ mod.desc }}</p>
                <div class="module-path" v-if="mod.path">
                  <i class="fa-regular fa-location-dot"></i> 路径：<code>{{ mod.path }}</code>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 管理员 -->
        <div class="role-guide-card role-guide-admin">
          <div class="role-guide-header">
            <span class="role-guide-badge admin-badge">管理员</span>
            <span class="role-guide-sub">用户管理 → 业务监管 → 数据统计</span>
          </div>
          <div class="role-guide-body">
            <div class="guide-module" v-for="(mod, idx) in adminGuide" :key="idx">
              <div class="module-icon"><i :class="mod.icon"></i></div>
              <div class="module-info">
                <h4>{{ mod.title }}</h4>
                <p>{{ mod.desc }}</p>
                <div class="module-path" v-if="mod.path">
                  <i class="fa-regular fa-location-dot"></i> 路径：<code>{{ mod.path }}</code>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ========== 业务流程概览 ========== -->
      <div class="section-block fade-in-section">
        <h2 class="section-title">🔄 核心业务流程</h2>
        <div class="flow-diagram">
          <div class="flow-step" v-for="(step, idx) in flowSteps" :key="idx">
            <div class="flow-node">
              <div class="flow-icon" :style="{ background: step.color }">
                <i :class="step.icon"></i>
              </div>
              <div class="flow-label">{{ step.label }}</div>
            </div>
            <div class="flow-arrow" v-if="idx < flowSteps.length - 1">
              <i class="fa-solid fa-chevron-right"></i>
            </div>
          </div>
        </div>
      </div>

      <!-- ========== 角色说明 ========== -->
      <div class="roles-section fade-in-section">
        <h2 class="section-title">👤 角色说明</h2>
        <div class="roles-grid">
          <div class="role-card role-tenant fade-in">
            <div class="role-icon">👤</div>
            <h3>租客</h3>
            <ul class="role-features">
              <li>浏览搜索所有房源</li>
              <li>收藏感兴趣的房源</li>
              <li>在线私信房东咨询</li>
              <li>预约看房申请</li>
              <li>在线签署租赁合同</li>
              <li>在线支付租金账单</li>
              <li>提交维修申请</li>
              <li>发起投诉反馈</li>
              <li>查看系统通知公告</li>
              <li>AI 智能问答助手</li>
            </ul>
          </div>
          <div class="role-card role-landlord fade-in">
            <div class="role-icon">🏠</div>
            <h3>房东</h3>
            <ul class="role-features">
              <li>发布管理自己的房源</li>
              <li>上传图片/视频</li>
              <li>上下架房源管理</li>
              <li>确认/拒绝租客预约</li>
              <li>从预约创建正式合同</li>
              <li>取消/终止合同</li>
              <li>查看租金收缴记录</li>
              <li>处理租客维修申请</li>
              <li>在线消息实时聊天</li>
              <li>AI 智能问答助手</li>
            </ul>
          </div>
          <div class="role-card role-admin fade-in">
            <div class="role-icon">⚙️</div>
            <h3>管理员</h3>
            <ul class="role-features">
              <li>全平台用户管理</li>
              <li>所有房源监管查看</li>
              <li>介入处理投诉纠纷</li>
              <li>管理维修申请</li>
              <li>查看统计报表数据</li>
              <li>发布官方新闻公告</li>
              <li>系统操作日志审计</li>
              <li>AI 智能问答助手</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- ========== 常见问题 ========== -->
      <div class="faq-section fade-in-section">
        <h2 class="section-title">❓ 常见问题</h2>
        <div class="faq-list">
          <div class="faq-item fade-in" v-for="(faq, idx) in faqs" :key="idx">
            <div class="faq-q">
              <span class="faq-q-icon">Q</span>
              {{ faq.q }}
            </div>
            <div class="faq-a">
              <span class="faq-a-icon">A</span>
              {{ faq.a }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import ParticlesBg from '@/components/ParticlesBg/index.vue'

// ========== 游客功能 ==========
const guestFeatures = [
  { icon: 'fa-solid fa-search', title: '浏览房源列表', desc: '查看所有已上架房源，支持按区域、户型、租金等条件筛选', color: '#1890ff' },
  { icon: 'fa-solid fa-house-chimney', title: '查看房源详情', desc: '查看房源图片、基本信息、租金、房东等详细信息', color: '#52c41a' },
  { icon: 'fa-solid fa-newspaper', title: '阅读新闻公告', desc: '浏览平台发布的官方新闻和公告信息', color: '#722ed1' },
  { icon: 'fa-regular fa-circle-question', title: '查看帮助手册', desc: '阅读完整使用教程，了解平台各项功能', color: '#fa8c16' },
  { icon: 'fa-solid fa-star', title: '特别鸣谢', desc: '查看项目所使用的开源技术和致谢名单', color: '#eb2f96' },
]

// ========== 注册步骤 ==========
const authSteps = [
  { title: '进入首页', desc: '打开平台首页（/），点击右上角「登录」按钮', tags: ['公开'] },
  { title: '注册账号', desc: '在登录弹窗中选择「注册」，填写邮箱地址并获取验证码，设置用户名和密码，选择角色（租客/房东）完成注册', tags: ['邮箱验证码'] },
  { title: '登录系统', desc: '使用注册的邮箱和密码登录，系统根据角色自动加载对应的功能菜单和页面', tags: ['JWT 鉴权'] },
  { title: '完善资料', desc: '登录后进入「个人中心」，可上传头像、设置真实姓名、手机号等个人信息', tags: ['可选'] },
]

// ========== 租客功能导览 ==========
const tenantGuide = [
  { icon: 'fa-solid fa-search', title: '搜索与筛选', desc: '在房源列表页通过区域、户型、租金区间、面积、装修情况等条件精确筛选房源，支持按最新/价格/面积排序', path: '顶部导航 → 房源搜索' },
  { icon: 'fa-solid fa-heart', title: '收藏房源', desc: '在房源列表或详情页点击收藏按钮，收藏感兴趣的房源，方便后续对比和查看', path: '房源卡片/详情页 → 收藏按钮' },
  { icon: 'fa-regular fa-message', title: '在线咨询', desc: '在房源详情页点击「联系房东」，与房东进行实时在线私信沟通，咨询房源详细信息', path: '房源详情页 → 联系房东' },
  { icon: 'fa-solid fa-calendar-check', title: '预约看房', desc: '在房源详情页提交预约申请，选择看房时间和备注信息，等待房东确认', path: '我的租赁 → 预约看房' },
  { icon: 'fa-solid fa-file-signature', title: '在线签约', desc: '房东确认预约后创建合同，租客查看合同条款并确认签署，合同即时生效', path: '我的租赁 → 在线签约' },
  { icon: 'fa-solid fa-money-bill-wave', title: '租金支付', desc: '合同生效后系统按月生成账单，在租金支付页面查看待付账单并完成模拟支付', path: '我的租赁 → 租金支付' },
  { icon: 'fa-solid fa-screwdriver-wrench', title: '维修申请', desc: '房屋设施出现问题时，提交维修申请并描述故障，等待房东处理', path: '维修投诉 → 维修申请' },
  { icon: 'fa-solid fa-circle-exclamation', title: '投诉管理', desc: '如遇服务纠纷需要协调时，可发起投诉，房东或管理员会介入处理', path: '维修投诉 → 投诉管理' },
  { icon: 'fa-solid fa-bell', title: '通知与消息', desc: '系统会在预约确认、合同签署、账单生成、维修处理等节点自动发送站内通知，也可与房东实时在线聊天', path: '各业务自动触发' },
  { icon: 'fa-solid fa-robot', title: 'AI 智能问答', desc: '在房源详情页或消息页面与 AI 助手对话，咨询租房相关问题，获取智能推荐', path: '房源详情页/消息 → AI 助手' },
]

// ========== 房东功能导览 ==========
const landlordGuide = [
  { icon: 'fa-solid fa-plus-circle', title: '发布房源', desc: '填写房源标题、地址、区域、户型、面积、租金、押金等信息，上传实拍图片和视频，即可成功发布', path: '我的房源 → 创建房源' },
  { icon: 'fa-solid fa-images', title: '图片视频管理', desc: '为房源上传多张图片并设置封面图，支持上传房源视频，所有媒体文件自动管理', path: '我的房源 → 房源列表 → 管理图片' },
  { icon: 'fa-solid fa-toggle-on', title: '房源状态管理', desc: '控制房源上下架：草稿 → 上架 → 下架/维修 → 恢复，合同签署后自动变为已出租', path: '我的房源 → 房源列表 → 操作按钮' },
  { icon: 'fa-solid fa-calendar-alt', title: '预约确认', desc: '查看租客提交的看房预约，确认或拒绝预约申请，确认后可进入签约流程', path: '租赁管理 → 预约确认' },
  { icon: 'fa-solid fa-file-contract', title: '合同管理', desc: '基于已确认的预约创建合同，填写租期和租金信息，租客确认后合同生效查看所有合同记录', path: '租赁管理 → 合同管理' },
  { icon: 'fa-solid fa-chart-line', title: '租金监控', desc: '查看所有租客的租金账单和缴费记录，监控租金收缴情况', path: '租赁管理 → 租金监控' },
  { icon: 'fa-solid fa-toolbox', title: '维修处理', desc: '查看租客提交的维修申请，处理、完成或关闭维修单', path: '租赁管理 → 维修处理' },
  { icon: 'fa-regular fa-message', title: '消息通信', desc: '与租客进行实时在线私信沟通，接收系统通知', path: '房源详情页 → 联系租客' },
  { icon: 'fa-solid fa-robot', title: 'AI 智能问答', desc: '使用 AI 助手解答租房管理中的常见问题', path: '消息 → AI 助手' },
]

// ========== 管理员功能导览 ==========
const adminGuide = [
  { icon: 'fa-solid fa-users', title: '用户管理', desc: '查看所有用户列表，创建新用户，编辑用户信息，启用或禁用用户账号', path: '后台 → 用户管理' },
  { icon: 'fa-solid fa-building', title: '房源监管', desc: '查看全平台所有房源信息，监管房源状态和内容', path: '后台 → 房源监管' },
  { icon: 'fa-solid fa-scale-balanced', title: '投诉处理', desc: '查看和介入处理租客提交的投诉，执行状态流转（受理/解决/关闭/驳回）', path: '后台 → 投诉处理' },
  { icon: 'fa-solid fa-chart-pie', title: '统计报表', desc: '查看房源利用率、租金收入趋势、活跃用户数、维修投诉数量等统计数据', path: '后台 → 报表统计' },
  { icon: 'fa-solid fa-bullhorn', title: '公告管理', desc: '发布和管理平台公告新闻，支持草稿和发布两种状态', path: '后台 → 公告管理' },
  { icon: 'fa-solid fa-clipboard-list', title: '操作日志', desc: '审计系统关键业务（合同/账单/报修/投诉等）的操作变更历史', path: '后台 → 操作日志' },
  { icon: 'fa-solid fa-robot', title: 'AI 智能问答', desc: '使用 AI 助手解答平台管理相关问题', path: '后台 → AI 助手' },
]

// ========== 核心业务流程 ==========
const flowSteps = [
  { icon: 'fa-solid fa-user-plus', label: '注册登录', color: '#1890ff' },
  { icon: 'fa-solid fa-search', label: '搜索房源', color: '#52c41a' },
  { icon: 'fa-solid fa-heart', label: '收藏咨询', color: '#eb2f96' },
  { icon: 'fa-solid fa-calendar-check', label: '预约看房', color: '#fa8c16' },
  { icon: 'fa-solid fa-file-signature', label: '签署合同', color: '#722ed1' },
  { icon: 'fa-solid fa-money-bill-wave', label: '支付租金', color: '#13c2c2' },
  { icon: 'fa-solid fa-screwdriver-wrench', label: '维修投诉', color: '#f5222d' },
]

// ========== 常见问题 ==========
const faqs = [
  { q: '一个邮箱可以注册多个账号吗？', a: '一个邮箱只能注册一个账号，注册时需选择角色（租客/房东），后期角色不可变更' },
  { q: '忘记密码怎么办？', a: '在登录页面点击「忘记密码」，通过注册邮箱接收验证码即可重置密码（当前已实现邮箱验证码接口）' },
  { q: '游客可以浏览哪些内容？', a: '游客可查看房源列表、房源详情、新闻公告、帮助手册和特别鸣谢页面。收藏、预约、签约等功能需要登录后使用' },
  { q: '房源发布后多久能被看到？', a: '房东发布房源后状态为「草稿」，手动点击「上架」后立即对外可见。合同签约成功后房源自动变为「已出租」' },
  { q: '如何上传房源图片？', a: '在创建或编辑房源时，点击图片上传区域，可选择多张图片上传，支持拖拽排序和设置为封面图' },
  { q: '预约看房的流程是什么？', a: '租客在房源详情页提交预约 → 房东在「预约确认」页面处理 → 确认后状态变为 confirmed → 可进入合同创建' },
  { q: '合同签署后可以修改吗？', a: '合同签署生效（active）后双方不可随意修改。如需调整，房东可终止合同后重新创建' },
  { q: '租金账单如何生成和支付？', a: '合同生效后房东手动创建账单，租客在「租金支付」页面查看待付账单，点击支付完成模拟支付' },
  { q: '如何联系房东或租客？', a: '在房源详情页点击「联系房东」即可创建会话，双方可在消息页面进行实时在线私信沟通' },
  { q: '维修申请的流程是什么？', a: '租客在「维修申请」页面提交 → 房东在「维修处理」页面查看并处理 → 处理完成后租客确认关闭' },
  { q: '如何发起投诉？', a: '租客在「投诉管理」页面选择关联合同并描述问题提交 → 房东或管理员处理解决' },
  { q: 'AI 智能问答能做什么？', a: 'AI 助手可以回答租房相关问题，如租金、押金、户型等，也能根据对话提取租客偏好，推荐合适的房源' },
  { q: '通知消息在哪里查看？', a: '系统会在预约确认、合同签署、账单生成、维修处理等关键节点自动发送站内通知，登录后在消息页面查看' },
  { q: '管理员后台如何进入？', a: '使用管理员账号登录后，顶部导航会出现「后台管理」入口，或直接访问 /admin 路径' },
  { q: '房东可以取消合同吗？', a: '合同状态为 pending（待租客确认）时，房东可以取消合同。合同已生效（active）时，房东可以终止合同，终止后房源恢复为可出租状态' },
  { q: '租客可以拒绝合同吗？', a: '租客收到合同后，如果不同意条款，可以选择「拒绝合同」，合同状态变为 rejected，房东可另行处理' },
  { q: '操作日志记录哪些内容？', a: '系统自动记录合同、账单、支付、报修、投诉、公告等关键业务的状态变更操作，包括操作人、操作类型、变更前后的状态' },
  { q: '收藏的房源在哪里查看？', a: '租客登录后在个人中心或房源列表页顶部可以查看已收藏的房源列表' },
]

const helpTitleChars = '帮助手册'.split('')

onMounted(() => {
  // 滚动触发淡入动画
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible')
        observer.unobserve(entry.target)
      }
    })
  }, { threshold: 0.1 })

  document.querySelectorAll('.fade-in-section, .fade-in').forEach(el => {
    observer.observe(el)
  })
})
</script>

<style scoped>
.help-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #fafafa 0%, #f0f5ff 100%);
  padding: 40px 0 80px 0;
  position: relative;
  overflow: hidden;
}

.container {
  position: relative;
  z-index: 10;
  max-width: 960px;
  margin: 0 auto;
  padding: 0 24px;
}

/* ===== 页面标题 ===== */
.page-header {
  text-align: center;
  margin-bottom: 50px;
}

.main-title {
  font-size: 42px;
  font-weight: 700;
  margin: 0 0 12px 0;
  display: inline-block;
}

.help-title-char {
  display: inline-block;
  opacity: 0;
  transform: translateY(20px);
  animation: helpTitleAppear 0.6s ease-out forwards;
  animation-delay: var(--delay, 0s);
  background: linear-gradient(90deg, #1890ff, #52c41a, #1890ff);
  background-size: 200% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: helpTitleAppear 0.6s ease-out forwards, helpShine 3s linear infinite;
  animation-delay: var(--delay, 0s), calc(var(--delay, 0s) + 0.4s);
}

@keyframes helpTitleAppear {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}

@keyframes helpShine {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.sub-title {
  font-size: 16px;
  color: #8c8c8c;
  margin: 0;
  letter-spacing: 3px;
}

/* ===== 动画 ===== */
.fade-in-section {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease-out;
}

.fade-in-section.visible {
  opacity: 1;
  transform: translateY(0);
}

.fade-in {
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.5s ease-out;
}

.fade-in.visible {
  opacity: 1;
  transform: translateY(0);
}

/* ===== 公共 ===== */
.section-block {
  margin-bottom: 60px;
}

.section-title {
  font-size: 26px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 16px 0;
  padding-left: 14px;
  border-left: 4px solid #1890ff;
  line-height: 1.4;
}

.section-desc {
  font-size: 15px;
  color: #8c8c8c;
  margin: 0 0 24px 0;
  padding-left: 18px;
}

/* ===== 平台简介 ===== */
.intro-section {
  margin-bottom: 50px;
}

.intro-card {
  background: linear-gradient(135deg, #e6f7ff 0%, #f6ffed 100%);
  border-radius: 16px;
  padding: 36px 40px;
  display: flex;
  gap: 28px;
  align-items: flex-start;
  border: 1px solid #bae7ff;
}

.intro-icon-wrapper {
  flex-shrink: 0;
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
}

.intro-text h2 {
  font-size: 22px;
  font-weight: 600;
  margin: 0 0 10px 0;
  color: #262626;
}

.intro-text p {
  font-size: 15px;
  color: #595959;
  line-height: 1.8;
  margin: 0 0 16px 0;
}

.intro-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.intro-meta span {
  font-size: 13px;
  color: #8c8c8c;
  background: #fff;
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid #e8e8e8;
}

.intro-meta span i {
  margin-right: 4px;
  color: #52c41a;
}

/* ===== 游客功能 ===== */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}

.feature-card {
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  display: flex;
  gap: 16px;
  align-items: flex-start;
  border: 1px solid #f0f0f0;
  transition: all 0.3s;
}

.feature-card:hover {
  border-color: #91d5ff;
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.08);
  transform: translateY(-2px);
}

.feature-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
}

.feature-info h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 600;
  color: #262626;
}

.feature-info p {
  margin: 0;
  font-size: 13px;
  color: #8c8c8c;
  line-height: 1.5;
}

/* ===== 注册步骤 ===== */
.step-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.step-item {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  background: #fff;
  border-radius: 10px;
  padding: 20px 24px;
  border: 1px solid #f0f0f0;
}

.step-badge {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 700;
}

.step-body h4 {
  margin: 0 0 6px 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.step-body p {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #595959;
  line-height: 1.6;
}

.step-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.step-tags span {
  font-size: 12px;
  color: #1890ff;
  background: #e6f7ff;
  padding: 2px 10px;
  border-radius: 10px;
  border: 1px solid #91d5ff;
}

/* ===== 功能导览 ===== */
.role-guide-card {
  background: #fff;
  border-radius: 14px;
  margin-bottom: 20px;
  overflow: hidden;
  border: 1px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.role-guide-header {
  padding: 18px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid #f5f5f5;
}

.role-guide-badge {
  font-size: 14px;
  font-weight: 600;
  padding: 4px 16px;
  border-radius: 20px;
  color: #fff;
}

.tenant-badge { background: linear-gradient(135deg, #1890ff, #096dd9); }
.landlord-badge { background: linear-gradient(135deg, #52c41a, #389e0d); }
.admin-badge { background: linear-gradient(135deg, #722ed1, #531dab); }

.role-guide-sub {
  font-size: 14px;
  color: #8c8c8c;
}

.role-guide-body {
  padding: 20px 24px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.guide-module {
  display: flex;
  gap: 14px;
  align-items: flex-start;
  padding: 14px;
  border-radius: 10px;
  background: #fafafa;
  transition: all 0.3s;
}

.guide-module:hover {
  background: #f0f5ff;
  transform: translateX(4px);
}

.module-icon {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #e6f7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1890ff;
  font-size: 16px;
}

.role-guide-tenant .module-icon { background: #e6f7ff; color: #1890ff; }
.role-guide-landlord .module-icon { background: #f6ffed; color: #52c41a; }
.role-guide-admin .module-icon { background: #f9f0ff; color: #722ed1; }

.module-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #262626;
}

.module-info p {
  margin: 0 0 6px 0;
  font-size: 13px;
  color: #595959;
  line-height: 1.5;
}

.module-path {
  font-size: 12px;
  color: #8c8c8c;
}

.module-path code {
  background: #f5f5f5;
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 12px;
  color: #1890ff;
}

/* ===== 业务流程 ===== */
.flow-diagram {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0;
  background: #fff;
  border-radius: 14px;
  padding: 32px 24px;
  border: 1px solid #f0f0f0;
}

.flow-step {
  display: flex;
  align-items: center;
  gap: 0;
}

.flow-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.flow-icon {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.flow-label {
  font-size: 13px;
  font-weight: 500;
  color: #595959;
  white-space: nowrap;
}

.flow-arrow {
  color: #d9d9d9;
  font-size: 18px;
  margin: 0 12px;
  margin-bottom: 26px;
}

/* ===== 角色说明 ===== */
.roles-section {
  margin-bottom: 60px;
}

.roles-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.role-card {
  background: #fff;
  border-radius: 12px;
  padding: 28px 22px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
}

.role-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.role-icon {
  font-size: 48px;
  margin-bottom: 14px;
}

.role-card h3 {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 18px 0;
  color: #262626;
}

.role-features {
  list-style: none;
  margin: 0;
  padding: 0;
  text-align: left;
}

.role-features li {
  padding: 7px 0;
  font-size: 14px;
  color: #595959;
  border-bottom: 1px dashed #f0f0f0;
  line-height: 1.5;
}

.role-features li:last-child {
  border-bottom: none;
}

.role-features li::before {
  content: '✓ ';
  color: #52c41a;
  font-weight: 700;
}

.role-tenant { border-top: 4px solid #1890ff; }
.role-landlord { border-top: 4px solid #52c41a; }
.role-admin { border-top: 4px solid #722ed1; }

/* ===== 常见问题 ===== */
.faq-section {
  margin-bottom: 20px;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.faq-item {
  background: #fff;
  border-radius: 10px;
  padding: 20px 24px;
  border: 1px solid #f0f0f0;
  transition: all 0.3s;
}

.faq-item:hover {
  border-color: #91d5ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.06);
}

.faq-q {
  font-size: 15px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 10px;
  display: flex;
  gap: 10px;
}

.faq-q-icon {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #1890ff;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.faq-a {
  font-size: 14px;
  color: #595959;
  line-height: 1.7;
  display: flex;
  gap: 10px;
}

.faq-a-icon {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #52c41a;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .main-title { font-size: 32px; }

  .intro-card {
    flex-direction: column;
    padding: 24px;
  }

  .roles-grid {
    grid-template-columns: 1fr;
  }

  .role-guide-body {
    grid-template-columns: 1fr;
  }

  .flow-diagram {
    flex-direction: column;
    gap: 12px;
  }

  .flow-step {
    flex-direction: column;
  }

  .flow-arrow {
    transform: rotate(90deg);
    margin: 4px 0;
  }

  .guide-module {
    padding: 12px;
  }
}
</style>
