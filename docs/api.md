# API 文档（当前实现）

Version: v1.14.0
Base URL: `http://127.0.0.1:8000`

统一前缀：

```text
/api/v1
```

------

# 一、通用约定

## 1. 请求头

### JSON 请求

```http
Content-Type: application/json
```

### 认证请求

```http
Authorization: Bearer <token>
```

------

## 2. 统一响应结构

### 成功

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

### 失败

```json
{
  "code": 3001,
  "message": "参数错误",
  "data": null
}
```

------

## 3. 错误码

| code | 含义                   |
| ---- | ---------------------- |
| 0    | 成功                   |
| 3001 | 参数错误               |
| 1001 | 用户不存在             |
| 1002 | 用户名或密码错误       |
| 1003 | 未登录 / token 无效    |
| 2001 | 房源不存在             |
| 2101 | 收藏不存在             |
| 2201 | 预约不存在             |
| 2202 | 非法预约状态           |
| 2203 | 不能预约自己的房源     |
| 2204 | 预约时间必须是未来时间 |
| 2501 | 账单不存在             |
| 2502 | 非法账单状态           |
| 2503 | 合同未生效，不能创建账单 |
| 2504 | 账单金额不合法         |
| 4009 | 资源冲突               |
| 5000 | 系统错误               |

------

## 4. 认证 Helper 说明

需要登录的接口必须携带：

```
Authorization: Bearer <token>
```

当前服务端通过最小认证 helper 获取当前用户：

```
app/common/dependencies.py
```

提供两个函数：

- `get_required_current_user_id()`
- `get_optional_current_user_id()`

#### get_required_current_user_id

用于必须登录的接口。

规则：

- 没有 `Authorization` 请求头，返回 `1003`
- token 格式错误，返回 `1003`
- token 过期或签名失败，返回 `1003`
- token 合法时，返回当前用户 id

适用接口：

```
GET    /api/v1/auth/me
POST   /api/v1/houses
GET    /api/v1/houses?mine=true
PUT    /api/v1/houses/{id}
PATCH  /api/v1/houses/{id}/publish
PATCH  /api/v1/houses/{id}/offline
DELETE /api/v1/houses/{id}
POST   /api/v1/favorites
GET    /api/v1/favorites
DELETE /api/v1/favorites/{house_id}
POST   /api/v1/appointments
GET    /api/v1/appointments
PATCH  /api/v1/appointments/{id}/confirm
PATCH  /api/v1/appointments/{id}/reject
PATCH  /api/v1/appointments/{id}/cancel
```

#### get_optional_current_user_id

用于可选登录的接口。

规则：

- 不携带 token 时，返回 `None`，按游客处理
- 携带合法 token 时，返回当前用户 id
- 携带非法 token 时，返回 `1003`

当前适用接口：

```
GET /api/v1/houses/{id}
```

该接口规则：

- `listed` 房源：游客和登录用户都可查看
- `draft/offline` 房源：只有房东本人可查看
- 已逻辑删除房源：统一返回房源不存在

#### 未登录响应

```
{
  "code": 1003,
  "message": "未登录",
  "data": null
}
```

# 二、User 模块

------

## 1. 创建用户（注册）

### 接口

```http
POST /api/v1/users
```

### 请求体

```json
{
  "username": "string",
  "password": "string",
  "email": "string（可选）"
}
```

### 成功响应（201）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "u1",
    "role": "tenant",
    "real_name": null,
    "phone": null,
    "email": "u1@example.com",
    "avatar": null,
    "status": "active",
    "created_at": "2026-04-22T10:00:00"
  }
}
```

### 失败响应

#### 用户名冲突（409）

```json
{
  "code": 4009,
  "message": "用户名已存在",
  "data": null
}
```

#### 参数错误（400）

```json
{
  "code": 3001,
  "message": "参数错误",
  "data": null
}
```

------

## 2. 获取用户列表（分页）

### 接口

```http
GET /api/v1/users
```

### Query 参数

| 参数      | 类型 | 默认值 | 说明                 |
| --------- | ---- | ------ | -------------------- |
| page      | int  | 1      | 页码                 |
| page_size | int  | 10     | 每页数量（最大 100） |

------

### 请求示例

```http
GET /api/v1/users?page=1&page_size=10
```

------

### 成功响应（200）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "username": "u1",
        "role": "tenant",
        "email": "u1@example.com",
        "status": "active",
        "created_at": "2026-04-22T10:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 10
  }
}
```

------

### 参数错误（400）

```json
{
  "code": 3001,
  "message": "参数错误",
  "data": null
}
```

------

## 3. 获取用户详情

### 接口

```http
GET /api/v1/users/{id}
```

------

### 成功响应（200）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "u1",
    "role": "tenant",
    "email": "u1@example.com",
    "status": "active",
    "created_at": "2026-04-22T10:00:00"
  }
}
```

------

### 用户不存在（404）

```json
{
  "code": 1001,
  "message": "用户不存在",
  "data": null
}
```

------

# 三、Auth 模块

------

## 1. 用户登录

### 接口

```http
POST /api/v1/auth/login
```

------

### 请求体

```json
{
  "username": "string",
  "password": "string"
}
```

------

### 成功响应（200）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "token": "xxxxx",
    "token_type": "Bearer"
  }
}
```

------

### 登录失败（401）

```json
{
  "code": 1002,
  "message": "用户名或密码错误",
  "data": null
}
```

------

## 2. 获取当前用户

### 接口

```http
GET /api/v1/auth/me
```

------

### 请求头

```http
Authorization: Bearer <token>
```

------

### 成功响应（200）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "u1",
    "role": "tenant",
    "email": "u1@example.com",
    "status": "active",
    "created_at": "2026-04-22T10:00:00"
  }
}
```

------

### 未登录 / token 无效（401）

```json
{
  "code": 1003,
  "message": "未登录或认证无效",
  "data": null
}
```

------

# 四、House 模块

## 0. 业务规则总览

### 0.1 房源状态

House 第一版只使用 3 个状态：

| status  | 含义              | 是否公开展示 |
| ------- | ----------------- | ------------ |
| draft   | 草稿 / 未发布     | 否           |
| listed  | 已上架            | 是           |
| offline | 已下架 / 放弃发布 | 否           |

### 0.2 状态流转

| 操作     | 允许流转                                   |
| -------- | ------------------------------------------ |
| 创建房源 | 默认 `draft`                               |
| 发布房源 | `draft -> listed`，`offline -> listed`     |
| 下架房源 | `listed -> offline`，`draft -> offline`    |
| 删除房源 | 设置 `deleted_at`，同时 `status = offline` |

### 0.3 可见性规则

| 场景                             | 可见数据                                              |
| -------------------------------- | ----------------------------------------------------- |
| 公共列表 `GET /houses`           | 未删除且 `status = listed`                            |
| 我的房源 `GET /houses?mine=true` | 当前用户自己的未删除房源，包含 `draft/listed/offline` |
| 公共详情 `GET /houses/{id}`      | 未删除且 `listed` 的房源                              |
| 房东本人看详情                   | 可看自己未删除的 `draft/listed/offline` 房源          |
| 删除后的房源                     | 不出现在任何列表；详情统一返回房源不存在              |

### 0.4 权限规则

- 创建、更新、发布、下架、删除房源必须登录。
- `landlord_id` 不允许前端传，由后端从 JWT token 解析当前用户 id 自动绑定。
- 更新、发布、下架、删除只能操作当前用户自己的房源。
- 非本人操作房源时，统一返回 `2001 house not found`。
- `PUT /houses/{id}` 不允许修改 `status`，状态只能通过 `publish/offline` 接口修改。

------

## 1. 创建房源

### 接口

```http
POST /api/v1/houses
```

### 是否需要认证

需要。

```http
Authorization: Bearer <token>
```

### 请求体

```json
{
  "title": "测试房源A",
  "address": "地址A",
  "region": "区域A",
  "community": "小区A（可选）",
  "house_type": "1室1厅",
  "area": 50,
  "rent": 2000,
  "deposit": 2000,
  "decoration": "精装修（可选）",
  "floor": "6/18（可选）",
  "orientation": "南（可选）",
  "description": "test"
}
```

### 请求字段说明

| 字段        | 类型    | 必填 | 说明              |
| ----------- | ------- | ---- | ----------------- |
| title       | string  | 是   | 房源标题          |
| address     | string  | 是   | 地址              |
| region      | string  | 是   | 区域              |
| community   | string  | 否   | 小区              |
| house_type  | string  | 是   | 户型              |
| area        | decimal | 是   | 面积，必须 `> 0`  |
| rent        | decimal | 是   | 月租，必须 `>= 0` |
| deposit     | decimal | 是   | 押金，必须 `>= 0` |
| decoration  | string  | 否   | 装修情况          |
| floor       | string  | 否   | 楼层              |
| orientation | string  | 否   | 朝向              |
| description | string  | 否   | 描述              |

说明：

- 请求体不允许包含 `landlord_id`。
- 请求体不允许包含 `status`。
- 创建成功后，后端自动设置 `status = draft`。

### 成功响应（201）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "landlord_id": 1,
    "title": "测试房源A",
    "address": "地址A",
    "region": "区域A",
    "community": null,
    "house_type": "1室1厅",
    "area": "50.00",
    "rent": "2000.00",
    "deposit": "2000.00",
    "decoration": null,
    "floor": null,
    "orientation": null,
    "description": "test",
    "status": "draft",
    "created_at": "2026-04-23T23:45:19",
    "updated_at": "2026-04-23T23:45:19"
  }
}
```

