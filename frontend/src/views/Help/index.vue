<template>
  <div class="help-page">
    <ParticlesBg />
    <div class="container">
      <div class="page-header">
        <h1 class="main-title">
          <span class="help-title-char" v-for="(char, idx) in helpTitleChars" :key="idx" :style="{ '--delay': `${idx * 0.15}s` }">
            {{ char }}
          </span>
        </h1>
        <p class="sub-title">中南找房 · 完整使用教程</p>
      </div>
      
      <div class="guide-section">
        <div class="guide-card fade-in" v-for="(item, idx) in guides" :key="idx" :style="{ animationDelay: `${idx * 0.15}s` }">
          <div class="guide-step">
            <span class="step-number">{{ idx + 1 }}</span>
          </div>
          <div class="guide-content">
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
            <div class="guide-tips" v-if="item.tips">
              <div class="tip-item" v-for="(tip, tipIdx) in item.tips" :key="tipIdx">
                <span class="tip-icon">💡</span>
                <span class="tip-text">{{ tip }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="roles-section fade-in-section" :style="{ animationDelay: '1.2s' }">
        <h2 class="section-title">角色说明</h2>
        <div class="roles-grid">
          <div class="role-card role-tenant fade-in" :style="{ animationDelay: '1.4s' }">
            <div class="role-icon">👤</div>
            <h3>租客</h3>
            <ul class="role-features">
              <li>浏览搜索所有房源</li>
              <li>预约看房申请</li>
              <li>在线签署租赁合同</li>
              <li>在线支付租金账单</li>
              <li>提交维修申请</li>
              <li>发起投诉反馈</li>
            </ul>
          </div>
          <div class="role-card role-landlord fade-in" :style="{ animationDelay: '1.55s' }">
            <div class="role-icon">🏠</div>
            <h3>房东</h3>
            <ul class="role-features">
              <li>发布管理自己的房源</li>
              <li>确认/拒绝租客预约</li>
              <li>从预约创建正式合同</li>
              <li>查看租金收缴记录</li>
              <li>处理租客维修申请</li>
              <li>在线消息实时聊天</li>
            </ul>
          </div>
          <div class="role-card role-admin fade-in" :style="{ animationDelay: '1.7s' }">
            <div class="role-icon">⚙️</div>
            <h3>管理员</h3>
            <ul class="role-features">
              <li>全平台用户管理</li>
              <li>所有房源监管审核</li>
              <li>介入处理投诉纠纷</li>
              <li>查看统计报表数据</li>
              <li>发布官方新闻公告</li>
              <li>系统操作日志审计</li>
            </ul>
          </div>
        </div>
      </div>
      
      <div class="faq-section fade-in-section" :style="{ animationDelay: '2.0s' }">
        <h2 class="section-title">常见问题</h2>
        <div class="faq-list">
          <div class="faq-item fade-in" v-for="(faq, idx) in faqs" :key="idx" :style="{ animationDelay: `${2.2 + idx * 0.12}s` }">
            <div class="faq-q">Q: {{ faq.q }}</div>
            <div class="faq-a">A: {{ faq.a }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import ParticlesBg from '@/components/ParticlesBg/index.vue'

const guides = [
  {
    title: '注册登录账号',
    desc: '进入首页点击右上角登录按钮，选择注册账号，填写手机号、验证码、设置密码即可完成注册。登录时选择自己的身份（租客/房东/管理员）进入对应角色页面。',
    tips: ['手机号必须真实有效，后续用于接收看房通知短信', '忘记密码可通过短信验证码快速找回']
  },
  {
    title: '搜索浏览房源',
    desc: '点击顶部「房源搜索」页面，可以通过区域筛选、价格区间输入、关键词搜索快速找到心仪的房源。点击任意房源卡片即可进入详情页查看全部照片和详细介绍。'
  },
  {
    title: '预约看房（租客端）',
    desc: '在房源详情页点击「预约看房」按钮，选择您方便的日期和时间段，提交预约申请。房东收到通知后会尽快处理您的申请。',
    tips: ['请提前和房东在线沟通确认时间', '预约状态可以在我的租赁-预约看房页面实时查看']
  },
  {
    title: '发布房源（房东端）',
    desc: '进入「我的房源-创建房源」页面，完整填写房源基本信息、上传实拍图片、设置租金价格和出租要求，提交后即可成功发布上架。',
    tips: ['上传真实清晰的房源图片能大幅提升预约率', '随时可以去房源列表页编辑修改房源信息']
  },
  {
    title: '合同签署',
    desc: '房东确认租客的看房预约后，即可一键创建正式租赁合同。合同双方在线确认无误后点击签署按钮，合同立即生效具有法律效应。',
    tips: ['请仔细阅读合同全部条款确认无误后再签署', '签署后的合同可以随时下载存档备份']
  },
  {
    title: '租金与账单',
    desc: '合同生效后系统会自动按月生成租金账单，租客在「我的租赁-租金支付」页面查看待付账单，点击支付按钮即可完成模拟支付操作。',
    tips: ['房东可以在租金监控页面查看所有租客的缴费记录', '逾期未缴系统会自动发送站内通知提醒']
  },
  {
    title: '维修与投诉',
    desc: '房屋设施出现问题，租客可以提交维修申请，填写故障描述和上传现场照片。如有服务纠纷，租客也可以发起投诉，管理员会介入公平处理。'
  }
]

const faqs = [
  { q: '一个手机号可以注册多个账号吗？', a: '一个手机号只能注册一个账号，系统会自动区分角色权限' },
  { q: '房源发布后多久能被其他人看到？', a: '正常情况下发布后立即上架对外可见' },
  { q: '签约后合同可以修改吗？', a: '合同签署生效后双方确认不可随意修改，如需调整请协商一致联系管理员' },
  { q: '忘记密码怎么办？', a: '在登录页点击忘记密码，通过手机号接收的验证码就能重置新密码' },
  { q: '如何联系对方沟通问题？', a: '进入消息中心的聊天页面，可以和对方发起实时在线消息对话' }
]

const helpTitleChars = '帮助手册'.split('')

onMounted(() => {
  document.querySelectorAll('.fade-in').forEach((el, idx) => {
    setTimeout(() => el.classList.add('visible'), parseFloat(el.style.animationDelay) * 1000 + 200)
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
  max-width: 900px;
  margin: 0 auto;
  padding: 0 24px;
}

.page-header {
  text-align: center;
  margin-bottom: 60px;
}

.main-title {
  font-size: 42px;
  font-weight: 700;
  margin: 0 0 12px 0;
  position: relative;
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
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes helpShine {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.fade-in {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.5s ease-out;
}

.fade-in.visible {
  opacity: 1;
  transform: translateY(0);
}

.fade-in-section {
  opacity: 0;
  transform: translateY(20px);
  animation: sectionAppear 0.5s ease-out forwards;
  animation-delay: var(--style);
}

@keyframes sectionAppear {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.sub-title {
  font-size: 16px;
  color: #8c8c8c;
  margin: 0;
  letter-spacing: 3px;
}

.guide-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 70px;
}

.guide-card {
  background: #fff;
  border-radius: 12px;
  padding: 28px 32px;
  display: flex;
  gap: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
}

.guide-card:hover {
  transform: translateX(6px);
  border-color: #91d5ff;
  box-shadow: 0 6px 24px rgba(24, 144, 255, 0.1);
}

.guide-step {
  flex-shrink: 0;
}

.step-number {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  color: #fff;
  font-size: 22px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.guide-content h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #262626;
}

.guide-content p {
  margin: 0 0 16px 0;
  font-size: 15px;
  color: #595959;
  line-height: 1.7;
}

.guide-tips {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #f6ffed;
  border-radius: 6px;
  padding: 8px 12px;
}

.tip-icon {
  flex-shrink: 0;
}

.tip-text {
  font-size: 14px;
  color: #389e0d;
  line-height: 1.5;
}

.section-title {
  font-size: 28px;
  font-weight: 600;
  color: #262626;
  margin: 0 0 32px 0;
  padding-left: 12px;
  border-left: 4px solid #1890ff;
}

.roles-section {
  margin-bottom: 70px;
}

.roles-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.role-card {
  background: #fff;
  border-radius: 12px;
  padding: 32px 24px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.role-icon {
  font-size: 52px;
  margin-bottom: 16px;
}

.role-card h3 {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 20px 0;
  color: #262626;
}

.role-features {
  list-style: none;
  margin: 0;
  padding: 0;
  text-align: left;
}

.role-features li {
  padding: 8px 0;
  font-size: 14px;
  color: #595959;
  border-bottom: 1px dashed #f0f0f0;
}

.role-features li:last-child {
  border-bottom: none;
}

.role-tenant {
  border-top: 4px solid #1890ff;
}

.role-landlord {
  border-top: 4px solid #52c41a;
}

.role-admin {
  border-top: 4px solid #722ed1;
}

.faq-section {
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.faq-item {
  background: #fff;
  border-radius: 10px;
  padding: 20px 24px;
  border: 1px solid #f0f0f0;
}

.faq-q {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 10px;
}

.faq-a {
  font-size: 15px;
  color: #595959;
  line-height: 1.7;
}

@media (max-width: 768px) {
  .guide-card {
    flex-direction: column;
  }
  
  .roles-grid {
    grid-template-columns: 1fr;
  }
}
</style>
