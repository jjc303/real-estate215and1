# API 接口规范（统一标准）

------

## 1. 基础约定

### 1.1 基础路径

```text
/api/v1
```

示例：

```text
/api/v1/users
/api/v1/houses
```

------

### 1.2 请求方式

| 方法   | 含义     |
| ------ | -------- |
| GET    | 查询     |
| POST   | 创建     |
| PUT    | 更新     |
| PATCH  | 部分更新 |
| DELETE | 删除     |

------

### 1.3 Content-Type

```text
application/json
```

------

## 2. 统一响应格式（强制）

所有接口必须返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

------

### 2.1 字段说明

| 字段    | 含义     |
| ------- | -------- |
| code    | 状态码   |
| message | 提示信息 |
| data    | 返回数据 |

------

### 2.2 成功示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "test"
  }
}
```

------

### 2.3 失败示例

```json
{
  "code": 1001,
  "message": "user not found",
  "data": null
}
```

------

## 3. 错误码规范

| code | 含义       |
| ---- | ---------- |
| 0    | 成功       |
| 1001 | 用户不存在 |
| 1002 | 密码错误   |
| 1003 | 未登录     |
| 1004 | 无权限     |
| 2001 | 房源不存在 |
| 3001 | 参数错误   |
| 5000 | 系统错误   |

------

## 4. 分页规范

### 请求参数

```text
?page=1&page_size=10
```

------

### 响应结构

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [],
    "total": 100,
    "page": 1,
    "page_size": 10
  }
}
```

------

## 5. 认证（JWT）

### Header

```text
Authorization: Bearer <token>
```

------

### 说明

- 登录成功返回 token
- 后续请求必须携带 token
- 服务端解析 token 获取用户信息

------

## 6. 命名规范

### 6.1 URL 使用名词（复数）

```text
/users
/houses
/contracts
```

------

### 6.2 不使用动词

```text
❌ /getUser
❌ /createHouse
```

------

## 7. 参数规范

### 7.1 JSON Body（POST / PUT）

```json
{
  "username": "string",
  "password": "string"
}
```

------

### 7.2 Query（GET）

```text
/users?page=1&page_size=10
```

------

### 7.3 Path

```text
/users/{id}
```

------

## 8. 示例接口

------

### 8.1 用户注册

```text
POST /api/v1/users
```

#### request

```json
{
  "username": "test",
  "password": "123456"
}
```

#### response

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "test"
  }
}
```

------

### 8.2 用户登录

```text
POST /api/v1/auth/login
```

#### request

```json
{
  "username": "test",
  "password": "123456"
}
```

#### response

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "token": "xxx"
  }
}
```

------

### 8.3 获取用户信息

```text
GET /api/v1/users/{id}
```

#### response

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "test"
  }
}
```

------

### 8.4 房源列表

```text
GET /api/v1/houses?page=1&page_size=10
```

------

### 8.5 收藏房源

```text
POST /api/v1/favorites
```

------

## 9. 约束（必须遵守）

```text
禁止：
- 返回非统一结构
- 返回裸字符串
- 使用不规范 URL
- 混用参数位置（query / body）
- 使用多个分页格式
```

------

## 10. 总结

```text
所有接口必须：
- 统一路径风格
- 统一响应结构
- 统一错误码
- 统一分页
- 统一认证方式
```