### 失败响应

#### 未登录（401）

```json
{
  "code": 1003,
  "message": "未登录",
  "data": null
}
```

#### 参数错误（400）

```json
{
  "code": 3001,
  "message": "bad request",
  "data": [
    {
      "loc": ["title"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

------

## 2. 公共房源列表

### 接口

```http
GET /api/v1/houses?page=1&page_size=10
```

### 是否需要认证

不需要。

### Query 参数

| 参数       | 类型    | 默认值 | 说明                                                 |
| ---------- | ------- | ------ | ---------------------------------------------------- |
| page       | int     | 1      | 页码，必须 `>= 1`                                    |
| page_size  | int     | 10     | 每页数量，最大 100                                   |
| region     | string  | 无     | 按区域精确筛选                                       |
| house_type | string  | 无     | 按户型精确筛选                                       |
| min_rent   | decimal | 无     | 月租下限，必须 `>= 0`                                |
| max_rent   | decimal | 无     | 月租上限，必须 `>= 0`                                |
| keyword    | string  | 无     | 关键字模糊匹配 `title/address/community/description` |
| min_area   | decimal | 无     | 面积下限，必须 `>= 0`                                |
| max_area   | decimal | 无     | 面积上限，必须 `>= 0`                                |

### 业务规则

- 只返回未删除房源。
- 只返回 `status = listed` 的房源。
- 默认按 `id DESC` 排序。
- 不返回 `draft/offline`。
- 支持筛选条件与分页同时使用。
- 当 `min_rent > max_rent` 或 `min_area > max_area` 时，返回 `3001 bad request`。
- 参数校验失败时，统一返回 JSON 结构，不返回 HTML 500 页面。

### 筛选示例

```http
GET /api/v1/houses?page=1&page_size=10&region=区域A&house_type=1室1厅&min_rent=1000&max_rent=3000&keyword=地铁&min_area=30&max_area=80
```

### 非法范围响应示例（400）

```json
{
  "code": 3001,
  "message": "bad request",
  "data": [
    {
      "type": "value_error",
      "loc": [],
      "msg": "Value error, min_rent cannot be greater than max_rent"
    }
  ]
}
```

### 成功响应（200）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "landlord_id": 1,
        "title": "测试房源A",
        "address": "地址A",
        "region": "区域A",
        "house_type": "1室1厅",
        "area": "50.00",
        "rent": "2000.00",
        "deposit": "2000.00",
        "status": "listed",
        "created_at": "2026-04-23T23:45:19",
        "updated_at": "2026-04-23T23:46:10"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
  }
}
```

------

## 3. 我的房源列表

### 接口

```http
GET /api/v1/houses?mine=true&page=1&page_size=10
```

### 是否需要认证

需要。

```http
Authorization: Bearer <token>
```

### 业务规则

- 只返回当前登录用户作为 `landlord` 的房源。
- 不混入公共房源。
- 只返回未删除房源。
- 返回状态包含 `draft/listed/offline`。
- 默认按 `id DESC` 排序。
- 支持以下筛选参数，并可与分页同时使用：
  - `region`
  - `house_type`
  - `min_rent`
  - `max_rent`
  - `keyword`
  - `min_area`
  - `max_area`
- `keyword` 匹配 `title / address / community / description`。

### Query 参数

| 参数       | 类型    | 默认值 | 说明                                                 |
| ---------- | ------- | ------ | ---------------------------------------------------- |
| mine       | bool    | true   | 固定表示查询当前用户自己的房源                       |
| page       | int     | 1      | 页码，必须 `>= 1`                                    |
| page_size  | int     | 10     | 每页数量，最大 100                                   |
| region     | string  | 无     | 按区域精确筛选                                       |
| house_type | string  | 无     | 按户型精确筛选                                       |
| min_rent   | decimal | 无     | 月租下限，必须 `>= 0`                                |
| max_rent   | decimal | 无     | 月租上限，必须 `>= 0`                                |
| keyword    | string  | 无     | 关键字模糊匹配 `title/address/community/description` |
| min_area   | decimal | 无     | 面积下限，必须 `>= 0`                                |
| max_area   | decimal | 无     | 面积上限，必须 `>= 0`                                |

### 请求示例

```http
GET /api/v1/houses?mine=true&page=1&page_size=10&region=区域A&min_rent=1000&keyword=精装
```

### 成功响应（200）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "landlord_id": 1,
        "title": "测试房源A",
        "status": "draft",
        "created_at": "2026-04-23T23:45:19",
        "updated_at": "2026-04-23T23:45:19"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
  }
}
```

### 未登录（401）

```json
{
  "code": 1003,
  "message": "未登录",
  "data": null
}
```

------

## 4. 获取房源详情

### 接口

```http
GET /api/v1/houses/{id}
```

### 是否需要认证

不强制。

如果请求头携带合法 token，系统会尝试识别当前用户，用于判断是否为房东本人。

### 业务规则

- `listed` 房源：所有人可查看。
- `draft/offline` 房源：只有房东本人可查看。
- 已删除房源：统一返回房源不存在。
- 非房东访问非公开房源：统一返回房源不存在。

### 成功响应（200）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "landlord_id": 1,
    "title": "测试房源A",
    "address": "地址A",
    "region": "区域A",
    "house_type": "1室1厅",
    "area": "50.00",
    "rent": "2000.00",
    "deposit": "2000.00",
    "description": "test",
    "status": "listed",
    "created_at": "2026-04-23T23:45:19",
    "updated_at": "2026-04-23T23:46:10"
  }
}
```

### 房源不存在 / 无权访问（404）

```json
{
  "code": 2001,
  "message": "house not found",
  "data": null
}
```

------

## 5. 更新房源资料

### 接口

```http
PUT /api/v1/houses/{id}
```

### 是否需要认证

需要。

```http
Authorization: Bearer <token>
```

### 请求体

```json
{
  "title": "更新后的房源标题",
  "address": "地址A",
  "region": "区域A",
  "community": "小区A",
  "house_type": "1室1厅",
  "area": 55,
  "rent": 2200,
  "deposit": 2200,
  "decoration": "精装修",
  "floor": "6/18",
  "orientation": "南",
  "description": "updated"
}
```

### 业务规则

- 只能更新当前用户自己的未删除房源。
- 不允许更新 `landlord_id`。
- 不允许更新 `status`。
- 请求体如果包含 `status`，按参数错误处理。
- 房源不存在或不属于当前用户，统一返回 `2001 house not found`。

### 成功响应（200）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "landlord_id": 1,
    "title": "更新后的房源标题",
    "status": "draft",
    "updated_at": "2026-04-23T23:50:00"
  }
}
```

### 禁止通过 PUT 修改 status

请求：

```json
{
  "status": "listed"
}
```

响应示例：

```json
{
  "code": 3001,
  "message": "bad request",
  "data": [
    {
      "loc": ["status"],
      "msg": "Extra inputs are not permitted",
      "type": "extra_forbidden"
    }
  ]
}
```

------

## 6. 发布房源

### 接口

```http
PATCH /api/v1/houses/{id}/publish
```

### 是否需要认证

需要。

### 业务规则

- 只能操作当前用户自己的未删除房源。
- 允许状态流转：
  - `draft -> listed`
  - `offline -> listed`
- 其他状态调用按非法状态流转处理。
- 不允许操作已删除房源。

### 成功响应（200）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "landlord_id": 1,
    "title": "测试房源A",
    "status": "listed",
    "updated_at": "2026-04-23T23:46:10"
  }
}
```

### 房源不存在 / 无权操作（404）

```json
{
  "code": 2001,
  "message": "house not found",
  "data": null
}
```

------

## 7. 下架房源

### 接口

```http
PATCH /api/v1/houses/{id}/offline
```

### 是否需要认证

