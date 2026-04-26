# AI Context（Backend Project）

Version: v1.6.2  
Last Updated: 2026-04-26  
Status: User + Auth + House + Favorite + Appointment + Conversation/Message HTTP + Contract 最小闭环已完成；House 列表筛选、参数异常处理、common 公共能力重构（含 BaseRepository）、Alembic 迁移接管与 HTTP smoke test 自动化已完成

------

# 0. 使用说明（给 AI）

这是一个**已完成 User、Auth、House 基础模块的 Flask 后端项目**。

请在回答时遵守：

- ❗不要从零设计项目
- ❗不要更换技术栈
- ❗不要修改现有架构
- ❗不要提前引入复杂权限系统
- ❗不要把 House 状态更新混入普通 update 接口
- ❗在当前结构上继续扩展功能

------

# 1. 项目概览

## 类型

- 课堂项目
- 单人开发后端
- 前后端分离
- 房屋租赁平台

## 技术栈

- Flask（App Factory 模式）
- SQLAlchemy 2.0（ORM）
- MySQL 8.0（Docker）
- PyMySQL
- PyJWT（认证）
- Werkzeug（密码哈希）
- Pydantic v2（数据校验）
- Gunicorn（Docker 启动）

------

# 2. 架构设计（强约束）

## 分层结构

```text
router → service → repository → model
```

## 分层职责

### router

- 解析 request
- schema 校验
- 提取 token
- 调用 service
- 返回统一响应

禁止：

- 不写业务逻辑
- 不操作数据库
- 不写状态流转逻辑
- 不写所有权判断细节

------

### service

- 业务逻辑
- 状态流转
- 所有权校验
- 事务控制（commit / rollback）
- 异常抛出
- ORM → dict 转换

要求：

- 返回 dict（schema-compatible）
- 不返回 ORM 对象

------

### repository

- 数据库 CRUD
- 查询封装

禁止：

- 不 commit
- 不 rollback
- 不写业务逻辑
- 不判断状态流转

------

# 3. 数据库设计

## Session

- 使用 `scoped_session`
- 每次请求通过 `g.db` 获取 session
- session 生命周期由 Flask request hooks 管理

## Base

- 所有模型继承同一个 `Base`
- `Base` 定义在 `app.core.database`

## Alembic 迁移管理

当前项目不再使用：

```python
Base.metadata.create_all(bind=engine)
```

当前规则：

- Flask app 启动阶段不自动建表
- `app.core.database.init_database(app)` 只负责初始化 `engine` 与 `SessionLocal`
- 数据库结构统一由 Alembic migration 管理
- `database.py` 不再 import 任何业务模块 model

常用命令：

```bash
alembic revision --autogenerate -m "xxx"
alembic upgrade head
alembic current
alembic history
alembic downgrade -1
```

------

# 4. Docker 开发环境

## 当前开发模式建议

- 后端代码挂载到容器：

```yaml
volumes:
  - ../backend:/app/backend
```

- Gunicorn 开发阶段使用 1 worker + reload：

```yaml
command: gunicorn -w 1 --reload -b 0.0.0.0:8000 app.main:app
```

原因：

- 挂载代码后，本地改代码容器可以立即看到。
- `--reload` 可自动重新加载 Python 代码。
- `-w 1` 便于开发阶段定位问题并减少 reload 复杂度。

## 部署阶段注意

部署或交付镜像时：

- 不建议挂载代码目录
- 不建议使用 `--reload`
- 可恢复为多 worker，例如：

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

## 常用命令

启动并构建：

```bash
docker compose up -d --build
```

查看状态：

```bash
docker compose ps
```

查看后端日志：

```bash
docker compose logs backend --tail=200
```

停止并删除容器但保留数据库卷：

```bash
docker compose down
```

清空数据库卷（谨慎）：

```bash
docker compose down --volumes
```

------

# 5. 已完成模块

------

## 5.1 User 模块

### 表

```text
users
```

关键字段：

- id
- username（唯一）
- password（hash）
- role
- real_name
- phone
- email
- avatar
- status
- created_at

### 接口

