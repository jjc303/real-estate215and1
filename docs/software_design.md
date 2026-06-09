# 房屋租赁平台 · 软件设计说明书

> 版本：v1.0  
> 状态：初稿  
> 最后更新：2026-06-08

---

## 文档版本记录

| 版本 | 日期 | 修改人 | 修改内容 |
|------|------|--------|----------|
| v1.0 | 2026-06-08 | - | 初稿，完成完整软件设计说明 |

---

## 1. 引言

### 1.1 目的

本文档旨在对房屋租赁平台进行全面的软件设计说明，明确系统的总体架构、功能模块划分、数据结构设计、逻辑结构设计以及系统概要设计，为后续的详细设计、编码实现、测试验收提供统一的依据和指导。

本文档的读者包括：

- **项目开发人员**：了解系统架构、模块职责、数据表结构，指导编码实现
- **项目测试人员**：理解业务流程和数据流转，设计测试用例
- **项目管理人员**：掌握系统全貌，进行进度管理和资源协调
- **项目验收方**：对照需求确认系统设计是否完备

### 1.2 项目背景

随着城市化进程的加速，房屋租赁市场需求日益增长。传统的租房方式存在信息不对称、流程繁琐、沟通效率低下等问题。房东难以高效管理房源和租客，租客找房需要反复实地跑盘，双方在预约、签约、缴租、报修等环节缺乏统一的线上管理工具。

本项目旨在开发一套面向 **房东、租客、管理员** 三类用户的房屋租赁平台，将传统租房流程全面线上化，并集成 AI 智能问答能力，提升租房全流程的效率和体验。

项目采用**前后端分离架构**，后端使用 **Flask（Python）** 提供业务 REST API，前端使用 **Vue 3** 构建单页应用（SPA），另设 **FastAPI（Python）AI 引擎** 提供 LLM/RAG/OCR 智能化服务。

---

## 2. 任务概述

### 2.1 目标

构建一个功能完整、可运行的房屋租赁管理平台，覆盖租房业务的全生命周期：

1. **用户与权限管理**：支持用户注册、登录、角色区分（房东/租客/管理员）、个人信息维护
2. **房源管理**：支持房源发布、编辑、上下架、多状态维护、图片/视频上传
3. 智能搜索和筛选：支持按区域、户型、租金等条件筛选房源
4. **在线沟通**：支持房东与租客间的站内消息会话
5. **预约看房**：租客发起预约，房东确认/拒绝，状态可追踪
6. **租赁签约**：基于预约确认生成合同，记录签约状态
7. **租金账单与支付**：按合同生成账单，支持模拟支付
8. **维修与投诉**：租客提交报修/投诉，房东处理，状态全程可追踪
9. **消息通知**：业务关键节点自动触发站内通知
10. **公告管理**：支持发布平台公告
11. **报表统计**：为管理员提供房源利用率、租金收入、用户活跃度等统计
12. **管理员后台**：用户管理、房源监管、投诉处理、系统审计
13. **AI 智能问答**：基于 RAG 技术的智能租房助手

### 2.2 假定和约束

**假定：**

- 用户具备基本的互联网操作能力
- 系统运行环境具备稳定的网络连接
- 浏览器支持现代 Web 标准（ES6+、CSS3）
- 用户邮箱地址真实有效（邮箱验证码功能）

**约束：**

| 约束类型 | 内容 |
|----------|------|
| **技术约束** | 后端使用 Flask + SQLAlchemy 2.0，前端使用 Vue 3 + Element Plus，数据库使用 MySQL 8.0 |
| **架构约束** | 前后端分离，Flask 后端与 AI 引擎（FastAPI）之间仅通过 HTTP 通信，禁止代码级 import |
| **数据库约束** | 数据库结构唯一来源为 Alembic migration，禁止使用 `db.create_all()` |
| **第一版简化** | 支付为模拟支付（不接真实网关），消息为 HTTP 轮询（不做 WebSocket），电子合同不做法律合规签章 |
| **多进程兼容** | Service / Repository 必须为无状态设计，所有 db 依赖显式传递 |
| **分层约束** | 严格遵循 `Router → Service → Repository → Model` 单向调用，禁止跨层调用 |

---

## 3. 系统设计

### 3.1 系统总体架构

系统采用 **前后端分离 + 模块化单体** 架构，由三个平级服务组成：

```
┌─────────────────────────────────────────────────────────────────┐
│                         ┌───────────────┐                       │
│                         │   Vue 3 前端   │                       │
│                         │  (SPA 客户端)  │                       │
│                         │  端口 5173     │                       │
│                         └───────┬───────┘                       │
│                                 │ HTTP/JSON                     │
│                                 │ /api/*                        │
│                         ┌───────▼───────┐                       │
│                         │  Flask 后端    │ ───HTTP──→ FastAPI   │
│                         │  (REST API)   │    AI 引擎            │
│                         │  端口 8000     │                       │
│                         └───────┬───────┘                       │
│                                 │                               │
│                         ┌───────▼───────┐                       │
│                         │   MySQL 8.0   │                       │
│                         │    数据库      │                       │
│                         └───────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

> **图 3-1：系统总体架构图**
> *（此处预留架构图空间）*

#### 3.1.1 各层职责

| 层级 | 技术选型 | 职责 |
|------|----------|------|
| **表现层（前端）** | Vue 3 + Element Plus | 用户交互界面，SPA 路由，状态管理，API 调用 |
| **业务层（后端）** | Flask + SQLAlchemy 2.0 | 业务 REST API，数据校验，状态流转，事务管理 |
| **AI 引擎** | FastAPI + Chroma + LLM | 智能问答，RAG 检索，OCR 识别 |
| **数据层** | MySQL 8.0 | 持久化存储，支持事务和复杂查询 |

#### 3.1.2 后端分层架构

后端严格遵循四层模型：

```
Router (Blueprint) → Service → Repository → Model / Schema
```

| 层次 | 职责 | 禁止 |
|------|------|------|
| **Router** | 接收请求、Schema 校验、调 Service | 写业务逻辑、直接调 Repository、处理事务 |
| **Service** | 业务逻辑、状态流转、权限校验、事务控制 | 保存状态、隐式获取 db、返回 ORM 对象 |
| **Repository** | 数据访问、条件筛选、分页查询 | commit / rollback、写业务规则 |
| **Model / Schema** | ORM 定义 / 请求响应校验 | 参与业务逻辑 |

### 3.2 基本功能结构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        房屋租赁管理平台                               │
├──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬────────────┤
│ 用户 │ 房源 │ 搜索 │ 消息 │ 租赁 │ 维修 │ 报表 │ 系统 │   AI      │
│ 权限 │ 管理 │ 推荐 │ 通知 │ 业务 │ 投诉 │ 统计 │ 后台 │  智能引擎  │
├──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼────────────┤
│注册  │发布  │条件  │私信  │预约  │报修  │房源  │用户  │智能问答   │
│登录  │编辑  │筛选  │会话  │签约  │申请  │统计  │管理  │RAG 检索   │
│角色  │上下架│推荐  │通知  │账单  │投诉  │租金  │房源  │偏好提取   │
│管理  │图片  │排序  │公告  │支付  │处理  │统计  │监管  │           │
│JWT   │视频  │      │      │合同  │      │活跃  │日志  │           │
│      │      │      │      │      │      │统计  │审计  │           │
└──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴────────────┘
```

