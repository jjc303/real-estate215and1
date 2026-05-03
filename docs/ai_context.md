# AI Context（Backend Project）

Version: v1.15.0  
Last Updated: 2026-05-03

Status:
- 当前项目已经形成完整的课程项目后端骨架，并完成 `User / Auth / House / Favorite / Appointment / Conversation / Contract / Bill / Payment / Repair / Complaint / News / Notification / Statistics / Admin` 的最小业务闭环
- 数据库迁移已经全面切换到 Alembic 管理
- `Notification` 已经彻底收口为统一批量创建接口
- `Operation Log` 审计能力已经落库并接入后台查询
- 现有主要业务流都已有 HTTP 风格测试覆盖
- `Auth` 已新增邮箱验证码发送、邮箱验证码注册、邮箱验证码登录能力

---

## 0. 这份文档是给谁用的

这份文档面向“下一次接手这个仓库的 AI / 开发者”，目标不是写市场宣传，也不是写需求草案，而是帮助接手者在一个新会话里快速建立正确上下文。

这份文档应该回答清楚以下问题：
- 这个项目现在做到哪一步了
- 当前代码的架构硬约束是什么
- 每个模块的职责、状态流和权限规则是什么
- 最近新增了什么能力
- 后续继续开发时哪些地方不能乱改

如果你接手的是实现任务，而不是文档任务，建议先读完本文，再看：
- [docs/api.md](/D:/a.python/real-estate215and1/docs/api.md)
- [docs/CHANGELOG.md](/D:/a.python/real-estate215and1/docs/CHANGELOG.md)

---

## 1. 项目概览

### 1.1 项目类型

- 课程项目
- 房屋租赁平台后端
- 前后端分离
- 模块化单体，不是微服务

### 1.2 当前技术栈

- Flask（App Factory）
- SQLAlchemy 2.0 ORM
- MySQL 8.0
- PyMySQL
- Pydantic v2
- PyJWT
- Werkzeug 密码哈希
- Gunicorn
- Docker Compose
- Alembic
- pytest

### 1.3 当前系统目标

系统已经不只是“用户 + 登录 + 房源”演示，而是一个覆盖租赁核心流程的后端：
- 用户注册与登录
- 房源管理与公开浏览
- 收藏与预约
- 站内会话消息
- 合同
- 账单
- 支付
- 报修
- 投诉
- 公告
- 通知
- 统计
- 后台管理
- 操作日志审计

---

## 2. 当前项目阶段判断

### 2.1 已完成的层面

从课程项目标准看，后端的“最小闭环”已经具备：
- 基础实体都已经有路由、service、repository、schema
- 权限模型已经成型
- 主要状态流已经落地
- 统一响应、统一错误码、统一分页结构已经稳定
- 数据库迁移不再依赖启动时自动建表
- 关键业务流已有自动化测试

### 2.2 还没有做的方向

当前项目还没有做以下“更重”的工程化内容：
- 第三方支付网关
- WebSocket 实时消息
- 消息推送队列 / 异步任务系统
- 复杂 RBAC 权限系统
- 文件上传服务
- 搜索引擎
- 审计快照 / 大字段变更历史
- 微服务拆分

不要在没有明确需求的情况下主动把项目往这些方向重构。

---

## 3. 架构硬约束

### 3.1 分层结构

当前项目明确遵循：

```text
router -> service -> repository -> model/schema
```

这是硬约束，不是建议。

### 3.2 router 职责

router 只负责：
- 解析 request
- 用 schema 做参数校验
- 从 token 提取当前用户 ID
- 调用 service
- 返回统一响应

router 不应该做：
- 业务逻辑判断
- 状态流转
- 数据库事务
- repository 直接调用
- 复杂权限细节

### 3.3 service 职责

service 是业务核心层，负责：
- 角色和资源权限校验
- 状态流转判断
- 跨 repository 协作
- 调用 NotificationService
- 调用 OperationLogService
- 事务控制
- 抛出明确业务异常
- ORM -> dict 的序列化输出