#### POST /api/v1/users

创建用户。

规则：

- 入参：username, password, email（可选）
- 密码使用 Werkzeug hash
- 成功 HTTP 201
- 用户名冲突返回 4009
- 不返回 password

#### GET /api/v1/users

用户列表分页。

规则：

- page 默认 1
- page_size 默认 10
- page_size 最大 100

返回结构：

```text
list / total / page / page_size
```

#### GET /api/v1/users/{id}

用户详情。

- 不存在 → 1001

------

## 5.2 Auth 模块

### POST /api/v1/auth/login

登录接口。

规则：

- 入参：username, password
- 用户不存在 / 密码错误统一返回：
  - code = 1002
  - message = 用户名或密码错误

成功返回：

```json
{
  "token": "xxx",
  "token_type": "Bearer"
}
```

### GET /api/v1/auth/me

获取当前用户。

Header：

```http
Authorization: Bearer <token>
```

错误情况统一返回 1003：

- token 缺失
- token 格式错误
- token 过期
- token 签名失败

成功返回当前用户信息，不含 password。

实现约束：

- router 使用 `get_required_current_user_id()`
- `AuthService.get_current_user(db, current_user_id)` 负责查询当前用户
- 如果 `current_user_id` 对应用户不存在，继续返回 `1003`

------

## 5.3 House 模块

### 当前状态

House 第一版最小闭环已完成，并已手动测试通过。

### 表

```text
houses
```

字段：

- id
- landlord_id
- title
- address
- region
- community
- house_type
- area
- rent
- deposit
- decoration
- floor
- orientation
- description
- status
- created_at
- updated_at
- deleted_at

说明：

- `landlord_id` 由当前 token 解析得到，不允许前端传。
- `deleted_at is not null` 表示逻辑删除。
- 删除后不做物理删除。

### 状态

House 第一版只使用：

```text
draft / listed / offline
```

含义：

| status  | 含义              |
| ------- | ----------------- |
| draft   | 草稿 / 未发布     |
| listed  | 已上架 / 对外展示 |
| offline | 已下架 / 放弃发布 |

### 状态流转

```text
创建：draft
publish：draft/offline -> listed
offline：listed/draft -> offline
DELETE：deleted_at = now，status = offline
```

### 可见性

公共列表：

```http
GET /api/v1/houses
```

只返回：

- 未删除
- status = listed

我的房源：

```http
GET /api/v1/houses?mine=true
```

只返回：

- 当前用户作为 landlord 的未删除房源
- 状态包含 draft/listed/offline
- 不混入公共 listed 房源

详情：

```http
GET /api/v1/houses/{id}
```

规则：

- listed：所有人可看
- draft/offline：只有房东本人可看
- deleted：统一返回 house not found
- 非本人访问非公开房源：返回 house not found

### 接口

#### POST /api/v1/houses

创建房源。

规则：

- 必须登录
- 从 JWT 获取 current_user_id
- 写入 landlord_id
- 默认 status = draft
- 不允许前端传 landlord_id/status

#### GET /api/v1/houses

公共房源列表。

规则：

- 不需要登录
- 只返回 listed + 未删除房源
- 分页返回 list/total/page/page_size
- 默认按 id DESC
- 支持筛选参数：
  - region
  - house_type
  - min_rent
  - max_rent
  - keyword
  - min_area
  - max_area
- `keyword` 匹配 `title/address/community/description`
- 支持筛选和分页同时使用

#### GET /api/v1/houses?mine=true

我的房源。

规则：

- 必须登录
- 只返回当前用户自己的房源
- 包含 draft/listed/offline
- 不返回 deleted
- 支持与公共列表一致的筛选参数：
  - region
  - house_type
  - min_rent
  - max_rent
  - keyword
  - min_area
  - max_area
- `keyword` 匹配 `title/address/community/description`
- 支持筛选和分页同时使用

#### GET /api/v1/houses/{id}

房源详情。

规则：

- listed 公开可见
- 非 listed 仅房东本人可见
- deleted 或无权访问返回 2001

#### PUT /api/v1/houses/{id}

更新房源资料。

