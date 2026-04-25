# AI Context（Backend Project）

Version: v1.1  
Last Updated: 2026-04-23  
Status: User + Auth + House 最小闭环已完成

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

## 开发阶段自动建表

当前开发阶段使用：

```python
Base.metadata.create_all(bind=engine)
```

执行位置：

- `app.core.database.init_database(app)`
- 仅在 `ENV == "development"` 时执行

注意：

- `create_all()` 只能创建不存在的表，不能安全修改已有表结构。
- 自动建表前必须显式 import model，例如：

```python
from importlib import import_module

import_module("app.modules.user.model")
import_module("app.modules.house.model")
```

- 不能在 `init_database(app)` 内直接写 `import app.modules.house.model` 并继续使用参数名 `app`，否则可能覆盖 Flask app 变量。
- 后续正式迁移阶段再考虑 Alembic。

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
- `-w 1` 避免开发阶段多个 worker 同时执行自动建表逻辑。

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

#### GET /api/v1/houses?mine=true

我的房源。

规则：

- 必须登录
- 只返回当前用户自己的房源
- 包含 draft/listed/offline
- 不返回 deleted

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

------



# 7. 错误码体系

| code | 含义                  |
| ---- | --------------------- |
| 0    | success               |
| 1001 | 用户不存在            |
| 1002 | 用户名或密码错误      |
| 1003 | 未登录 / token 无效   |
| 2001 | 房源不存在 / 无权访问 |
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
- Alembic 迁移
- 房源图片 / 视频
- 房源审核流
- 收藏
- 预约
- 聊天
- 合同
- 账单 / 支付
- 报修 / 投诉
- 管理后台

------

# 9. 当前阶段

```text
User + Auth + House 最小闭环已完成
```

系统能力：

- 用户注册
- 用户登录
- JWT 认证
- 当前用户获取
- 房源创建
- 房源公共列表
- 我的房源列表
- 房源详情
- 房源更新
- 房源发布
- 房源下架
- 房源逻辑删除
- 最小所有权校验
- 统一响应 + 异常体系

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

------

# 11. 下一步开发方向

建议下一步优先做：

```text
Search / 房源筛选增强
```

原因：

- 和 House 强相关
- 只读为主，风险低
- 不引入复杂状态
- 可以马上提升前端可用性

建议筛选项：

- region
- house_type
- min_rent
- max_rent
- keyword（title/address/community）

之后再考虑：

```text
Favorite → Appointment → Conversation → Contract/Bill/Payment
```

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