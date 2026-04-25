# Changelog

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

### House 模块最小闭环完成

------

## Added

### House 模块

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

### House 数据模型

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

### House 接口

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

### House 状态机

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

### House 可见性规则

新增并验证以下可见性规则：

- 公共列表只返回未删除的 `listed` 房源。
- `mine=true` 只返回当前登录用户自己的未删除房源。
- `mine=true` 不混入公共房源。
- `draft/offline` 不对外公开。
- 房东本人可查看自己的 `draft/listed/offline` 房源。
- 删除后的房源不出现在任何列表中。
- 删除后的房源详情统一返回 `house not found`。

------

### House 最小所有权校验

新增最小所有权控制：

- 创建房源时，从 JWT token 解析当前用户 id，自动写入 `landlord_id`。
- 更新、发布、下架、删除只能操作自己的房源。
- 非本人操作房源时，统一返回 `2001 house not found`。
- 不做完整 RBAC 权限系统。

------

### House 参数校验

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

### 自动建表（开发阶段）

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

### Docker 开发模式调整

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

## Changed

### House 删除策略

明确 `DELETE /api/v1/houses/{id}` 为逻辑删除：

- 设置 `deleted_at`
- 同时将 `status` 置为 `offline`
- 不做物理删除
- 删除后不出现在任何列表或详情中
- 删除后不能再执行 update/publish/offline/delete

------

### House 状态更新策略

明确普通更新接口不允许修改状态：

- `PUT /api/v1/houses/{id}` 只更新房源资料
- `status` 只能通过以下接口修改：
  - `PATCH /api/v1/houses/{id}/publish`
  - `PATCH /api/v1/houses/{id}/offline`

这样将“资料更新”和“业务状态流转”分离。

------

### House 查询策略

明确列表查询分为两条独立分支：

- `mine=false` 或不传：公共房源列表，只返回 `listed`
- `mine=true`：我的房源列表，只返回当前用户自己的房源

两条分支不混合、不兜底、不互相补数据。

------

## Fixed

### 修复 House 路由 404

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

### 修复 houses 表不存在导致 5000

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

### 修复 `import app.modules.xxx` 覆盖 Flask app 参数的问题

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

## Verified

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

## Notes

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

### Initial Release（基础版本完成）

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
  - GET /api/v1/users/{id}
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

## Design Decisions

- 采用分层架构：
  - router → service → repository → model
- service 负责事务控制（commit / rollback）
- repository 不允许 commit
- service 不返回 ORM 对象，仅返回 dict
- 使用 g.db 管理 request 级 session
- 使用 PyJWT 而非 session 机制（无状态认证）

------

## Notes

v1.0 阶段未实现：

- login_required（认证中间件）
- 权限系统（role 控制）
- refresh token / token 黑名单
- Alembic 数据库迁移
