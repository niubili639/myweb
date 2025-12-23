# FastAPI Backend

模块化单体骨架，包含认证、情侣空间（纪念日/Markdown 记录/相册）、Qwen 智能体（问答/图片生成）、数据库封装与健康检查。

## 本地运行

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
copy .env.example .env
uvicorn app.main:app --reload
```

- API 前缀：`/api/v1`
- 健康检查：`GET /api/v1/health`
- Hello：`GET /api/v1/hello?name=you`
- 认证：`POST /api/v1/auth/register`、`POST /api/v1/auth/login`、`GET /api/v1/auth/me`
- 千问：`POST /api/v1/spaces/ai/chat`、`POST /api/v1/spaces/ai/image`（需管理员设置 API Key）
- 情侣空间：`POST /api/v1/couples`、`GET /api/v1/couples/me`、`POST /api/v1/couples/{id}/notes`
- 相册：`POST /api/v1/media/{coupleId}/photos`

## 数据库

- 当前示例指向远程 MySQL：`mysql+pymysql://appuser:appuser@114.55.55.110:3306/appdb`。
- 若提供其他 MySQL 连接串（容器内示例 `mysql+pymysql://appuser:appuser@mysql:3306/appdb`），应用会自动使用对应数据库。
- 若提供 Postgres 连接串（例如 `postgresql+psycopg2://postgres:postgres@localhost:5432/appdb`），应用会自动使用 Postgres。

## Alembic 迁移

```powershell
cd apps/api
alembic upgrade head
alembic revision -m "your message"  # 如需新增迁移
```

## 测试

```powershell
cd apps/api
pytest
```

## 代码质量

- `ruff` 配置在 `pyproject.toml` 中，执行 `ruff check .`
- 首次注册用户自动成为管理员，便于在 `/api/v1/auth/apikey` 设置 Qwen Key。