规则：

- 必须登录
- 只能更新自己的未删除房源
- 不允许修改 landlord_id
- 不允许修改 status
- 请求体包含 status 时按参数错误处理

#### PATCH /api/v1/houses/{id}/publish

发布房源。

规则：

- 必须登录
- 只能操作自己的未删除房源
- draft/offline -> listed

#### PATCH /api/v1/houses/{id}/offline

下架房源。

规则：

- 必须登录
- 只能操作自己的未删除房源
- listed/draft -> offline
- draft -> offline 表示“放弃发布”

#### DELETE /api/v1/houses/{id}

逻辑删除房源。

规则：

- 必须登录
- 只能删除自己的未删除房源
- 设置 deleted_at
- 同时 status = offline
- 删除后不出现在任何列表和详情中
- 删除后不可再次 update/publish/offline/delete

------

## 5.4 Favorite 模块

### 当前状态

Favorite 第一版最小闭环已完成。

### 表

```text
favorites
```

字段：

- id
- user_id
- house_id
- created_at

说明：

- `user_id + house_id` 唯一约束，禁止重复收藏。
- Favorite 不引入状态字段。
- Favorite 不改变 House 的状态流转。

### 接口

#### POST /api/v1/favorites

收藏房源。

规则：

- 必须登录
- 从 JWT 获取 `current_user_id`
- 只允许收藏未删除且 `listed` 的房源
- 房源不存在、已删除、非 `listed`，统一返回 `2001`
- 重复收藏返回 `4009`
- 成功返回：
  - `house_id`
  - `favorite_created_at`
  - `house`

#### GET /api/v1/favorites

我的收藏列表。

规则：

- 必须登录
- 只返回当前用户自己的收藏
- 只返回当前仍 `listed` 且未删除的房源
- 分页返回 `list/total/page/page_size`
- 列表项结构：
  - `house_id`
  - `favorite_created_at`
  - `house`

#### DELETE /api/v1/favorites/{house_id}

取消收藏。

规则：

- 必须登录
- 只删除当前用户自己的收藏
- 若当前用户没有收藏该房源，返回 `2101 收藏不存在`



------

# 6. 安全设计

## 密码

使用 Werkzeug：

- generate_password_hash
- check_password_hash

## JWT

算法：

```text
HS256
```

payload 固定结构：

```json
{
  "sub": "str(user_id)",
  "exp": "timestamp"
}
```

说明：

- sub 必须为字符串类型 user_id
- exp 必须存在
- 当前 token_type 固定为 Bearer

已实现 helper：

- `extract_bearer_token(header)`
- `get_current_user_id_from_token(token)`

## 认证 Helper

当前项目已新增最小认证 helper，用于统一 router 层的 token 解析逻辑。

文件位置：

```
app/common/dependencies.py
```

当前提供两个函数：

- `get_required_current_user_id()`
- `get_optional_current_user_id()`

#### 规则说明

`get_required_current_user_id()` 用于必须登录接口：

- 从 `Authorization` 请求头提取 Bearer token
- 解析 JWT
- 返回 `current_user_id`
- token 缺失、格式错误、过期、签名失败时统一返回 `1003 未登录`

`get_optional_current_user_id()` 用于可选登录接口：

- 没有 `Authorization` 时返回 `None`
- 有 `Authorization` 时尝试解析 token
- token 合法时返回 `current_user_id`
- token 无效时仍返回 `1003 未登录`

#### 当前使用位置

已替换以下 router 中重复的 token 解析代码：

- `auth/router.py`
- `house/router.py`

#### 使用约束

- router 负责调用 helper 获取 `current_user_id`
- service 显式接收 `current_user_id` 或 `landlord_id`
- service 不直接读取 `request`
- service 不直接读取 `g.current_user_id`
- 当前不实现完整 `login_required` 装饰器
- 当前不实现 role 权限系统
- JWT 解析逻辑仍复用 `app/core/security.py`

#### 当前认证分工

