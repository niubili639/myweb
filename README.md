# Monorepo: Vue3 + FastAPI Starter

一套可长期扩展的前后端分离 Monorepo 骨架，包含：

- 前端：Vue 3 + Vite + TypeScript（`apps/web`）—— 登录、情侣空间、Markdown 日记、AI 问答 & 图片生成、相册
- 后端：FastAPI + SQLAlchemy + Alembic（`apps/api`）—— JWT 登录、角色（系统管理员 / 普通管理员 / 用户）、千问 API 代理、MySQL/SQLite
- 运维：Dockerfile / docker-compose（`ops` 目录预留）

## 快速开始

### 本地后端（Python）

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
copy .env.example .env  # 或手动创建
uvicorn app.main:app --reload
```

接口：`http://localhost:8000/api/v1/health`
> 首个注册用户自动成为管理员，可在前端或 API 设置 Qwen API Key。

### 本地前端（Node 18+）

```powershell
cd apps/web
npm install
npm run dev -- --host
```

默认端口：`http://localhost:5173`，通过 Vite 代理将 `/api` 指向 `http://localhost:8000`。

### Docker Compose

```powershell
docker compose up -d
```

- 默认启动 `api`（使用 SQLite 可直接运行），同时提供可选的 `postgres` / `redis` / `mysql` 服务。
- 当前示例使用远程 MySQL：`mysql+pymysql://appuser:appuser@114.55.55.110:3306/appdb`。
- 如需使用容器内 MySQL，将 `DATABASE_URL` 改为 `mysql+pymysql://appuser:appuser@mysql:3306/appdb`。
- Postgres 连接串示例：`postgresql+psycopg2://postgres:postgres@postgres:5432/appdb`。

## 目录结构

- `apps/api`：FastAPI 应用，模块化单体结构（core/db/modules），含 auth / couples / media / spaces(Qwen)
- `apps/web`：Vue3 前端（Pinia、Router、axios 封装、日记/相册/AI 界面）
- `ops`：预留运维脚本/配置
- `docker-compose.yml`：一键启用后端（可选数据库）

## 环境变量

- `apps/api/.env.example` 提供示例：
  - `PROJECT_NAME`、`ENVIRONMENT`
  - `DATABASE_URL`（缺省使用 SQLite）
  - `API_V1_PREFIX=/api/v1`
  - `ALLOWED_ORIGINS=http://localhost:5173`
  - `SECRET_KEY`、`ACCESS_TOKEN_EXPIRE_MINUTES`
  - `QWEN_API_KEY`、`QWEN_MODEL`、`QWEN_IMAGE_MODEL`

## 常见问题（Windows）

- **虚拟环境执行策略**：若提示执行策略限制，使用 `Set-ExecutionPolicy -Scope Process Bypass`.
- **端口占用**：8000/5173 若被占用，可在 `uvicorn` 或 `vite.config.ts` 中调整。
- **依赖安装慢**：可配置国内镜像，如 `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -e .`。
- **未配置 Qwen Key**：管理员在前端「配置千问 API Key」或调用 `/api/v1/auth/apikey` 设置。

## 后续扩展提示

- 已预留 `modules/auth|spaces|couples|media` 目录及路由占位，可逐步填充。
- Alembic 已初始化并提供 `simple_kv` 示例迁移，可继续追加迁移。

### Windows 一键启动脚本
在仓库根目录运行 `ops\start-dev.bat`，会自动弹出两个终端窗口：
- FastAPI 后端：缺少虚拟环境会自动创建 `.venv`，缺 `.env` 会从 `.env.example` 复制，随后安装依赖并运行 `uvicorn app.main:app --reload`
- Vite 前端：缺 `node_modules` 自动执行 `npm install`，随后运行 `npm run dev -- --host`

默认访问：后端 `http://localhost:8000` ，前端 `http://localhost:5173`
