# Changelog

## v1.15.0 - 2026-05-03

### Added

#### Auth 邮箱验证码注册与登录

- 新增 `email_verification_codes` 表，用于保存邮箱验证码哈希、业务类型、过期时间和使用状态
- 新增 Auth 接口：
  - `POST /api/v1/auth/email/code`
  - `POST /api/v1/auth/email/register`
  - `POST /api/v1/auth/email/login`
- 新增 `app/common/email.py`，使用标准库 `smtplib` 发送验证码邮件
- 新增 `backend/tests/service/test_auth_service.py`，覆盖邮箱验证码发送、注册、登录和回滚场景
- 新增 `backend/.env.example` 中的 SMTP 和验证码配置示例

### Changed

#### AuthService 主导邮箱验证码流程

- 邮箱验证码发送、邮箱验证码注册、邮箱验证码登录全部收口到 `AuthService`
- `AuthService.send_email_code(...)`、`email_register(...)`、`email_login(...)` 统一使用 service 层 `try / commit / rollback` 模板
- 验证码只保存哈希，不明文入库
- 发送邮件失败时整笔事务回滚，不在数据库里残留验证码记录
- 邮箱验证码注册由 `AuthService` 直接构造 `User` ORM，并调用 `UserRepository.create(...)` 落库
- `UserService` 不参与邮箱验证码注册 / 登录流程

#### email 规范化与唯一约束

- 所有通过 email 查询或入库的位置统一先执行：
  - `strip()`
  - `lower()`
  - 空字符串转 `None`
- `users.email` 增加唯一索引
- migration 在加唯一索引前会先把历史 `users.email = ''` 清洗为 `NULL`
- 如果存在重复的非空 email，migration 允许失败并提示人工清理
- 旧 `/api/v1/users` 注册流程补充 email normalize 和重复 email 校验，以兼容唯一约束

#### username 自动生成

- 邮箱验证码注册不再要求前端传 `username`
- 后端统一生成 `user_<random_hex>` 风格用户名
- 优先使用 `secrets.token_hex(4)`，最多重试 5 次
- 极端冲突时使用更长随机串兜底

### Added Migration

- `c1e2f3a4b5c6_add_email_verification_codes_table.py`

### Notes

- 本次继续使用 MySQL 保存验证码，不引入 Redis、Celery、APScheduler 或异步队列
- 当前不做过期验证码定时清理；后续可增加 admin-only 清理接口或独立脚本
- 当前仓库原有用户名密码注册接口仍为 `POST /api/v1/users`

## v1.14.2 - 2026-05-02

### Changed

#### Notification 批量接口彻底收口

- `NotificationService` 只保留 `create_notification(...)` 一个创建入口
- 删除 `create_notifications(...)`
- 单用户与多用户通知统一走 `NotificationRepository.bulk_create(...)`
- `POST /api/v1/notifications` 保持单用户 HTTP 接口不变，由 router 从返回列表中解包 `result[0]`
- `News / Payment / Repair / Complaint / Contract / Bill / Admin` 全部迁移到同一个批量通知 service 接口
- 删除旧的业务侧循环单发路径，不再保留批量与单条并存

#### 操作日志审计能力补充

- 新增 `operation_logs` 表与 `operation_log` 模块
- 新增 `GET /api/v1/admin/logs` 后台日志分页查询接口
- `Repair / Complaint / Contract / Bill / Payment / News` 关键写操作在同一事务内记录操作日志
- 日志写入失败时，对应业务操作整体回滚

### Added

- Alembic migration:
  - `b5c4d3e2f1a0_add_operation_logs_table.py`
- Notification service 单测：
  - `backend/tests/service/test_notification_service.py`

### Verified

- `pytest backend/tests/service/test_notification_service.py -q` 通过
- 结果：`8 passed`
- `docker compose -f deploy/docker-compose.yml exec backend pytest tests/api/test_payment_flow.py tests/api/test_news_flow.py tests/api/test_repair_flow.py tests/api/test_complaint_flow.py tests/api/test_admin_flow.py -q` 通过
- 结果：`10 passed`

## v1.14.1 - 2026-05-02

### Changed

#### Payment / Bill 支付闭环补强

- `POST /api/v1/payments` 改为先判断账单是否存在，再单独校验支付权限
- 非账单所属租客、房东、admin 支付统一返回 `1004`
- 支付成功后，除 landlord 的 `Bill paid` 通知外，新增 tenant 的 `Payment successful` 通知
- 两条通知与 Payment 创建、Bill 状态更新保持同一事务提交

### Verified

- `docker compose exec backend pytest tests/api/test_payment_flow.py -q` 通过
- 结果：`2 passed`

## v1.14.0 - 2026-05-02

### Added

#### News / 公告模块

新增 News 第一版完整模块：

- `app/modules/news/model.py`
- `app/modules/news/schema.py`
- `app/modules/news/repository.py`
- `app/modules/news/service.py`
- `app/modules/news/router.py`

新增表：

- `news`

新增接口：

- `POST /api/v1/news`
- `GET /api/v1/news`
- `GET /api/v1/news/{id}`
- `PATCH /api/v1/news/{id}`
- `DELETE /api/v1/news/{id}`

### Changed

#### News 业务规则

- 公告状态第一版固定为：
  - `draft`
  - `published`
- admin 默认可查看全部公告
- tenant / landlord / 游客仅可查看 `published`
- 删除策略采用物理删除
- 公告发布或更新已发布公告时，复用 `NotificationService` 给全部 `active tenant + active landlord` 发通知
- 已发通知记录保留，不随公告删除

#### 公共层补充

- `app/common/enums.py` 新增 `NewsStatus`
- `app/core/exceptions.py` 新增：
  - `3002 news not found`
  - `3003 invalid news status`
- `app/modules/user/repository.py` 新增按角色查询 active 用户方法，供公告通知批量分发复用
- Alembic 新增：
  - `a4b3c2d1e0f9_add_news_table.py`