要求：
- service 返回 `dict` 或分页 `dict`
- 不直接把 ORM 对象返回给 router

### 3.4 repository 职责

repository 只负责：
- 查询
- create / update / delete
- 条件筛选
- 分页查询

repository 不允许：
- `commit`
- `rollback`
- 写业务规则
- 判断状态是否合法

### 3.5 schema 约束

当前项目所有 schema 都继承 `BaseSchema`。

统一特点：
- `extra="forbid"`
- 使用 Pydantic v2
- 字符串常在 validator 中 `strip()`
- 可选字符串空串转 `None`
- 查询 schema 固定使用 `page/page_size`

---

## 4. 运行时与数据库约束

### 4.1 Session 模型

- 使用 `scoped_session`
- 每次请求通过 `g.db` 获取数据库 session
- session 生命周期由 Flask request hook 管理

### 4.2 数据库结构来源

当前数据库结构唯一事实来源是：
- Alembic migration

不要再回到：
- `db.create_all()`
- 启动应用自动建表

### 4.3 当前数据库表

按模块看，当前主要表已经包括：
- `users`
- `houses`
- `favorites`
- `appointments`
- `conversations`
- `messages`
- `contracts`
- `bills`
- `payments`
- `repairs`
- `complaints`
- `notifications`
- `news`
- `operation_logs`

### 4.4 时间策略

- 统一使用 UTC
- 返回给前端时为 ISO 8601 字符串

---

## 5. 全局规则

### 5.1 统一响应

成功：
- `code = 0`
- `message = "success"`

失败：
- `code != 0`
- `data = null`

### 5.2 通用权限规则

- `1003`：未登录或 token 无效
- `1004`：无权限

### 5.3 统一分页

当前项目列表返回统一结构：
- `list`
- `total`
- `page`
- `page_size`

service 侧统一复用：
- `get_offset()`
- `build_page_result()`

### 5.4 公开接口

当前允许匿名访问：
- `GET /api/v1/houses`
- `GET /api/v1/houses/{id}`
- `GET /api/v1/news`
- `GET /api/v1/news/{id}`

### 5.5 admin-only 策略

admin-only 接口不在 router 里写复杂判断，而是在 service 里统一处理。

如果普通 `tenant / landlord` 调 admin-only 接口，应返回：
- `1004`

---

## 6. 当前模块清单与实现状态

### 6.1 User / Auth

已实现：
- 注册
- 登录
- 登录态查询
- 当前用户资料查询
- 当前用户资料更新
- 邮箱验证码发送
- 邮箱验证码注册
- 邮箱验证码登录

角色：
- `tenant`
- `landlord`
- `admin`

状态：
- `active`
- `disabled`

当前没有做：
- 忘记密码
- 短信验证码
- 邮件找回密码

Auth v1.15.0 额外事实：
- 新增接口：
  - `POST /api/v1/auth/email/code`
  - `POST /api/v1/auth/email/register`
  - `POST /api/v1/auth/email/login`
- `AuthService` 主导邮箱验证码发送、校验、注册、登录、JWT 签发和事务控制
- `UserRepository` 只做用户表数据访问
- `UserService` 不参与邮箱验证码注册 / 登录流程
- 允许 `UserService` 为旧 `POST /api/v1/users` 增加 email normalize 和重复 email 校验，但仅限兼容 `users.email` 唯一约束
- 新增表：`email_verification_codes`
- 验证码固定 6 位数字，默认有效期 5 分钟
- 同一 `email + biz_type` 60 秒内不能重复发送
- 验证码只保存 `code_hash`，不明文入库
- email 在所有查询和入库前统一先做：
  - `strip()`
  - `lower()`
  - 空字符串转 `None`
