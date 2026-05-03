# API 文档（当前实现）

Version: v1.15.0  
Base URL: `http://127.0.0.1:8000`  
统一前缀：`/api/v1`

---

## 1. 文档说明

这是一份面向前端联调的“当前实现版”接口文档，只描述仓库里已经实现并验证过的接口行为。

阅读约定：
- 本文档以当前代码行为为准，不追溯历史版本差异
- 所有时间字段均为 UTC，返回格式为 ISO 8601 字符串
- 所有列表接口默认使用统一分页结构
- 权限不足、状态不允许、资源不存在等错误，均通过统一错误码返回

---

## 2. 通用约定

### 2.1 认证

需要登录的接口统一使用：

```http
Authorization: Bearer <token>
```

未登录或 token 无效时，统一返回：

```json
{
  "code": 1003,
  "message": "unauthorized",
  "data": null
}
```

### 2.2 Content-Type

JSON 请求统一使用：

```http
Content-Type: application/json
```

### 2.3 统一成功响应

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

删除类接口通常返回：

```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

### 2.4 统一失败响应

```json
{
  "code": 3001,
  "message": "bad request",
  "data": null
}
```

### 2.5 分页结构

分页 query 统一使用：
- `page`：默认 `1`
- `page_size`：默认 `10`

分页响应统一结构：

```json
{
  "list": [],
  "total": 0,
  "page": 1,
  "page_size": 10
}
```

### 2.6 当前公开可匿名访问接口

- `GET /api/v1/houses`
- `GET /api/v1/houses/{id}`
- `GET /api/v1/news`
- `GET /api/v1/news/{id}`

其余接口默认需要登录。

---

## 3. 错误码速查

### 3.1 通用错误

- `1003`：未登录或 token 无效
- `1004`：无权限访问
- `3001`：请求参数错误
- `5000`：服务器内部错误

### 3.2 用户与认证

- `1001`：用户不存在
- `1002`：用户名或密码错误
- `2002`：用户名或邮箱已存在

### 3.3 房源 / 收藏 / 预约

- `2101`：房源不存在
- `2102`：房源状态不允许当前操作
- `2201`：收藏记录不存在
- `2202`：已收藏该房源
- `2301`：预约不存在
- `2302`：预约状态不允许当前操作

### 3.4 会话 / 合同 / 账单 / 支付

- `2401`：会话不存在
- `2402`：消息不存在
- `2501`：合同或账单相关资源不存在
- `2502`：合同状态不允许当前操作
- `2503`：账单状态不允许当前操作
- `2601`：支付记录不存在
- `2602`：账单当前状态不允许支付
- `2603`：支付金额不匹配
- `2604`：账单已支付

### 3.5 报修 / 投诉 / 通知 / 公告

- `2701`：报修不存在
- `2702`：报修状态不允许当前操作
- `2801`：投诉不存在
- `2802`：投诉状态不允许当前操作
- `2901`：通知不存在
- `2902`：通知状态不允许当前操作
- `3002`：公告不存在
- `3003`：公告状态非法

---

## 4. User 模块

### 4.1 模块说明

User 模块负责普通注册、个人资料查询与修改。

角色取值：
- `tenant`
- `landlord`
- `admin`

用户状态取值：
- `active`
- `disabled`

### 4.2 接口列表

- `POST /api/v1/users`
- `GET /api/v1/users/me`
- `PUT /api/v1/users/me`

### 4.3 注册

`POST /api/v1/users`

请求体：

```json
{
  "username": "alice",
  "password": "123456",
  "role": "tenant",
  "real_name": "Alice",
  "phone": "13800000000",
  "email": "alice@example.com",
  "avatar": "https://example.com/avatar.png"
}
```

字段规则：
- `username`：1-50
- `password`：6-255
- `role`：默认 `tenant`
- `real_name`：最长 50
- `phone`：最长 20
- `email`：最长 100
- `avatar`：最长 255

返回：
- 创建成功返回用户基础信息
- 不返回密码

### 4.4 获取当前用户

`GET /api/v1/users/me`

返回字段核心包括：
- `id`
- `username`
- `role`
- `status`
- `real_name`
- `phone`
- `email`
- `avatar`
- `created_at`

### 4.5 更新个人资料

`PUT /api/v1/users/me`

说明：
- 只能修改自己的资料
- 允许更新基础展示信息
- 不能通过该接口改角色

---

## 5. Auth 模块

### 5.1 接口列表

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/email/code`
- `POST /api/v1/auth/email/register`
- `POST /api/v1/auth/email/login`
- `GET /api/v1/auth/me`