### Verified

- News blueprint 已注册到 `/api/v1/news`
- 新增 HTTP 测试文件：
  - `backend/tests/api/test_news_flow.py`
- `docker compose exec backend pytest tests/api/test_news_flow.py -q` 通过
- 结果：`2 passed`

## v1.13.0 - 2026-05-02

### Added

#### Admin 后台管理模块

新增 Admin 第一版完整模块：

- `app/modules/admin/schema.py`
- `app/modules/admin/repository.py`
- `app/modules/admin/service.py`
- `app/modules/admin/router.py`

新增接口：
- `GET /api/v1/admin/users`
- `GET /api/v1/admin/users/{id}`
- `POST /api/v1/admin/users`
- `PUT /api/v1/admin/users/{id}`
- `PATCH /api/v1/admin/users/{id}/status`
- `GET /api/v1/admin/houses`
- `GET /api/v1/admin/houses/{id}`
- `GET /api/v1/admin/complaints`
- `GET /api/v1/admin/complaints/{id}`
- `PATCH /api/v1/admin/complaints/{id}/process`
- `PATCH /api/v1/admin/complaints/{id}/resolve`
- `PATCH /api/v1/admin/complaints/{id}/reject`
- `PATCH /api/v1/admin/complaints/{id}/close`
- `GET /api/v1/admin/repairs`
- `GET /api/v1/admin/repairs/{id}`
- `PATCH /api/v1/admin/repairs/{id}/process`
- `PATCH /api/v1/admin/repairs/{id}/complete`
- `PATCH /api/v1/admin/repairs/{id}/reject`
- `PATCH /api/v1/admin/repairs/{id}/close`
- `GET /api/v1/admin/contracts`
- `GET /api/v1/admin/contracts/{id}`
- `PATCH /api/v1/admin/contracts/{id}/status`

### Changed

#### Admin 第一版业务边界

- Admin 统一使用 `/api/v1/admin` 前缀
- 所有后台接口仅允许 admin 调用
- User 的“删除”在第一版仅表现为启用 / 禁用
- House 第一版后台只做只读列表和详情，不做审核和状态修改
- Complaint / Repair 后台状态流直接复用现有 admin 兼容逻辑
- Contract 后台状态流固定为：
  - `pending -> active`
  - `pending -> cancelled`
  - `active -> terminated`
- Admin 模块可复用 Notification 发通知
- Statistics 保持独立前缀 `/api/v1/statistics`

### Verified

- Admin blueprint 已注册到 `/api/v1/admin`
- 新增 HTTP 测试文件：
  - `backend/tests/api/test_admin_flow.py`
- `docker compose exec backend pytest tests/api/test_admin_flow.py -q` 通过
- 结果：`2 passed`

## v1.12.0 - 2026-05-02

### Added

#### Statistics 统计模块

新增 Statistics 第一版只读模块：

- `app/modules/statistics/schema.py`
- `app/modules/statistics/repository.py`
- `app/modules/statistics/service.py`
- `app/modules/statistics/router.py`

新增接口：

- `GET /api/v1/statistics/house-utilization`
- `GET /api/v1/statistics/rent-income`
- `GET /api/v1/statistics/active-users`
- `GET /api/v1/statistics/complaint-repair-count`

### Changed

#### Statistics 业务规则

- Statistics 第一版不新增表，直接聚合现有业务数据
- 仅 admin 可访问统计接口
- `house-utilization` 统计未删除房源与 active contract 占用率
- `rent-income` 按 `Payment.paid_at` 聚合累计收入和月度收入
- `active-users` 统计 `users.status = active`
- `complaint-repair-count` 统计报修和投诉总数

### Verified

- Statistics blueprint 已注册到 `/api/v1/statistics`
- 新增 HTTP 测试文件：
  - `backend/tests/api/test_statistics_flow.py`

## v1.11.0 - 2026-05-02

### Added

#### Notification 通知模块

新增 Notification 第一版完整模块：

- `app/modules/notification/model.py`
- `app/modules/notification/schema.py`
- `app/modules/notification/repository.py`
- `app/modules/notification/service.py`
- `app/modules/notification/router.py`

新增表：

- `notifications`

新增接口：

- `POST /api/v1/notifications`
- `GET /api/v1/notifications`
- `GET /api/v1/notifications/{id}`
- `PATCH /api/v1/notifications/{id}/read`

新增错误码：

- `2901 notification not found`
- `2902 invalid notification status`

新增 migration：

- `f1a7b92d4c33_add_notifications_table.py`

### Changed

#### Notification 业务规则

- Notification 采用单用户站内通知模型
- 状态集合：
  - `unread`
  - `read`
- 主流程保持：
  - `unread -> read`
- 所有用户只允许读取和操作自己的通知
- `POST /api/v1/notifications` 仅 admin 手动或系统测试使用
- 推荐 `source_type`：
  - `repair`
  - `complaint`
  - `contract`
  - `bill`
- `created_at / updated_at` 按 UTC 处理
- 标记已读时显式更新 `updated_at`
- 第一版不提供 `DELETE /notifications/{id}`，不做物理删除

#### 自动通知联动

- `Repair / Complaint / Contract / Bill` 状态变更时自动创建通知
- `Payment` 中 bill paid 场景自动创建通知
- tenant / landlord / admin 只接收自己相关通知

### Verified

- Notification blueprint 已注册到 `/api/v1/notifications`
- 新增 HTTP 测试文件：
  - `backend/tests/api/test_notification_flow.py`

## v1.10.0 - 2026-05-02

### Added

#### Complaint 投诉模块

新增 Complaint 第一版完整模块：

- `app/modules/complaint/model.py`
- `app/modules/complaint/schema.py`
- `app/modules/complaint/repository.py`
- `app/modules/complaint/service.py`
- `app/modules/complaint/router.py`

新增表：

- `complaints`

新增接口：