需要。

### 业务规则

- 只能操作当前用户自己的未删除房源。
- 允许状态流转：
  - `listed -> offline`
  - `draft -> offline`（等价于“放弃发布”）
- `offline -> offline` 按非法状态流转处理。
- 不允许操作已删除房源。

### 成功响应（200）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "landlord_id": 1,
    "title": "测试房源A",
    "status": "offline",
    "updated_at": "2026-04-23T23:47:00"
  }
}
```

------

## 8. 删除房源（逻辑删除）

### 接口

```http
DELETE /api/v1/houses/{id}
```

### 是否需要认证

需要。

### 业务规则

- 只能删除当前用户自己的未删除房源。
- 删除为逻辑删除，不做物理删除。
- 删除时设置 `deleted_at`。
- 删除时同时将 `status` 置为 `offline`。
- 删除后房源不出现在任何列表中。
- 删除后 `GET /api/v1/houses/{id}` 统一返回房源不存在。
- 删除后不能再次更新、发布、下架或删除。

### 成功响应（200）

```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

### 房源不存在 / 无权操作（404）

```json
{
  "code": 2001,
  "message": "house not found",
  "data": null
}
```

------

# 五、Favorite 模块

## 1. 收藏房源

### 接口

```http
POST /api/v1/favorites
```

### 是否需要认证

需要。

```http
Authorization: Bearer <token>
```

### 请求体

```json
{
  "house_id": 1
}
```

### 业务规则

- 只允许收藏未删除且 `status = listed` 的房源。
- 房源不存在、已删除、非 `listed`，统一返回 `2001 房源不存在`。
- 不允许重复收藏。
- 同一用户对同一房源只能有一条收藏记录。

### 成功响应（201）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "house_id": 1,
    "favorite_created_at": "2026-04-24T10:00:00",
    "house": {
      "id": 1,
      "title": "测试房源",
      "region": "区域A",
      "address": "地址A",
      "house_type": "1室1厅",
      "area": "50.00",
      "rent": "2000.00",
      "deposit": "2000.00",
      "status": "listed"
    }
  }
}
```

### 房源不存在（404）

```json
{
  "code": 2001,
  "message": "house not found",
  "data": null
}
```

### 重复收藏（409）

```json
{
  "code": 4009,
  "message": "favorite already exists",
  "data": null
}
```

------

## 2. 我的收藏列表

### 接口

```http
GET /api/v1/favorites?page=1&page_size=10
```

### 是否需要认证

需要。

### Query 参数

| 参数      | 类型 | 默认值 | 说明                 |
| --------- | ---- | ------ | -------------------- |
| page      | int  | 1      | 页码                 |
| page_size | int  | 10     | 每页数量（最大 100） |

### 业务规则

- 只返回当前用户自己的收藏。
- 只返回当前仍 `listed` 且未删除的房源。
- 默认按收藏时间倒序。
- 返回结构为 `house_id + favorite_created_at + house`。

### 成功响应（200）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "house_id": 1,
        "favorite_created_at": "2026-04-24T10:00:00",
        "house": {
          "id": 1,
          "title": "测试房源",
          "region": "区域A",
          "address": "地址A",
          "house_type": "1室1厅",
          "area": "50.00",
          "rent": "2000.00",
          "deposit": "2000.00",
          "status": "listed"
        }
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
  }
}
```

------

## 3. 取消收藏

### 接口

```http
DELETE /api/v1/favorites/{house_id}
```

### 是否需要认证

需要。

### 业务规则

- 只取消当前用户自己的收藏。
- 若当前用户未收藏该房源，返回 `2101 收藏不存在`。

### 成功响应（200）

```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

### 收藏不存在（404）

```json
{
  "code": 2101,
  "message": "收藏不存在",
  "data": null
}
```

------

# 六、Windows CMD 测试命令示例

## 1. 注册用户

```bash
curl -X POST http://127.0.0.1:8000/api/v1/users -H "Content-Type: application/json" -d "{\"username\":\"userA\",\"password\":\"123456\",\"email\":\"userA@example.com\"}"
```

## 2. 登录

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"username\":\"userA\",\"password\":\"123456\"}"
```

设置 token：

```bash
set TOKEN_A=这里粘贴登录返回的token
```

## 3. 创建房源

```bash
curl -X POST http://127.0.0.1:8000/api/v1/houses -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN_A%" -d "{\"title\":\"测试房源A\",\"address\":\"地址A\",\"region\":\"区域A\",\"house_type\":\"1室1厅\",\"area\":50,\"rent\":2000,\"deposit\":2000,\"description\":\"test\"}"
```

## 4. 我的房源

```bash
curl "http://127.0.0.1:8000/api/v1/houses?mine=true" -H "Authorization: Bearer %TOKEN_A%"
```

## 5. 发布房源

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/houses/1/publish -H "Authorization: Bearer %TOKEN_A%"
```

## 6. 下架房源

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/houses/1/offline -H "Authorization: Bearer %TOKEN_A%"
```

## 7. 删除房源

```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/houses/1 -H "Authorization: Bearer %TOKEN_A%"
```

------

# 七、说明

- User/Auth/House/Favorite 四个模块当前均使用统一响应结构。
- House 模块第一版不实现图片/视频、审核流、预约、合同、支付等功能。
- House 模块第一版仅做最小所有权校验，不做完整 RBAC 权限系统。
- House 列表筛选当前仅增强现有 `GET /api/v1/houses` 和 `GET /api/v1/houses?mine=true`，未新增独立 Search 模块。
- Pydantic 参数校验异常当前统一转换为 JSON `3001 bad request`，不再返回 Flask 默认 HTML 500。
- Favorite 第一版不做“是否已收藏”字段回填到 House 接口。
- 当前项目不再使用 `Base.metadata.create_all()` 自动建表。
- 数据库结构统一通过 Alembic migration 管理。


------

# 九、Appointment 模块补充

> 本节为 v1.4 新增内容。保留前文所有 User / Auth / House / Favorite 文档。

## 1. 业务规则总览

所有 Appointment 接口都必须登录。

Appointment 第一版状态：

| status    | 含义       |
| --------- | ---------- |
| pending   | 待房东确认 |
| confirmed | 房东已确认 |
| rejected  | 房东已拒绝 |
| cancelled | 租客已取消 |
| expired   | 已过期     |

`status` 是数据库真实状态。`display_status` 是前端展示状态。

第一版约定：

- 数据库正常业务流转只主动写入 `pending / confirmed / rejected / cancelled`。
- `expired` 不通过定时任务写回数据库。
- 如果 `status = pending` 且 `appointment_time` 已经过期，则返回 `display_status = expired`。
- 其他情况 `display_status = status`。

`relation_role` 表示当前用户在预约中的身份：

| relation_role | 含义           |
| ------------- | -------------- |
| tenant        | 当前用户是租客 |
| landlord      | 当前用户是房东 |

## 2. 创建预约

### 接口

```http
POST /api/v1/appointments
```

### 请求体

```json
{
  "house_id": 1,
  "appointment_time": "2026-04-25T15:00:00",
  "remark": "想下午看房"
}
```

### 规则

- 必须登录。
- `tenant_id` 从 token 获取。
- `landlord_id` 从 House 表读取，前端不能传。
- 只能预约未删除且 `listed` 的房源。
- 不能预约自己的房源。
- `appointment_time` 必须是未来时间。
- 创建后 `status = pending`。
- 房源不存在、已删除、非 `listed`，统一返回 `2001`。