- 邮箱验证码注册时 username 固定生成 `user_<random_hex>`
- `users.email` 已进入唯一约束路线；migration 会先把历史空字符串 email 清洗为 `NULL`
- 当前继续使用 MySQL 保存验证码，不引入 Redis、Celery、APScheduler 或异步任务

### 6.2 House

已实现：
- 房东创建房源
- 房源列表
- 房源详情
- 房东更新自己的房源
- 发布
- 下架
- 删除

状态流：
- `draft`
- `listed`
- `offline`

重要约束：
- 游客可看公开房源
- 房东只能操作自己的房源
- `House` 更偏“主业务数据”，状态流不要随意简化

### 6.3 Favorite

已实现：
- 收藏房源
- 我的收藏列表
- 取消收藏

重要约束：
- 收藏主体是当前登录用户
- 重复收藏会报错

### 6.4 Appointment

已实现：
- 租客发起预约
- 列表
- 房东确认 / 拒绝
- 租客取消

状态流：
- `pending`
- `confirmed`
- `rejected`
- `cancelled`
- `expired`

重要约束：
- 预约是合同的前置条件

### 6.5 Conversation / Message

已实现：
- 基于房源创建会话
- 会话列表
- 会话详情
- 消息列表
- 发送消息
- 标记已读

当前特点：
- 是 HTTP 轮询消息模型
- 不是 WebSocket 实时聊天

### 6.6 Contract

已实现：
- 房东基于预约创建合同
- 列表
- 详情
- 租客确认
- 租客拒绝
- 取消
- 终止
- admin 可在后台改合同状态

状态流：
- `pending`
- `active`
- `rejected`
- `cancelled`
- `terminated`

重要约束：
- 合同是账单、报修、投诉的根节点之一

### 6.7 Bill

已实现：
- 创建账单
- 列表
- 详情
- 取消账单
- 标记逾期

账单类型：
- `rent`
- `deposit`
- `other`

账单状态：
- `unpaid`
- `paid`
- `cancelled`
- `overdue`

重要约束：
- `overdue` 仍允许后续支付
- 当前版本没有退款、部分支付、支付回调

### 6.8 Payment

已实现：
- 创建支付
- 支付列表
- 支付详情

当前支付模型：
- 课程项目里的“支付记录 + 账单状态流转”
- 不接第三方网关

支付方式：
- `mock`
- `offline`

重要业务规则：
- 只有账单所属 `tenant` 可以支付
- `landlord`、`admin`、其他 tenant 调支付接口都返回 `1004`
- 支付成功时：
  - 创建 `payment`
  - 更新 `bill.status = paid`
  - 给 tenant 和 landlord 发通知
  - 写 `operation_log`

失败规则：
- 账单不存在：`2501`
- 账单状态不允许支付：`2602`
- 金额不匹配：`2603`
- 账单已支付：`2604`

### 6.9 Repair

已实现：
- 租客创建报修
- 报修列表
- 报修详情
- 租客关闭
- 房东或 admin 处理 / 完成 / 拒绝 / 关闭 / 重开

状态流：
- `pending`
- `processing`
- `completed`
- `rejected`
- `closed`
- `cancelled`
- `reopened`

当前联动：
- 状态变更会产生通知
- 关键写操作会写操作日志

### 6.10 Complaint

已实现：
- 租客创建投诉
- 列表
- 详情
- 租客关闭
- 房东或 admin 处理 / 解决 / 拒绝 / 关闭

状态流：
- `pending`
- `processing`
- `resolved`
- `rejected`
- `closed`

当前联动：
- 状态变更会产生通知
- 关键写操作会写操作日志

### 6.11 News

已实现：
- admin 创建公告
- 公告列表
- 公告详情
- admin 更新公告
- admin 删除公告

状态：
- `draft`
- `published`

权限规则：
- `POST / PATCH / DELETE` 为 admin-only
- 游客、tenant、landlord 只能看到 `published`
- admin 默认可以看到全部