- `POST /api/v1/complaints`
- `GET /api/v1/complaints`
- `GET /api/v1/complaints/{id}`
- `PATCH /api/v1/complaints/{id}/process`
- `PATCH /api/v1/complaints/{id}/resolve`
- `PATCH /api/v1/complaints/{id}/reject`
- `PATCH /api/v1/complaints/{id}/close`

新增错误码：

- `2801 complaint not found`
- `2802 invalid complaint status`
- `2803 contract status is not allowed for complaint`

新增 migration：

- `c8f91d4b2a10_add_complaints_table.py`

### Changed

#### Complaint 业务规则

- Complaint 必须基于当前租客自己的 `active contract` 创建
- 前端只允许传 `contract_id / description`
- `house_id / tenant_id / landlord_id` 由后端从 contract 自动写入
- 状态集合：
  - `pending`
  - `processing`
  - `resolved`
  - `closed`
  - `rejected`
- 主流程保持：
  - `pending -> processing -> resolved -> closed`
- 可选分支支持：
  - `pending -> rejected`
- tenant 允许：
  - `create`
  - `close`
- landlord 允许：
  - `process`
  - `resolve`
  - `reject`
- admin 复用同一套 `/api/v1/complaints` 接口，可执行所有合法状态流
- 第一版保留 `cancelled_at` 作为预留字段，但不开放 `cancelled` 状态与接口
- 第一版不提供 `DELETE /complaints/{id}`，不做物理删除

### Verified

- Complaint blueprint 已注册到 `/api/v1/complaints`
- 新增 HTTP 测试文件：
  - `backend/tests/api/test_complaint_flow.py`

## v1.9.0 - 2026-05-02

### Added

#### Repair 报修模块

新增 Repair 第一版完整模块：

- `app/modules/repair/model.py`
- `app/modules/repair/schema.py`
- `app/modules/repair/repository.py`
- `app/modules/repair/service.py`
- `app/modules/repair/router.py`

新增表：

- `repairs`

新增接口：

- `POST /api/v1/repairs`
- `GET /api/v1/repairs`
- `GET /api/v1/repairs/{id}`
- `PATCH /api/v1/repairs/{id}/process`
- `PATCH /api/v1/repairs/{id}/complete`
- `PATCH /api/v1/repairs/{id}/reject`
- `PATCH /api/v1/repairs/{id}/close`
- `PATCH /api/v1/repairs/{id}/reopen`

新增错误码：

- `2701 repair not found`
- `2702 invalid repair status`
- `2703 contract status is not allowed for repair`

新增 migration：

- `7b4d6c2a9f31_add_repairs_table.py`

### Changed

#### Repair 业务规则

- Repair 必须基于当前租客自己的 `active contract` 创建
- 前端只允许传 `contract_id / description`
- `house_id / tenant_id / landlord_id` 由后端从 contract 自动写入
- 状态集合：
  - `pending`
  - `processing`
  - `completed`
  - `closed`
  - `rejected`
  - `cancelled`
  - `reopened`
- 主流程保持：
  - `pending -> processing -> completed -> closed`
- 可选分支支持：
  - `pending -> rejected`
  - `completed -> reopened`
  - `closed -> reopened`
  - `reopened -> processing`
  - `reopened -> rejected`
- tenant 允许：
  - `create`
  - `close`
  - `reopen`
- landlord 允许：
  - `process`
  - `complete`
  - `reject`
- admin 复用同一套 `/api/v1/repairs` 接口，可执行所有合法状态流
- 第一版不提供 `DELETE /repairs/{id}`，不做物理删除

### Verified

- Repair blueprint 已注册到 `/api/v1/repairs`
- 新增 HTTP 测试文件：
  - `backend/tests/api/test_repair_flow.py`
- 已覆盖主流程、reopen/reject 分支、角色权限、合同状态校验、分页与状态异常场景
- 当前环境已完成源码级编译校验与 Flask 路由注册校验
- 尚未在当前线程内执行真实 `pytest tests/api/test_repair_flow.py -q`
  - 依赖运行中的 API 服务与已升级到最新 migration 的数据库

## v1.8.0 - 2026-04-28

### Added

#### Payment 支付记录模块

新增 Payment 第一版完整模块：

- `app/modules/payment/model.py`
- `app/modules/payment/schema.py`
- `app/modules/payment/repository.py`
- `app/modules/payment/service.py`
- `app/modules/payment/router.py`

新增表：

- `payments`

新增接口：
- `POST /api/v1/payments`
- `GET /api/v1/payments`
- `GET /api/v1/payments/{id}`

新增错误码：

- `2601 支付记录不存在`
- `2602 账单状态不允许支付`
- `2603 支付金额不匹配`
- `2604 账单已支付`

新增 migration：
- `4d4e0ca9ef73_add_payments_table.py`

### Changed

#### Payment 业务规则

- Payment 第一版只做模拟支付和支付记录
- 不接第三方支付
- 不做支付回调
- 不做退款
- 不做部分支付
- `POST /payments` 请求体只允许 `bill_id / amount / payment_method / remark`
- 前端不允许传 `contract_id / house_id / tenant_id / landlord_id / status / paid_at`
- `contract_id / house_id / tenant_id / landlord_id` 由后端从 bill 自动写入
- `payment_method` 第一版只允许 `mock / offline`
- `amount` 必须严格等于 `bill.amount`
- 只有租客可以支付自己的 bill
- 允许支付 `unpaid / overdue`
- 禁止支付 `cancelled / paid`
- 成功支付在同一事务内先插入 Payment，再更新 `Bill.status = paid`
- 非参与者访问 payment 统一返回 `2601`
- 重复支付同一 bill 返回 `2604`

### Verified

- `alembic upgrade head` 已执行到 `4d4e0ca9ef73`
- `pytest backend/tests/api/test_payment_flow.py -q` 通过
- 结果：`2 passed`
- `pytest backend/tests/api/test_bill_flow.py -q` 回归通过
- 结果：`2 passed`
- 已覆盖 `unpaid bill` 支付、`overdue bill` 支付、重复支付、越权访问、金额不匹配、`cancelled bill` 禁止支付