- `security.py`：负责 token 生成、token 提取、JWT 解码、密码校验
- `dependencies.py`：负责在 router 层获取当前用户 id
- `router.py`：负责选择必须登录或可选登录
- `service.py`：负责根据当前用户 id 执行业务逻辑和所有权校验
- `AuthService.get_current_user()`：按 `current_user_id` 查询用户，而不是接收 token

------

## 6.1 参数校验异常处理

当前项目已统一处理 Pydantic 参数校验异常。

规则：

- 捕获 `pydantic.ValidationError`
- 统一返回：
  - `code = 3001`
  - `message = bad request`
  - `data = error.errors()`
- 即使 `ValidationError.errors()` 中包含原始异常对象，也必须先规范化为可 JSON 序列化的数据
- 不允许回退为 Flask 默认 HTML 500 页面

当前已确认修复的场景：

- `GET /api/v1/houses?min_rent=3000&max_rent=1000`
- `GET /api/v1/houses?min_area=100&max_area=50`

以上请求现在都返回统一 JSON `3001 bad request`。

------



# 7. 错误码体系

| code | 含义                  |
| ---- | --------------------- |
| 0    | success               |
| 1001 | 用户不存在            |
| 1002 | 用户名或密码错误      |
| 1003 | 未登录 / token 无效   |
| 2001 | 房源不存在 / 无权访问 |
| 2101 | 收藏不存在            |
| 2201 | 预约不存在            |
| 2202 | 非法预约状态          |
| 2203 | 不能预约自己的房源    |
| 2204 | 预约时间必须是未来时间 |
| 2301 | 会话不存在            |
| 2302 | 不能联系自己的房源    |
| 2401 | 合同不存在            |
| 2402 | 非法合同状态          |
| 2403 | 不能和自己的房源签合同 |
| 2404 | 合同时间不合法        |
| 2405 | 房源已有生效合同      |
| 3001 | 参数错误              |
| 4004 | 路由不存在            |
| 4009 | 资源冲突              |
| 5000 | 系统错误              |

------

# 8. 当前未实现（刻意未做）

以下功能当前不实现：

- 完整 login_required 装饰器体系
- 完整 RBAC 权限控制
- refresh token
- token 黑名单
- 房源图片 / 视频
- 房源审核流
- 账单 / 支付
- 报修 / 投诉
- 管理后台

------

# 9. 当前阶段

```text
User + Auth + House + Favorite + Appointment + Conversation/Message HTTP + Contract 最小闭环已完成，House 列表筛选、参数异常处理、common 公共能力重构、Alembic 迁移接管与 HTTP smoke test 自动化已完成
```

系统能力：

- 用户注册
- 用户登录
- JWT 认证
- 当前用户获取
- 房源创建
- 房源公共列表
- 我的房源列表
- 房源列表筛选（region / house_type / rent / area / keyword）
- 房源详情
- 房源更新
- 房源发布
- 房源下架
- 房源逻辑删除
- 收藏房源
- 我的收藏列表
- 取消收藏
- 创建会话
- 会话列表
- 消息列表
- 发送消息
- 标记消息已读
- 创建合同
- 合同列表
- 合同详情
- 确认合同
- 拒绝合同
- 取消合同
- 终止合同
- 最小所有权校验
- 统一响应 + 异常体系
- pytest + requests 真实 HTTP smoke test

------

# 10. 已验证测试项

House 模块已验证：

- 创建房源默认 `draft`
- 公共列表不显示 `draft`
- `mine=true` 可以看到自己的 `draft`
- `publish` 后状态变为 `listed`
- `listed` 出现在公共列表
- `offline` 后公共列表不可见
- `mine=true` 仍可见自己的 `offline`
- `DELETE` 后公共列表不可见
- `DELETE` 后 `mine=true` 不可见
- `DELETE` 后详情返回 `2001`
- 非本人操作返回 `2001`
- `PUT` 不能修改 `status`
- `mine=true` 不带 token 返回 `1003`
- House 列表支持按 `region`
- House 列表支持按 `house_type`
- House 列表支持按 `min_rent/max_rent`
- House 列表支持按 `min_area/max_area`
- House 列表支持按 `keyword(title/address/community/description)`
- 筛选参数可与分页同时使用
- `min_rent > max_rent` 返回 `3001`
- `min_area > max_area` 返回 `3001`
- House 参数校验失败不再返回 Flask 默认 HTML 500
- `ValidationError` 统一返回 JSON `3001 bad request`
- 收藏未删除且 `listed` 房源成功
- 收藏不存在 / 已删除 / 非 `listed` 房源返回 `2001`
- 重复收藏返回 `4009`
- 我的收藏列表只返回当前仍 `listed` 且未删除的房源
- 取消未收藏房源返回 `2101`