> **图 3-2：基本功能结构图**
> *（此处预留功能结构图空间）*

### 3.3 基本功能结构图描述

| 一级模块 | 二级模块 | 功能描述 |
|----------|----------|----------|
| **用户权限** | 注册 | 支持邮箱验证码注册，选择角色（房东/租客） |
| | 登录 | 账号密码登录，JWT Token 鉴权 |
| | 角色管理 | 三类角色（房东/租客/管理员），权限路由控制 |
| | 个人信息 | 查看/编辑个人资料，头像上传 |
| **房源管理** | 房源发布 | 填写标题、地址、户型、租金、面积等信息 |
| | 房源编辑 | 编辑已发布房源信息 |
| | 上下架 | 房源状态管理（草稿/上架/出租/下架/维修） |
| | 图片/视频 | 多图片上传排序，封面设置，视频上传 |
| **搜索推荐** | 条件筛选 | 按区域、户型、租金区间、面积、装修等过滤 |
| | 排序 | 最新发布、租金最低、面积最大 |
| | 推荐 | 同区域、同价位、同户型、热门房源推荐 |
| **消息通知** | 在线私信 | 租客与房东一对一消息会话 |
| | 站内通知 | 业务状态变更自动触发通知 |
| | 公告 | 管理员发布平台公告 |
| **租赁业务** | 预约看房 | 租客发起→房东确认/拒绝→状态追踪 |
| | 合同签约 | 基于预约确认创建合同，状态流转 |
| | 租金账单 | 按合同生成租金账单，到期提醒 |
| | 支付 | 模拟支付，记录支付流水 |
| **维修投诉** | 维修申请 | 租客提交→房东处理→完成/关闭 |
| | 投诉处理 | 租客发起→房东/管理员处理→解决/关闭 |
| **报表统计** | 房源统计 | 总数、已出租数、空置数、出租率 |
| | 收入统计 | 每月租金收入汇总 |
| | 用户统计 | 用户增长、活跃用户数 |
| | 业务统计 | 维修/投诉数量统计 |
| **系统后台** | 用户管理 | 用户列表、创建、启用/禁用 |
| | 房源监管 | 全部房源只读查看 |
| | 投诉处理 | 管理员介入处理 |
| | 日志审计 | 操作日志记录与查询 |
| **AI 引擎** | 智能问答 | 租房相关对话，基于 RAG 检索 |
| | 偏好提取 | 从对话中提取用户偏好 |
| | OCR 识别 | 图片文字识别 |

### 3.4 功能结构管理模块描述

#### 3.4.1 用户与权限模块

- **数据流**：用户提交注册信息 → 后端校验 → 写入 users 表 → 返回 JWT Token
- **状态集**：用户状态 `active / disabled`
- **角色集**：`tenant / landlord / admin`
- **权限控制**：基于路由级中间件 + 装饰器，JWT 携带用户角色信息

#### 3.4.2 房源管理模块

- **数据流**：房东创建房源 → 写入 houses 表 → 上传图片写入 house_images 表 → 房源上架 → 前端展示
- **状态集**：`draft → listed → rented / offline / maintenance`
- **核心规则**：
  - 签约成功后房源自动变为 `rented`
  - 仅房源所有者（房东）可编辑/下架
  - 图片支持多张上传、排序、封面设置

#### 3.4.3 搜索与推荐模块

- **数据流**：用户输入筛选条件 → 后端多条件组合查询 → 分页返回结果
- **筛选维度**：`region / house_type / min_rent / max_rent / min_area / max_area / decoration / keyword`
- **推荐策略**：规则化推荐（同区域、同价位、同户型、热门、最新）

#### 3.4.4 消息与通知模块

- **在线消息**：基于 `conversations（会话）` + `messages（消息）` 表，唯一约束 `(tenant_id, landlord_id, house_id)`
- **站内通知**：业务关键节点（预约、签约、账单、报修、投诉）自动调用 `NotificationService.create_notification()`
- **公告**：管理员发布 `news` 表，状态 `draft / published`

#### 3.4.5 租赁业务模块

- **预约流程**：租客提交预约 → 房东确认 → 生成 `appointments` 记录 → 可进入签约
- **签约流程**：基于已确认的预约 → 创建 `contracts` → 双方确认 → 状态变为 `active`
- **账单流程**：合同生效后按周期生成 `bills` → 租客支付 → 生成 `payments` 记录
- **支付方式**：`mock`（模拟支付） / `offline`（线下支付）
- **状态联动**：合同 `active` → 房源变为 `rented`

#### 3.4.6 维修与投诉模块

- **维修流程**：租客提交（基于 active contract）→ 房东处理 → 完成/关闭
- **投诉流程**：租客提交（基于 active contract）→ 房东/管理员处理 → 解决/关闭
- **状态集**：维修 `pending → processing → completed → closed`（可选分支 `rejected / cancelled / reopened`）；投诉 `pending → processing → resolved → closed`（可选 `rejected`）
- **操作日志**：关键状态变更同步写入 `operation_logs` 表

#### 3.4.7 报表统计模块

- **数据来源**：直接聚合 `houses / contracts / payments / users / repairs / complaints` 表
- **接口**：`house-utilization / rent-income / active-users / complaint-repair-count`
- **权限**：仅 admin 角色可访问

#### 3.4.8 系统后台管理模块

- **用户管理**：列表、详情、创建、更新、启用/禁用
- **房源管理**：后台只读查看（不做审核上架）
- **投诉/维修**：admin 可执行所有合法状态流转
- **操作日志**：记录关键业务的变更历史

#### 3.4.9 AI 智能引擎模块

- **技术栈**：FastAPI + Chroma（向量库）+ 百炼 LLM + 百炼 Embedding
- **核心能力**：
  - RAG 检索增强问答：基于房源知识库 + 对话上下文
  - 用户偏好提取：从对话中提取租客偏好，辅助推荐
  - OCR 识别：图片文字提取（预留接口）
- **集成方式**：Flask 后端通过 HTTP 调用 AI 引擎 API

### 3.5 业务流程图

#### 3.5.1 租客找房 → 入住全流程