## v1.7.0 - 2026-04-28

### Added

#### Bill 账单模块

新增 Bill 第一版完整模块：

- `app/modules/bill/model.py`
- `app/modules/bill/schema.py`
- `app/modules/bill/repository.py`
- `app/modules/bill/service.py`
- `app/modules/bill/router.py`

新增表：

- `bills`

新增接口：

- `POST /api/v1/bills`
- `GET /api/v1/bills`
- `GET /api/v1/bills/{id}`
- `PATCH /api/v1/bills/{id}/cancel`
- `PATCH /api/v1/bills/{id}/mark-overdue`

新增错误码：

- `2501 账单不存在`
- `2502 非法账单状态`
- `2503 合同未生效，不能创建账单`
- `2504 账单金额不合法`

新增 migration：

- `e196c0dcb397_add_bills_table.py`

### Changed

#### Bill 业务规则

- Bill 必须基于 `active contract` 创建
- `POST /bills` 请求体只允许 `contract_id / bill_type / amount / due_date / remark`
- 前端不允许传 `house_id / tenant_id / landlord_id`
- `house_id / tenant_id / landlord_id` 由后端从 contract 自动写入
- `bill_type` 第一版只允许 `rent / deposit / other`
- `amount` 必须大于 `0`
- 第一版不做 Payment，不新增 `payment` 表，不新增 `mark-paid` 接口
- `paid` 只在状态常量中预留，不提供公开状态修改接口

#### mark-overdue 规则增强

- `PATCH /api/v1/bills/{id}/mark-overdue` 只允许 `unpaid -> overdue`
- 必须满足当前日期已经大于 `bill.due_date`
- 状态不合法或 `due_date` 未过期时统一返回 `2502`

### Verified

- `pytest backend/tests/api/test_bill_flow.py -q` 通过
- 结果：`2 passed`
- 已覆盖 Bill 主流程与参数/权限错误场景
- 已覆盖 `mark-overdue` 的 `due_date` 校验


## v1.6.2 - 2026-04-26

### Added

#### HTTP 接口自动化 smoke test

新增真实 HTTP 冒烟测试文件：

- `backend/tests/api/conftest.py`
- `backend/tests/api/test_smoke_flow.py`

新增测试依赖：

- `pytest>=8.0,<9.0`
- `requests>=2.31,<3.0`

测试约定：

- 默认 `API_BASE_URL = http://127.0.0.1:8000`
- 可通过环境变量 `API_BASE_URL` 覆盖
- 不清空数据库
- 不依赖固定数据库 id
- 仅验证真实 HTTP 接口，不直接调用 service

覆盖业务主流程：

- 注册房东用户
- 注册租客用户
- 双方登录
- 房东创建并发布房源
- 租客收藏房源
- 租客创建预约
- 房东确认预约
- 租客创建会话并发送消息
- 房东查看会话列表并校验目标会话 `unread_count`
- 房东标记会话已读
- 房东基于 confirmed appointment 创建合同
- 租客确认合同
- 查询合同详情并确认 `status = active`

### Verified

- `pytest backend/tests/api/test_smoke_flow.py -q` 通过
- 结果：`1 passed`
- 关键断言已覆盖：
  - `house.status == listed`
  - `appointment.status == confirmed`
  - `message.content` 已 `strip`
  - `read.updated >= 1`
  - `contract.status == active`
- 运行时存在 `PytestCacheWarning`：
  - 当前工作目录 `.pytest_cache` 无写权限
  - 不影响测试执行结果

## v1.6.1 - 2026-04-26

### Changed

#### common BaseRepository 等价重构

本轮只做 repository 基础能力抽取，不新增业务模块，不修改接口、响应字段、错误码、数据库表结构、Alembic migration 和 service 业务规则。

新增 common 文件：

- `app/common/base_repository.py`

提供基础能力：

- `create(db, obj)`
- `get_by_id(db, obj_id)`
- `delete(db, obj)`
- `count_all(db)`
- `list_page(db, offset, limit)`

已接入继承的 repository：

- `UserRepository`
- `FavoriteRepository`
- `AppointmentRepository`
- `ConversationRepository`
- `MessageRepository`
- `ContractRepository`
- `HouseRepository`

约束：

- repository 仍不 `commit / rollback`
- service 仍显式传入 `db`
- 不读取 `g / request / current_user`
- 不把软删除、状态、权限和复杂业务查询下沉到 BaseRepository
- `HouseRepository` 原有 `listed / deleted_at / mine / filter` 查询保持不变
- `MessageRepository` 保留：
  - `list_by_conversation_id`
  - `count_by_conversation_id`
  - `get_last_by_conversation_id`
  - `count_unread_for_user_in_conversation`
  - `mark_read_for_user_in_conversation`

### Verified

- `BaseRepository` 和改造后的各 repository 可正常通过 AST 语法解析
- `MessageRepository` 已改为继承 `BaseRepository[Message]`，并仅删除完全等价的 `create`
- 业务查询条件未改动，尤其是 House 的 `deleted_at / listed / mine / filter`、Favorite 的可见性过滤、Conversation/Contract 的参与人过滤
- `python -m compileall` 因现有 `__pycache__` 文件权限问题未能完成字节码写入，不影响本轮代码等价重构本身

## v1.6.0 - 2026-04-26

### Added

#### Contract 合同模块

新增 Contract 第一版完整模块：

- `app/modules/contract/model.py`
- `app/modules/contract/schema.py`
- `app/modules/contract/repository.py`
- `app/modules/contract/service.py`
- `app/modules/contract/router.py`

新增接口：

- `POST /api/v1/contracts`
- `GET /api/v1/contracts`
- `GET /api/v1/contracts/{id}`
- `PATCH /api/v1/contracts/{id}/confirm`
- `PATCH /api/v1/contracts/{id}/reject`
- `PATCH /api/v1/contracts/{id}/cancel`
- `PATCH /api/v1/contracts/{id}/terminate`

