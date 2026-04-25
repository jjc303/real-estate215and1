# API 文档（当前实现）

Version: v1.0
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

| code | 含义                |
| ---- | ------------------- |
| 0    | 成功                |
| 3001 | 参数错误            |
| 1001 | 用户不存在          |
| 1002 | 用户名或密码错误    |
| 1003 | 未登录 / token 无效 |
| 4009 | 资源冲突            |
| 5000 | 系统错误            |

------

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

# 四、说明

- 所有时间字段为 ISO 格式
- 所有接口返回均遵循统一响应结构
- 所有用户返回数据均不包含 password
- token 使用 JWT（Bearer 模式）

------