### 5.2 用户名密码登录

`POST /api/v1/auth/login`

请求体：

```json
{
  "username": "alice",
  "password": "123456"
}
```

返回：

```json
{
  "token": "jwt-token",
  "token_type": "Bearer"
}
```

### 5.3 发送邮箱验证码

`POST /api/v1/auth/email/code`

请求体：

```json
{
  "email": "alice@example.com",
  "biz_type": "register"
}
```

字段说明：
- `email`：合法邮箱地址
- `biz_type`：`register` 或 `login`

业务规则：
- email 在 service 中统一先做 `strip() -> lower() -> 空串转 None`
- 验证码固定 6 位数字，默认有效期 5 分钟
- 同一 `email + biz_type` 60 秒内不允许重复发送
- 验证码只保存哈希，接口不会返回验证码明文
- `register`：邮箱未注册时允许发送，已注册返回 `2002`
- `login`：邮箱已注册且用户状态为 `active` 时允许发送；未注册返回 `1001`；非 `active` 返回 `1004`

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "message": "email code sent"
  }
}
```

常见错误：
- `2002`：邮箱已注册（发送 register 验证码）
- `1001`：用户不存在（发送 login 验证码）
- `1004`：用户状态不允许登录
- `3001`：验证码发送过快、参数错误、业务类型非法
- `5000`：邮件发送失败或 SMTP 配置错误

### 5.4 邮箱验证码注册

`POST /api/v1/auth/email/register`

请求体：

```json
{
  "email": "alice@example.com",
  "code": "123456",
  "role": "tenant",
  "password": "12345678",
  "real_name": "Alice",
  "phone": "13800000000",
  "avatar": "https://example.com/avatar.png"
}
```

字段说明：
- `email`：必填邮箱
- `code`：6 位数字验证码
- `role`：`tenant` 或 `landlord`，默认 `tenant`
- `password`：可选；不传时后端会生成随机不可记忆密码哈希，仅用于满足旧用户表非空约束
- `real_name / phone / avatar`：可选

业务规则：
- 只接受 `register` 类型、未过期、未使用的最新验证码
- 同一验证码只能使用一次
- 注册成功后验证码会被标记为已使用
- 前端不需要传 `username`
- 后端自动生成 `user_<random_hex>` 风格用户名
- 旧普通注册接口仍然是 `POST /api/v1/users`，不会被本接口替代

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "token": "jwt-token",
    "token_type": "Bearer",
    "user": {
      "id": 1,
      "username": "user_a1b2c3d4",
      "email": "alice@example.com",
      "role": "tenant",
      "status": "active"
    }
  }
}
```

常见错误：
- `2002`：邮箱已注册，或 username 极端冲突兜底
- `3001`：验证码错误、验证码过期、验证码已使用、参数错误
- `5000`：服务器内部错误

### 5.5 邮箱验证码登录

`POST /api/v1/auth/email/login`

请求体：

```json
{
  "email": "alice@example.com",
  "code": "123456"
}
```

业务规则：
- 只接受 `login` 类型、未过期、未使用的最新验证码
- 用户必须已注册
- 用户状态必须为 `active`
- 登录成功后验证码会被标记为已使用