#### Contract 数据模型

新增表：

- `contracts`

关键规则：

- Contract 第一版必须基于 `confirmed appointment` 创建
- 前端不传 `house_id / tenant_id / landlord_id`
- 后端从 `appointment_id` 自动确定 `house_id / tenant_id / landlord_id`
- 同一 `appointment_id` 同时只能有一个 `pending` 合同
- 如果同一 `appointment_id` 已有 `pending` 合同，再创建返回 `4009`
- 同一 `house_id` 同时只能有一个 `active` 合同
- `active` 后第一版不修改 `House.status`

### Changed

#### 新增 Contract 错误码

- `2401 合同不存在`
- `2402 非法合同状态`
- `2403 不能和自己的房源签合同`
- `2404 合同时间不合法`
- `2405 房源已有生效合同`

#### 接入 Alembic migration

新增 migration：

- `21d28ff28027_add_contracts_table.py`

该 migration 只新增：

- `contracts`

未修改旧表结构。

### Verified

- Contract 模块文件可正常导入
- `/api/v1/contracts` 相关 7 个路由已成功挂载
- `alembic history` 链路正常
- 临时 SQLite 环境下 `alembic upgrade head` 成功执行到 `21d28ff28027_add_contracts_table`

## v1.5.0 - 2026-04-26

### Added

#### Conversation / Message HTTP 非实时消息模块

新增 Conversation 第一版完整模块：

- `app/modules/conversation/model.py`
- `app/modules/conversation/schema.py`
- `app/modules/conversation/repository.py`
- `app/modules/conversation/service.py`
- `app/modules/conversation/router.py`

新增能力：

- 围绕指定房源创建会话
- 返回当前用户参与的会话列表
- 查看会话消息列表
- 发送非实时消息
- 标记会话消息为已读

第一版明确不做：

- WebSocket
- Redis
- 实时推送
- 在线状态

#### Conversation / Message 数据模型

新增表：

- `conversations`
- `messages`

关键规则：

- `tenant_id + landlord_id + house_id` 唯一
- 同一租客围绕同一房源联系同一房东，只能有一个会话
- 已存在会话时，`POST /api/v1/conversations` 直接返回已有会话
- 发送消息成功后同步刷新 `Conversation.updated_at`
- `Message.content` 保存 `strip()` 后的结果

### Changed

#### 新增 Conversation 错误码

- `2301 会话不存在`
- `2302 不能联系自己的房源`

#### 接入 Alembic migration

新增 migration：

- `8599342798d7_add_conversations_and_messages.py`

该 migration 只新增：

- `conversations`
- `messages`

未修改旧表结构。

## v1.4.2 - 2026-04-26

### Changed

#### Alembic 接管数据库结构管理

本轮只切换数据库建表机制，不新增业务模块，不改变接口路径、响应字段、错误码、业务规则和状态流转。

- `backend/requirements.txt` 新增 `alembic>=1.13,<2.0`
- 新增 `backend/alembic.ini`
- 新增 `backend/alembic/env.py`
- 新增 `backend/alembic/versions/`
- 新增首版 migration `create_initial_tables`

#### Flask 启动阶段取消自动建表

修改 `app/core/database.py`：

- 删除开发环境中的 `Base.metadata.create_all(bind=engine)`
- 删除为 `create_all()` 服务的业务 model import 逻辑
- 保留 `engine` 初始化
- 保留 `SessionLocal / scoped_session`
- 保留 `before_request` 打开 `g.db`
- 保留 `teardown_request` 关闭 `g.db`

说明：

- `database.py` 不再 import 任何业务模块 model
- 数据库结构统一由 Alembic migration 管理

### Added

#### 首版数据库迁移

新增首版 migration `create_initial_tables`，用于创建当前已有表：

- `users`
- `houses`
- `favorites`
- `appointments`

约束：

- 不修改表名
- 不修改字段名
- 不新增业务字段
- 不删除已有字段
- 不修改状态值
- 只保留现有 model 中已定义的外键、唯一约束和索引

### Notes

常用命令：

```bash
alembic revision --autogenerate -m "xxx"
alembic upgrade head
alembic current
alembic history
alembic downgrade -1
```

## v1.4.1 - 2026-04-26

### Changed

#### common 公共能力替换重构完成

本轮只做 common 抽取与替换，不新增业务能力，不改变接口路径、响应字段、错误码、业务规则和状态流转。

新增 common 文件：

- `app/common/base_model.py`
- `app/common/base_schema.py`
- `app/common/pagination.py`
- `app/common/enums.py`

### Model Refactor

新增 `BaseModel`：

- `id`
- `created_at`
- `updated_at`

新增 `SoftDeleteMixin`：

- `deleted_at`

当前 model 继承关系：

- `User(BaseModel)`
- `House(BaseModel, SoftDeleteMixin)`
- `Favorite(BaseModel)`
- `Appointment(BaseModel)`

约束：

- `deleted_at` 只保留在 House。
- User / Favorite / Appointment 没有新增 `deleted_at`。
- Favorite / Appointment 通过 `BaseModel` 统一拥有 `updated_at`。
- 未修改任何 `__tablename__`。
- 未修改已有字段名。

### Schema Refactor

新增 `BaseSchema`：

- `from_attributes=True`
- `extra="forbid"`

说明：

- Read schema 复用 `from_attributes=True`。
- 对原本不强制 `extra="forbid"` 的 schema，显式覆盖配置，保持旧行为。
- 未改变接口请求校验语义。

### Pagination Refactor

新增并使用：

- `get_offset()`
- `build_page_result()`

已用于：

- User 列表
- House 列表
- Favorite 列表
- Appointment 列表

分页响应结构保持不变：

```text
list / total / page / page_size
```

### Enum Refactor

新增字符串常量类：