HTTP 自动化 smoke test 已验证：

- 测试文件：`backend/tests/api/test_smoke_flow.py`
- 测试方式：`pytest + requests`
- 默认目标：`http://127.0.0.1:8000`
- 可通过环境变量 `API_BASE_URL` 覆盖目标地址
- 覆盖完整业务主流程：
  - 注册房东
  - 注册租客
  - 双方登录
  - 房东创建并发布房源
  - 租客收藏房源
  - 租客创建预约
  - 房东确认预约
  - 租客创建会话
  - 租客发送消息
  - 房东查看会话列表并校验目标会话 `unread_count`
  - 房东标记会话已读
  - 房东基于 confirmed appointment 创建合同
  - 租客确认合同
  - 查询合同详情并确认 `status = active`
- 关键断言已覆盖：
  - `house.status == listed`
  - `appointment.status == confirmed`
  - `message.content` 保存前已 `strip`
  - `read.updated >= 1`
  - `contract.status == active`
- 运行命令：

```bash
cd backend
pytest tests/api/test_smoke_flow.py -q
```

或：

```bash
set API_BASE_URL=http://127.0.0.1:8000
pytest tests/api/test_smoke_flow.py -q
```

------

# 11. 下一步开发方向

建议下一步优先做：

```text
Bill / Payment
```

原因：

- Appointment、Conversation 与 Contract 已经完成最小闭环
- 可以直接承接租赁业务主流程
- 仍然不需要引入复杂权限系统

------

# 12. 对 AI 的约束（必须遵守）

- 不改变架构
- 不引入新框架
- 不修改 JWT 结构
- 不修改现有错误码语义
- 不提前设计复杂权限系统
- 不把 status 放进普通 update
- 不让前端传 landlord_id
- 不物理删除 House
- 按现有风格继续扩展模块

------

# 13. 新会话使用方式

新会话时：

1. 粘贴本文件
2. 说明需求，例如：

```text
基于这个项目，帮我继续做 Search 房源筛选增强模块。
```


------

# 14. v1.4 Appointment 与 v1.4.1 common 重构补充

> 本节为当前最新补充，保留前文历史内容。若前文仍出现“预约未实现”等旧描述，以本节为准。

## 14.1 当前最新状态

当前后端已完成：

```text
User + Auth + House + Favorite + Appointment + Conversation/Message HTTP + Contract 最小闭环
```

同时已完成 common 公共能力替换重构：

- `app/common/base_model.py`
- `app/common/base_repository.py`
- `app/common/base_schema.py`
- `app/common/pagination.py`
- `app/common/enums.py`

同时已补充自动化接口冒烟测试：

- `backend/tests/api/test_smoke_flow.py`
- `backend/tests/api/conftest.py`

当前下一步建议：

```text
Bill / Payment
```

也可以根据课程展示需要，优先做：

```text
Repair / Complaint
```

------

## 14.2 Appointment 预约看房模块

### 当前状态

Appointment 第一版最小闭环已完成。

### 表

```text
appointments
```

字段：

- id
- house_id
- tenant_id
- landlord_id
- appointment_time
- remark
- status
- created_at
- updated_at

说明：

- `tenant_id` 从当前 token 解析得到。
- `landlord_id` 从 House 表读取，前端不允许传。
- `appointment_time` 表示租客期望看房时间。
- Appointment 不改变 House 状态。
- 第一版不做房东可预约时间段管理、日历、通知、改期、评价、定时任务。

### 状态

Appointment 第一版状态：

```text
pending / confirmed / rejected / cancelled / expired
```