### 成功响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "house_id": 1,
    "tenant_id": 2,
    "landlord_id": 1,
    "appointment_time": "2026-04-25T15:00:00",
    "remark": "想下午看房",
    "status": "pending",
    "display_status": "pending",
    "created_at": "2026-04-26T10:00:00",
    "updated_at": "2026-04-26T10:00:00",
    "relation_role": "tenant",
    "house": {
      "id": 1,
      "title": "测试房源",
      "region": "区域A",
      "address": "地址A",
      "house_type": "1室1厅",
      "area": "50.00",
      "rent": "2000.00",
      "deposit": "2000.00",
      "status": "listed"
    }
  }
}
```

## 3. 查看预约列表

### 接口

```http
GET /api/v1/appointments?page=1&page_size=10
```

### 规则

- 必须登录。
- 返回与当前用户相关的预约：`tenant_id == current_user_id OR landlord_id == current_user_id`。
- 支持分页。
- 默认按 `created_at DESC, id DESC`。
- 返回 `list / total / page / page_size`。

## 4. 房东确认预约

### 接口

```http
PATCH /api/v1/appointments/{id}/confirm
```

规则：

- 只有房东本人可以确认。
- 仅允许有效 `pending -> confirmed`。
- 已过期 pending 不能确认，返回 `2202`。
- 非房东或预约不存在，返回 `2201`。

## 5. 房东拒绝预约

### 接口

```http
PATCH /api/v1/appointments/{id}/reject
```

规则：

- 只有房东本人可以拒绝。
- 仅允许有效 `pending -> rejected`。
- 已过期 pending 不能拒绝，返回 `2202`。
- 非房东或预约不存在，返回 `2201`。

## 6. 租客取消预约

### 接口

```http
PATCH /api/v1/appointments/{id}/cancel
```

规则：

- 只有租客本人可以取消。
- 允许 `pending -> cancelled`、`confirmed -> cancelled`。
- `rejected / cancelled / expired` 不允许取消，返回 `2202`。
- 非租客或预约不存在，返回 `2201`。

## 7. Appointment 错误码

| code | 含义                   |
| ---- | ---------------------- |
| 2201 | 预约不存在             |
| 2202 | 非法预约状态           |
| 2203 | 不能预约自己的房源     |
| 2204 | 预约时间必须是未来时间 |

------

# 十、Conversation / Message 模块补充

> 本节为 v1.5 新增内容。保留前文所有 User / Auth / House / Favorite / Appointment 文档。

## 1. 业务规则总览

所有 Conversation / Message 接口都必须登录。

第一版明确不做：

- WebSocket
- Redis
- 实时推送
- 在线状态

会话创建规则：

- 只能针对未删除且 `listed` 的房源创建会话。
- 当前用户不能联系自己的房源。
- `tenant_id` 从 token 获取。
- `landlord_id` 从 House 表读取。
- 同一租客围绕同一房源联系同一房东，只能有一个会话。
- 如果会话已存在，直接返回已有会话。

消息规则：

- `content` 去掉首尾空白后不能为空。
- 保存到数据库的是 `content.strip()` 的结果。
- 发送消息成功后，会同步刷新 `Conversation.updated_at`。
- `PATCH /read` 只标记 `sender_id != current_user_id AND read_at IS NULL` 的消息。

## 2. 创建会话

### 接口

```http
POST /api/v1/conversations
```

### 请求体

```json
{
  "house_id": 1
}
```

### 规则

- 必须登录。
- 只能针对未删除且 `listed` 的房源创建会话。
- 当前用户不能联系自己的房源。
- 若会话不存在，则创建新会话并返回 `201`。
- 若会话已存在，则直接返回已有会话并返回 `200`。

### 成功响应（201 / 200）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "house_id": 1,
    "tenant_id": 2,
    "landlord_id": 1,
    "created_at": "2026-04-26T18:00:00",
    "updated_at": "2026-04-26T18:00:00",
    "house": {
      "id": 1,
      "title": "测试房源",
      "region": "区域A",
      "address": "地址A",
      "house_type": "1室1厅",
      "area": "50.00",
      "rent": "2000.00",
      "deposit": "2000.00",
      "status": "listed"
    },
    "last_message": null,
    "last_message_at": null,
    "unread_count": 0
  }
}
```

## 3. 查看会话列表

### 接口

```http
GET /api/v1/conversations?page=1&page_size=10
```

### 规则

- 必须登录。
- 只返回当前用户参与的会话。
- 条件：`tenant_id = current_user_id OR landlord_id = current_user_id`。
- 支持分页。
- 默认按 `updated_at DESC, id DESC`。
- 列表项包含 `house` 摘要、`last_message`、`last_message_at`、`unread_count`。

## 4. 查看消息列表

### 接口

```http
GET /api/v1/conversations/{id}/messages?page=1&page_size=10
```

### 规则

- 必须登录。
- 只有会话参与者可以查看。
- 支持分页。
- 默认按 `created_at ASC, id ASC`。

## 5. 发送消息

### 接口

```http
POST /api/v1/conversations/{id}/messages
```

### 请求体

```json
{
  "content": "你好，这个房子还在吗？"
}
```

### 规则

- 必须登录。
- 只有会话参与者可以发送。
- `sender_id` 从 token 获取。
- `content.strip()` 后不能为空。
- 保存到数据库的是去首尾空白后的内容。
- 成功后刷新所属会话的 `updated_at`。

### 成功响应（201）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "conversation_id": 1,
    "sender_id": 2,
    "content": "你好，这个房子还在吗？",
    "created_at": "2026-04-26T18:05:00",
    "read_at": null
  }
}
```

## 6. 标记已读

### 接口

```http
PATCH /api/v1/conversations/{id}/read
```

### 规则

- 必须登录。
- 只有会话参与者可以操作。
- 将当前会话中 `sender_id != current_user_id AND read_at IS NULL` 的消息设置 `read_at = now`。

### 成功响应（200）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "updated": 3
  }
}
```

## 7. Conversation 错误码

| code | 含义               |
| ---- | ------------------ |
| 2301 | 会话不存在         |
| 2302 | 不能联系自己的房源 |

------

# 十一、Contract 模块补充

> 本节为 v1.6 新增内容。保留前文所有 User / Auth / House / Favorite / Appointment / Conversation 文档。

## 1. 业务规则总览

所有 Contract 接口都必须登录。

第一版明确不做：

- PDF
- 电子签章
- 真实支付
- 真实法律合同

Contract 第一版必须基于 `confirmed appointment` 创建。

创建规则：

- 创建接口仅房东可调用。
- 前端不允许传 `house_id / tenant_id / landlord_id`。
- 后端根据 `appointment_id` 自动确定 `house_id / tenant_id / landlord_id`。
- appointment 不存在或不属于当前房东，返回 `2201`。
- appointment 状态不是 `confirmed`，返回 `2402`。
- appointment 对应 house 不存在或已删除，返回 `2001`。
- 同一 `appointment_id` 同时只能有一个 `pending` 合同。
- 同一 `house_id` 同时只能有一个 `active` 合同。
- `active` 后第一版不修改 `House.status`。

Contract 第一版状态：

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

## 2. 创建合同

### 接口

```http
POST /api/v1/contracts
```

### 请求体

```json
{
  "appointment_id": 1,
  "start_date": "2026-05-01",
  "end_date": "2027-05-01",
  "monthly_rent": 2000,
  "deposit": 2000,
  "remark": "一年期合同"
}
```

### 规则

- 必须登录。
- 仅房东可调用。
- appointment 必须存在且属于当前房东。
- appointment 状态必须是 `confirmed`。
- 创建成功后 `status = pending`。
- 同一 `appointment_id` 若已有 `pending` 合同，返回 `4009`。
- 同一 `house_id` 若已有 `active` 合同，返回 `2405`。

