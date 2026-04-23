# Changelog

## v1.0 - 2026-04-22

### 🎉 Initial Release（基础版本完成）

------

## Added

### Core 基础层

- 实现配置系统（config.py）
- 实现 SQLAlchemy 数据库连接与 session 管理（g.db）
- 实现统一响应结构（success / fail）
- 实现统一异常体系（AppException 及子类）
- 实现文件日志系统（仅写文件，不输出控制台）

------

### User 模块（最小读写闭环）

- 用户表（users）建模完成
- 支持用户创建：
  - POST /api/v1/users
  - 密码使用 Werkzeug 哈希
- 支持用户查询：
  - GET /api/v1/users/
- 支持分页查询：
  - GET /api/v1/users
  - 默认 page=1, page_size=10
  - 限制 page_size <= 100
- 用户名唯一约束
- 返回数据不包含 password 字段

------

### Auth 模块（最小认证闭环）

- 实现登录接口：
  - POST /api/v1/auth/login
- 实现当前用户接口：
  - GET /api/v1/auth/me
- 接入 JWT 认证（PyJWT）
  - payload 包含 sub + exp
  - sub = user_id（字符串）
- 支持 Bearer Token 认证
- 实现 token 校验（签名 + 过期）

------

## Changed

### 认证错误统一策略

- 登录失败（用户不存在 / 密码错误）统一返回：
  - code = 1002
  - message = 用户名或密码错误

### token 错误统一策略

以下情况统一返回 1003：

- token 缺失
- token 格式错误
- token 签名失败
- token 过期

------

## Fixed

- 修复 created_at 无默认值导致插入失败的问题
- 修复 MySQL + PyMySQL 在 caching_sha2_password 下依赖 cryptography 的问题
- 修复 Docker 环境下数据库连接与权限问题

------

## Design Decisions（重要设计决策）

- 采用分层架构：
  - router → service → repository → model
- service 负责事务控制（commit / rollback）
- repository 不允许 commit
- service 不返回 ORM 对象，仅返回 dict
- 使用 g.db 管理 request 级 session
- 使用 PyJWT 而非 session 机制（无状态认证）

------

## Notes

- 当前未实现：
  - login_required（认证中间件）
  - 权限系统（role 控制）
  - refresh token / token 黑名单
  - Alembic 数据库迁移
- 当前阶段：
  - ✅ User + Auth 最小闭环已完成
  - 🚧 下一步：House（房源模块）