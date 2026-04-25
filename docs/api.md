# API 文档（当前实现）

Version: v1.3.1
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
- 当前开发阶段可使用 `Base.metadata.create_all()` 自动创建缺失表，后续如进入正式迁移阶段再引入 Alembic。


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

# 十、common 公共能力补充

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

说明：

- `BaseModel` 提供 `id / created_at / updated_at`。
- `SoftDeleteMixin` 提供 `deleted_at`。
- `deleted_at` 只用于 House。
- Favorite / Appointment 有 `updated_at`。
- Favorite / Appointment 没有 `deleted_at`。

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
