# 项目架构文档 · 房屋租赁平台

> 版本：v1.17.0  
> 架构模式：前后端分离 · 模块化单体  
> 技术栈：Flask + Vue 3 + FastAPI（AI 引擎）

---

## 目录

1. [项目概览](#1-项目概览)
2. [整体架构](#2-整体架构)
3. [后端架构（Flask）](#3-后端架构flask)
4. [前端架构（Vue 3）](#4-前端架构vue-3)
5. [AI 引擎架构（FastAPI）](#5-ai-引擎架构fastapi)
6. [部署架构](#6-部署架构)
7. [API 设计规范](#7-api-设计规范)
8. [数据流说明](#8-数据流说明)
9. [项目目录树](#9-项目目录树)

---

## 1. 项目概览

### 1.1 项目定位

面向 **房东、租客、管理员** 三类用户的房屋租赁平台，将传统租房流程线上化，并集成 AI 智能问答能力。

### 1.2 系统边界

**系统负责：**

- 用户注册、登录、身份区分
- 房源发布、编辑、下架、展示
- 房源图片与用户头像上传、管理、静态访问
- 房源搜索与推荐
- 房东和租客在线消息沟通
- 看房预约
- 合同生成与签约记录
- 租金账单与支付记录
- 维修申请与处理
- 投诉处理
- 管理员后台管理与统计报表
- AI 智能问答

**第一版简化处理：**

- 电子合同不做法律合规签章
- 支付为模拟支付，不接真实第三方支付网关
- 不做多因素认证
- 消息为 HTTP 轮询，不做 WebSocket 实时推送
- 不做异步任务队列

### 1.3 目标用户与核心操作

| 用户角色 | 核心目标 | 主要操作 |
|---------|---------|---------|
| **房东** | 发布并管理房源，处理租赁事务 | 发布/编辑房源、处理预约、签约、报修、投诉 |
| **租客** | 找房并完成租住过程 | 搜索房源、预约看房、签约、支付、报修、投诉 |
| **管理员** | 维持平台正常运行 | 用户管理、房源监管、投诉处理、统计报表 |

---

## 2. 整体架构

### 2.1 系统组成

项目由三个平级服务 + 一组部署配置组成：

```
real-estate215and1/
├── backend/       # Flask 主后端 —— 提供业务 REST API
├── frontend/      # Vue 3 前端 —— SPA 客户端
├── ai-engine/     # FastAPI AI 引擎 —— 提供 LLM/RAG/OCR 服务
└── deploy/        # Docker Compose 部署配置
```

### 2.2 架构拓扑图

```
┌──────────────┐      HTTP/JSON      ┌──────────────────┐
│              │  ──────────────────> │                  │
│   Frontend   │   /api/v1/*         │  Flask Backend   │
│   (Vue 3)    │  <────────────────── │  (端口 8000)     │
│              │      JSON Response   │                  │
└──────────────┘                      └───────┬──────────┘
                                              │
                                     HTTP/JSON │
                                              │
                                              ▼
                                   ┌──────────────────┐
                                   │                  │
                                   │   AI Engine      │
                                   │   (FastAPI)      │
                                   │   (端口 9000)     │
                                   │                  │
                                   └──────────────────┘
```

### 2.3 重要约束

- **Flask backend 不允许 import ai-engine 的 Python 代码**，两者只通过 HTTP 集成
- **前端通过 Vite proxy 转发 /api 请求到后端**，避免跨域问题
- **Flask 后端不保存 AI 对话记录**，不新增 AI 相关数据库表
- **数据库结构唯一来源是 Alembic migration**，禁止 `db.create_all()`

---

## 3. 后端架构（Flask）

### 3.1 技术栈

| 组件 | 技术选型 |
|------|---------|
| Web 框架 | Flask（App Factory 模式） |
| ORM | SQLAlchemy 2.0（select 风格） |
| 数据库 | MySQL 8.0 |
| 数据库驱动 | PyMySQL |
| 数据校验 | Pydantic v2 |
| 认证 | PyJWT（HS256） |
| 密码哈希 | Werkzeug |
| 数据库迁移 | Alembic |
| 测试 | pytest + requests（HTTP 冒烟测试） |
| WSGI 服务器 | Gunicorn |

### 3.2 分层架构（硬约束）

```
Blueprint(router) → service → repository → model/schema
```

每一层职责清晰，**禁止跨层调用**：

```
┌─────────────────────────────────────────────────────────┐
│  Router                                                  │
│  职责：接收请求 → Schema 校验 → 获取当前用户 → 调 service │
│  禁止：写业务逻辑、直接调 repository、处理事务             │
├─────────────────────────────────────────────────────────┤
│  Service                                                 │
│  职责：业务逻辑、状态流转、权限校验、事务、序列化输出       │
│  禁止：保存状态、隐式获取 db、返回 ORM 对象               │
├─────────────────────────────────────────────────────────┤
│  Repository                                              │
│  职责：数据访问、条件筛选、分页查询                       │
│  禁止：commit / rollback、写业务规则                     │
├─────────────────────────────────────────────────────────┤
│  Model / Schema                                          │
│  Model：SQLAlchemy ORM 定义                              │
│  Schema：Pydantic v2 请求/响应校验                       │
└─────────────────────────────────────────────────────────┘
```

### 3.3 应用入口（App Factory）

```
backend/app/
├── main.py              # 入口文件
└── factory.py           # App Factory：加载配置 → 初始化 DB → 注册蓝图 → 注册异常处理
```

`create_app()` 执行顺序：

1. `load_config(app)` —— 加载配置
2. `setup_logging(app)` —— 配置日志
3. `init_database(app)` —— 初始化数据库连接 + 注册 request hook
4. `register_blueprints(app)` —— 注册所有模块蓝图
5. `register_error_handlers(app)` —— 注册全局异常处理

### 3.4 数据库 Session 管理

采用 `scoped_session` + Flask request hook 模式：

```python
# 每次请求前创建 session
@app.before_request
def open_db():
    g.db = SessionLocal()

# 每次请求后关闭 session
@app.teardown_request
def close_db(_exception):
    g.db.close()
    SessionLocal.remove()
```

**规则：**

- session 通过 `g.db` 获取，**请求级生命周期**
- service 显式接收 `db` 参数，**禁止隐式获取**
- repository 接收 `db` 参数，**禁止 commit/rollback**
- 事务由 service 统一控制：`try → commit → except → rollback`

### 3.5 核心模块

```
backend/app/
├── core/                # 基础设施
│   ├── config.py        # 配置加载（环境变量 → Flask config）
│   ├── database.py      # 数据库引擎 + Session 管理
│   ├── security.py      # JWT 生成/校验 + 密码哈希
│   ├── exceptions.py    # 统一异常体系
│   ├── response.py      # 统一响应格式
│   └── logging.py       # 日志配置
├── common/              # 公共组件
│   ├── base_model.py    # SQLAlchemy Base
│   ├── base_repository.py  # 基础 CRUD
│   ├── base_schema.py   # Pydantic 基类
│   ├── pagination.py    # 分页工具
│   ├── enums.py         # 枚举定义
│   ├── dependencies.py  # 通用依赖
│   ├── email.py         # 邮件发送
│   └── ai_engine_client.py  # AI 引擎 HTTP 客户端
├── container/           # 依赖注入
│   ├── repositories.py  # Repository 单例容器
│   └── services.py      # Service 单例容器
└── modules/             # 业务模块（16 个）
```

### 3.6 业务模块清单

| 模块 | 路由前缀 | 职责 |
|------|---------|------|
| **User** | `/api/v1/users` | 用户注册、列表、详情 |
| **Auth** | `/api/v1/auth` | 登录、JWT、邮箱验证码注册/登录 |
| **House** | `/api/v1/houses` | 房源 CRUD、上下架 |
| **HouseImage** | `/api/v1/houses/{id}/images` | 房源图片上传与管理 |
| **UserAvatar** | `/api/v1/users/me/avatar` | 用户头像上传与历史 |
| **Favorite** | `/api/v1/favorites` | 收藏/取消收藏 |
| **Appointment** | `/api/v1/appointments` | 预约看房 |
| **Conversation** | `/api/v1/conversations` | 站内消息会话 |
| **Contract** | `/api/v1/contracts` | 合同创建与状态流转 |
| **Bill** | `/api/v1/bills` | 租金账单 |
| **Payment** | `/api/v1/payments` | 支付记录 |
| **Repair** | `/api/v1/repairs` | 报修申请 |
| **Complaint** | `/api/v1/complaints` | 投诉处理 |
| **News** | `/api/v1/news` | 公告管理 |
| **Notification** | `/api/v1/notifications` | 站内通知 |
| **Statistics** | `/api/v1/statistics` | 统计报表（只读） |
| **Admin** | `/api/v1/admin` | 后台管理 |
| **AI** | `/api/v1/ai` | AI 对话代理 |
| **Operation Log** | (通过 admin) | 操作日志审计 |

### 3.7 模块结构规范

每个业务模块遵循统一目录结构：

```
module_name/
├── __init__.py
├── model.py         # SQLAlchemy ORM 定义
├── schema.py        # Pydantic 请求/响应 Schema
├── repository.py    # 数据访问层
├── service.py       # 业务逻辑层
└── router.py        # 路由定义
```

### 3.8 统一响应格式

**成功响应：**

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

**失败响应：**

```json
{
  "code": 1001,
  "message": "user not found",
  "data": null
}
```

**分页响应：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [],
    "total": 100,
    "page": 1,
    "page_size": 10
  }
}
```

### 3.9 错误码体系

| 范围 | 含义 |
|------|------|
| 0 | 成功 |
| 1001-1004 | 用户/认证错误 |
| 2001-2002 | 资源不存在/冲突 |
| 2101-2102 | 房源错误 |
| 2201-2204 | 收藏/预约错误 |
| 2301-2302 | 会话/消息错误 |
| 2401-2405 | 合同错误 |
| 2501-2504 | 账单错误 |
| 2601-2604 | 支付错误 |
| 2701-2703 | 报修错误 |
| 2801-2803 | 投诉错误 |
| 2901-2902 | 通知错误 |
| 3001-3003 | 参数/公告错误 |
| 4000-5000 | 通用/系统错误 |

### 3.10 数据库表清单

当前共有 **17 张业务表**（不含 alembic 版本表）：

| 表名 | 所属模块 | 说明 |
|------|---------|------|
| `users` | User/Auth | 用户表 |
| `houses` | House | 房源表 |
| `house_images` | HouseImage | 房源图片表 |
| `user_avatars` | UserAvatar | 用户头像表 |
| `favorites` | Favorite | 收藏表 |
| `appointments` | Appointment | 预约表 |
| `conversations` | Conversation | 会话表 |
| `messages` | Conversation | 消息表 |
| `contracts` | Contract | 合同表 |
| `bills` | Bill | 账单表 |
| `payments` | Payment | 支付记录表 |
| `repairs` | Repair | 报修表 |
| `complaints` | Complaint | 投诉表 |
| `notifications` | Notification | 通知表 |
| `news` | News | 公告表 |
| `operation_logs` | Operation Log | 操作日志表 |
| `email_verification_codes` | Auth | 邮箱验证码表 |

### 3.11 关键设计决策

**Notification 已收口：**

所有通知创建统一通过 `NotificationService.create_notification()` 单入口，支持批量创建，禁止业务侧循环逐个创建。

**操作日志已接入：**

Repair / Complaint / Contract / Bill / Payment / News 的关键写操作在同一事务内记录操作日志，日志写入失败时业务整体回滚。

**多进程兼容：**

- service/repository 均为无状态设计
- 所有 db 显式传递
- 无全局业务变量
- 无 request/g 泄露
- 单进程 → 多进程无需修改业务代码

---

## 4. 前端架构（Vue 3）

### 4.1 技术栈

| 组件 | 技术选型 |
|------|---------|
| 框架 | Vue 3（Composition API + `<script setup>`） |
| 构建工具 | Vite 8 |
| UI 组件库 | Element Plus |
| 状态管理 | Pinia |
| 路由 | Vue Router 5 |
| HTTP 客户端 | Axios |
| 图标库 | Font Awesome 6 |
| 包管理器 | npm |

### 4.2 目录结构

```
frontend/
├── public/               # 静态资源
├── src/
│   ├── api/              # API 接口封装（按模块拆分）
│   │   ├── index.js      # 统一导出
│   │   ├── auth.js       # 认证相关
│   │   ├── house.js      # 房源相关
│   │   ├── appointment.js
│   │   ├── conversation.js
│   │   ├── favorite.js
│   │   ├── payment.js
│   │   ├── repair.js
│   │   └── complaint.js
│   ├── assets/           # 静态资源（图片等）
│   ├── components/       # 公共组件
│   │   ├── Header.vue        # 顶栏
│   │   ├── NavBar.vue        # 导航栏
│   │   ├── SearchBar.vue     # 搜索栏
│   │   ├── HouseCard.vue     # 房源卡片
│   │   ├── LoginModal.vue    # 登录/注册弹窗
│   │   ├── ChatPopup.vue     # 聊天弹窗
│   │   ├── Pagination.vue    # 分页组件
│   │   ├── Dialog.vue        # 通用对话框
│   │   ├── UserButton.vue    # 用户按钮
│   │   ├── houseBar.vue      # 房源侧边栏
│   │   └── ParticlesBg/      # 背景粒子动画
│   ├── config/
│   │   └── menus.js     # 按角色的菜单配置
│   ├── mock/            # 模拟数据
│   ├── router/
│   │   └── index.js     # 路由配置
│   ├── stores/
│   │   ├── user.js      # 用户状态（Pinia）
│   │   └── counter.js   # 示例 store
│   ├── utils/
│   │   ├── request.js   # Axios 封装（拦截器）
│   │   ├── errorHandler.js  # 全局错误处理
│   │   ├── logger.js    # 前端日志
│   │   └── tools.js     # 工具函数
│   ├── views/           # 页面组件
│   │   ├── Home/        # 首页
│   │   ├── HouseList/   # 房源列表
│   │   ├── HouseDetail/ # 房源详情
│   │   ├── MyHouses/    # 我的房源（房东）
│   │   ├── Reservation/ # 预约管理
│   │   ├── Contracts/   # 合同管理
│   │   ├── Bills/       # 账单管理
│   │   ├── Repair/      # 维修处理（房东）
│   │   ├── ServiceRepair/ # 维修申请（租客）
│   │   ├── Complaint/   # 投诉管理
│   │   ├── Profile/     # 个人中心
│   │   ├── PublicNews/  # 公告
│   │   ├── Admin/       # 后台管理
│   │   ├── Help/        # 帮助手册
│   │   └── Thanks/      # 特别鸣谢
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── index.html
├── vite.config.js       # Vite 配置
├── package.json
└── jsconfig.json
```

### 4.3 路由设计

| 路由路径 | 页面 | 角色 |
|---------|------|------|
| `/` | 首页 | 公开 |
| `/houseList` | 房源列表 | 公开 |
| `/houseDetail/:id` | 房源详情 | 公开 |
| `/news` | 公告 | 公开 |
| `/help` | 帮助手册 | 公开 |
| `/thanks` | 特别鸣谢 | 公开 |
| `/lease/appointment` | 预约看房 | 租客 |
| `/lease/contract` | 在线签约 | 租客 |
| `/lease/payment` | 租金支付 | 租客 |
| `/service/repair` | 维修申请 | 租客 |
| `/service/complaint` | 投诉管理 | 租客 |
| `/profile` | 个人中心 | 登录用户 |
| `/myhouses/publish` | 发布房源 | 房东 |
| `/myhouses/list` | 房源列表 | 房东 |
| `/myhouses/edit/:id` | 编辑房源 | 房东 |
| `/reservation` | 预约确认 | 房东 |
| `/contracts` | 合同管理 | 房东 |
| `/manage/rent` | 租金监控 | 房东 |
| `/manage/repair` | 维修处理 | 房东 |
| `/admin` | 后台管理 | 管理员 |

### 4.4 菜单体系

菜单根据用户角色动态生成，定义在 `src/config/menus.js`：

| 角色 | 菜单项 |
|------|--------|
| **guest** | 首页、房源搜索、新闻通知、帮助手册、鸣谢 |
| **tenant** | 首页、房源搜索、预约看房、在线签约、租金支付、维修申请、投诉管理、新闻通知、个人中心 |
| **landlord** | 首页、我的房源（创建/列表）、房源列表、预约确认、合同管理、租金监控、维修处理、新闻通知、个人中心 |
| **admin** | 用户管理、房源监管、投诉处理、报表统计、系统监控、新闻管理 |

### 4.5 请求流程

```
Vue Component → API 模块 → Axios 实例 → 请求拦截器（加 Token）
  → Vite Proxy（/api → http://127.0.0.1:8000）→ Flask Backend
  → 响应拦截器（统一解包）→ Component 消费数据
```

**Axios 封装关键点（`src/utils/request.js`）：**

- baseURL：`/api`（通过 Vite proxy 转发）
- 请求拦截器：自动从 localStorage 取 token，加到 `Authorization: Bearer` 头
- 响应拦截器：直接返回 `response.data`（后端统一结构）
- 401 处理：非认证接口 401 时清除 token 并跳转首页

### 4.6 状态管理

使用 Pinia（`src/stores/user.js`），管理：

- `isLoggedIn` —— 登录状态
- `userName / userRole / userId / userAvatar` —— 用户信息
- `showLogin / showRegister` —— 弹窗状态
- `currentMenus` —— 根据角色计算的菜单
- 登录/注册倒计时逻辑

### 4.7 Vite 配置

- **代理**：`/api` → `http://127.0.0.1:8000`
- **路径别名**：`@` → `./src`
- **分包策略**：vue-vendor、element-plus、fontawesome 独立 chunk
- **关闭 HMR overlay**：避免开发时频繁弹窗

---

## 5. AI 引擎架构（FastAPI）

### 5.1 技术栈

| 组件 | 技术选型 |
|------|---------|
| Web 框架 | FastAPI |
| LLM 客户端 | 自定义 LLM Service |
| 向量数据库 | Chroma |
| 嵌入模型 | 百炼 Embedding |
| OCR | 百炼 OCR |
| 内存/会话管理 | SessionHistory |
| RAG 框架 | 自定义 RAG Manager |
| 测试 | pytest |

### 5.2 核心结构

```
ai-engine/
├── api/
│   ├── main.py              # FastAPI 入口
│   ├── routes/
│   │   ├── rental.py        # 租房对话路由
│   │   ├── ocr.py           # OCR 路由（保留但未公开）
│   │   └── status.py        # 健康检查
│   ├── schemas/
│   │   ├── common.py        # 通用 Schema
│   │   ├── rental.py        # 租房对话 Schema
│   │   └── status.py        # 状态 Schema
│   └── dependencies.py      # 依赖注入
├── config/
│   └── config.py            # 配置系统
├── services/
│   ├── base.py              # 服务基类
│   ├── llm_service.py       # LLM 调用
│   ├── embedding_service.py # 嵌入服务
│   ├── ocr_service.py       # OCR 服务
│   ├── rental_service.py    # 租房对话服务（核心）
│   ├── service_manager.py   # 服务管理器
│   ├── session_history.py   # 会话历史
│   └── rag/
│       ├── manager.py       # RAG 管理器
│       └── store.py         # 向量存储
├── prompts/
│   ├── rental/
│   │   ├── general_chat_prompt.py    # 通用对话提示词
│   │   ├── house_chat_prompt.py      # 房源对话提示词
│   │   ├── memory_extract_prompt.py  # 偏好提取提示词
│   │   └── rag_answer_prompt.py      # RAG 回答提示词
│   └── ocr.py               # OCR 提示词
├── data/
│   └── rental_knowledge.md  # 租房知识库（RAG 源）
├── utils/
│   ├── auth.py              # API Key 鉴权
│   ├── exceptions.py        # 异常处理
│   └── logger.py            # 日志
└── tests/                   # 测试
```

### 5.3 公开接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/rental/house-chat` | POST | 房源专属问答 |
| `/api/v1/rental/chat` | POST | 通用租房问答 |
| `/api/v1/status` | GET | 健康检查 |

### 5.4 核心能力

- **LLM 对话**：多轮对话，支持上下文记忆
- **RAG 检索增强**：基于租房知识库的检索增强回答
- **会话记忆**：提取租房偏好（如预算、区域偏好），不提取敏感信息
- **OCR**：能力保留，第一版未公开路由

### 5.5 Flask 集成方式

Flask 后端通过 `AIEngineClient`（HTTP 客户端）调用 ai-engine：

- `POST /api/v1/ai/house-chat` → 转发到 `POST /api/v1/rental/house-chat`
- `POST /api/v1/ai/chat` → 转发到 `POST /api/v1/rental/chat`
- Flask 负责鉴权、房源可见性校验、上下文组装、异常转换
- 请求头携带 `X-API-Key` 鉴权

---

## 6. 部署架构

### 6.1 Docker Compose 部署

`deploy/docker-compose.yml` 定义了三类容器：

```
┌─────────────────────────────────────────────────┐
│                  rental_ai_net                   │
│              （bridge 网络）                      │
│                                                   │
│  ┌──────────────┐   ┌──────────────┐             │
│  │    MySQL     │   │   Backend    │             │
│  │  端口 3307   │   │  端口 8000   │             │
│  │  用户: rent  │   │  Gunicorn x4 │             │
│  └──────────────┘   └──────┬───────┘             │
│                            │ HTTP                │
│                            ▼                      │
│                     ┌──────────────┐             │
│                     │  AI Engine   │             │
│                     │  端口 9000   │             │
│                     └──────────────┘             │
└─────────────────────────────────────────────────┘
```

### 6.2 容器说明

| 服务 | 镜像 | 端口 | 说明 |
|------|------|------|------|
| **mysql** | mysql:8.0 | 3307:3306 | 数据库，utf8mb4，时区 Asia/Shanghai |
| **backend** | 自定义 | 8000:8000 | Flask 应用，Gunicorn 4 workers，热重载 |
| **ai-engine** | 自定义 | 9000:9000 | FastAPI 应用（在 ai-engine 的 compose 中定义） |

### 6.3 环境变量

**后端核心环境变量：**

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URI` | 数据库连接串 | `mysql+pymysql://rent_user:rent_pass@mysql:3306/rent_db` |
| `SMTP_*` 系列 | 邮件发送配置 | 需在 `.env` 中配置 |
| `AI_ENGINE_BASE_URL` | AI 引擎地址 | `http://ai-engine:9000` |
| `AI_ENGINE_API_KEY` | AI 引擎鉴权密钥 | `change-me` |
| `JWT_SECRET_KEY` | JWT 签名密钥 | `dev-jwt-secret-key` |

### 6.4 本地开发

**后端（Flask）：**

```bash
cd backend
pip install -r requirements.txt
flask run --host 0.0.0.0 --port 8000
```

**前端：**

```bash
cd frontend
npm install
npm run dev    # Vite 开发服务器，端口自动分配，代理 /api 到 8000
```

**AI 引擎：**

```bash
cd ai-engine
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 9000
```

---

## 7. API 设计规范

### 7.1 通用规范

| 项目 | 规范 |
|------|------|
| 基础路径 | `/api/v1` |
| Content-Type | `application/json` |
| 认证方式 | JWT Bearer Token（`Authorization: Bearer <token>`） |
| 公开接口 | `GET /houses`、`GET /houses/{id}`、`GET /news`、`GET /news/{id}` |
| 时间格式 | UTC ISO 8601 字符串 |
| 金额/面积 | Decimal 按字符串返回 |

### 7.2 URL 命名规范

- 使用名词复数：`/users`、`/houses`、`/contracts`
- 不使用动词：禁止 `/getUser`、`/createHouse`
- 参数位置规范：POST/PUT 用 JSON Body，GET 用 Query，路径参数用 `{id}`

### 7.3 HTTP 方法语义

| 方法 | 含义 |
|------|------|
| GET | 查询 |
| POST | 创建 |
| PUT | 全量更新 |
| PATCH | 部分更新/状态变更 |
| DELETE | 删除 |

### 7.4 路由总表

```
/api/v1/users              # User 模块
/api/v1/auth               # Auth 模块
/api/v1/ai                 # AI 模块
/api/v1/houses             # House 模块
/api/v1/houses/{id}/images # HouseImage 子资源
/api/v1/users/me/avatar    # UserAvatar 子资源
/uploads/<path>            # 上传文件静态访问
/api/v1/news               # News 模块
/api/v1/favorites          # Favorite 模块
/api/v1/appointments       # Appointment 模块
/api/v1/conversations      # Conversation 模块
/api/v1/contracts          # Contract 模块
/api/v1/bills              # Bill 模块
/api/v1/payments           # Payment 模块
/api/v1/repairs            # Repair 模块
/api/v1/complaints         # Complaint 模块
/api/v1/notifications      # Notification 模块
/api/v1/statistics         # Statistics 模块
/api/v1/admin              # Admin 模块
```

---

## 8. 数据流说明

### 8.1 核心业务流

```
租客找房：
  注册/登录 → 搜索房源 → 查看详情 → 咨询房东 → 预约看房
  → 房东确认 → 线下看房 → 达成意向 → 在线签约 → 支付租金
  → 入住后报修/投诉

房东出租：
  注册/登录 → 发布房源 → 上架 → 接收咨询 → 处理预约
  → 确认签约 → 查看租金 → 处理报修

管理员：
  登录后台 → 用户管理 → 投诉处理 → 公告管理 → 统计报表 → 日志查看
```

### 8.2 状态流转

**房源状态：** `draft → listed → offline`

**预约状态：** `pending → confirmed | rejected | cancelled | expired`

**合同状态：** `pending → active → terminated | cancelled | rejected`

**账单状态：** `unpaid → paid | cancelled | overdue`

**报修状态：** `pending → processing → completed → closed`  
（可选分支：`rejected`、`cancelled`、`reopened`）

**投诉状态：** `pending → processing → resolved → closed`  
（可选分支：`rejected`）

**通知状态：** `unread → read`

**公告状态：** `draft → published`

### 8.3 模块间联动

```
Appointment → Contract → Bill → Payment
                ├──→ Repair
                └──→ Complaint
                
状态变更 → Notification（自动） + OperationLog（自动）
```

---

## 9. 项目目录树

```
real-estate215and1/
│
├── backend/                           # Flask 后端
│   ├── app/
│   │   ├── main.py                    # 应用入口
│   │   ├── factory.py                 # App Factory
│   │   ├── core/                      # 基础设施
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   ├── exceptions.py
│   │   │   ├── response.py
│   │   │   └── logging.py
│   │   ├── common/                    # 公共层
│   │   │   ├── base_model.py
│   │   │   ├── base_repository.py
│   │   │   ├── base_schema.py
│   │   │   ├── pagination.py
│   │   │   ├── enums.py
│   │   │   ├── dependencies.py
│   │   │   ├── email.py
│   │   │   └── ai_engine_client.py
│   │   ├── container/                 # DI 容器
│   │   │   ├── repositories.py
│   │   │   └── services.py
│   │   └── modules/                   # 业务模块
│   │       ├── user/                  # 用户
│   │       ├── auth/                  # 认证
│   │       ├── house/                 # 房源
│   │       ├── house_image/           # 房源图片
│   │       ├── user_avatar/           # 用户头像
│   │       ├── favorite/              # 收藏
│   │       ├── appointment/           # 预约
│   │       ├── conversation/          # 消息
│   │       ├── contract/              # 合同
│   │       ├── bill/                  # 账单
│   │       ├── payment/               # 支付
│   │       ├── repair/                # 报修
│   │       ├── complaint/             # 投诉
│   │       ├── news/                  # 公告
│   │       ├── notification/          # 通知
│   │       ├── statistics/            # 统计
│   │       ├── admin/                 # 后台
│   │       ├── ai/                    # AI 代理
│   │       └── operation_log/         # 日志
│   ├── alembic/                       # 数据库迁移
│   ├── tests/                         # 测试
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic.ini
│
├── frontend/                          # Vue 3 前端
│   ├── src/
│   │   ├── api/                       # API 封装
│   │   ├── components/                # 公共组件
│   │   ├── config/                    # 配置（菜单）
│   │   ├── router/                    # 路由
│   │   ├── stores/                    # Pinia 状态
│   │   ├── utils/                     # 工具（Axios、错误处理）
│   │   ├── views/                     # 页面
│   │   ├── App.vue                    # 根组件
│   │   └── main.js                    # 入口
│   ├── vite.config.js
│   └── package.json
│
├── ai-engine/                         # FastAPI AI 引擎
│   ├── api/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── schemas/
│   │   └── dependencies.py
│   ├── services/
│   │   ├── rental_service.py          # 租房对话服务
│   │   ├── llm_service.py
│   │   ├── embedding_service.py
│   │   ├── rag/
│   │   └── session_history.py
│   ├── prompts/                       # 提示词
│   ├── data/                          # RAG 知识库
│   ├── config/
│   ├── utils/
│   ├── tests/
│   └── requirements.txt
│
├── deploy/                            # 部署配置
│   ├── docker-compose.yml
│   └── .env.example
│
├── docs/                              # 文档
│   ├── backend_architecture.md
│   ├── backend_api_spec.md
│   ├── api.md
│   ├── ai_context.md
│   ├── mission.md
│   ├── CHANGELOG.md
│   └── project_architecture.md        # 本文档
│
├── scripts/
│   └── init_db.py
│
├── README.md
└── package.json
```

---

> **文档维护说明**：本文档旨在为接手项目的开发者提供全局架构视角。阅读顺序建议：  
> 先读本文档了解全貌 → [backend_architecture.md](backend_architecture.md) 了解后端细则 → [api.md](api.md) 查看接口详情 → [ai_context.md](ai_context.md) 了解开发上下文。