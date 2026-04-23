# AI Context（Backend Project）

Version: v1.0
Last Updated: 2026-04-22
Status: User + Auth 最小闭环已完成

------

# 0. 使用说明（给 AI）

这是一个**已完成基础模块的 Flask 后端项目**。

请在回答时遵守：

- ❗不要从零设计项目
- ❗不要更换技术栈
- ❗不要修改现有架构
- ❗在当前结构上继续扩展功能

------

# 1. 项目概览

## 类型

- 单人开发后端
- 前后端分离

## 技术栈

- Flask（App Factory 模式）
- SQLAlchemy 2.0（ORM）
- MySQL（Docker）
- PyJWT（认证）
- Werkzeug（密码哈希）
- Pydantic（数据校验）

------

# 2. 架构设计（强约束）

## 分层结构

```
router → service → repository → model
```

## 分层职责

### router

- 解析 request
- schema 校验
- 调用 service
- 返回统一响应

❌ 不写业务逻辑
❌ 不操作数据库

------

### service

- 业务逻辑
- 事务控制（commit / rollback）
- 异常抛出

✔ 返回 dict（schema-compatible）
❌ 不返回 ORM 对象

------

### repository

- 数据库 CRUD

❌ 不 commit
❌ 不写业务逻辑

------

# 3. 数据库设计

## Session

- 使用 scoped_session
- 每次请求通过 `g.db` 获取
- 生命周期由 Flask request 管理

## Base

- 所有模型继承 `Base`

------

# 4. 已完成模块

------

## 4.1 User 模块

### 表

```
users
```

关键字段：

- id
- username（唯一）
- password（hash）
- role
- status
- created_at

------

### 接口

#### POST /api/v1/users

创建用户

- 入参：username, password
- 密码：Werkzeug hash
- 成功：HTTP 201
- 冲突：4009
- 不返回 password

------

#### GET /api/v1/users

用户列表（分页）

- 默认：
  - page = 1
  - page_size = 10
- 限制：
  - page >= 1
  - page_size <= 100

返回结构：

```
list / total / page / page_size
```

------

#### GET /api/v1/users/

单用户查询

- 不存在 → 1001

------

## 4.2 Auth 模块

------

### POST /api/v1/auth/login

登录接口

- 入参：username, password
- 用户不存在 / 密码错误：
  - 统一返回 1002
  - message = “用户名或密码错误”

成功返回：

```
{
  token,
  token_type = "Bearer"
}
```

------

### GET /api/v1/auth/me

当前用户接口

Header：

```
Authorization: Bearer <token>
```

错误情况统一：

- token 缺失
- token 格式错误
- token 过期
- token 签名失败

→ 返回 1003

成功返回当前用户信息（不含 password）

------

# 5. 安全设计

## 密码

使用 Werkzeug：

- generate_password_hash
- check_password_hash

------

## JWT

### 算法

```
HS256
```

### payload（固定结构）

```
{
  sub: str(user_id),
  exp: timestamp
}
```

说明：

- sub 必须为字符串类型 user_id
- exp 必须存在

------

# 6. 错误码体系

| code | 含义                |
| ---- | ------------------- |
| 0    | success             |
| 3001 | 参数错误            |
| 1001 | 用户不存在          |
| 1002 | 用户名或密码错误    |
| 1003 | 未登录 / token 无效 |
| 4009 | 资源冲突            |
| 5000 | 系统错误            |

------

# 7. 当前未实现（刻意未做）

以下功能当前**不实现**：

- login_required（认证中间件）
- 权限控制（role）
- refresh token
- token 黑名单
- Alembic 迁移

------

# 8. 当前阶段

```
User + Auth 最小闭环已完成
```

系统能力：

- 用户注册
- 用户登录
- JWT 认证
- 当前用户获取
- 分页查询
- 统一响应 + 异常体系

------

# 9. 下一步开发方向

下一阶段：

```
House（房源模块）
```

要求：

- 复用现有分层结构
- 部分接口需要登录
- 到此阶段再考虑抽 login_required
- 不破坏现有 auth 设计

------

# 10. 对 AI 的约束（必须遵守）

- 不改变架构
- 不引入新框架
- 不修改错误码
- 不改变 JWT 结构
- 不提前设计复杂权限系统
- 按现有风格扩展模块

------

# 11. 使用方式

新会话时：

1. 粘贴本文件
2. 说明需求，例如：

```
基于这个项目，帮我设计 house 模块
```

------