### 成功响应（201）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "house_id": 1,
    "tenant_id": 2,
    "landlord_id": 1,
    "appointment_id": 3,
    "start_date": "2026-05-01",
    "end_date": "2027-05-01",
    "monthly_rent": "2000.00",
    "deposit": "2000.00",
    "status": "pending",
    "remark": "一年期合同",
    "created_at": "2026-04-26T21:00:00",
    "updated_at": "2026-04-26T21:00:00",
    "house": {
      "id": 1,
      "title": "测试房源",
      "region": "区域A",
      "address": "地址A",
      "house_type": "1室1厅",
      "area": "50.00",
      "rent": "2000.00",
      "deposit": "2000.00",
      "status": "listed"
    }
  }
}
```

## 3. 查看合同列表

### 接口

```http
GET /api/v1/contracts?page=1&page_size=10
```

### 规则

- 必须登录。
- 返回当前用户参与的合同：`tenant_id == current_user_id OR landlord_id == current_user_id`。
- 支持分页。
- 默认按 `created_at DESC, id DESC`。

## 4. 查看合同详情

### 接口

```http
GET /api/v1/contracts/{id}
```

### 规则

- 必须登录。
- 只有合同参与者可以查看。
- 非参与者统一返回 `2401`。

## 5. 租客确认合同

### 接口

```http
PATCH /api/v1/contracts/{id}/confirm
```

### 规则

- 必须登录。
- 仅合同 tenant 可调用。
- 仅允许 `pending -> active`。
- 执行前再次检查同一 `house_id` 没有其他 `active` 合同。
- 成功后第一版不修改 `House.status`。

## 6. 租客拒绝合同

### 接口

```http
PATCH /api/v1/contracts/{id}/reject
```

### 规则

- 必须登录。
- 仅合同 tenant 可调用。
- 仅允许 `pending -> rejected`。

## 7. 房东取消合同

### 接口

```http
PATCH /api/v1/contracts/{id}/cancel
```

### 规则

- 必须登录。
- 仅合同 landlord 可调用。
- 仅允许 `pending -> cancelled`。

## 8. 房东终止合同

### 接口

```http
PATCH /api/v1/contracts/{id}/terminate
```

### 规则

- 必须登录。
- 仅合同 landlord 可调用。
- 仅允许 `active -> terminated`。

## 9. Contract 错误码

| code | 含义                   |
| ---- | ---------------------- |
| 2401 | 合同不存在             |
| 2402 | 非法合同状态           |
| 2403 | 不能和自己的房源签合同 |
| 2404 | 合同时间不合法         |
| 2405 | 房源已有生效合同       |

------

# 十二、common 公共能力补充

当前项目已完成 common 公共能力替换重构。

## 1. base_model.py

文件：

```text
app/common/base_model.py
```

提供：

- `BaseModel`
- `SoftDeleteMixin`

当前继承关系：

| Model       | 继承关系                            |
| ----------- | ----------------------------------- |
| User        | `User(BaseModel)`                   |
| House       | `House(BaseModel, SoftDeleteMixin)` |
| Favorite    | `Favorite(BaseModel)`               |
| Appointment | `Appointment(BaseModel)`            |
| Conversation| `Conversation(BaseModel)`           |
| Message     | `Message(BaseModel)`                |
| Contract    | `Contract(BaseModel)`               |

说明：

- `BaseModel` 提供 `id / created_at / updated_at`。
- `SoftDeleteMixin` 提供 `deleted_at`。
- `deleted_at` 只用于 House。
- Favorite / Appointment / Conversation / Message / Contract 有 `updated_at`。
- Favorite / Appointment / Conversation / Message / Contract 没有 `deleted_at`。

## 2. pagination.py

文件：

```text
app/common/pagination.py
```

提供：

- `get_offset(page, page_size)`
- `build_page_result(items, total, page, page_size)`

统一分页响应：

```json
{
  "list": [],
  "total": 0,
  "page": 1,
  "page_size": 10
}
```

## 3. enums.py

文件：

```text
app/common/enums.py
```

提供：

- `HouseStatus`
- `AppointmentStatus`

说明：

- 数据库存储仍是字符串。
- 接口返回仍是字符串。
- 不改变状态流转规则。

## 4. base_schema.py

文件：

```text
app/common/base_schema.py
```

提供：

- `BaseSchema`

默认配置：

```text
from_attributes=True
extra="forbid"
```

说明：

- 不改变现有接口请求校验语义。
- 对原本不强制 forbid 的 schema 保留旧行为。
# 十三、Bill 模块补充

> 本节为 v1.7 新增内容。保留前文所有 User / Auth / House / Favorite / Appointment / Conversation / Contract 文档。

## 1. 业务规则总览

所有 Bill 接口都必须登录。

第一版明确不做：

- Payment
- `payment` 表
- `mark-paid` 接口
- 真实支付

Bill 必须基于 `active contract` 创建。

创建规则：

- `POST /api/v1/bills` 仅房东可调用
- 请求体只允许：
  - `contract_id`
  - `bill_type`
  - `amount`
  - `due_date`
  - `remark`
- 不允许前端传：
  - `house_id`
  - `tenant_id`
  - `landlord_id`
- 后端从 contract 自动写入：
  - `house_id`
  - `tenant_id`
  - `landlord_id`
- `bill_type` 第一版只允许：
  - `rent`
  - `deposit`
  - `other`
- `amount` 必须大于 `0`
- `due_date` 必须是合法 `Date`，格式错误返回 `3001`
- 合同不存在或不属于当前房东，返回 `2401`
- 合同不是 `active`，返回 `2503`

Bill 第一版状态：

| status    | 含义 |
| --------- | ---- |
| unpaid    | 待支付 |
| paid      | 预留，第一版无公开接口 |
| cancelled | 已取消 |
| overdue   | 已逾期 |

允许的公开状态流转：

- `create -> unpaid`
- `unpaid -> cancelled`
- `unpaid -> overdue`
- `overdue -> cancelled`

## 2. 创建账单

### 接口

```http
POST /api/v1/bills
```

### 请求体

```json
{
  "contract_id": 1,
  "bill_type": "rent",
  "amount": 2500,
  "due_date": "2026-05-10",
  "remark": "May rent"
}
```

### 成功响应（201）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "contract_id": 1,
    "house_id": 1,
    "tenant_id": 2,
    "landlord_id": 1,
    "bill_type": "rent",
    "amount": "2500.00",
    "due_date": "2026-05-10",
    "status": "unpaid",
    "remark": "May rent",
    "created_at": "2026-04-28T10:00:00",
    "updated_at": "2026-04-28T10:00:00"
  }
}
```

## 3. 查看账单列表

### 接口

```http
GET /api/v1/bills?page=1&page_size=10
```

### 规则

- 仅返回当前用户参与的账单
- 条件：`tenant_id == current_user_id OR landlord_id == current_user_id`
- 支持分页
- 默认按 `created_at DESC, id DESC`

## 4. 查看账单详情

### 接口

```http
GET /api/v1/bills/{id}
```

### 规则

- 房东和租客都可查看自己参与的账单
- 非参与者统一返回 `2501`

## 5. 取消账单

### 接口

```http
PATCH /api/v1/bills/{id}/cancel
```

### 规则

- 仅账单所属房东可调用
- 仅允许：
  - `unpaid -> cancelled`
  - `overdue -> cancelled`
- 非参与者统一返回 `2501`
- 非法账单状态流转返回 `2502`

## 6. 标记账单逾期

### 接口

```http
PATCH /api/v1/bills/{id}/mark-overdue
```

### 规则

- 仅账单所属房东可调用
- 只允许 `unpaid -> overdue`
- 必须当前日期已经超过 `due_date`
- 非参与者统一返回 `2501`
- 状态不合法或 `due_date` 未过期时统一返回 `2502`

## 7. Bill 错误码

| code | 含义 |
| ---- | ---- |
| 2501 | 账单不存在 |
| 2502 | 非法账单状态 |
| 2503 | 合同未生效，不能创建账单 |
| 2504 | 账单金额不合法 |

继续复用：

- `1003` 未登录
- `2401` 合同不存在
- `3001` 参数错误
- `4009` 资源冲突
- `5000` 系统错误
# 十四、Payment 模块补充

> 本节为 v1.8 新增内容。Payment 第一版只做模拟支付和支付记录，不接第三方支付，不做回调，不做退款，不做部分支付。

## 1. 业务规则总览

所有 Payment 接口都必须登录。

Payment 第一版只提供：

- `POST /api/v1/payments`
- `GET /api/v1/payments`
- `GET /api/v1/payments/{id}`

核心规则：

- 只有租客可以支付自己的 bill
- 房东不能支付
- 只有 `unpaid / overdue` bill 允许支付
- `cancelled / paid` bill 不允许支付
- 成功支付时，后端在同一事务中：
  1. 先插入 Payment
  2. 再更新 `Bill.status = paid`
- 重复支付同一 bill 返回 `2604`
- 非参与者访问 payment 返回 `2601`

## 2. Payment 表结构

```text
payments
```

字段：

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

说明：

- `bill_id` 必填
- `contract_id / house_id / tenant_id / landlord_id` 不允许前端传，由后端从 bill 自动写入
- `amount` 必须等于 `bill.amount`
- `payment_method` 只允许：
  - `mock`
  - `offline`
- `status` 第一版只写入 `success`
- `paid_at` 返回统一 ISO 8601 格式

## 3. 创建支付记录

### 接口

```http
POST /api/v1/payments
```

### 请求体

只允许：

- `bill_id`
- `amount`
- `payment_method`
- `remark`

示例：

```json
{
  "bill_id": 1,
  "amount": 2600,
  "payment_method": "mock",
  "remark": "tenant mock payment"
}
```

### 成功响应（201）

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "bill_id": 1,
    "contract_id": 1,
    "house_id": 1,
    "tenant_id": 2,
    "landlord_id": 1,
    "amount": "2600.00",
    "payment_method": "mock",
    "status": "success",
    "paid_at": "2026-04-28T19:00:00",
    "remark": "tenant mock payment",
    "created_at": "2026-04-28T19:00:00",
    "updated_at": "2026-04-28T19:00:00"
  }
}
```

### 规则

- 仅租客本人可调用
- bill 不存在或当前用户无权支付该 bill，返回 `2501`
- `amount` 必须严格等于 `bill.amount`，否则返回 `2603`
- 允许支付：
  - `unpaid`
  - `overdue`
- 以下状态不允许支付，返回 `2602`
  - `cancelled`
- bill 已支付或重复支付返回 `2604`

## 4. 支付记录列表

### 接口

```http
GET /api/v1/payments?page=1&page_size=10
```

### 规则

- 只有 bill 参与者可查看
- 支持分页
- 默认：
  - `page = 1`
  - `page_size = 10`
- 返回：
  - `list / total / page / page_size`

### 成功响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "bill_id": 1,
        "contract_id": 1,
        "house_id": 1,
        "tenant_id": 2,
        "landlord_id": 1,
        "amount": "2600.00",
        "payment_method": "mock",
        "status": "success",
        "paid_at": "2026-04-28T19:00:00",
        "remark": "tenant mock payment",
        "created_at": "2026-04-28T19:00:00",
        "updated_at": "2026-04-28T19:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10
  }
}
```