含义：

| status    | 含义       |
| --------- | ---------- |
| pending   | 待房东确认 |
| confirmed | 房东已确认 |
| rejected  | 房东已拒绝 |
| cancelled | 租客已取消 |
| expired   | 已过期     |

重要约束：

- 数据库正常业务流转只主动写入 `pending / confirmed / rejected / cancelled`。
- `expired` 第一版不通过定时任务自动写回数据库。
- `expired` 只通过 `display_status` 和操作校验体现。
- 如果数据库 `status = pending` 且 `appointment_time < 当前时间`，返回时 `display_status = expired`。
- 其他情况 `display_status = status`。

### 接口

#### POST /api/v1/appointments

创建预约。

规则：

- 必须登录。
- 请求体包含 `house_id`、`appointment_time`、可选 `remark`。
- 当前用户作为 `tenant_id`。
- `landlord_id` 从 House 表读取。
- 只能预约未删除且 `listed` 的房源。
- 不能预约自己的房源。
- `appointment_time` 必须是未来时间。
- 创建后 `status = pending`。
- 房源不存在、已删除、非 `listed`，统一返回 `2001`。

#### GET /api/v1/appointments

查看预约列表。

规则：

- 必须登录。
- 返回与当前用户相关的预约：`tenant_id == current_user_id OR landlord_id == current_user_id`。
- 支持分页：`page`、`page_size`。
- 返回 `list / total / page / page_size`。
- 列表项包含预约字段、`status`、`display_status`、`relation_role`、`house` 摘要。

`relation_role`：

- 当前用户是租客：`tenant`
- 当前用户是房东：`landlord`

#### PATCH /api/v1/appointments/{id}/confirm

房东确认预约。

规则：

- 必须登录。
- 只有房东本人可以确认。
- 仅允许有效 `pending -> confirmed`。
- 已过期 pending 不允许确认，返回 `2202`。
- 非房东或预约不存在，返回 `2201`。

#### PATCH /api/v1/appointments/{id}/reject

房东拒绝预约。

规则：

- 必须登录。
- 只有房东本人可以拒绝。
- 仅允许有效 `pending -> rejected`。
- 已过期 pending 不允许拒绝，返回 `2202`。
- 非房东或预约不存在，返回 `2201`。

#### PATCH /api/v1/appointments/{id}/cancel

租客取消预约。

规则：

- 必须登录。
- 只有租客本人可以取消。
- 允许 `pending -> cancelled`、`confirmed -> cancelled`。
- `rejected / cancelled / expired` 不允许取消，返回 `2202`。
- 非租客或预约不存在，返回 `2201`。

### Appointment 错误码

| code | 含义                   |
| ---- | ---------------------- |
| 2201 | 预约不存在             |
| 2202 | 非法预约状态           |
| 2203 | 不能预约自己的房源     |
| 2204 | 预约时间必须是未来时间 |

### Appointment 已验证

- 未登录访问 Appointment 接口返回 `1003`。
- 租客创建预约成功，状态为 `pending`。
- 房东可确认自己的有效 pending 预约。
- 房东可拒绝自己的有效 pending 预约。
- 租客可取消自己的 pending / confirmed 预约。
- 房东不能预约自己的房源，返回 `2203`。
- 非未来时间预约返回 `2204`。
- 预约不存在 / 越权操作返回 `2201`。
- 非法状态流转返回 `2202`。
- 预约列表返回 `status`、`display_status`、`relation_role`、`house`。

------

## 14.3 common 公共能力重构

当前已完成 common 公共能力替换重构。

### 新增或完善文件

```text
app/common/base_model.py
app/common/base_repository.py
app/common/base_schema.py
app/common/pagination.py
app/common/enums.py
```

### base_model.py

提供：

- `BaseModel`
- `SoftDeleteMixin`

`BaseModel` 包含：

- `id`
- `created_at`
- `updated_at`

`SoftDeleteMixin` 包含：

- `deleted_at`

当前 model 继承关系：