- `HouseStatus`
- `AppointmentStatus`

说明：

- 数据库存储值不变。
- 接口返回值不变。
- 状态流转规则不变。
- 不引入复杂 Python Enum 行为。

### Fixed

#### Pydantic 参数校验异常统一返回 JSON

修复 `app/core/exceptions.py` 中的参数校验异常处理：

- 继续统一捕获 `pydantic.ValidationError`
- 统一返回：
  - `code = 3001`
  - `message = bad request`
  - `data = error.errors()`
- 对 `ValidationError.errors()` 中可能出现的非 JSON 可序列化对象做规范化处理。
- 避免参数校验失败时掉回 Flask 默认 HTML `500 Internal Server Error`。

影响场景：

- `GET /api/v1/houses?min_rent=3000&max_rent=1000`
- `GET /api/v1/houses?min_area=100&max_area=50`

修复后，这些请求统一返回 JSON `3001 bad request`，不再返回 HTML 500。

------

## v1.4 - 2026-04-26

### Added

#### Appointment 预约看房模块最小闭环

新增 Appointment 第一版完整模块：

- `app/modules/appointment/model.py`
- `app/modules/appointment/schema.py`
- `app/modules/appointment/repository.py`
- `app/modules/appointment/service.py`
- `app/modules/appointment/router.py`

新增接线：

- 注册 `/api/v1/appointments` blueprint
- 新增 `AppointmentRepository`
- 新增 `AppointmentService`
- 开发环境自动建表时显式导入 `app.modules.appointment.model`

#### Appointment 数据模型

新增 `appointments` 表。

字段包括：

- id
- house_id
- tenant_id
- landlord_id
- appointment_time
- remark
- status
- created_at
- updated_at

#### Appointment 接口

新增接口：

```text
POST   /api/v1/appointments
GET    /api/v1/appointments
PATCH  /api/v1/appointments/{id}/confirm
PATCH  /api/v1/appointments/{id}/reject
PATCH  /api/v1/appointments/{id}/cancel
```

实现能力：

- 租客创建预约
- 查看与当前用户相关的预约列表
- 房东确认预约
- 房东拒绝预约
- 租客取消预约

#### Appointment 状态

新增预约状态：

```text
pending / confirmed / rejected / cancelled / expired
```

说明：

- 创建预约默认 `pending`。
- `confirmed` 表示房东已确认。
- `rejected` 表示房东已拒绝。
- `cancelled` 表示租客已取消。
- `expired` 第一版不自动写回数据库，只通过 `display_status` 和操作校验体现。

#### Appointment 错误码

新增错误码：

- `2201 预约不存在`
- `2202 非法预约状态`
- `2203 不能预约自己的房源`
- `2204 预约时间必须是未来时间`

### Changed

#### Appointment 业务规则

- 只能预约未删除且 `listed` 的房源。
- 租客不能预约自己的房源。
- `tenant_id` 从 token 获取。
- `landlord_id` 从 House 表读取。
- `appointment_time` 必须是未来时间。
- 预约列表返回与当前用户相关的预约。
- 列表项返回预约字段、`status`、`display_status`、`relation_role`、`house` 摘要。
- 越权访问预约统一按“预约不存在”处理，返回 `2201`。
- 非法状态流转返回 `2202`。

### Verified

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


## v1.3.1 - 2026-04-26

### Fixed

#### Pydantic 参数校验异常统一返回 JSON

修复 `app/core/exceptions.py` 中的参数校验异常处理：

- 继续统一捕获 `pydantic.ValidationError`
- 统一返回：
  - `code = 3001`
  - `message = bad request`
  - `data = error.errors()`
- 对 `ValidationError.errors()` 中可能出现的非 JSON 可序列化对象做规范化处理
- 避免参数校验失败时掉回 Flask 默认 HTML `500 Internal Server Error`

影响场景：

- `GET /api/v1/houses?min_rent=3000&max_rent=1000`
- `GET /api/v1/houses?min_area=100&max_area=50`

修复后，这些请求统一返回 JSON `3001 bad request`，不再返回 HTML 500。

## v1.3 - 2026-04-25

### Added

#### Favorite 模块最小闭环

新增 Favorite 第一版完整模块：

- `app/modules/favorite/model.py`
- `app/modules/favorite/schema.py`
- `app/modules/favorite/repository.py`
- `app/modules/favorite/service.py`
- `app/modules/favorite/router.py`

新增接线：

- 注册 `/api/v1/favorites` blueprint
- 新增 `FavoriteRepository`
- 新增 `FavoriteService`
- 开发环境自动建表时显式导入 `app.modules.favorite.model`

#### Favorite 数据模型

新增 `favorites` 表。

字段包括：

- id
- user_id
- house_id
- created_at

设计决策：

- `user_id + house_id` 唯一约束，禁止重复收藏
- Favorite 不引入状态字段
- Favorite 不改变 House 的状态流转

#### Favorite 接口

新增接口：

```text
POST   /api/v1/favorites
GET    /api/v1/favorites
DELETE /api/v1/favorites/{house_id}
```

实现能力：

- 收藏房源
- 我的收藏列表
- 取消收藏

### Changed

#### Favorite 收藏规则

- 只允许收藏未删除且 `listed` 的房源
- 房源不存在、已删除、非 `listed`，统一返回 `2001 house not found`
- 我的收藏列表只返回当前仍 `listed` 且未删除的房源
- 收藏成功响应返回：
  - `house_id`
  - `favorite_created_at`
  - `house`

#### Favorite 专属错误码

新增错误码：

- `2101 收藏不存在`

用于：

- `DELETE /api/v1/favorites/{house_id}` 时，当前用户未收藏该房源

### Verified

- Favorite 三个接口均必须登录，统一复用现有认证 helper
- 收藏未删除且 `listed` 房源成功
- 收藏不存在 / 已删除 / 非 `listed` 房源返回 `2001`
- 重复收藏返回 `4009`
- 我的收藏列表支持分页，且只返回当前仍 `listed` 且未删除的房源
- 取消未收藏房源返回 `2101`