## 5. 支付记录详情

### 接口

```http
GET /api/v1/payments/{id}
```

### 规则

- 只有 bill 参与者可以查看
- 非参与者统一返回 `2601`

## 6. Payment 错误码

| code | 含义 |
| ---- | ---- |
| 2601 | 支付记录不存在 |
| 2602 | 账单状态不允许支付 |
| 2603 | 支付金额不匹配 |
| 2604 | 账单已支付 |

继续复用：

- `1003` 未登录
- `2501` 账单不存在
- `3001` 参数错误
- `4009` 资源冲突
- `5000` 系统错误

------

# 十五、Repair 模块补充

> 本节为 v1.9 新增内容。Repair 第一版实现为 HTTP 报修模块，不做附件上传，不做物理删除，不新增 admin 专用路径。

## 1. 业务规则总览

所有 Repair 接口都必须登录。

Repair 必须基于当前租客自己的 `active contract` 创建。

请求体第一版只允许传：

- `contract_id`
- `description`

前端不允许传：

- `house_id`
- `tenant_id`
- `landlord_id`
- `status`
- 所有时间字段

后端从 contract 自动写入：

- `house_id`
- `tenant_id`
- `landlord_id`

## 2. Repair 表结构

```text
repairs
```

字段包括：

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

## 3. Repair 状态与流转

状态集合：

```text
pending / processing / completed / closed / rejected / cancelled / reopened
```

主流程：

- `create -> pending`
- `pending -> processing`
- `processing -> completed`
- `completed -> closed`

可选分支：

- `pending -> rejected`
- `completed -> reopened`
- `closed -> reopened`
- `reopened -> processing`
- `reopened -> rejected`

说明：

- `rejected / cancelled` 作为结束状态保留
- 第一版保留 `cancelled` 状态常量与表字段，但不提供公开 `cancel` 接口
- 第一版不提供 `DELETE /repairs/{id}`

## 4. 角色与权限规则

tenant：

- `create`
- `close`
- `reopen`

landlord：

- `process`
- `complete`
- `reject`

admin：

- 可查看全部 repair
- 可执行所有合法状态流

访问规则：

- tenant 只看自己的 repair
- landlord 只看自己房源/合同相关的 repair
- admin 可看全部
- 非参与者访问或操作统一返回 `2701`

## 5. Repair 接口

```text
POST  /api/v1/repairs
GET   /api/v1/repairs
GET   /api/v1/repairs/{id}
PATCH /api/v1/repairs/{id}/process
PATCH /api/v1/repairs/{id}/complete
PATCH /api/v1/repairs/{id}/reject
PATCH /api/v1/repairs/{id}/close
PATCH /api/v1/repairs/{id}/reopen
```

### 5.1 创建报修

```http
POST /api/v1/repairs
```

请求体示例：

```json
{
  "contract_id": 1,
  "description": "kitchen sink is leaking"
}
```

规则：

- 必须登录
- 仅 tenant 可创建
- `contract_id` 必须属于当前 tenant
- `contract.status` 必须是 `active`
- 创建成功后 `status = pending`

### 5.2 报修列表

```http
GET /api/v1/repairs?page=1&page_size=10
GET /api/v1/repairs?page=1&page_size=10&status=pending
```

规则：

- 必须登录
- 支持分页
- 支持按 `status` 筛选
- tenant 只看自己的
- landlord 只看关联房源的
- admin 可看全部

### 5.3 报修详情

```http
GET /api/v1/repairs/{id}
```

规则：

- 必须登录
- 非参与者统一返回 `2701`

### 5.4 process / complete / reject / close / reopen

```http
PATCH /api/v1/repairs/{id}/process
PATCH /api/v1/repairs/{id}/complete
PATCH /api/v1/repairs/{id}/reject
PATCH /api/v1/repairs/{id}/close
PATCH /api/v1/repairs/{id}/reopen
```

规则：

- `process`：landlord/admin，`pending/reopened -> processing`
- `complete`：landlord/admin，`processing -> completed`
- `reject`：landlord/admin，`pending/reopened -> rejected`
- `close`：tenant/admin，`completed -> closed`
- `reopen`：tenant/admin，`completed/closed -> reopened`

非法状态操作统一返回 `2702`。

## 6. Repair 错误码

| code | 含义 |
| ---- | ---- |
| 2701 | 报修不存在或当前用户无权访问 |
| 2702 | 非法报修状态操作 |
| 2703 | contract 不是 active，不允许创建报修 |

继续复用：

- `1003` 未登录
- `1004` role 不允许执行该动作
- `2401` 合同不存在或不属于当前用户
- `3001` 参数错误
- `5000` 系统错误

# 十七、Notification 模块补充

> 本节为 v1.11 新增内容。Notification 第一版实现为站内通知模块，不做物理删除，不做广播通知，只提供单用户通知收件箱能力。

## 1. 基本规则

所有 Notification 接口都必须登录。

通知只允许当前用户查看和操作自己的记录。

`POST /api/v1/notifications` 仅保留给：

- admin 手动创建
- 系统测试

第一版推荐 `source_type`：

- `repair`
- `complaint`
- `contract`
- `bill`

## 2. Notification 表结构

```text
notifications
-
id
user_id
source_type
source_id
title
message
status
created_at
updated_at
```

说明：

- `status` 默认 `unread`
- `created_at / updated_at` 按 UTC 处理
- 索引包含：
  - `user_id`
  - `status`
  - `created_at`

## 3. Notification 状态与流转

状态集合：

- `unread`
- `read`

主流程：

- `create -> unread`
- `unread -> read`

说明：

- `read` 视为终态
- 第一版不提供 `DELETE /notifications/{id}`
- 标记已读时会更新 `updated_at`

## 4. 角色与权限规则

tenant：

- 可查看自己的通知
- 可将自己的通知标记为已读

landlord：

- 可查看自己的通知
- 可将自己的通知标记为已读

admin：

- 可查看自己的通知
- 可将自己的通知标记为已读
- 可通过 `POST /api/v1/notifications` 手动创建通知

访问规则：

- 所有角色都只能看自己的 notification
- 非拥有者访问或操作统一返回 `2901`

## 5. Notification 接口

```text
POST  /api/v1/notifications
GET   /api/v1/notifications
GET   /api/v1/notifications/{id}
PATCH /api/v1/notifications/{id}/read
```

### 5.1 手动创建通知

```http
POST /api/v1/notifications
```

请求体示例：

```json
{
  "user_id": 1,
  "source_type": "repair",
  "source_id": 12,
  "title": "Repair update",
  "message": "Your repair has a new update."
}
```

规则：

- 必须登录
- 仅 admin 可创建
- `user_id` 必须存在
- 创建成功后 `status = unread`

### 5.2 通知列表

```http
GET /api/v1/notifications?page=1&page_size=10
GET /api/v1/notifications?page=1&page_size=10&status=unread
GET /api/v1/notifications?page=1&page_size=10&status=read
```

规则：

- 必须登录
- 仅返回当前用户自己的通知
- 支持分页
- 支持按 `status` 筛选

### 5.3 通知详情

```http
GET /api/v1/notifications/{id}
```

规则：

- 必须登录
- 非拥有者统一返回 `2901`

### 5.4 标记已读

```http
PATCH /api/v1/notifications/{id}/read
```

规则：

- 仅允许 `unread -> read`
- 已经是 `read` 时返回 `2902`
- 成功后会刷新 `updated_at`

## 6. 自动通知触发

以下模块在状态变更后自动创建通知：

- `Repair`
- `Complaint`
- `Contract`
- `Bill`
- `Payment` 中触发的 `bill paid` 场景

接收规则：

- tenant 只接收自己的相关通知
- landlord 只接收自己的相关通知
- admin 只接收自己的相关通知
- 第一版不做广播通知

## 7. Notification 错误码

| code | 含义 |
| ---- | ---- |
| 2901 | 通知不存在或当前用户无权访问 |
| 2902 | 非法通知状态操作 |

继续复用：