成功响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "token": "jwt-token",
    "token_type": "Bearer",
    "user": {
      "id": 1,
      "username": "user_a1b2c3d4",
      "email": "alice@example.com",
      "role": "tenant",
      "status": "active"
    }
  }
}
```

常见错误：
- `1001`：用户不存在
- `1004`：用户状态不允许登录
- `3001`：验证码错误、验证码过期、验证码已使用、参数错误

### 5.6 登录态信息

`GET /api/v1/auth/me`

说明：
- 需要登录
- 返回当前 token 对应用户信息

### 5.7 SMTP 配置示例

```env
SMTP_SERVER=smtp.qq.com
SMTP_PORT=465
SMTP_USER=your_email@qq.com
SMTP_PASS=your_authorization_code
SMTP_USE_SSL=true
SMTP_USE_TLS=false
EMAIL_CODE_EXPIRE_MINUTES=5
EMAIL_CODE_RESEND_SECONDS=60
```

---

## 6. House 模块

### 6.1 模块说明

房源模块是平台核心公开内容。普通访客可查看列表和详情，房东可创建和管理自己的房源。

房源状态：
- `draft`
- `listed`
- `offline`

### 6.2 接口列表

- `POST /api/v1/houses`
- `GET /api/v1/houses`
- `GET /api/v1/houses/{id}`
- `PUT /api/v1/houses/{id}`
- `PATCH /api/v1/houses/{id}/publish`
- `PATCH /api/v1/houses/{id}/offline`
- `DELETE /api/v1/houses/{id}`

### 6.3 创建房源

`POST /api/v1/houses`

权限：
- 仅 `landlord`

请求体字段：
- `title`：1-100
- `address`：1-255
- `region`：1-100
- `community`：可选，最长 100
- `house_type`：1-50
- `area`：大于 0
- `rent`：大于等于 0
- `deposit`：大于等于 0
- `decoration`：可选，最长 50
- `floor`：可选，最长 50
- `orientation`：可选，最长 50
- `description`：可选

### 6.4 房源返回字段

`HouseReadSchema` 字段：
- `id`
- `landlord_id`
- `title`
- `address`
- `region`
- `community`
- `house_type`
- `area`
- `rent`
- `deposit`
- `decoration`
- `floor`
- `orientation`
- `description`
- `status`
- `created_at`
- `updated_at`

列表接口 `list` 中每一项和详情接口 `data` 都使用这套字段。

### 6.5 房源列表

`GET /api/v1/houses`

支持 query：
- `page`
- `page_size`
- `mine`：是否只看自己的房源
- `region`
- `house_type`
- `min_rent`
- `max_rent`
- `keyword`
- `min_area`
- `max_area`

前端使用建议：
- 游客和普通用户默认看公开房源
- 房东在个人中心可配合 `mine=true` 查看自己的房源

### 6.6 房源详情

`GET /api/v1/houses/{id}`

### 6.7 状态流转规则

- 新建房源默认进入 `draft`
- `publish`：草稿转 `listed`
- `offline`：已上架房源可下架
- `delete`：逻辑删除，不推荐前端继续展示

---

## 7. Favorite 模块

### 7.1 接口列表

- `POST /api/v1/favorites`
- `GET /api/v1/favorites`
- `DELETE /api/v1/favorites/{house_id}`

### 7.2 说明

- 收藏主体为当前登录用户
- 只能收藏存在的房源
- 重复收藏会返回业务错误
- 列表返回收藏记录及关联房源简要信息

返回字段：
- `house_id`
- `favorite_created_at`
- `house`

其中 `house` 字段为：
- `id`
- `title`
- `region`
- `address`
- `house_type`
- `area`
- `rent`
- `deposit`
- `status`

---

## 8. Appointment 模块

### 8.1 模块说明

预约看房由租客发起，房东处理。它是后续创建合同的重要前置步骤。

预约状态：
- `pending`
- `confirmed`
- `rejected`
- `cancelled`
- `expired`

### 8.2 接口列表

- `POST /api/v1/appointments`
- `GET /api/v1/appointments`
- `PATCH /api/v1/appointments/{id}/confirm`
- `PATCH /api/v1/appointments/{id}/reject`
- `PATCH /api/v1/appointments/{id}/cancel`

### 8.3 创建预约

请求体：

```json
{
  "house_id": 1,
  "appointment_time": "2026-05-03T10:00:00",
  "remark": "周末上午方便"
}
```

字段规则：
- `house_id >= 1`
- `appointment_time` 为 datetime
- `remark` 最长 1000，空串会转为 `null`

### 8.4 返回字段

说明：
- 租客看自己的预约
- 房东看自己房源相关预约
- 返回对象字段：
  - `id`
  - `house_id`
  - `tenant_id`
  - `landlord_id`
  - `appointment_time`
  - `remark`
  - `status`
  - `display_status`
  - `created_at`
  - `updated_at`
  - `relation_role`
  - `house`

其中 `house` 字段为：
- `id`
- `title`
- `region`
- `address`
- `house_type`
- `area`
- `rent`
- `deposit`
- `status`

### 8.5 列表接口

`GET /api/v1/appointments`

分页 `list` 中每一项都使用上面的完整返回结构。

### 8.6 状态流转

- 租客创建后为 `pending`
- 房东可 `confirm` 或 `reject`
- 租客可 `cancel`
- 过期由系统业务语义体现为 `expired`

---

## 9. Conversation / Message 模块

### 9.1 模块说明

会话模块用于围绕某个房源进行站内沟通。

### 9.2 接口列表

- `POST /api/v1/conversations`
- `GET /api/v1/conversations`
- `GET /api/v1/conversations/{id}`
- `GET /api/v1/conversations/{id}/messages`
- `POST /api/v1/conversations/{id}/messages`
- `PATCH /api/v1/conversations/{id}/read`

### 9.3 创建会话

请求体：

```json
{
  "house_id": 1
}
```

说明：
- 一般由租客对房源发起
- 创建后双方围绕该房源会有一个会话容器

### 9.4 发送消息

请求体：

```json
{
  "content": "你好，这套房还能预约吗？"
}
```

字段规则：
- `content`：1-1000

### 9.5 列表返回重点

会话列表返回核心字段：
- `id`
- `house_id`
- `tenant_id`
- `landlord_id`
- `created_at`
- `updated_at`
- `house`
- `last_message`
- `last_message_at`
- `unread_count`

其中：
- `house` 字段包含 `id/title/region/address/house_type/area/rent/deposit/status`
- `last_message` 字段包含 `id/sender_id/content/created_at/read_at`

消息对象字段为：
- `id`
- `conversation_id`
- `sender_id`
- `content`
- `created_at`
- `read_at`

---

## 10. Contract 模块

### 10.1 模块说明

合同由房东基于预约创建，租客确认后生效。

合同状态：
- `pending`
- `active`
- `rejected`
- `cancelled`
- `terminated`

### 10.2 接口列表

- `POST /api/v1/contracts`
- `GET /api/v1/contracts`
- `GET /api/v1/contracts/{id}`
- `PATCH /api/v1/contracts/{id}/confirm`
- `PATCH /api/v1/contracts/{id}/reject`
- `PATCH /api/v1/contracts/{id}/cancel`
- `PATCH /api/v1/contracts/{id}/terminate`

### 10.3 创建合同

请求体：

```json
{
  "appointment_id": 1,
  "start_date": "2026-06-01",
  "end_date": "2027-05-31",
  "monthly_rent": 3000,
  "deposit": 3000,
  "remark": "一年整租"
}
```

字段规则：
- `appointment_id >= 1`
- `monthly_rent >= 0`
- `deposit >= 0`
- `remark` 最长 1000

### 10.4 状态规则

- 房东创建后为 `pending`
- 租客 `confirm` 后进入 `active`
- 租客可 `reject`
- 合同可 `cancel`
- 生效合同可 `terminate`

### 10.5 返回字段

合同对象字段：
- `id`
- `house_id`
- `tenant_id`
- `landlord_id`
- `appointment_id`
- `start_date`
- `end_date`
- `monthly_rent`
- `deposit`
- `status`
- `remark`
- `created_at`
- `updated_at`
- `house`

其中 `house` 字段包含：
- `id`
- `title`
- `region`
- `address`
- `house_type`
- `area`
- `rent`
- `deposit`
- `status`

---

## 11. Bill 模块

### 11.1 模块说明

账单挂在合同下，用于租金、押金等费用管理。

账单类型：
- `rent`
- `deposit`
- `other`

账单状态：
- `unpaid`
- `paid`
- `cancelled`
- `overdue`

### 11.2 接口列表

- `POST /api/v1/bills`
- `GET /api/v1/bills`
- `GET /api/v1/bills/{id}`
- `PATCH /api/v1/bills/{id}/cancel`
- `PATCH /api/v1/bills/{id}/overdue`

### 11.3 创建账单

请求体：

```json
{
  "contract_id": 1,
  "bill_type": "rent",
  "amount": 3000,
  "due_date": "2026-06-05",
  "remark": "2026年6月房租"
}
```

字段规则：
- `contract_id >= 1`
- `bill_type` 取值为 `rent/deposit/other`
- `amount > 0`
- `remark` 最长 1000

### 11.4 说明

- 一般由房东创建
- 账单列表对合同参与双方开放
- `overdue` 仅表示逾期，仍允许后续支付

### 11.5 返回字段

账单对象字段：
- `id`
- `contract_id`
- `house_id`
- `tenant_id`
- `landlord_id`
- `bill_type`
- `amount`
- `due_date`
- `status`
- `remark`
- `created_at`
- `updated_at`

---

## 12. Payment 模块

### 12.1 模块说明

支付模块围绕账单支付行为展开。当前实现不是第三方支付，而是课程项目里的模拟支付记录。

支付方式：
- `mock`
- `offline`

### 12.2 接口列表

- `POST /api/v1/payments`
- `GET /api/v1/payments`
- `GET /api/v1/payments/{id}`

### 12.3 创建支付

`POST /api/v1/payments`

权限：
- 只有账单所属 `tenant` 可以支付
- `landlord`、`admin`、其他租客调用都返回 `1004`

请求体：

```json
{
  "bill_id": 1,
  "amount": 3000,
  "payment_method": "mock",
  "remark": "在线支付"
}
```

字段规则：
- `bill_id >= 1`
- `amount > 0`
- `payment_method` 只能为 `mock/offline`
- `remark` 最长 1000

### 12.4 创建支付后的联动

支付成功时会同时发生：
- 创建 `payment` 记录
- 对应 `bill.status` 更新为 `paid`
- 给 tenant 和 landlord 各创建一条通知
- 写入一条操作日志，模块为 `payment`，动作一般为 `pay`

### 12.5 失败场景

- 账单不存在：`2501`
- 账单状态不允许支付：`2602`
- 金额不匹配：`2603`
- 已支付或重复支付：`2604`

### 12.6 支付详情与列表

说明：
- 账单参与双方都能查看支付记录
- 非参与者查看详情会返回 `2601`

### 12.7 返回字段

支付对象字段：
- `id`
- `bill_id`
- `contract_id`
- `house_id`
- `tenant_id`
- `landlord_id`
- `amount`
- `payment_method`
- `status`
- `paid_at`
- `remark`
- `created_at`
- `updated_at`

---

## 13. Repair 模块

### 13.1 模块说明

报修由租客针对合同发起，房东或管理员处理。

报修状态：
- `pending`
- `processing`
- `completed`
- `rejected`
- `closed`
- `cancelled`
- `reopened`

### 13.2 接口列表

- `POST /api/v1/repairs`
- `GET /api/v1/repairs`
- `GET /api/v1/repairs/{id}`
- `PATCH /api/v1/repairs/{id}/process`
- `PATCH /api/v1/repairs/{id}/complete`
- `PATCH /api/v1/repairs/{id}/reject`
- `PATCH /api/v1/repairs/{id}/close`
- `PATCH /api/v1/repairs/{id}/reopen`

### 13.3 创建报修

请求体：

```json
{
  "contract_id": 1,
  "description": "厨房水龙头漏水"
}
```

字段规则：
- `contract_id >= 1`
- `description`：1-2000

### 13.4 列表筛选

支持：
- `page`
- `page_size`
- `status`

### 13.5 状态流转

- 租客创建后为 `pending`
- 房东或管理员 `process`
- 房东或管理员 `complete` 或 `reject`
- 租客或管理员可在规则允许时 `close`
- 租客或管理员可在规则允许时 `reopen`

### 13.6 返回字段

报修对象字段：
- `id`
- `contract_id`
- `house_id`
- `tenant_id`
- `landlord_id`
- `description`
- `status`
- `processed_at`
- `completed_at`
- `closed_at`
- `rejected_at`
- `cancelled_at`
- `reopened_at`
- `created_at`
- `updated_at`

---

## 14. Complaint 模块

### 14.1 模块说明

投诉由租客针对合同发起，房东或管理员处理。

投诉状态：
- `pending`
- `processing`
- `resolved`
- `rejected`
- `closed`

### 14.2 接口列表

- `POST /api/v1/complaints`
- `GET /api/v1/complaints`
- `GET /api/v1/complaints/{id}`
- `PATCH /api/v1/complaints/{id}/process`
- `PATCH /api/v1/complaints/{id}/resolve`
- `PATCH /api/v1/complaints/{id}/reject`
- `PATCH /api/v1/complaints/{id}/close`

### 14.3 创建投诉

请求体：

```json
{
  "contract_id": 1,
  "description": "房东长期不处理漏水问题"
}
```

字段规则：
- `contract_id >= 1`
- `description`：1-2000

### 14.4 列表筛选

支持：
- `page`
- `page_size`
- `status`

### 14.5 返回字段

投诉对象字段：
- `id`
- `contract_id`
- `house_id`
- `tenant_id`
- `landlord_id`
- `description`
- `status`
- `processed_at`
- `resolved_at`
- `closed_at`
- `rejected_at`
- `cancelled_at`
- `created_at`
- `updated_at`

---

## 15. News 模块

### 15.1 模块说明

公告模块对前端公开展示，对管理侧提供增删改能力。

公告状态：
- `draft`
- `published`

### 15.2 接口列表

- `POST /api/v1/news`
- `GET /api/v1/news`
- `GET /api/v1/news/{id}`
- `PATCH /api/v1/news/{id}`
- `DELETE /api/v1/news/{id}`

### 15.3 权限规则

- `POST /PATCH /DELETE`：仅 `admin`
- `GET 列表 / 详情`：
  - 游客、tenant、landlord 只能看 `published`
  - admin 登录后默认可看全部

### 15.4 创建与更新参数

请求体：

```json
{
  "title": "五一假期平台维护通知",
  "content": "平台将在周六凌晨进行维护。",
  "status": "published"
}
```

字段规则：
- `title`：1-200
- `content`：1-5000
- `status`：默认 `draft`

### 15.5 公告列表

支持 query：
- `page`
- `page_size`
- `status`

说明：
- 前台首页可直接使用该接口拉取公告列表
- tenant / landlord 传 `status=draft` 也不会获得草稿权限

### 15.6 发布联动

当公告创建为 `published`，或已发布公告被更新时：
- 会给全部 `active tenant + active landlord` 创建通知
- 不给 admin 发公告通知
- 会写入操作日志

### 15.7 删除规则

- 物理删除
- 已经发出的通知不会级联删除

### 15.8 返回字段

公告对象字段：
- `id`
- `title`
- `content`
- `author_id`
- `status`
- `created_at`
- `updated_at`

---

## 16. Notification 模块

### 16.1 模块说明

通知模块用于站内消息提醒。前端只看到单用户 HTTP 接口，但后端 service 内部已经统一为批量创建实现。

通知状态：
- `unread`
- `read`

### 16.2 接口列表

- `POST /api/v1/notifications`
- `GET /api/v1/notifications`
- `GET /api/v1/notifications/{id}`
- `PATCH /api/v1/notifications/{id}/read`

### 16.3 手动创建通知

`POST /api/v1/notifications`

权限：
- 仅 `admin`

请求体：

```json
{
  "user_id": 2,
  "source_type": "admin",
  "source_id": 1,
  "title": "系统通知",
  "message": "请尽快完善资料"
}
```

说明：
- HTTP 层仍然是单用户接口
- router 内部会把 service 返回的列表取第一项返回给前端
- 不提供手动批量通知 HTTP 接口

### 16.4 列表与详情

`GET /api/v1/notifications`

支持 query：
- `page`
- `page_size`
- `status`

说明：
- 只查询当前登录用户自己的通知
- 不能读取别人的通知

### 16.5 已读

`PATCH /api/v1/notifications/{id}/read`

说明：
- 只能把自己的 `unread` 通知标为 `read`
- 已经是 `read` 时会返回状态错误

### 16.6 当前自动通知来源

当前项目中，以下模块会自动创建通知：
- `Repair`
- `Complaint`
- `Contract`
- `Bill`
- `Payment`
- `News`
- `Admin`

### 16.7 后端内部实现说明

这部分给前端理解行为差异用：
- `NotificationService` 只保留一个 `create_notification(...)` 创建入口
- 内部支持 `user_id` 或 `user_ids`
- 统一使用批量写入
- 事务由业务 service 控制，失败整体回滚

### 16.8 返回字段

通知对象字段：
- `id`
- `user_id`
- `source_type`
- `source_id`
- `title`
- `message`
- `status`
- `created_at`
- `updated_at`

---

## 17. Statistics 模块

### 17.1 模块说明

统计模块面向登录用户和管理员返回看板类数据。

### 17.2 接口列表

- `GET /api/v1/statistics/house-utilization`
- `GET /api/v1/statistics/rent-income`
- `GET /api/v1/statistics/active-users`
- `GET /api/v1/statistics/complaint-repair-count`

### 17.3 权限说明

- 当前统计接口均为 `admin-only`

### 17.4 返回字段

`GET /api/v1/statistics/house-utilization` 返回：
- `total_houses`
- `occupied_houses`
- `utilization_rate`

`GET /api/v1/statistics/rent-income` 返回：
- `total_income`
- `monthly_income`

其中 `monthly_income` 每项字段：
- `month`
- `amount`

`GET /api/v1/statistics/active-users` 返回：
- `active_user_count`

`GET /api/v1/statistics/complaint-repair-count` 返回：
- `repair_count`
- `complaint_count`

---

## 18. Admin 模块

### 18.1 模块说明

Admin 模块是后台管理入口，全部接口仅 `admin` 可用。

### 18.2 接口列表

用户管理：
- `GET /api/v1/admin/users`
- `GET /api/v1/admin/users/{id}`
- `POST /api/v1/admin/users`
- `PUT /api/v1/admin/users/{id}`
- `PATCH /api/v1/admin/users/{id}/status`

房源管理：
- `GET /api/v1/admin/houses`
- `GET /api/v1/admin/houses/{id}`

投诉管理：
- `GET /api/v1/admin/complaints`
- `GET /api/v1/admin/complaints/{id}`
- `PATCH /api/v1/admin/complaints/{id}/process`
- `PATCH /api/v1/admin/complaints/{id}/resolve`
- `PATCH /api/v1/admin/complaints/{id}/reject`
- `PATCH /api/v1/admin/complaints/{id}/close`

报修管理：
- `GET /api/v1/admin/repairs`
- `GET /api/v1/admin/repairs/{id}`
- `PATCH /api/v1/admin/repairs/{id}/process`
- `PATCH /api/v1/admin/repairs/{id}/complete`
- `PATCH /api/v1/admin/repairs/{id}/reject`
- `PATCH /api/v1/admin/repairs/{id}/close`

合同管理：
- `GET /api/v1/admin/contracts`
- `GET /api/v1/admin/contracts/{id}`
- `PATCH /api/v1/admin/contracts/{id}/status`

操作日志：
- `GET /api/v1/admin/logs`

### 18.3 用户管理说明

管理员可以：
- 创建用户
- 更新用户资料
- 修改用户状态
- 查看平台用户分页列表

用户对象字段：
- `id`
- `username`
- `role`
- `real_name`
- `phone`
- `email`
- `avatar`
- `status`
- `created_at`
- `updated_at`

### 18.4 房源管理说明

管理员房源列表支持：
- `page`
- `page_size`
- `region`
- `house_type`
- `min_rent`
- `max_rent`
- `keyword`
- `min_area`
- `max_area`

后台房源对象字段与普通房源详情一致：
- `id`
- `landlord_id`
- `title`
- `address`
- `region`
- `community`
- `house_type`
- `area`
- `rent`
- `deposit`
- `decoration`
- `floor`
- `orientation`
- `description`
- `status`
- `created_at`
- `updated_at`

### 18.5 合同管理说明

管理员可修改合同状态，允许的状态值：
- `active`
- `terminated`
- `cancelled`

后台合同对象字段与普通合同详情一致。

### 18.6 操作日志查询

`GET /api/v1/admin/logs`

支持 query：
- `page`
- `page_size`
- `module`
- `user_id`

`module` 当前支持：
- `repair`
- `complaint`
- `contract`
- `bill`
- `payment`
- `news`

返回单条日志核心字段：
- `id`
- `user_id`
- `module`
- `record_id`
- `action`
- `before_status`
- `after_status`
- `created_at`
- `updated_at`

---

## 19. 操作日志说明

### 19.1 当前记录范围

系统当前会对以下关键写操作记录操作日志：
- `Repair`
- `Complaint`
- `Contract`
- `Bill`
- `Payment`
- `News`

### 19.2 日志字段含义

- `user_id`：谁触发了该操作
- `module`：所属业务模块
- `record_id`：对应业务记录 ID
- `action`：动作，例如 `create`、`update`、`delete`、`pay`
- `before_status`：操作前状态，可为空
- `after_status`：操作后状态，可为空

### 19.3 前端使用建议

- 后台审计页可直接使用 `GET /api/v1/admin/logs`
- 可按模块筛选，也可按操作用户筛选
- 适合做“最新操作记录”列表和详情抽屉

---

## 20. 前端对接建议

- 登录后统一保存 JWT，所有受保护接口带 `Authorization`
- 对所有分页接口，统一适配 `list / total / page / page_size`
- 对公告、房源、统计、通知等首页内容，建议按模块分别封装 API client
- 对状态按钮类操作，优先根据当前状态决定是否展示，而不是依赖后端报错后再回退
- 对 `1004` 应直接提示“无权限”
- 对 `3001` 应提示“参数错误或表单不完整”
- 对业务错误码建议保留原码，便于界面显示更准确的提示

---

## 21. 常见响应示例

### 21.1 分页列表示例

以 `GET /api/v1/news?page=1&page_size=10` 为例：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "title": "五一假期平台维护通知",
        "content": "平台将在周六凌晨进行维护。",
        "author_id": 3,
        "status": "published",
        "created_at": "2026-05-02T08:00:00",
        "updated_at": "2026-05-02T08:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
  }
}
```