## v1.2 - 2026-04-25

### Changed

#### House 列表筛选增强

在不新增模块、不新增表、不改变状态流转的前提下，增强现有列表接口：

- `GET /api/v1/houses`
- `GET /api/v1/houses?mine=true`

新增支持筛选参数：

- `region`
- `house_type`
- `min_rent`
- `max_rent`
- `keyword`
- `min_area`
- `max_area`

实现规则：

- 公共列表仍只返回 `listed` 且未删除房源
- `mine=true` 仍只返回当前用户自己的未删除房源
- 筛选条件可与分页同时使用
- `keyword` 匹配 `title / address / community / description`
- repository 只负责查询封装，不写业务逻辑
- service 仍保持 `list_houses(...)` 单入口
- 不改变 `publish / offline / delete / update` 逻辑
- 不引入新的权限系统

#### House 查询参数校验增强

更新 `HouseListQuerySchema`：

- 新增列表筛选字段校验
- 支持空白字符串规范化为 `None`
- 增加范围校验：
  - `min_rent <= max_rent`
  - `min_area <= max_area`
- 非法范围继续按现有 `3001 bad request` 返回

#### 认证 helper 收口完成

- `GET /api/v1/auth/me` 的 router 继续只负责获取 `current_user_id`
- `AuthService.get_current_user()` 改为接收 `current_user_id`
- `AuthService` 根据 `current_user_id` 查询用户并返回 dict
- 若 token 对应用户不存在，继续返回 `1003`
- 不改变 JWT 结构、错误码和统一响应格式

### Verified

- `GET /api/v1/auth/me` 通过 `get_required_current_user_id()` 获取当前用户
- `AuthService.get_current_user(db, current_user_id)` 可正常返回用户信息
- `GET /api/v1/houses` 支持筛选 + 分页
- `GET /api/v1/houses?mine=true` 支持筛选 + 分页
- `keyword` 支持匹配 `title/address/community/description`
- `min_rent > max_rent` 返回 `3001`
- `min_area > max_area` 返回 `3001`



## v1.1 - 2026-04-23

> House 模块最小闭环完成

------

### Added

#### House 模块

新增房源模块完整第一版，包括：

- `app/modules/house/model.py`
- `app/modules/house/schema.py`
- `app/modules/house/repository.py`
- `app/modules/house/service.py`
- `app/modules/house/router.py`

新增 House 蓝图注册：

```text
/api/v1/houses
```

新增 container 装配：

- `get_house_repository()`
- `get_house_service()`

------

#### House 数据模型

新增 `houses` 表。

字段包括：

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

设计决策：

- `landlord_id` 绑定当前登录用户。
- `landlord_id` 不允许前端传。
- 使用 `deleted_at` 做逻辑删除。
- 删除后不做物理删除。

------

#### House 接口

新增接口：

```text
POST   /api/v1/houses
GET    /api/v1/houses
GET    /api/v1/houses?mine=true
GET    /api/v1/houses/{id}
PUT    /api/v1/houses/{id}
PATCH  /api/v1/houses/{id}/publish
PATCH  /api/v1/houses/{id}/offline
DELETE /api/v1/houses/{id}
```

实现能力：

- 创建房源
- 公共房源列表
- 我的房源列表
- 房源详情
- 更新房源资料
- 发布房源
- 下架房源
- 逻辑删除房源

------

#### House 状态机

House 第一版状态固定为：

```text
draft / listed / offline
```

状态含义：

| 状态    | 含义              |
| ------- | ----------------- |
| draft   | 草稿 / 未发布     |
| listed  | 已上架 / 对外展示 |
| offline | 已下架 / 放弃发布 |

状态流转：

```text
创建：draft
publish：draft/offline -> listed
offline：listed/draft -> offline
DELETE：deleted_at = now，status = offline
```

------

#### House 可见性规则

新增并验证以下可见性规则：

- 公共列表只返回未删除的 `listed` 房源。
- `mine=true` 只返回当前登录用户自己的未删除房源。
- `mine=true` 不混入公共房源。
- `draft/offline` 不对外公开。
- 房东本人可查看自己的 `draft/listed/offline` 房源。
- 删除后的房源不出现在任何列表中。
- 删除后的房源详情统一返回 `house not found`。

------

#### House 最小所有权校验

新增最小所有权控制：

- 创建房源时，从 JWT token 解析当前用户 id，自动写入 `landlord_id`。
- 更新、发布、下架、删除只能操作自己的房源。
- 非本人操作房源时，统一返回 `2001 house not found`。
- 不做完整 RBAC 权限系统。

------

#### House 参数校验

新增 Pydantic schema：

- `HouseCreateSchema`
- `HouseUpdateSchema`
- `HouseListQuerySchema`
- `HouseReadSchema`

校验规则：

- `title` 必填
- `address` 必填
- `region` 必填
- `house_type` 必填
- `area > 0`
- `rent >= 0`
- `deposit >= 0`
- `page >= 1`
- `page_size <= 100`
- `mine` 默认为 `false`

限制：

- `HouseCreateSchema` 不接收 `landlord_id/status`。
- `HouseUpdateSchema` 不接收 `landlord_id/status`。
- 请求体包含 `status` 时，按参数错误处理。

------

#### 自动建表（开发阶段）

开发阶段在 `app.core.database.init_database(app)` 中支持自动创建缺失表：

```python
Base.metadata.create_all(bind=engine)
```

约束：

- 仅在 `ENV == "development"` 时执行。
- 执行前显式导入 model。
- 使用 `import_module(...)` 避免覆盖 Flask app 变量。

示例：

```python
from importlib import import_module

if flask_app.config.get("ENV") == "development":
    import_module("app.modules.user.model")
    import_module("app.modules.house.model")
    Base.metadata.create_all(bind=engine)
```

说明：