重要实现：
- 删除为物理删除
- 发布公告或更新已发布公告时，会给所有 `active tenant + active landlord` 发通知
- 不给 admin 发公告通知
- 公告写操作已接入操作日志

### 6.12 Notification

这是最近一次重要收口点。

当前状态：
- Notification 创建能力已经彻底收口
- service 层只保留一个创建入口

唯一创建入口：

```python
NotificationService.create_notification(
    db,
    *,
    user_ids: list[int] | None = None,
    user_id: int | None = None,
    source_type: str,
    source_id: int,
    title: str,
    message: str,
    current_user_id=None,
    require_admin=False,
    auto_commit=True,
)
```

当前规则：
- `user_id` 和 `user_ids` 不能同时为空
- 也不能同时传
- `user_id` 会标准化为单元素 `user_ids`
- `user_ids=[]` 是参数错误
- 内部统一校验用户存在性
- 内部统一走 `NotificationRepository.bulk_create(...)`
- 返回值统一是 `list[dict]`
- 单用户创建也返回单元素列表

HTTP 层兼容策略：
- `POST /api/v1/notifications` 仍然是单用户接口
- router 从 service 返回列表中取 `[0]`
- 所以前端不感知内部批量收口

当前通知读取能力：
- 当前用户通知列表
- 当前用户通知详情
- 标记已读

通知状态：
- `unread`
- `read`

当前自动通知来源：
- `Repair`
- `Complaint`
- `Contract`
- `Bill`
- `Payment`
- `News`
- `Admin`

明确结论：
- 不允许再新增 `create_notifications(...)`
- 不允许业务侧手工循环逐个创建通知
- 所有通知创建必须收口到 `create_notification(...)`

### 6.13 Statistics

已实现：
- 房源利用率统计
- 租金收入统计
- 活跃用户统计
- 投诉 / 报修数量统计

定位：
- 聚合型接口
- 给后台仪表盘使用

权限：
- 当前 statistics 模块 4 个接口都是 `admin-only`

### 6.14 Admin

已实现：
- 用户管理
- 房源管理查询
- 投诉管理
- 报修管理
- 合同管理
- 操作日志查询

重要接口：
- `GET /api/v1/admin/users`
- `GET /api/v1/admin/houses`
- `GET /api/v1/admin/complaints`
- `GET /api/v1/admin/repairs`
- `GET /api/v1/admin/contracts`
- `GET /api/v1/admin/logs`

说明：
- admin 模块本身不追求“独立后台系统”，而是后端管理接口集合

### 6.15 Operation Log

这是最近新增的重要审计能力。

表：
- `operation_logs`

字段：
- `id`
- `user_id`
- `module`
- `record_id`
- `action`
- `before_status`
- `after_status`
- `created_at`
- `updated_at`

当前已记录模块：
- `repair`
- `complaint`
- `contract`
- `bill`
- `payment`
- `news`

当前设计原则：
- 只记录关键写操作
- 不记录读操作
- 不存完整快照
- 只记录操作前后状态
- 日志写入和业务操作在同一事务里
- 任一失败要整体回滚

查询接口：
- `GET /api/v1/admin/logs`

筛选：
- `page`
- `page_size`
- `module`
- `user_id`

---

## 7. 当前路由总表

Factory 当前注册的 blueprint 前缀为：

- `/api/v1/users`
- `/api/v1/auth`
- `/api/v1/houses`
- `/api/v1/news`
- `/api/v1/favorites`
- `/api/v1/appointments`
- `/api/v1/conversations`
- `/api/v1/contracts`
- `/api/v1/bills`
- `/api/v1/payments`
- `/api/v1/repairs`
- `/api/v1/complaints`
- `/api/v1/notifications`
- `/api/v1/statistics`
- `/api/v1/admin`

---

## 8. Notification 与 Operation Log 的当前结论

这是当前最容易在后续会话里被误判的部分，需要单独强调。