```
注册/登录 → 搜索房源 → 查看详情 → 收藏/咨询 → 预约看房
    ↓
房东确认 ← 等待房东处理
    ↓ 确认
线下看房 → 达成意向 → 在线签约 → 支付租金 → 入住
    ↓                                          ↓
  未达成                                  维修申请 / 投诉
```

> **图 3-5-1：租客找房入住流程图**
> *（此处预留业务流程图空间）*

#### 3.5.2 房东出租管理流程

```
注册/登录 → 发布房源 → 上传图片/视频 → 上架
    ↓
接收咨询 ← 处理预约 → 确认看房 → 线下带看
    ↓
确认签约 → 查看租金 → 处理维修/投诉
```

> **图 3-5-2：房东出租管理流程图**
> *（此处预留业务流程图空间）*

#### 3.5.3 管理员后台管理流程

```
登录后台 → 用户管理 / 房源监管 / 投诉处理 / 公告发布 / 报表查看
```

> **图 3-5-3：管理员后台管理流程图**
> *（此处预留业务流程图空间）*

#### 3.5.4 预约 → 签约 → 支付核心业务流程

```
租客                    房东                    系统
  │                      │                      │
  │── 提交预约 ─────────→│                      │
  │                      │── 确认预约 ─────────→│
  │←──── 确认通知 ───────│                      │
  │                      │                      │── 生成合同记录
  │── 确认签约 ─────────→│                      │
  │                      │── 确认签约 ─────────→│── 合同 active
  │                      │                      │── 房源 → rented
  │                      │                      │── 生成账单
  │── 支付租金 ─────────→│                      │
  │                      │                      │── 生成支付记录
```

> **图 3-5-4：核心业务时序流程图**
> *（此处预留时序图空间）*

#### 3.5.5 维修申请处理流程

```
租客                    房东                    系统
  │                      │                      │
  │── 提交报修 ─────────→│                      │── 创建 repair（pending）
  │                      │                      │── 通知租客/房东
  │                      │── 开始处理 ─────────→│── processing
  │                      │── 维修完成 ─────────→│── completed
  │── 确认关闭 ─────────→│                      │── closed
  │                      │                      │── 记录操作日志
```

> **图 3-5-5：维修申请处理流程图**
> *（此处预留流程图空间）*

---

## 4. 数据结构设计

### 4.1 用户管理子模块数据需求

| 数据项 | 字段名 | 类型 | 长度 | 约束 |
|--------|--------|------|------|------|
| 用户ID | id | INT | - | PK, 自增 |
| 用户名 | username | VARCHAR | 50 | UNIQUE, NOT NULL |
| 密码 | password | VARCHAR | 255 | NOT NULL |
| 角色 | role | VARCHAR | 20 | NOT NULL, 默认 tenant |
| 真实姓名 | real_name | VARCHAR | 50 | 可空 |
| 手机号 | phone | VARCHAR | 20 | 可空 |
| 邮箱 | email | VARCHAR | 100 | UNIQUE, 可空 |
| 状态 | status | VARCHAR | 20 | NOT NULL, 默认 active |
| 创建时间 | created_at | DATETIME | - | NOT NULL |
| 更新时间 | updated_at | DATETIME | - | NOT NULL |

### 4.2 房源管理子模块数据需求

| 数据项 | 字段名 | 类型 | 长度 | 约束 |
|--------|--------|------|------|------|
| 房源ID | id | INT | - | PK, 自增 |
| 房东ID | landlord_id | INT | - | FK → users.id |
| 标题 | title | VARCHAR | 100 | NOT NULL |
| 地址 | address | VARCHAR | 255 | NOT NULL |
| 区域 | region | VARCHAR | 100 | NOT NULL |
| 小区 | community | VARCHAR | 100 | 可空 |
| 户型 | house_type | VARCHAR | 50 | NOT NULL |
| 面积 | area | DECIMAL | 10,2 | NOT NULL |
| 租金 | rent | DECIMAL | 10,2 | NOT NULL |
| 押金 | deposit | DECIMAL | 10,2 | NOT NULL |
| 装修 | decoration | VARCHAR | 50 | 可空 |
| 楼层 | floor | VARCHAR | 50 | 可空 |
| 朝向 | orientation | VARCHAR | 50 | 可空 |
| 描述 | description | TEXT | - | 可空 |
| 状态 | status | VARCHAR | 20 | NOT NULL, 默认 draft |
| 删除时间 | deleted_at | DATETIME | - | 可空（软删除） |
| 创建/更新时间 | - | - | - | 继承 BaseModel |

**房源图片表（house_images）：**

| 数据项 | 字段名 | 类型 | 长度 | 约束 |
|--------|--------|------|------|------|
| ID | id | INT | - | PK, 自增 |
| 房源ID | house_id | INT | - | FK → houses.id |
| URL | url | VARCHAR | 500 | NOT NULL |
| 对象键 | object_key | VARCHAR | 500 | NOT NULL |
| MIME类型 | mime_type | VARCHAR | 100 | NOT NULL |
| 文件大小 | size_bytes | INT | - | NOT NULL |
| 宽度 | width | INT | - | 可空 |
| 高度 | height | INT | - | 可空 |
| 排序 | sort_order | INT | - | 默认 0 |
| 是否封面 | is_cover | BOOL | - | 默认 false |
| 状态 | status | VARCHAR | 20 | 默认 active |

**房源视频表（house_videos）：**

| 数据项 | 字段名 | 类型 | 长度 | 约束 |
|--------|--------|------|------|------|
| ID | id | INT | - | PK, 自增 |
| 房源ID | house_id | INT | - | FK → houses.id |
| URL | url | VARCHAR | 500 | NOT NULL |
| 对象键 | object_key | VARCHAR | 500 | NOT NULL |
| MIME类型 | mime_type | VARCHAR | 100 | NOT NULL |
| 文件大小 | size_bytes | INT | - | NOT NULL |
| 时长(秒) | duration | INT | - | 可空 |
| 状态 | status | VARCHAR | 20 | 默认 active |

### 4.3 租赁管理子模块数据需求

**预约表（appointments）：**

| 数据项 | 字段名 | 类型 | 长度 | 约束 |
|--------|--------|------|------|------|
| ID | id | INT | - | PK, 自增 |
| 房源ID | house_id | INT | - | FK → houses.id |
| 租客ID | tenant_id | INT | - | FK → users.id |
| 房东ID | landlord_id | INT | - | FK → users.id |
| 预约时间 | appointment_time | DATETIME | - | NOT NULL |
| 备注 | remark | TEXT | - | 可空 |
| 状态 | status | VARCHAR | 20 | 默认 pending |

**合同表（contracts）：**