### 21.2 房源详情示例

`GET /api/v1/houses/{id}`

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "landlord_id": 2,
    "title": "近地铁一室一厅",
    "address": "xx路88号",
    "region": "浦东新区",
    "community": "阳光花园",
    "house_type": "1室1厅1卫",
    "area": "58.00",
    "rent": "3200.00",
    "deposit": "3200.00",
    "decoration": "精装",
    "floor": "8/18",
    "orientation": "南",
    "description": "拎包入住",
    "status": "listed",
    "created_at": "2026-05-01T10:00:00",
    "updated_at": "2026-05-02T09:00:00"
  }
}
```

### 21.3 支付成功响应示例

`POST /api/v1/payments`

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 5,
    "bill_id": 8,
    "contract_id": 3,
    "house_id": 12,
    "tenant_id": 21,
    "landlord_id": 9,
    "amount": "3000.00",
    "payment_method": "mock",
    "status": "success",
    "paid_at": "2026-05-02T12:30:00",
    "remark": "在线支付",
    "created_at": "2026-05-02T12:30:00",
    "updated_at": "2026-05-02T12:30:00"
  }
}
```

### 21.4 通知列表示例

`GET /api/v1/notifications`

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 11,
        "user_id": 21,
        "source_type": "payment",
        "source_id": 8,
        "title": "Payment successful",
        "message": "Your payment has been recorded.",
        "status": "unread",
        "created_at": "2026-05-02T12:30:00",
        "updated_at": "2026-05-02T12:30:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
  }
}
```

### 21.5 后台日志列表示例

`GET /api/v1/admin/logs`

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 7,
        "user_id": 3,
        "module": "payment",
        "record_id": 5,
        "action": "pay",
        "before_status": "unpaid",
        "after_status": "paid",
        "created_at": "2026-05-02T12:30:00",
        "updated_at": "2026-05-02T12:30:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
  }
}
```