### 8.1 Notification 已彻底收口

不要再做这些事：
- 新增第二个批量通知 service 方法
- 恢复 `create_notifications(...)`
- 在业务 service 里手工循环逐个创建通知
- 让有的模块走批量，有的模块走单发

正确做法：
- 所有通知创建都走 `NotificationService.create_notification(...)`
- 单用户、多用户、不同文案分组，全部都调用这一个接口

### 8.2 Operation Log 已经接入关键业务流

以下模块的关键写操作已经应该写日志：
- `Repair`
- `Complaint`
- `Contract`
- `Bill`
- `Payment`
- `News`

后续新增关键后台操作时，要判断是否也应接入日志。

---

## 9. 当前测试覆盖

当前至少已经有这些测试：
- `tests/api/test_smoke_flow.py`
- `tests/api/test_news_flow.py`
- `tests/api/test_payment_flow.py`
- `tests/api/test_repair_flow.py`
- `tests/api/test_complaint_flow.py`
- `tests/api/test_admin_flow.py`
- `tests/service/test_notification_service.py`

覆盖重点包括：
- 主要 HTTP 业务流
- News CRUD 与通知
- Payment 支付闭环与通知
- Repair / Complaint 状态流
- Admin 查询
- Notification 统一批量接口的参数校验与回滚

---

## 10. 重要错误码速查

通用：
- `1003`：unauthorized
- `1004`：forbidden
- `3001`：bad request

News：
- `3002`：news not found
- `3003`：invalid news status

Payment：
- `2601`：payment not found
- `2602`：bill status is not payable
- `2603`：payment amount mismatch
- `2604`：bill already paid

Repair：
- `2701`：repair not found
- `2702`：repair status invalid

Complaint：
- `2801`：complaint not found
- `2802`：complaint status invalid

Notification：
- `2901`：notification not found
- `2902`：notification status invalid

注意：
- 不是所有模块都按“千位块”绝对严格划分
- 继续扩展时优先复用现有风格，不要随意发明混乱的新分段

---

## 11. 当前已知工程约束

### 11.1 不要重做架构

不要做这些事情：
- 改成微服务
- 改成 DDD 大重构
- 改成全异步框架
- 把 service / repository 重新洗牌

### 11.2 不要破坏事务边界

常见错误：
- 在 repository 里偷偷 `commit`
- 在 router 里直接写状态流
- 在通知 / 日志失败时只回滚一半

当前正确模式是：
- 业务 service 统一控制事务
- 业务操作、通知、操作日志在需要时同事务提交

### 11.3 不要让文档继续堆历史补丁

当前文档已重构为“当前事实版”。后续更新原则：
- `api.md` 维护当前 API 事实
- `ai_context.md` 维护当前项目交接上下文
- `CHANGELOG.md` 记录版本演进

不要再把“版本补充段”不断叠到 `api.md` 和 `ai_context.md` 正文后面。

---

## 12. 如果下一次会话继续开发，建议先看什么

建议顺序：

1. 先读本文，确认架构、规则和当前完成度  
2. 再看 [docs/api.md](/D:/a.python/real-estate215and1/docs/api.md)，确认外部接口事实  
3. 如要改业务，优先读对应模块的：
   - `router.py`
   - `service.py`
   - `repository.py`
   - `schema.py`
4. 如涉及数据库，先看 Alembic migration 与 model
5. 如涉及回归，先跑对应 `tests/api/*.py` 和 `tests/service/*.py`

---

## 13. 当前最可能的下一步工作

如果继续往下做，最自然的方向通常是：
- 前后端联调阶段的细节修正
- 补更多真实业务筛选字段
- 完善后台管理体验
- 增补更多测试覆盖
- 优化文档示例和错误说明

如果要做新功能，优先选择“沿现有架构扩展”的方式，不要引入与课程项目规模不匹配的复杂基础设施。