| 数据项 | 字段名 | 类型 | 长度 | 约束 |
|--------|--------|------|------|------|
| ID | id | INT | - | PK, 自增 |
| 房源ID | house_id | INT | - | FK → houses.id |
| 租客ID | tenant_id | INT | - | FK → users.id |
| 房东ID | landlord_id | INT | - | FK → users.id |
| 预约ID | appointment_id | INT | - | FK → appointments.id |
| 开始日期 | start_date | DATE | - | NOT NULL |
| 结束日期 | end_date | DATE | - | NOT NULL |
| 月租金 | monthly_rent | DECIMAL | 10,2 | NOT NULL |
| 押金 | deposit | DECIMAL | 10,2 | NOT NULL |
| 状态 | status | VARCHAR | 20 | 默认 pending |
| 备注 | remark | TEXT | - | 可空 |

**账单表（bills）：**

| 数据项 | 字段名 | 类型 | 长度 | 约束 |
|--------|--------|------|------|------|
| ID | id | INT | - | PK, 自增 |
| 合同ID | contract_id | INT | - | FK → contracts.id |
| 房源ID | house_id | INT | - | FK → houses.id |
| 租客ID | tenant_id | INT | - | FK → users.id |
| 房东ID | landlord_id | INT | - | FK → users.id |
| 账单类型 | bill_type | VARCHAR | 20 | NOT NULL |
| 金额 | amount | DECIMAL | 10,2 | NOT NULL |
| 截止日期 | due_date | DATE | - | NOT NULL |
| 状态 | status | VARCHAR | 20 | 默认 unpaid |
| 备注 | remark | TEXT | - | 可空 |

**支付表（payments）：**

| 数据项 | 字段名 | 类型 | 长度 | 约束 |
|--------|--------|------|------|------|
| ID | id | INT | - | PK, 自增 |
| 账单ID | bill_id | INT | - | FK → bills.id, UNIQUE |
| 合同ID | contract_id | INT | - | FK → contracts.id |
| 房源ID | house_id | INT | - | FK → houses.id |
| 租客ID | tenant_id | INT | - | FK → users.id |
| 房东ID | landlord_id | INT | - | FK → users.id |
| 金额 | amount | DECIMAL | 10,2 | NOT NULL |
| 支付方式 | payment_method | VARCHAR | 20 | NOT NULL |
| 状态 | status | VARCHAR | 20 | 默认 success |
| 支付时间 | paid_at | DATETIME | - | NOT NULL |
| 备注 | remark | TEXT | - | 可空 |

### 4.4 消息/维修/投诉子模块数据需求

**会话表（conversations）：**

| 数据项 | 字段名 | 类型 | 长度 | 约束 |
|--------|--------|------|------|------|
| ID | id | INT | - | PK, 自增 |
| 房源ID | house_id | INT | - | FK → houses.id |
| 租客ID | tenant_id | INT | - | FK → users.id |
| 房东ID | landlord_id | INT | - | FK → users.id |
| 唯一约束 | - | - | - | (tenant_id, landlord_id, house_id) |

**消息表（messages）：**

| 数据项 | 字段名 | 类型 | 长度 | 约束 |
|--------|--------|------|------|------|
| ID | id | INT | - | PK, 自增 |
| 会话ID | conversation_id | INT | - | FK → conversations.id |
| 发送者ID | sender_id | INT | - | FK → users.id |
| 内容 | content | TEXT | - | NOT NULL |
| 已读时间 | read_at | DATETIME | - | 可空 |

**通知表（notifications）：**

| 数据项 | 字段名 | 类型 | 长度 | 约束 |
|--------|--------|------|------|------|
| ID | id | INT | - | PK, 自增 |
| 用户ID | user_id | INT | - | FK → users.id |
| 来源类型 | source_type | VARCHAR | 50 | NOT NULL |
| 来源ID | source_id | INT | - | NOT NULL |
| 标题 | title | VARCHAR | 200 | NOT NULL |
| 内容 | message | TEXT | - | NOT NULL |
| 状态 | status | VARCHAR | 20 | 默认 unread |

**维修表（repairs）：**

| 数据项 | 字段名 | 类型 | 长度 | 约束 |
|--------|--------|------|------|------|
| ID | id | INT | - | PK, 自增 |
| 合同ID | contract_id | INT | - | FK → contracts.id |
| 房源ID | house_id | INT | - | FK → houses.id |
| 租客ID | tenant_id | INT | - | FK → users.id |
| 房东ID | landlord_id | INT | - | FK → users.id |
| 描述 | description | TEXT | - | NOT NULL |
| 状态 | status | VARCHAR | 20 | 默认 pending |
| 处理时间 | processed_at | DATETIME | - | 可空 |
| 完成时间 | completed_at | DATETIME | - | 可空 |
| 关闭时间 | closed_at | DATETIME | - | 可空 |
| 拒绝时间 | rejected_at | DATETIME | - | 可空 |
| 取消时间 | cancelled_at | DATETIME | - | 可空 |
| 重开时间 | reopened_at | DATETIME | - | 可空 |

**投诉表（complaints）：**

| 数据项 | 字段名 | 类型 | 长度 | 约束 |
|--------|--------|------|------|------|
| ID | id | INT | - | PK, 自增 |
| 合同ID | contract_id | INT | - | FK → contracts.id |
| 房源ID | house_id | INT | - | FK → houses.id |
| 租客ID | tenant_id | INT | - | FK → users.id |
| 房东ID | landlord_id | INT | - | FK → users.id |
| 描述 | description | TEXT | - | NOT NULL |
| 状态 | status | VARCHAR | 20 | 默认 pending |
| 处理时间 | processed_at | DATETIME | - | 可空 |
| 解决时间 | resolved_at | DATETIME | - | 可空 |
| 关闭时间 | closed_at | DATETIME | - | 可空 |
| 拒绝时间 | rejected_at | DATETIME | - | 可空 |

### 4.5 实体联系图（E-R 图）

```
┌───────────┐    1:N    ┌───────────┐
│   User    │───────────│   House   │
│ (user_id) │           │ (house_id)│
└─────┬─────┘           └─────┬─────┘
      │                       │
      │ 1:N                   │ 1:N
      │                       │
      │          ┌────────────┼────────────┐
      │          │            │            │
      ▼          ▼            ▼            ▼
┌──────────┐ ┌────────┐ ┌──────────┐ ┌───────────┐
│Contract  │ │Favorite│ │HouseImage│ │HouseVideo │
├──────────┤ ├────────┤ ├──────────┤ ├───────────┤
│tenant_id │ │user_id │ │house_id  │ │house_id   │
│landlord  │ │house_id│ └──────────┘ └───────────┘
└────┬─────┘ └────────┘
     │
     │ 1:N
     │
┌────┴──────────────┐
│                   │
┌───────┐     ┌──────────┐     ┌──────────┐
│ Bill  │─────│ Payment  │     │  Repair  │
├───────┤     ├──────────┤     ├──────────┤
│contract_id  │bill_id   │     │contract_id│
└───────┘     └──────────┘     └──────────┘

┌──────────────┐     ┌──────────────┐
│ Conversation │─────│   Message    │
├──────────────┤     ├──────────────┤
│  tenant_id   │     │conversation  │
│  landlord_id │     │  sender_id   │
│  house_id    │     └──────────────┘
└──────────────┘

┌──────────┐     ┌───────────┐     ┌──────────┐
│Appoint   │     │ Complaint│     │Notifica  │
│-ment     │     │          │     │-tion     │
├──────────┤     ├──────────┤     ├──────────┤
│house_id  │     │contract_id    │user_id   │
│tenant_id │     │house_id  │     │source_type│
│landlord  │     │tenant_id │     └──────────┘
└──────────┘     └──────────┘

┌────────┐     ┌─────────────┐
│  News  │     │OperationLog │
├────────┤     ├─────────────┤
│author  │     │user_id      │
└────────┘     │module       │
               │action       │
               └─────────────┘
```

