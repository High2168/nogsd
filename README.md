# 基于协同过滤的就业推荐系统

## 项目简介

本项目是一个基于协同过滤算法的就业推荐系统，为毕业生提供个性化的职位推荐服务。

## 界面预览

系统界面全部为**中文**，包含：
- 首页：热门职位展示、系统特色介绍
- 职位列表：搜索、筛选、分页
- 职位详情：职位信息、投递、收藏
- 推荐页面：个性化推荐结果、匹配理由
- 个人中心：用户画像管理

## 技术栈

### 后端
- Python 3.10+
- Django 4.2
- Django REST Framework
- MySQL / SQLite
- Redis (缓存)

### 前端
- Vue 3 + TypeScript
- Vite
- Element Plus
- Pinia (状态管理)
- ECharts (可视化)

### 推荐算法
- User-based Collaborative Filtering (基于用户的协同过滤)
- Item-based Collaborative Filtering (基于物品的协同过滤)
- 混合推荐策略
- 冷启动处理

## 项目结构

```
nogsd/
├── backend/                 # Django后端
│   ├── config/              # 项目配置
│   ├── apps/
│   │   ├── users/           # 用户模块
│   │   ├── jobs/            # 职位模块
│   │   ├── recommendations/ # 推荐模块
│   │   └── data/            # 数据管理
│   ├── scripts/             # 工具脚本
│   └── requirements.txt
├── frontend/                # Vue前端
│   ├── src/
│   │   ├── api/             # API接口
│   │   ├── components/      # 组件
│   │   ├── views/           # 页面
│   │   ├── stores/          # 状态管理
│   │   └── router/          # 路由
│   └── package.json
└── README.md
```

## 快速开始（推荐）

### 方式一：Windows一键启动

1. **启动后端**：双击运行 `backend/start.bat`
2. **导入数据**：双击运行 `backend/import_data.bat`（首次运行需要）
3. **启动前端**：双击运行 `frontend/start.bat`

### 方式二：命令行启动

#### 环境要求
- Python 3.10+
- Node.js 18+

#### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建管理员
python manage.py createsuperuser

# 启动服务
python manage.py runserver
```

#### 导入职位数据

```bash
# 在backend目录下，激活虚拟环境后
python manage.py shell

# 在shell中执行:
>>> from apps.data.import_data import import_data
>>> import_data(r"path/to/job_posts.csv", limit=2000)
```

或者直接运行：
```bash
python manage.py shell -c "from apps.data.import_data import import_data; import_data(r'你的CSV文件路径', limit=2000)"
```

#### 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:3000 |
| 后端API | http://localhost:8000/api/ |
| 管理后台 | http://localhost:8000/admin/ |
| API文档 | http://localhost:8000/api/docs/ |

### 测试账号

- **管理员**: 启动时创建
- **普通用户**: user1 ~ user300，密码: `123456`

## 主要功能

### 用户功能
- 用户注册/登录 (JWT认证)
- 用户画像管理
- 职位浏览和搜索
- 职位收藏和投递
- 个性化推荐

### 推荐功能
- 基于协同过滤的职位推荐
- 冷启动用户处理
- 推荐理由展示
- 实时更新推荐

### 管理功能
- 职位管理
- 用户管理
- 交互数据分析
- 推荐效果监控

## API接口

| 接口 | 方法 | 描述 |
|------|------|------|
| /api/auth/register/ | POST | 用户注册 |
| /api/auth/login/ | POST | 用户登录 |
| /api/users/profile/ | GET/PUT | 用户画像 |
| /api/jobs/ | GET | 职位列表 |
| /api/jobs/{id}/ | GET | 职位详情 |
| /api/recommendations/ | GET | 获取推荐 |
| /api/recommendations/interact/ | POST | 用户交互 |

## 推荐算法说明

### User-based CF
基于用户的协同过滤，找到与目标用户兴趣相似的用户，推荐这些用户喜欢的职位。

### Item-based CF
基于物品的协同过滤，推荐与用户历史喜欢的职位相似的其他职位。

### 混合策略
融合User-based和Item-based的结果，加权生成最终推荐。

### 冷启动处理
对于新用户，基于用户画像（技能、期望职位、薪资等）匹配职位特征进行推荐。

## 部署说明

### 生产环境配置

1. 修改 `backend/config/settings.py`:
   - 设置 `DEBUG = False`
   - 配置 `ALLOWED_HOSTS`
   - 配置MySQL数据库
   - 配置Redis缓存

2. 使用 Gunicorn + Nginx 部署后端

3. 构建前端静态文件:
   ```bash
   cd frontend
   npm run build
   ```

## 开发计划

- [x] 项目架构设计
- [x] 数据库模型设计
- [x] 用户认证系统
- [x] 职位管理API
- [x] 协同过滤算法
- [x] 前端页面开发
- [ ] 算法性能优化
- [ ] 系统测试
- [ ] 文档完善

## 许可证

本项目仅用于毕业设计，未经授权不得用于商业用途。