| Model       | 继承关系                            |
| ----------- | ----------------------------------- |
| User        | `User(BaseModel)`                   |
| House       | `House(BaseModel, SoftDeleteMixin)` |
| Favorite    | `Favorite(BaseModel)`               |
| Appointment | `Appointment(BaseModel)`            |

约束：

- 所有 model 仍使用同一个 `app.core.database.Base`。
- 不在任何 model 中重新 `declarative_base()`。
- `deleted_at` 只给 House 使用。
- User / Favorite / Appointment 不新增 `deleted_at`。
- Favorite / Appointment 通过 `BaseModel` 统一拥有 `updated_at`。
- 未修改任何 `__tablename__`。
- 未修改已有字段名。
- 未改变接口响应结构。

### base_repository.py

提供：

- `BaseRepository[T]`

当前只承接最基础的数据访问能力：

- `create(db, obj)`
- `get_by_id(db, obj_id)`
- `delete(db, obj)`
- `count_all(db)`
- `list_page(db, offset, limit)`

约束：

- 使用 SQLAlchemy 2.0 `select` 风格
- 不 `commit`
- 不 `rollback`
- 不读取 `g / request / current_user`
- 不处理业务状态
- 不处理软删除
- 不处理权限
- 不组装分页响应结构
- 不把复杂业务查询下沉到 BaseRepository

当前已逐步接入继承的 repository：

- `UserRepository`
- `FavoriteRepository`
- `AppointmentRepository`
- `ConversationRepository`
- `MessageRepository`
- `ContractRepository`
- `HouseRepository`（仅复用基础 `create/get_by_id`，保留原有 `listed / deleted_at / mine / filter` 查询）

说明：

- 本轮是等价重构，不改变接口返回、错误码、事务边界和业务查询条件
- `MessageRepository` 仅删除了与基类完全等价的 `create`，其余消息查询和已读更新逻辑保持不变

### base_schema.py

提供：

- `BaseSchema`

默认配置：

```text
from_attributes=True
extra="forbid"
```

说明：

- Read schema 可直接复用 `from_attributes=True`。
- 对原本不强制 `extra="forbid"` 的 schema，显式覆盖配置，保持旧行为。
- 不改变接口请求校验语义。

### pagination.py

提供：

- `get_offset(page, page_size)`
- `build_page_result(items, total, page, page_size)`

用于统一列表返回：

```json
{
  "list": [],
  "total": 0,
  "page": 1,
  "page_size": 10
}
```

已用于：

- User 列表
- House 列表
- Favorite 列表
- Appointment 列表

### enums.py

------

## 14.4 Conversation / Message HTTP 消息模块

### 当前状态

Conversation / Message 第一版 HTTP 非实时消息模块已完成。

第一版明确不做：

- WebSocket
- Redis
- 实时推送
- 在线状态

### 表

```text
conversations
messages
```

`conversations` 字段：

- id
- house_id
- tenant_id
- landlord_id
- created_at
- updated_at

`messages` 字段：

- id
- conversation_id
- sender_id
- content
- created_at
- updated_at
- read_at

约束：

- `tenant_id + landlord_id + house_id` 唯一
- 同一租客围绕同一房源联系同一房东，只能有一个会话
- 已存在会话时，`POST /api/v1/conversations` 直接返回已有会话
- 消息内容保存前会做 `content.strip()`
- 成功发送消息后，会同步刷新 `Conversation.updated_at`

### 接口

```text
POST  /api/v1/conversations
GET   /api/v1/conversations
GET   /api/v1/conversations/{id}/messages
POST  /api/v1/conversations/{id}/messages
PATCH /api/v1/conversations/{id}/read
```

### 规则

- 所有接口必须登录
- 创建会话只允许针对未删除且 `listed` 的房源
- 当前用户不能联系自己的房源
- 房源不存在、已删除、非 `listed` 时创建会话返回 `2001`
- 房源下架或删除后不能再新建会话
- 已存在的会话和消息记录不会因房源下架或删除自动删除
- 会话列表只返回当前用户参与的会话
- 会话列表返回 `house` 摘要、`last_message`、`last_message_at`、`unread_count`
- 会话列表默认按 `Conversation.updated_at DESC, id DESC`
- 消息列表仅参与者可查看，默认按 `created_at ASC, id ASC`
- `PATCH /read` 只标记 `sender_id != current_user_id AND read_at IS NULL` 的消息