- 当前阶段不引入 Alembic。
- `create_all()` 只负责创建不存在的表，不负责安全迁移已有表结构。

------

#### Docker 开发模式调整

后端开发模式建议调整为：

- 挂载后端代码：

```yaml
volumes:
  - ../backend:/app/backend
```

- Gunicorn 开发阶段使用 1 worker + reload：

```yaml
command: gunicorn -w 1 --reload -b 0.0.0.0:8000 app.main:app
```

原因：

- 避免每次修改 Python 代码后都 rebuild。
- `--reload` 方便开发阶段自动重载。
- `-w 1` 避免多个 worker 同时执行开发期自动建表逻辑。

------

### Changed

#### House 删除策略

明确 `DELETE /api/v1/houses/{id}` 为逻辑删除：

- 设置 `deleted_at`
- 同时将 `status` 置为 `offline`
- 不做物理删除
- 删除后不出现在任何列表或详情中
- 删除后不能再执行 update/publish/offline/delete

------

#### House 状态更新策略

明确普通更新接口不允许修改状态：

- `PUT /api/v1/houses/{id}` 只更新房源资料
- `status` 只能通过以下接口修改：
  - `PATCH /api/v1/houses/{id}/publish`
  - `PATCH /api/v1/houses/{id}/offline`

这样将“资料更新”和“业务状态流转”分离。

------

#### House 查询策略

明确列表查询分为两条独立分支：

- `mine=false` 或不传：公共房源列表，只返回 `listed`
- `mine=true`：我的房源列表，只返回当前用户自己的房源

两条分支不混合、不兜底、不互相补数据。

------

### Fixed

#### 修复 House 路由 404

问题：

- `POST /api/v1/houses` 返回 4004

原因：

- House blueprint 未正确加载或容器未运行最新代码

修复：

- 确认 `factory.py` 中注册：

```python
app.register_blueprint(house_bp, url_prefix="/api/v1/houses")
```

- 开发环境使用代码挂载，减少“本地代码已改但容器仍运行旧镜像”的问题。

------

#### 修复 houses 表不存在导致 5000

问题：

```text
Table 'rent_db.houses' doesn't exist
```

原因：

- `Base.metadata.create_all()` 执行时，`House` model 未注册进 `Base.metadata`。

修复：

- 在开发环境自动建表前显式导入：

```python
import_module("app.modules.user.model")
import_module("app.modules.house.model")
```

------

#### 修复 `import app.modules.xxx` 覆盖 Flask app 参数的问题

问题：

```text
AttributeError: module 'app' has no attribute 'extensions'
```

原因：

- 在 `init_database(app)` 函数中写：

```python
import app.modules.user.model
import app.modules.house.model
```

导致局部变量 `app` 被 Python import 语句绑定为包名，覆盖原来的 Flask app 参数。

修复：

- 将参数名改为 `flask_app`
- 使用 `import_module("app.modules.house.model")`

------

### Verified

House 模块已手动验证通过：

- 注册用户
- 登录并获取 token
- 创建房源成功
- 创建后默认 `status = draft`
- 公共列表不显示 `draft`
- `GET /houses?mine=true` 可看到自己的 `draft`
- `publish` 后状态变为 `listed`
- `listed` 房源进入公共列表
- `offline` 后状态变为 `offline`
- `offline` 房源不出现在公共列表
- `mine=true` 仍可看到自己的 `offline`
- 删除后公共列表不可见
- 删除后我的列表不可见
- 删除后详情返回 `2001`
- 非本人操作返回 `2001`
- `PUT` 传入 `status` 返回参数错误
- `mine=true` 不带 token 返回 `1003`

------

### Notes

当前仍未实现：

- 完整 login_required 装饰器
- 完整 RBAC 权限系统
- refresh token / token 黑名单
- Alembic 迁移
- House 图片 / 视频
- House 审核流
- Search 高级筛选
- Favorite 收藏
- Appointment 预约
- Conversation 聊天
- Contract 合同
- Bill / Payment 支付
- Repair / Complaint
- Admin 后台

------

## v1.0 - 2026-04-22

> Initial Release（基础版本完成）

------

### Added

#### Core 基础层

- 实现配置系统（config.py）
- 实现 SQLAlchemy 数据库连接与 session 管理（g.db）
- 实现统一响应结构（success / fail）
- 实现统一异常体系（AppException 及子类）
- 实现文件日志系统（仅写文件，不输出控制台）

------

#### User 模块（最小读写闭环）

- 用户表（users）建模完成
- 支持用户创建：
  - POST /api/v1/users
  - 密码使用 Werkzeug 哈希
- 支持用户查询：
  - GET /api/v1/users/{id}
- 支持分页查询：
  - GET /api/v1/users
  - 默认 page=1, page_size=10
  - 限制 page_size <= 100
- 用户名唯一约束
- 返回数据不包含 password 字段

------

#### Auth 模块（最小认证闭环）

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

### Changed

#### 认证错误统一策略

- 登录失败（用户不存在 / 密码错误）统一返回：
  - code = 1002
  - message = 用户名或密码错误

#### token 错误统一策略

以下情况统一返回 1003：

- token 缺失
- token 格式错误
- token 签名失败
- token 过期

------

### Fixed

- 修复 created_at 无默认值导致插入失败的问题
- 修复 MySQL + PyMySQL 在 caching_sha2_password 下依赖 cryptography 的问题
- 修复 Docker 环境下数据库连接与权限问题

------

### Design Decisions

- 采用分层架构：
  - router → service → repository → model
- service 负责事务控制（commit / rollback）
- repository 不允许 commit
- service 不返回 ORM 对象，仅返回 dict
- 使用 g.db 管理 request 级 session
- 使用 PyJWT 而非 session 机制（无状态认证）

------

### Notes

v1.0 阶段未实现：

- login_required（认证中间件）
- 权限系统（role 控制）
- refresh token / token 黑名单
- Alembic 数据库迁移
