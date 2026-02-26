# 🎬 Video Parser

<div align="center">

[![GitHub stars](https://img.shields.io/github/stars/cxzrdxy/video-parser-main?style=flat-square)](https://github.com/cxzrdxy/video-parser-main/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/cxzrdxy/video-parser-main?style=flat-square)](https://github.com/cxzrdxy/video-parser-main/network)
[![License](https://img.shields.io/github/license/cxzrdxy/video-parser-main?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-00a393?style=flat-square)](https://fastapi.tiangolo.com/)
[![Gradio](https://img.shields.io/badge/Gradio-5.44+-orange?style=flat-square)](https://gradio.app/)

> 多平台视频解析下载系统 | FastAPI + Gradio + AI 智能分析

</div>

## ✨ 项目简介

Video Parser 是一个功能强大的多平台视频解析下载系统，采用 FastAPI 构建后端 API 服务，配合 Gradio 构建友好的可视化前端界面。系统支持抖音、快手、哔哩哔哩、小红书、好看视频等主流短视频平台的视频解析与下载，并集成 Qwen3-VL 大模型实现视频内容的智能分析与理解。

## 🎯 核心功能

### 📥 视频解析与下载
- **多平台支持**: 抖音、快手、哔哩哔哩、小红书、好看视频、微视、梨视频、皮皮搞笑
- **智能识别**: 自动检测视频平台和类型
- **批量处理**: 支持批量解析和下载
- **封面提取**: 自动提取视频封面图

### 🤖 AI 视频分析
- **Qwen3-VL 集成**: 基于通义千问视觉大模型
- **内容理解**: 智能分析视频内容，生成描述
- **关键帧提取**: 自动提取视频关键帧进行分析
- **多场景适用**: 内容审核、视频分类、标签生成

### 👥 用户系统
- **用户认证**: 安全的登录注册机制
- **积分制度**: 下载积分与权限管理
- **下载记录**: 完整的下载历史记录
- **排行榜**: 用户贡献排行榜

### 🛠️ 技术架构
- **后端**: FastAPI (异步高性能 API 框架)
- **前端**: Gradio (交互式 Web UI)
- **AI**: Qwen3-VL (ModelScope API)
- **数据库**: MySQL (用户数据、下载记录)
- **部署**: Docker + Docker Compose

## 🚀 快速开始

### 环境要求

| 环境 | 版本要求 |
|------|----------|
| Python | ≥ 3.11 |
| MySQL | ≥ 5.7 |
| Docker | ≥ 20.10 |
| FFmpeg | 最新版本 |

### 本地运行

```bash
# 1. 克隆项目
git clone https://github.com/cxzrdxy/video-parser-main.git
cd video-parser-main

# 2. 创建虚拟环境 (可选)
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置以下必要变量：
# - QWEN_API_KEY: ModelScope API 密钥
# - DB_PASSWORD: MySQL 数据库密码

# 5. 初始化数据库
mysql -u root -p < schema.sql

# 6. 启动服务
# 终端 1: 启动后端 API
python api.py

# 终端 2: 启动前端界面
python app.py
```

### Docker 部署 (推荐)

```bash
# 1. 修改 .env 配置
cp .env.example .env
# 编辑 .env 文件配置必要的环境变量

# 2. 使用 docker-compose 启动
docker-compose up -d

# 3. 查看服务状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f
```

### 服务访问

| 服务 | 地址 |
|------|------|
| Gradio 前端 | http://localhost:7860 |
| FastAPI 文档 | http://localhost:5001/docs |
| API 健康检查 | http://localhost:5001/health |

## 📁 项目结构

```
video-parser-main/
│
├── 📄 核心文件
├── api.py                    # FastAPI 后端主入口
├── app.py                    # Gradio 前端界面
├── qwen3vl.py                # Qwen3-VL 视频分析工具
├── schema.sql                # 数据库表结构
├── requirements.txt          # Python 依赖
├── Dockerfile                # Docker 镜像配置
├── docker-compose.yml        # Docker Compose 配置
└── docker-entrypoint.sh      # 容器启动脚本
│
├── ⚙️ 配置文件
└── configs/
    ├── business_config.json  # 业务配置 (平台映射、域名白名单)
    ├── general_constants.py  # 全局常量
    └── logging_config.py    # 日志配置
│
├── 💻 源代码
├── src/
│   ├── api/                  # API 接口模块
│   │   ├── parse.py         # 视频解析
│   │   ├── download.py      # 视频下载
│   │   ├── login.py         # 用户登录
│   │   ├── records.py       # 下载记录
│   │   ├── ranking.py       # 排行榜
│   │   └── ...
│   │
│   ├── database/             # 数据库模块
│   │   ├── db_manager.py    # 数据库连接管理
│   │   ├── userinfo_query.py # 用户信息查询
│   │   ├── records_query.py # 下载记录查询
│   │   └── ...
│   │
│   └── downloaders/          # 视频下载器
│       ├── base_downloader.py    # 下载器基类
│       ├── douyin_downloader.py  # 抖音下载器
│       ├── bilibili_downloader.py# 哔哩哔哩下载器
│       ├── xiaohongshu_downloader.py  # 小红书下载器
│       └── ...
│
├── 🧪 测试客户端
└── test_client/
    ├── client_douyin.py
    ├── client_bilibili.py
    ├── client_xiaohongshu.py
    └── ...
│
└── 🛠️ 工具函数
    └── utils/
        ├── web_fetcher.py    # 网页请求工具
        ├── vigenere_cipher.py # 加密工具
        ├── douyin_utils/     # 抖音签名相关
        └── ...
```

## 📡 API 接口

### 核心接口

| 接口路径 | 方法 | 说明 |
|----------|------|------|
| `/parse` | POST | 解析视频链接，返回视频信息 |
| `/download` | POST | 下载视频到服务器 |
| `/login` | POST | 用户登录认证 |
| `/register` | POST | 用户注册 |
| `/records` | GET | 获取用户下载记录 |
| `/ranking` | GET | 获取下载排行榜 |
| `/upload_score` | POST | 上传下载积分 |
| `/refresh_video` | POST | 刷新视频状态 |
| `/health` | GET | 服务健康检查 |

### 请求示例

```bash
# 解析视频
curl -X POST http://localhost:5001/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "https://v.douyin.com/xxx"}'

# 下载视频
curl -X POST http://localhost:5001/download \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://v.douyin.com/xxx", "video_id": "xxx"}'
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 必填 | 说明 | 默认值 |
|--------|------|------|--------|
| `QWEN_API_KEY` | ✅ | ModelScope API 密钥 | - |
| `QWEN_API_BASE_URL` | - | API 基础地址 | https://api-inference.modelscope.cn/v1 |
| `QWEN_MODEL_ID` | - | Qwen 模型 ID | Qwen/Qwen3-VL-8B-Instruct |
| `MAX_FRAMES` | - | 视频分析提取帧数 | 6 |
| `DB_HOST` | - | MySQL 地址 | localhost |
| `DB_PORT` | - | MySQL 端口 | 3306 |
| `DB_USER` | - | MySQL 用户名 | root |
| `DB_PASSWORD` | ✅ | MySQL 密码 | - |
| `DB_NAME` | - | 数据库名称 | video_parser |
| `DOMAIN` | - | 服务域名 | http://127.0.0.1:5001 |

### 获取 QWEN_API_KEY

1. 访问 [ModelScope 魔搭社区](https://modelscope.cn/)
2. 注册/登录账号
3. 进入「我的模型」-「访问令牌」
4. 创建 API 密钥并填入配置

## 🔧 高级用法

### Qwen3-VL 视频分析

```bash
# 分析指定目录下的所有视频
python qwen3vl.py --dir ./downloads

# 分析单个视频
python qwen3vl.py --video ./downloads/sample.mp4

# 指定输出帧数
python qwen3vl.py --video ./downloads/sample.mp4 --frames 8
```

### 使用测试客户端

```bash
# 测试抖音视频解析
python test_client/client_douyin.py

# 测试 B 站视频解析
python test_client/client_bilibili.py

# 测试小红书视频解析
python test_client/client_xiaohongshu.py
```

## 📦 Docker 相关命令

```bash
# 构建镜像
docker build -t video-parser .

# 运行容器
docker run -d -p 5001:5001 -p 7860:7860 --name video-parser video-parser

# 停止容器
docker-compose down

# 重启服务
docker-compose restart

# 查看实时日志
docker-compose logs -f video-parser

# 进入容器
docker exec -it video-parser bash
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/xxx`)
3. 提交更改 (`git commit -m 'Add xxx'`)
4. 推送分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 高性能 Python Web 框架
- [Gradio](https://gradio.app/) - 快速构建机器学习 Web UI
- [Qwen](https://www.qwenlm.ai/) - 阿里通义千问大模型
- [ModelScope](https://modelscope.cn/) - 魔搭社区

---

<div align="center">

⭐ 喜欢这个项目？请给它一个 Star！

</div>