### 错误码

| code | 含义               |
| ---- | ------------------ |
| 2301 | 会话不存在         |
| 2302 | 不能联系自己的房源 |

继续复用：

- `1003` 未登录
- `2001` 房源不存在
- `3001` 参数错误
- `5000` 系统错误

提供简单字符串常量类：

- `HouseStatus`
  - `DRAFT = "draft"`
  - `LISTED = "listed"`
  - `OFFLINE = "offline"`
- `AppointmentStatus`
  - `PENDING = "pending"`
  - `CONFIRMED = "confirmed"`
  - `REJECTED = "rejected"`
  - `CANCELLED = "cancelled"`
  - `EXPIRED = "expired"`

说明：

- 仅收口重复状态字符串。
- 不使用复杂 Python Enum 行为。
- 数据库存储值仍是字符串。
- 接口返回值仍是字符串。
- 不改变状态流转规则。

------

## 14.5 Contract 合同模块

### 当前状态

Contract 第一版最小闭环已完成。

第一版明确不做：

- PDF
- 电子签章
- 真实支付
- 真实法律合同

### 表

```text
contracts
```

字段：

- id
- house_id
- tenant_id
- landlord_id
- appointment_id
- start_date
- end_date
- monthly_rent
- deposit
- status
- remark
- created_at
- updated_at

说明：

- Contract 第一版必须基于 `confirmed appointment` 创建。
- 前端不允许传 `house_id / tenant_id / landlord_id`。
- 后端通过 `appointment_id` 自动确定 `house_id / tenant_id / landlord_id`。
- `appointment_id` 第一版必填，不可为空。
- `appointment_id` 第一版不加唯一约束。

### 状态

Contract 第一版状态：

```text
pending / active / rejected / cancelled / terminated
```

含义：

| status     | 含义                    |
| ---------- | ----------------------- |
| pending    | 房东已创建，等待租客确认 |
| active     | 租客已确认，合同生效    |
| rejected   | 租客拒绝该合同          |
| cancelled  | 房东在生效前取消        |
| terminated | 生效后被房东终止        |

允许流转：

- `create -> pending`
- `pending -> active`
- `pending -> rejected`
- `pending -> cancelled`
- `active -> terminated`

终态：

- `rejected`
- `cancelled`
- `terminated`

### 接口

```text
POST  /api/v1/contracts
GET   /api/v1/contracts
GET   /api/v1/contracts/{id}
PATCH /api/v1/contracts/{id}/confirm
PATCH /api/v1/contracts/{id}/reject
PATCH /api/v1/contracts/{id}/cancel
PATCH /api/v1/contracts/{id}/terminate
```

### 规则

- 所有接口必须登录
- 创建合同仅房东可调用
- 创建合同必须基于当前房东自己的 `confirmed appointment`
- appointment 不存在或不属于当前房东，返回 `2201`
- appointment 状态不是 `confirmed`，返回 `2402`
- appointment 对应 house 不存在或已删除，返回 `2001`
- `tenant_id == landlord_id`，返回 `2403`
- 同一 `appointment_id` 同时只能有一个 `pending` 合同
- 如果同一 `appointment_id` 已有 `pending` 合同，再创建返回 `4009`
- 同一 `house_id` 同时只能有一个 `active` 合同
- `active` 后第一版不修改 `House.status`
- 非参与者访问详情、确认、拒绝、取消、终止统一返回 `2401`

### 错误码

| code | 含义                    |
| ---- | ----------------------- |
| 2401 | 合同不存在              |
| 2402 | 非法合同状态            |
| 2403 | 不能和自己的房源签合同  |
| 2404 | 合同时间不合法          |
| 2405 | 房源已有生效合同        |

继续复用：

- `1003` 未登录
- `2001` 房源不存在
- `2201` 预约不存在
- `3001` 参数错误
- `4009` 资源冲突
- `5000` 系统错误