> **图 4-5：实体联系（E-R）图**
> *（此处预留 E-R 图空间）*

**核心实体关系说明：**

1. **User → House**（1:N）：一个房东可以发布多套房源
2. **House → HouseImage / HouseVideo**（1:N）：一套房源可以有多张图片和多个视频
3. **User → Favorite**（1:N）：一个用户可以收藏多套房源
4. **User / House → Appointment**（N:1）：一个房源可以有多个预约
5. **User / House → Conversation**（N:1）：一个房源对一个租客-房东对只有一个会话
6. **Conversation → Message**（1:N）：一个会话下有多条消息
7. **Contract → Bill**（1:N）：一个合同可以有多期账单
8. **Bill → Payment**（1:1）：一个账单对应一笔支付
9. **Contract → Repair**（1:N）：一个合同下可以有多个维修申请
10. **Contract → Complaint**（1:N）：一个合同下可以有多个投诉

---

## 5. 逻辑结构设计

### 5.1 用户相关数据表

#### 5.1.1 users（用户表）

```sql
CREATE TABLE users (
    id          INT           PRIMARY KEY AUTO_INCREMENT,
    username    VARCHAR(50)   NOT NULL UNIQUE,
    password    VARCHAR(255)  NOT NULL,
    role        VARCHAR(20)   NOT NULL DEFAULT 'tenant',
    real_name   VARCHAR(50)   NULL,
    phone       VARCHAR(20)   NULL,
    email       VARCHAR(100)  NULL UNIQUE,
    status      VARCHAR(20)   NOT NULL DEFAULT 'active',
    created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
```

#### 5.1.2 email_verification_codes（邮箱验证码表）

```sql
CREATE TABLE email_verification_codes (
    id          INT           PRIMARY KEY AUTO_INCREMENT,
    email       VARCHAR(100)  NOT NULL,
    code        VARCHAR(6)    NOT NULL,
    used        TINYINT(1)    NOT NULL DEFAULT 0,
    expires_at  DATETIME      NOT NULL,
    created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_evc_email ON email_verification_codes(email);
```

#### 5.1.3 user_avatars（用户头像表）

```sql
CREATE TABLE user_avatars (
    id          INT           PRIMARY KEY AUTO_INCREMENT,
    user_id     INT           NOT NULL,
    url         VARCHAR(500)  NOT NULL,
    object_key  VARCHAR(500)  NOT NULL,
    mime_type   VARCHAR(100)  NOT NULL,
    size_bytes  INT           NOT NULL,
    is_current  TINYINT(1)    NOT NULL DEFAULT 0,
    created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_user_avatars_user_id ON user_avatars(user_id);
```

### 5.2 房源相关数据表

#### 5.2.1 houses（房源表）

```sql
CREATE TABLE houses (
    id            INT           PRIMARY KEY AUTO_INCREMENT,
    landlord_id   INT           NOT NULL,
    title         VARCHAR(100)  NOT NULL,
    address       VARCHAR(255)  NOT NULL,
    region        VARCHAR(100)  NOT NULL,
    community     VARCHAR(100)  NULL,
    house_type    VARCHAR(50)   NOT NULL,
    area          DECIMAL(10,2) NOT NULL,
    rent          DECIMAL(10,2) NOT NULL,
    deposit       DECIMAL(10,2) NOT NULL,
    decoration    VARCHAR(50)   NULL,
    floor         VARCHAR(50)   NULL,
    orientation   VARCHAR(50)   NULL,
    description   TEXT          NULL,
    status        VARCHAR(20)   NOT NULL DEFAULT 'draft',
    deleted_at    DATETIME      NULL,
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (landlord_id) REFERENCES users(id)
);

CREATE INDEX idx_houses_landlord_id ON houses(landlord_id);
CREATE INDEX idx_houses_status ON houses(status);
CREATE INDEX idx_houses_region ON houses(region);
CREATE INDEX idx_houses_rent ON houses(rent);
CREATE INDEX idx_houses_house_type ON houses(house_type);
```

#### 5.2.2 house_images（房源图片表）

```sql
CREATE TABLE house_images (
    id          INT           PRIMARY KEY AUTO_INCREMENT,
    house_id    INT           NOT NULL,
    url         VARCHAR(500)  NOT NULL,
    object_key  VARCHAR(500)  NOT NULL,
    mime_type   VARCHAR(100)  NOT NULL,
    size_bytes  INT           NOT NULL,
    width       INT           NULL,
    height      INT           NULL,
    sort_order  INT           NOT NULL DEFAULT 0,
    is_cover    TINYINT(1)    NOT NULL DEFAULT 0,
    status      VARCHAR(20)   NOT NULL DEFAULT 'active',
    created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (house_id) REFERENCES houses(id)
);

CREATE INDEX idx_house_images_house_id ON house_images(house_id);
```

#### 5.2.3 house_videos（房源视频表）

```sql
CREATE TABLE house_videos (
    id          INT           PRIMARY KEY AUTO_INCREMENT,
    house_id    INT           NOT NULL,
    url         VARCHAR(500)  NOT NULL,
    object_key  VARCHAR(500)  NOT NULL,
    mime_type   VARCHAR(100)  NOT NULL,
    size_bytes  INT           NOT NULL,
    duration    INT           NULL,
    status      VARCHAR(20)   NOT NULL DEFAULT 'active',
    created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (house_id) REFERENCES houses(id)
);

CREATE INDEX idx_house_videos_house_id ON house_videos(house_id);
```

#### 5.2.4 favorites（收藏表）

```sql
CREATE TABLE favorites (
    id          INT       PRIMARY KEY AUTO_INCREMENT,
    user_id     INT       NOT NULL,
    house_id    INT       NOT NULL,
    created_at  DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (house_id) REFERENCES houses(id),
    UNIQUE KEY uq_favorites_user_house (user_id, house_id)
);

CREATE INDEX idx_favorites_user_id ON favorites(user_id);
CREATE INDEX idx_favorites_house_id ON favorites(house_id);
```