- `1001` 用户不存在
- `1003` 未登录
- `1004` role 不允许执行该动作
- `3001` 参数错误
- `5000` 系统错误

# 十八、Statistics 模块补充

> 本节为 v1.12 新增内容。Statistics 第一版实现为只读后台统计模块，不新增表，不做时间范围筛选、导出或多维分析。

## 1. 基本规则

所有 Statistics 接口都必须登录。

所有 Statistics 接口仅允许 admin 调用：

- tenant 调用返回 `1004`
- landlord 调用返回 `1004`

本模块不新增独立统计表，直接聚合现有业务表：

- `houses`
- `contracts`
- `payments`
- `users`
- `repairs`
- `complaints`

## 2. Statistics 接口

```text
GET /api/v1/statistics/house-utilization
GET /api/v1/statistics/rent-income
GET /api/v1/statistics/active-users
GET /api/v1/statistics/complaint-repair-count
```

## 3. House Utilization

```http
GET /api/v1/statistics/house-utilization
```

返回字段：

- `total_houses`
- `occupied_houses`
- `utilization_rate`

统计口径：

- `total_houses`：未逻辑删除的房源总数
- `occupied_houses`：存在 `active contract` 的去重房源数
- `utilization_rate`：`occupied_houses / total_houses`

无数据时：

- `total_houses = 0`
- `occupied_houses = 0`
- `utilization_rate = 0.0`

## 4. Rent Income

```http
GET /api/v1/statistics/rent-income
```

返回字段：

- `total_income`
- `monthly_income`

`monthly_income` 结构：

```json
[
  {
    "month": "2026-05",
    "amount": 2600.0
  }
]
```

统计口径：

- 总收入：累计已支付租金金额
- 月度收入：按支付时间聚合月度金额
- 时间维度以 `Payment.paid_at` 为准
- 第一版仅统计 `bill_type = rent`

无数据时：

- `total_income = 0.0`
- `monthly_income = []`

## 5. Active Users

```http
GET /api/v1/statistics/active-users
```

返回字段：

- `active_user_count`

统计口径：

- `users.status = active` 的用户数量
- 第一版不引入最近登录、行为活跃等复杂定义

无数据时返回 `0`。

## 6. Complaint Repair Count

```http
GET /api/v1/statistics/complaint-repair-count
```

返回字段：

- `repair_count`
- `complaint_count`

统计口径：

- `repair_count`：`repairs` 表总数
- `complaint_count`：`complaints` 表总数

第一版不按状态拆分，不按时间窗口过滤。

## 7. Statistics 错误码

本模块不新增专属错误码，继续复用：

- `1003` 未登录
- `1004` role 不允许执行该动作
- `3001` 参数错误
- `5000` 系统错误

# 二十一、Admin 模块补充

> 本节为 v1.13 新增内容。Admin 第一版实现为后台统一管理入口，路由前缀为 `/api/v1/admin`，所有接口仅允许 admin 调用。

## 1. 基本规则

所有 Admin 接口都必须登录。

所有 Admin 接口仅允许 admin 调用：

- tenant 调用返回 `1004`
- landlord 调用返回 `1004`

Admin 第一版当前覆盖：

- 用户管理
- 房源只读管理
- 投诉管理
- 报修管理
- 合同管理

说明：

- 第一版不新增 admin 专用统计镜像路由
- 第一版不提供 Admin 删除用户接口
- House 在第一版不走 admin 审核流，房东仍可直接上架
- House 在第一版后台只提供列表和详情，不提供状态修改

## 2. Admin 路由列表

```text
GET   /api/v1/admin/users
GET   /api/v1/admin/users/{id}
POST  /api/v1/admin/users
PUT   /api/v1/admin/users/{id}
PATCH /api/v1/admin/users/{id}/status

GET   /api/v1/admin/houses
GET   /api/v1/admin/houses/{id}

GET   /api/v1/admin/complaints
GET   /api/v1/admin/complaints/{id}
PATCH /api/v1/admin/complaints/{id}/process
PATCH /api/v1/admin/complaints/{id}/resolve
PATCH /api/v1/admin/complaints/{id}/reject
PATCH /api/v1/admin/complaints/{id}/close

GET   /api/v1/admin/repairs
GET   /api/v1/admin/repairs/{id}
PATCH /api/v1/admin/repairs/{id}/process
PATCH /api/v1/admin/repairs/{id}/complete
PATCH /api/v1/admin/repairs/{id}/reject
PATCH /api/v1/admin/repairs/{id}/close

GET   /api/v1/admin/contracts
GET   /api/v1/admin/contracts/{id}
PATCH /api/v1/admin/contracts/{id}/status
```

## 3. 用户管理

### 3.1 用户列表

```http
GET /api/v1/admin/users?page=1&page_size=10
```

规则：

- 仅 admin 可访问
- 支持分页
- 返回 `list / total / page / page_size`

### 3.2 用户详情

```http
GET /api/v1/admin/users/{id}
```

规则：

- 仅 admin 可访问
- 用户不存在返回 `1001`

### 3.3 创建用户

```http
POST /api/v1/admin/users
```

请求体示例：

```json
{
  "username": "managed_user",
  "password": "Password123!",
  "role": "tenant",
  "email": "managed_user@example.com",
  "status": "active"
}
```

规则：

- 仅 admin 可创建
- `status` 仅允许：
  - `active`
  - `disabled`
- 用户名冲突返回 `4009`

### 3.4 更新用户

```http
PUT /api/v1/admin/users/{id}
```

规则：

- 仅 admin 可更新
- 支持更新：
  - `username`
  - `password`
  - `role`
  - `real_name`
  - `phone`
  - `email`
  - `avatar`
- 不存在返回 `1001`
- 用户名冲突返回 `4009`

### 3.5 启用 / 禁用用户

```http
PATCH /api/v1/admin/users/{id}/status
```

请求体示例：

```json
{
  "status": "disabled"
}
```

规则：

- 第一版“删除”仅表现为启用 / 禁用
- 不做物理删除

## 4. 房源后台只读管理

### 4.1 房源列表

```http
GET /api/v1/admin/houses?page=1&page_size=10
```

规则：

- 仅 admin 可访问
- 支持分页
- 支持与 House 列表一致的筛选参数：
  - `region`
  - `house_type`
  - `min_rent`
  - `max_rent`
  - `keyword`
  - `min_area`
  - `max_area`
- 第一版只看未逻辑删除房源

### 4.2 房源详情

```http
GET /api/v1/admin/houses/{id}
```

规则：

- 仅 admin 可访问
- 房源不存在返回 `2001`
- 第一版不提供后台 `publish / offline / status` 修改接口

## 5. 投诉后台管理

```http
GET   /api/v1/admin/complaints
GET   /api/v1/admin/complaints/{id}
PATCH /api/v1/admin/complaints/{id}/process
PATCH /api/v1/admin/complaints/{id}/resolve
PATCH /api/v1/admin/complaints/{id}/reject
PATCH /api/v1/admin/complaints/{id}/close
```

规则：

- admin 可查看全部 complaint
- admin 复用 complaint 现有状态流规则：
  - `pending -> processing`
  - `processing -> resolved`
  - `pending -> rejected`
  - `resolved -> closed`
- 非法状态操作返回 `2802`
- 不存在返回 `2801`

## 6. 报修后台管理

```http
GET   /api/v1/admin/repairs
GET   /api/v1/admin/repairs/{id}
PATCH /api/v1/admin/repairs/{id}/process
PATCH /api/v1/admin/repairs/{id}/complete
PATCH /api/v1/admin/repairs/{id}/reject
PATCH /api/v1/admin/repairs/{id}/close
```

规则：

- admin 可查看全部 repair
- admin 复用 repair 现有状态流规则：
  - `pending/reopened -> processing`
  - `processing -> completed`
  - `pending/reopened -> rejected`
  - `completed -> closed`
- 非法状态操作返回 `2702`
- 不存在返回 `2701`

## 7. 合同后台管理

### 7.1 合同列表 / 详情

```http
GET /api/v1/admin/contracts?page=1&page_size=10
GET /api/v1/admin/contracts/{id}
```

规则：

- admin 可查看全部 contract
- 不存在返回 `2401`

### 7.2 修改合同状态

```http
PATCH /api/v1/admin/contracts/{id}/status
```

请求体示例：

```json
{
  "status": "terminated"
}
```

第一版允许输入：

- `active`
- `terminated`
- `cancelled`

允许流转：

- `pending -> active`
- `pending -> cancelled`
- `active -> terminated`

不开放：

- admin 直接改成 `rejected`
- 任意未定义状态跳转

非法状态操作返回 `2402`。

## 8. Admin 模块错误码

Admin 第一版不新增专属错误码，继续复用：

