# 后端项目结构规范（Flask · 模块化单体）

------

## 1. 架构

```text
Blueprint → service → repository → model
```

规则：

- router 不写业务
- repository 不写业务
- service 负责业务 + 事务

------

## 2. 目录结构（完整）

```text
backend/
  app/
    main.py
    factory.py

    core/
      config.py
      database.py
      security.py
      exceptions.py
      response.py
      logging.py

    common/
      base_model.py
      base_repository.py
      pagination.py
      enums.py
      utils.py

    container/
      repositories.py
      services.py
      tools.py

    modules/
      auth/
        router.py
        service.py
        schema.py

      user/
        model.py
        repository.py
        service.py
        schema.py
        router.py

      house/
        model.py
        repository.py
        service.py
        schema.py
        router.py

      search/
        service.py
        schema.py
        router.py

      favorite/
        model.py
        repository.py
        service.py
        schema.py
        router.py

      appointment/
        model.py
        repository.py
        service.py
        schema.py
        router.py

      conversation/
        model.py
        repository.py
        service.py
        schema.py
        router.py

      contract/
        model.py
        repository.py
        service.py
        schema.py
        router.py

      bill/
        model.py
        repository.py
        service.py
        schema.py
        router.py

      payment/
        model.py
        repository.py
        service.py
        schema.py
        router.py

      repair/
        model.py
        repository.py
        service.py
        schema.py
        router.py

      complaint/
        model.py
        repository.py
        service.py
        schema.py
        router.py

      news/
        model.py
        repository.py
        service.py
        schema.py
        router.py

      notification/
        model.py
        repository.py
        service.py
        schema.py
        router.py

      statistics/
        service.py
        schema.py
        router.py

      log/
        model.py
        repository.py
        service.py
        schema.py
        router.py

      storage/
        service.py
        schema.py
        router.py

      admin/
        router.py
        service.py
        schema.py

    tests/

  alembic/
  requirements.txt
```

------

## 3. 应用入口

```python
def create_app(config_name=None):
    app = Flask(__name__)

    load_config(app)
    init_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_hooks(app)

    return app
```

------

## 4. DB 规则（核心）

```text
scoped_session = 底层工具
g.db           = 唯一入口
@app.before_request
def open_db():
    g.db = SessionLocal()

@app.teardown_request
def close_db(_):
    if hasattr(g, "db"):
        g.db.close()
        SessionLocal.remove()
```

数据库结构管理：

- 不使用 `Base.metadata.create_all()`
- 统一使用 Alembic migration 管理表结构
- 启动 Flask app 不负责自动建表

常用命令：

```bash
alembic revision --autogenerate -m "xxx"
alembic upgrade head
alembic current
alembic history
alembic downgrade -1
```

------

## 5. DB 使用（强制）

```python
service.create(g.db, data)
repository.get(db, ...)
```

禁止：

- service 获取 db
- repository 创建 db
- 使用全局 session

------

## 6. schema

```python
data = Schema(**(request.get_json() or {}))
```

规则：

- 只用 Pydantic
- 不混用其他校验
- schema 不参与 ORM

------

## 7. router 标准

```python
@bp.route("/", methods=["POST"])
def create():
    data = Schema(**(request.get_json() or {}))
    service = get_service()
    return success(service.create(g.db, data))
```

------

## 8. 分层职责

router：

- 接收请求
- 校验参数
- 调 service

service：

- 业务逻辑
- 状态流转
- 事务

repository：

- 数据访问
- 查询封装

------

## 9. 事务

```python
try:
    ...
    db.commit()
except:
    db.rollback()
    raise
```

------

## 10. 响应

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

------

## 11. container

```python
_service = Service(repo)

def get_service():
    return _service
```

规则：

允许：

- 无状态 service / repo

禁止：

- request
- g
- db
- current_user

------

## 12. 业务模块

auth：登录 / JWT
user：用户
house：房源
search：筛选（只读）
favorite：收藏

appointment：预约
conversation：聊天
contract：合同
bill：账单
payment：支付

repair：报修
complaint：投诉
news：公告
notification：通知

statistics：统计（只读）
log：日志
storage：文件
admin：后台

------

## 13. 强约束（必须）

```text
禁止：
- repository commit
- service 保存状态
- 返回 ORM 对象
- 隐式获取 db
- 多套校验体系
- router 写业务
```

------

## 14. 原则

- service 无状态
- session 请求级
- 显式依赖
- 单向调用
- 模块内聚

------

## 15. 多进程兼容约束（必须）

### 15.1 状态约束

禁止：

- 全局变量存业务数据
- service / repo 内保存状态
- container 单例保存动态数据

```text
状态必须放数据库 / 外部存储
```

------

### 15.2 Session 约束

- session 仅通过 g.db
- 禁止保存 session

------

### 15.3 请求上下文约束

禁止保存：

- request
- g
- current_user

------

### 15.4 并发约束

禁止：

- 手写线程
- asyncio
- 业务层并发

------

## 16. 运行模型

开发：

- 单进程

部署：

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app.main:app"
```

------

## 17. 多进程检查清单

必须满足：

- service 无状态
- repository 无状态
- 无全局业务变量
- 所有 db 显式传递
- 无 request/g 泄露

------

## 18. 结论

```
满足本规范：
单进程 → 多进程无需修改业务代码
```