### 5.3 租赁/合同相关数据表

#### 5.3.1 appointments（预约表）

```sql
CREATE TABLE appointments (
    id                INT           PRIMARY KEY AUTO_INCREMENT,
    house_id          INT           NOT NULL,
    tenant_id         INT           NOT NULL,
    landlord_id       INT           NOT NULL,
    appointment_time  DATETIME      NOT NULL,
    remark            TEXT          NULL,
    status            VARCHAR(20)   NOT NULL DEFAULT 'pending',
    created_at        DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (house_id) REFERENCES houses(id),
    FOREIGN KEY (tenant_id) REFERENCES users(id),
    FOREIGN KEY (landlord_id) REFERENCES users(id)
);

CREATE INDEX idx_appointments_house_id ON appointments(house_id);
CREATE INDEX idx_appointments_tenant_id ON appointments(tenant_id);
CREATE INDEX idx_appointments_landlord_id ON appointments(landlord_id);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_appointments_time ON appointments(appointment_time);
```

#### 5.3.2 contracts（合同表）

```sql
CREATE TABLE contracts (
    id              INT           PRIMARY KEY AUTO_INCREMENT,
    house_id        INT           NOT NULL,
    tenant_id       INT           NOT NULL,
    landlord_id     INT           NOT NULL,
    appointment_id  INT           NOT NULL,
    start_date      DATE          NOT NULL,
    end_date        DATE          NOT NULL,
    monthly_rent    DECIMAL(10,2) NOT NULL,
    deposit         DECIMAL(10,2) NOT NULL,
    status          VARCHAR(20)   NOT NULL DEFAULT 'pending',
    remark          TEXT          NULL,
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (house_id) REFERENCES houses(id),
    FOREIGN KEY (tenant_id) REFERENCES users(id),
    FOREIGN KEY (landlord_id) REFERENCES users(id),
    FOREIGN KEY (appointment_id) REFERENCES appointments(id)
);

CREATE INDEX idx_contracts_house_id ON contracts(house_id);
CREATE INDEX idx_contracts_tenant_id ON contracts(tenant_id);
CREATE INDEX idx_contracts_landlord_id ON contracts(landlord_id);
CREATE INDEX idx_contracts_status ON contracts(status);
```

#### 5.3.3 bills（账单表）

```sql
CREATE TABLE bills (
    id            INT           PRIMARY KEY AUTO_INCREMENT,
    contract_id   INT           NOT NULL,
    house_id      INT           NOT NULL,
    tenant_id     INT           NOT NULL,
    landlord_id   INT           NOT NULL,
    bill_type     VARCHAR(20)   NOT NULL,
    amount        DECIMAL(10,2) NOT NULL,
    due_date      DATE          NOT NULL,
    status        VARCHAR(20)   NOT NULL DEFAULT 'unpaid',
    remark        TEXT          NULL,
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (contract_id) REFERENCES contracts(id),
    FOREIGN KEY (house_id) REFERENCES houses(id),
    FOREIGN KEY (tenant_id) REFERENCES users(id),
    FOREIGN KEY (landlord_id) REFERENCES users(id)
);

CREATE INDEX idx_bills_contract_id ON bills(contract_id);
CREATE INDEX idx_bills_tenant_id ON bills(tenant_id);
CREATE INDEX idx_bills_status ON bills(status);
CREATE INDEX idx_bills_due_date ON bills(due_date);
CREATE INDEX idx_bills_bill_type ON bills(bill_type);
```

#### 5.3.4 payments（支付表）

```sql
CREATE TABLE payments (
    id              INT           PRIMARY KEY AUTO_INCREMENT,
    bill_id         INT           NOT NULL,
    contract_id     INT           NOT NULL,
    house_id        INT           NOT NULL,
    tenant_id       INT           NOT NULL,
    landlord_id     INT           NOT NULL,
    amount          DECIMAL(10,2) NOT NULL,
    payment_method  VARCHAR(20)   NOT NULL,
    status          VARCHAR(20)   NOT NULL DEFAULT 'success',
    paid_at         DATETIME      NOT NULL,
    remark          TEXT          NULL,
    created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (bill_id) REFERENCES bills(id),
    FOREIGN KEY (contract_id) REFERENCES contracts(id),
    FOREIGN KEY (house_id) REFERENCES houses(id),
    FOREIGN KEY (tenant_id) REFERENCES users(id),
    FOREIGN KEY (landlord_id) REFERENCES users(id),
    UNIQUE KEY uq_payments_bill_id (bill_id)
);

CREATE INDEX idx_payments_tenant_id ON payments(tenant_id);
CREATE INDEX idx_payments_landlord_id ON payments(landlord_id);
CREATE INDEX idx_payments_payment_method ON payments(payment_method);
CREATE INDEX idx_payments_created_at ON payments(created_at);
```

### 5.4 消息/维修/投诉相关数据表

#### 5.4.1 conversations（会话表）

```sql
CREATE TABLE conversations (
    id           INT       PRIMARY KEY AUTO_INCREMENT,
    house_id     INT       NOT NULL,
    tenant_id    INT       NOT NULL,
    landlord_id  INT       NOT NULL,
    created_at   DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (house_id) REFERENCES houses(id),
    FOREIGN KEY (tenant_id) REFERENCES users(id),
    FOREIGN KEY (landlord_id) REFERENCES users(id),
    UNIQUE KEY uq_conversations_tenant_landlord_house (tenant_id, landlord_id, house_id)
);

CREATE INDEX idx_conversations_house_id ON conversations(house_id);
CREATE INDEX idx_conversations_tenant_id ON conversations(tenant_id);
CREATE INDEX idx_conversations_landlord_id ON conversations(landlord_id);
```

#### 5.4.2 messages（消息表）

```sql
CREATE TABLE messages (
    id                INT       PRIMARY KEY AUTO_INCREMENT,
    conversation_id   INT       NOT NULL,
    sender_id         INT       NOT NULL,
    content           TEXT      NOT NULL,
    read_at           DATETIME  NULL,
    created_at        DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME  NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (conversation_id) REFERENCES conversations(id),
    FOREIGN KEY (sender_id) REFERENCES users(id)
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_sender_id ON messages(sender_id);
CREATE INDEX idx_messages_read_at ON messages(read_at);
CREATE INDEX idx_messages_conv_created_id ON messages(conversation_id, created_at, id);
```

#### 5.4.3 repairs（维修表）