- `1001` 用户不存在
- `1003` 未登录
- `1004` role 不允许执行该动作
- `2001` 房源不存在
- `2401` 合同不存在
- `2402` 非法合同状态
- `2701` 报修不存在或无权访问
- `2702` 非法报修状态操作
- `2801` 投诉不存在或无权访问
- `2802` 非法投诉状态操作
- `3001` 参数错误
- `4009` 资源冲突
- `5000` 系统错误

# 十六、Complaint 模块补充

> 本节为 v1.10 新增内容。Complaint 第一版实现为 HTTP 投诉模块，不做附件上传，不做物理删除，不新增 admin 专用路径。

## 1. 基本规则

所有 Complaint 接口都必须登录。

Complaint 必须基于当前租客自己的 `active contract` 创建。

创建时前端只允许提交：

- `contract_id`
- `description`

以下字段由后端根据 contract 自动写入：

- `house_id`
- `tenant_id`
- `landlord_id`

## 2. Complaint 表结构

```text
complaints
-
id
contract_id
house_id
tenant_id
landlord_id
description
status
processed_at
resolved_at
closed_at
rejected_at
cancelled_at
created_at
updated_at
```

说明：

- `status` 默认 `pending`
- `cancelled_at` 仅为未来扩展预留字段
- 第一版不引入 `cancelled` 状态
- 索引包含：
  - `contract_id`
  - `house_id`
  - `tenant_id`
  - `landlord_id`
  - `status`
  - `created_at`

## 3. Complaint 状态与流转

状态集合：

- `pending`
- `processing`
- `resolved`
- `closed`
- `rejected`

主流程：

- `create -> pending`
- `pending -> processing`
- `processing -> resolved`
- `resolved -> closed`

可选分支：

- `pending -> rejected`

说明：

- `closed / rejected` 作为公开流程终态
- 第一版不提供 `DELETE /complaints/{id}`

## 4. 角色与权限规则

tenant：

- `create`
- `close`

landlord：

- `process`
- `resolve`
- `reject`

admin：

- 可查看全部 complaint
- 可执行所有合法状态流

访问规则：

- tenant 只看自己的 complaint
- landlord 只看自己房源/合同相关的 complaint
- admin 可看全部
- 非参与者访问或操作统一返回 `2801`

## 5. Complaint 接口

```text
POST  /api/v1/complaints
GET   /api/v1/complaints
GET   /api/v1/complaints/{id}
PATCH /api/v1/complaints/{id}/process
PATCH /api/v1/complaints/{id}/resolve
PATCH /api/v1/complaints/{id}/reject
PATCH /api/v1/complaints/{id}/close
```

### 5.1 创建投诉

```http
POST /api/v1/complaints
```

请求体示例：

```json
{
  "contract_id": 1,
  "description": "repeated construction noise late at night"
}
```

规则：

- 必须登录
- 仅 tenant 可创建
- `contract_id` 必须属于当前 tenant
- `contract.status` 必须是 `active`
- 创建成功后 `status = pending`

### 5.2 投诉列表

```http
GET /api/v1/complaints?page=1&page_size=10
GET /api/v1/complaints?page=1&page_size=10&status=pending
```

规则：

- 必须登录
- 支持分页
- 支持按 `status` 筛选
- tenant 只看自己的
- landlord 只看关联房源的
- admin 可看全部

### 5.3 投诉详情

```http
GET /api/v1/complaints/{id}
```

规则：

- 必须登录
- 非参与者统一返回 `2801`

### 5.4 process / resolve / reject / close

```http
PATCH /api/v1/complaints/{id}/process
PATCH /api/v1/complaints/{id}/resolve
PATCH /api/v1/complaints/{id}/reject
PATCH /api/v1/complaints/{id}/close
```

规则：

- `process`：landlord/admin，`pending -> processing`
- `resolve`：landlord/admin，`processing -> resolved`
- `reject`：landlord/admin，`pending -> rejected`
- `close`：tenant/admin，`resolved -> closed`

非法状态操作统一返回 `2802`。

## 6. Complaint 错误码

| code | 含义 |
| ---- | ---- |
| 2801 | 投诉不存在或当前用户无权访问 |
| 2802 | 非法投诉状态操作 |
| 2803 | contract 不是 active，不允许创建投诉 |

继续复用：

- `1003` 未登录
- `1004` role 不允许执行该动作
- `2401` 合同不存在或不属于当前用户
- `3001` 参数错误
- `5000` 系统错误
# 二十二、News 模块补充

> 本节为 v1.14 新增内容。News 第一版实现为平台公告模块，路由前缀为 `/api/v1/news`，写接口仅允许 admin 调用。

## 1. 基本规则

- 状态仅包含：
  - `draft`
  - `published`
- admin 默认可查看全部公告
- tenant / landlord / 游客仅可查看 `published`
- 删除为物理删除
- 公告发布或更新已发布公告时，会触发站内通知

## 2. News 表结构

字段：

```text
id
title
content
author_id
status
created_at
updated_at
```

说明：

- `author_id -> users.id`
- `created_at` 建索引
- `status` 默认 `draft`

## 3. News 接口

```text
POST   /api/v1/news
GET    /api/v1/news
GET    /api/v1/news/{id}
PATCH  /api/v1/news/{id}
DELETE /api/v1/news/{id}
```

### 3.1 创建公告

```http
POST /api/v1/news
```

请求体示例：

```json
{
  "title": "System maintenance notice",
  "content": "The platform will be unavailable from 02:00 to 03:00.",
  "status": "published"
}
```

规则：

- 必须登录
- 仅 admin 可调用
- `title` 去除首尾空白后必须非空
- `content` 去除首尾空白后必须非空
- `status = published` 时创建后触发通知

### 3.2 公告列表

```http
GET /api/v1/news?page=1&page_size=10
GET /api/v1/news?page=1&page_size=10&status=draft
GET /api/v1/news?page=1&page_size=10&status=published
```

规则：

- 支持分页
- 支持按 `status` 筛选
- admin 默认可看 `draft + published`
- tenant / landlord / 游客仅返回 `published`
- 非 admin 即使传 `status=draft`，仍按 `published` 处理

### 3.3 公告详情

```http
GET /api/v1/news/{id}
```

规则：

- admin 可查看任意状态公告
- tenant / landlord / 游客仅可查看 `published`
- 不存在或无权查看统一返回 `3002`

### 3.4 更新公告

```http
PATCH /api/v1/news/{id}
```

请求体示例：

```json
{
  "content": "Updated announcement content."
}
```

规则：

- 必须登录
- 仅 admin 可调用
- 支持部分更新：
  - `title`
  - `content`
  - `status`
- 空 body 或全部字段为空统一返回 `3001`
- 更新后若状态为 `published`，触发通知

### 3.5 删除公告

```http
DELETE /api/v1/news/{id}
```

规则：

- 必须登录
- 仅 admin 可调用
- 物理删除公告
- 已生成的 notification 记录保留

## 4. Notification 联动

- 创建 `draft` 不触发通知
- 创建 `published` 触发通知
- 更新已发布公告再次触发通知
- 通知目标为所有 `active tenant` 与 `active landlord`
- 不给 admin 发公告通知
- `source_type = news`

## 5. News 错误码

| code | 含义 |
| ---- | ---- |
| 3002 | 公告不存在或当前用户无权访问 |
| 3003 | 非法公告状态 |

继续复用：

- `1003` 未登录
- `1004` role 不允许执行该动作
- `3001` 参数错误
- `5000` 系统错误

# 二十三、Payment v1.14.1 补充

> 本节为 v1.14.1 补充内容。若前文 Payment 权限或通知规则与本节不一致，以本节为准。

## 1. 支付权限修正

- `POST /api/v1/payments` 仅允许账单所属 tenant 调用
- bill 不存在时返回 `2501`
- 非账单所属租客、房东、admin 支付统一返回 `1004`
- `GET /api/v1/payments` 与 `GET /api/v1/payments/{id}` 仍只允许 bill 参与者访问
- 非参与者查看 payment 统一返回 `2601`

## 2. 支付成功联动

支付成功时，后端在同一事务中：

1. 插入 `Payment`
2. 更新 `Bill.status = paid`
3. 给 landlord 创建 `Bill paid` 通知
4. 给 tenant 创建 `Payment successful` 通知

说明：

- 两条通知都使用 `source_type = bill`
- `source_id = bill.id`
- 任一通知创建失败则整体回滚

## 3. 当前错误语义

- `2501`：账单真实不存在
- `2602`：账单状态不允许支付
- `2603`：支付金额不匹配
- `2604`：账单已支付
- `1004`：当前用户无权支付该账单