---

## 22. 前端类型定义建议

如果前端要先建 TypeScript 类型，可以按下面这几个核心对象优先落类型。

### 22.1 User

```ts
type User = {
  id: number;
  username: string;
  role: "tenant" | "landlord" | "admin";
  real_name: string | null;
  phone: string | null;
  email: string | null;
  avatar: string | null;
  status: "active" | "disabled";
  created_at: string;
};
```

### 22.2 House

```ts
type House = {
  id: number;
  landlord_id: number;
  title: string;
  address: string;
  region: string;
  community: string | null;
  house_type: string;
  area: string;
  rent: string;
  deposit: string;
  decoration: string | null;
  floor: string | null;
  orientation: string | null;
  description: string | null;
  status: "draft" | "listed" | "offline";
  created_at: string;
  updated_at: string;
};
```

### 22.3 News

```ts
type News = {
  id: number;
  title: string;
  content: string;
  author_id: number;
  status: "draft" | "published";
  created_at: string;
  updated_at: string;
};
```

### 22.4 Payment

```ts
type Payment = {
  id: number;
  bill_id: number;
  contract_id: number;
  house_id: number;
  tenant_id: number;
  landlord_id: number;
  amount: string;
  payment_method: "mock" | "offline";
  status: "success";
  paid_at: string;
  remark: string | null;
  created_at: string;
  updated_at: string;
};
```

### 22.5 Notification

```ts
type Notification = {
  id: number;
  user_id: number;
  source_type: string;
  source_id: number;
  title: string;
  message: string;
  status: "unread" | "read";
  created_at: string;
  updated_at: string;
};
```

### 22.6 OperationLog

```ts
type OperationLog = {
  id: number;
  user_id: number;
  module: "repair" | "complaint" | "contract" | "bill" | "payment" | "news";
  record_id: number;
  action: string;
  before_status: string | null;
  after_status: string | null;
  created_at: string;
  updated_at: string;
};
```

### 22.7 通用分页类型

```ts
type PageResult<T> = {
  list: T[];
  total: number;
  page: number;
  page_size: number;
};
```

---

## 23. 当前已验证测试

已经覆盖并验证过的主要测试流包括：
- `tests/api/test_smoke_flow.py`
- `tests/api/test_news_flow.py`
- `tests/api/test_payment_flow.py`
- `tests/api/test_repair_flow.py`
- `tests/api/test_complaint_flow.py`
- `tests/api/test_admin_flow.py`
- `tests/service/test_notification_service.py`

如果前端联调时出现与本文档不一致的行为，应优先检查当前代码和最近一次测试结果。