```sql
CREATE TABLE repairs (
    id            INT           PRIMARY KEY AUTO_INCREMENT,
    contract_id   INT           NOT NULL,
    house_id      INT           NOT NULL,
    tenant_id     INT           NOT NULL,
    landlord_id   INT           NOT NULL,
    description   TEXT          NOT NULL,
    status        VARCHAR(20)   NOT NULL DEFAULT 'pending',
    processed_at  DATETIME      NULL,
    completed_at  DATETIME      NULL,
    closed_at     DATETIME      NULL,
    rejected_at   DATETIME      NULL,
    cancelled_at  DATETIME      NULL,
    reopened_at   DATETIME      NULL,
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (contract_id) REFERENCES contracts(id),
    FOREIGN KEY (house_id) REFERENCES houses(id),
    FOREIGN KEY (tenant_id) REFERENCES users(id),
    FOREIGN KEY (landlord_id) REFERENCES users(id)
);

CREATE INDEX idx_repairs_contract_id ON repairs(contract_id);
CREATE INDEX idx_repairs_tenant_id ON repairs(tenant_id);
CREATE INDEX idx_repairs_landlord_id ON repairs(landlord_id);
CREATE INDEX idx_repairs_status ON repairs(status);
CREATE INDEX idx_repairs_created_at ON repairs(created_at);
```

#### 5.4.4 complaints（投诉表）

```sql
CREATE TABLE complaints (
    id            INT           PRIMARY KEY AUTO_INCREMENT,
    contract_id   INT           NOT NULL,
    house_id      INT           NOT NULL,
    tenant_id     INT           NOT NULL,
    landlord_id   INT           NOT NULL,
    description   TEXT          NOT NULL,
    status        VARCHAR(20)   NOT NULL DEFAULT 'pending',
    processed_at  DATETIME      NULL,
    resolved_at   DATETIME      NULL,
    closed_at     DATETIME      NULL,
    rejected_at   DATETIME      NULL,
    cancelled_at  DATETIME      NULL,
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (contract_id) REFERENCES contracts(id),
    FOREIGN KEY (house_id) REFERENCES houses(id),
    FOREIGN KEY (tenant_id) REFERENCES users(id),
    FOREIGN KEY (landlord_id) REFERENCES users(id)
);

CREATE INDEX idx_complaints_contract_id ON complaints(contract_id);
CREATE INDEX idx_complaints_tenant_id ON complaints(tenant_id);
CREATE INDEX idx_complaints_landlord_id ON complaints(landlord_id);
CREATE INDEX idx_complaints_status ON complaints(status);
CREATE INDEX idx_complaints_created_at ON complaints(created_at);
```

#### 5.4.5 notifications（通知表）

```sql
CREATE TABLE notifications (
    id           INT           PRIMARY KEY AUTO_INCREMENT,
    user_id      INT           NOT NULL,
    source_type  VARCHAR(50)   NOT NULL,
    source_id    INT           NOT NULL,
    title        VARCHAR(200)  NOT NULL,
    message      TEXT          NOT NULL,
    status       VARCHAR(20)   NOT NULL DEFAULT 'unread',
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);
```

#### 5.4.6 news（公告表）

```sql
CREATE TABLE news (
    id           INT           PRIMARY KEY AUTO_INCREMENT,
    title        VARCHAR(200)  NOT NULL,
    content      TEXT          NOT NULL,
    author_id    INT           NOT NULL,
    status       VARCHAR(20)   NOT NULL DEFAULT 'draft',
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (author_id) REFERENCES users(id)
);

CREATE INDEX idx_news_status ON news(status);
CREATE INDEX idx_news_created_at ON news(created_at);
```

### 5.5 系统配置/日志数据表

#### 5.5.1 operation_logs（操作日志表）

```sql
CREATE TABLE operation_logs (
    id             INT           PRIMARY KEY AUTO_INCREMENT,
    user_id        INT           NOT NULL,
    module         VARCHAR(50)   NOT NULL,
    record_id      INT           NOT NULL,
    action         VARCHAR(50)   NOT NULL,
    before_status  VARCHAR(50)   NULL,
    after_status   VARCHAR(50)   NULL,
    created_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_operation_logs_user_id ON operation_logs(user_id);
CREATE INDEX idx_operation_logs_module ON operation_logs(module);
CREATE INDEX idx_operation_logs_created_at ON operation_logs(created_at);
```

---

## 6. 系统概要设计

### 6.1 主要包含系统

系统由以下核心子系统组成，各子系统之间的关系及数据流向如下：

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端 SPA（Vue 3）                         │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐│
│  │首页  │ │房源  │ │搜索  │ │消息  │ │个人  │ │后台  │ │其他  ││
│  │      │ │列表  │ │筛选  │ │通知  │ │中心  │ │管理  │ │页面  ││
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘│
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/JSON (Vite Proxy → /api/*)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Flask 后端（端口 8000）                       │
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ 注册登录  │ │ 房源管理  │ │ 租赁签约  │ │ 消息通知         │  │
│  │ 子系统    │ │ 子系统    │ │ 子系统    │ │ 子系统           │  │
│  ├──────────┤ ├──────────┤ ├──────────┤ ├──────────────────┤  │
│  │Auth/User │ │House/    │ │Contract/ │ │Conversation/     │  │
│  │模块      │ │HouseImg  │ │Bill/     │ │Notification      │  │
│  │          │ │Favorite  │ │Payment   │ │模块              │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │ 维修投诉  │ │ 报表统计  │ │ 后台管理  │ │ AI 代理          │  │
│  │ 子系统    │ │ 子系统    │ │ 子系统    │ │ 子系统           │  │
│  ├──────────┤ ├──────────┤ ├──────────┤ ├──────────────────┤  │
│  │Repair/   │ │Statistics│ │Admin/    │ │AI Router →       │  │
│  │Complaint │ │模块      │ │Operation │ │HTTP → AI 引擎    │  │
│  │模块      │ │          │ │Log 模块  │ │                  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────────┐
    │ MySQL 8.0│    │ File     │    │ FastAPI AI   │
    │ 数据库   │    │ Storage  │    │ 引擎(端口9000)│
    └──────────┘    └──────────┘    └──────────────┘
```

> **图 6-1：系统概要架构图**
> *（此处预留系统概要架构图空间）*

**各子系统列表：**

| 序号 | 子系统 | 核心模块 | 功能概要 |
|------|--------|----------|----------|
| 1 | **注册登录子系统** | Auth / User | 邮箱验证码注册、账号密码登录、JWT 鉴权、角色权限控制 |
| 2 | **房源管理子系统** | House / HouseImage / HouseVideo / Favorite | 房源 CRUD、图片视频上传、收藏、状态流转 |
| 3 | **智能搜索子系统** | House（筛选接口） | 多条件组合筛选、排序、规则推荐 |
| 4 | **租赁签约子系统** | Appointment / Contract / Bill / Payment | 预约看房、合同签署、账单生成、支付记录 |
| 5 | **消息通知子系统** | Conversation / Message / Notification / News | 站内私信、业务通知、公告管理 |
| 6 | **维修投诉子系统** | Repair / Complaint | 维修申请与处理、投诉发起与处理 |
| 7 | **报表统计子系统** | Statistics | 房源利用率、租金收入、用户活跃度、业务统计 |
| 8 | **后台管理子系统** | Admin / OperationLog | 用户管理、房源监管、投诉处理、日志审计 |
| 9 | **AI 智能子系统** | AI Router（Flask）→ AI Engine（FastAPI） | 智能问答、RAG 检索、偏好提取 |

### 6.2 子模块功能及异常设计

#### 6.2.1 注册登录子系统

| 项目 | 内容 |
|------|------|
| **功能描述** | 支持邮箱验证码注册、账号密码登录、JWT Token 鉴权、用户角色区分（tenant/landlord/admin） |
| **可能异常** | ① 邮箱已注册 ② 验证码错误/过期 ③ 用户名已存在 ④ 密码错误 ⑤ 账号已被禁用 ⑥ JWT Token 过期/无效 |
| **异常处理** | ① 返回 2001 用户已存在错误 ② 返回验证码错误提示 ③ 返回用户名重复提示 ④ 登录失败返回 1002 认证错误 ⑤ 返回 1004 账号禁用提示 ⑥ 返回 401 引导重新登录 |
| **备注** | 密码使用 Werkzeug 哈希存储；JWT 采用 HS256 算法，Token 中携带 user_id 和 role |

#### 6.2.2 房源管理子系统

| 项目 | 内容 |
|------|------|
| **功能描述** | 房东发布/编辑/删除房源，上传图片视频，上架/下架管理，租客收藏房源 |
| **可能异常** | ① 非房东用户尝试操作 ② 操作非自己的房源 ③ 房源状态不允许编辑 ④ 上传文件格式不支持 ⑤ 文件大小超限 ⑥ 收藏重复 |
| **异常处理** | ① 返回 403 权限不足 ② 返回 2002 资源不属于当前用户 ③ 返回 2102 状态冲突 ④ 返回 3002 文件格式错误 ⑤ 返回 3002 文件大小超限 ⑥ 返回 2001 资源已存在 |
| **备注** | 房源状态流转：`draft → listed → rented / offline / maintenance`；软删除使用 `deleted_at` 字段 |

#### 6.2.3 智能搜索子系统

| 项目 | 内容 |
|------|------|
| **功能描述** | 按区域、户型、租金区间、面积、装修等条件筛选房源，支持多排序方式，提供规则化推荐 |
| **可能异常** | ① 参数格式错误 ② 分页参数超出范围 |
| **异常处理** | ① 返回参数校验错误提示 ② 自动修正分页参数 |
| **备注** | 仅查询 `listed` 状态的房源；推荐策略包括同区域、同价位、同户型、热门、最新 |

#### 6.2.4 租赁签约子系统

| 项目 | 内容 |
|------|------|
| **功能描述** | 租客提交预约→房东确认→基于确认的预约创建合同→双方确认→合同 active→生成账单→支付 |
| **可能异常** | ① 预约时间冲突 ② 预约状态不允许确认 ③ 合同状态流转非法 ④ 合同已过期 ⑤ 账单重复生成 ⑥ 重复支付 ⑦ 支付金额不匹配 |
| **异常处理** | ① 返回 2204 时间冲突 ② 返回 2202 状态不允许 ③ 返回 2402 状态冲突 ④ 返回 2401 合同过期 ⑤ 返回 2502 账单已存在 ⑥ 返回 2602 重复支付 ⑦ 返回 2601 金额不匹配 |
| **备注** | 合同 `active` 后房源自动变为 `rented`；支付为模拟支付，不接真实网关；`payments.bill_id` 有唯一约束 |

#### 6.2.5 消息通知子系统

| 项目 | 内容 |
|------|------|
| **功能描述** | 租客与房东一对一私信（基于房源会话），业务节点自动触发站内通知，管理员发布公告 |
| **可能异常** | ① 会话不存在 ② 非会话参与方发送消息 ③ 通知创建失败 ④ 非本人查看通知 |
| **异常处理** | ① 返回 2301 会话不存在 ② 返回 2302 非会话成员 ③ 事务回滚并记录错误日志 ④ 返回 2902 权限不足 |
| **备注** | 消息为 HTTP 轮询模式，不做 WebSocket；通知通过 `NotificationService.create_notification()` 统一入口创建 |

#### 6.2.6 维修投诉子系统

| 项目 | 内容 |
|------|------|
| **功能描述** | 维修：租客提交→房东处理→完成/关闭（可选拒绝/取消/重开）；投诉：租客发起→房东/管理员处理→解决/关闭 |
| **可能异常** | ① 非 active 合同提交 ② 非合同参与者操作 ③ 状态流转顺序错误 ④ 重复提交流程 |
| **异常处理** | ① 返回 2701/2801 合同未生效 ② 返回 2702/2802 非参与者 ③ 返回 2703/2803 状态冲突 ④ 业务层面限制 |
| **备注** | 必须基于当前租客自己的 `active contract` 创建；关键状态变更同步记录操作日志 |

#### 6.2.7 报表统计子系统

| 项目 | 内容 |
|------|------|
| **功能描述** | 提供房源利用率、租金收入趋势、活跃用户数、维修/投诉数量等只读统计接口 |
| **可能异常** | ① 非 admin 访问 ② 数据量过大导致统计缓慢 |
| **异常处理** | ① 返回 403 权限不足 ② 优化 SQL 查询，添加必要索引 |
| **备注** | 仅 admin 可访问；数据直接聚合已有业务表，不新增统计专用表；`rent-income` 以 `Payment.paid_at` 为时间口径 |

#### 6.2.8 后台管理子系统

| 项目 | 内容 |
|------|------|
| **功能描述** | 用户列表/创建/启用禁用、房源只读查看、投诉/维修管理、操作日志查询 |
| **可能异常** | ① 非 admin 访问 ② 禁用超级管理员自身 ③ 操作日志记录失败 |
| **异常处理** | ① 返回 403 权限不足 ② 业务层面校验阻止 ③ 事务回滚 |
| **备注** | 所有 admin 接口统一前缀 `/api/v1/admin`；操作日志记录在 `operation_logs` 表 |

#### 6.2.9 AI 智能子系统

| 项目 | 内容 |
|------|------|
| **功能描述** | 提供租房相关的智能问答服务，基于 RAG（检索增强生成）技术，支持上下文记忆和偏好提取 |
| **可能异常** | ① AI 引擎不可达 ② LLM 调用超时 ③ 向量库检索失败 ④ 对话会话过期 |
| **异常处理** | ① 返回 500 服务不可用提示 ② 超时返回友好提示 ③ 返回兜底回答 ④ 创建新会话 |
| **备注** | Flask 后端通过 HTTP 调用 AI 引擎；AI 引擎基于 FastAPI + Chroma + 百炼 LLM |

---

> **文档结束**
