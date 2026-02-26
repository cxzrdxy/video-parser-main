# Video Parser

视频解析下载系统 - 支持多平台视频解析下载

## 项目简介

一个基于 FastAPI + Gradio 的多平台视频解析下载系统，支持抖音、哔哩哔哩、小红书、快手、好看视频等主流平台的视频解析与下载。

## 功能特性

- **多平台支持**: 抖音、快手、哔哩哔哩、小红书、好看视频、微视、梨视频、皮皮搞笑
- **双端服务**: FastAPI 后端 API + Gradio 前端界面
- **AI 视频分析**: 集成 Qwen3-VL 模型，支持视频内容智能分析
- **Docker 部署**: 支持 Docker 和 Docker Compose 一键部署
- **用户管理**: 完整的用户权限和积分系统

## 技术栈

- **后端**: FastAPI + Python 3.11
- **前端**: Gradio
- **AI**: Qwen3-VL (ModelScope)
- **数据库**: MySQL
- **部署**: Docker + Docker Compose

## 快速开始

### 本地运行

1. 克隆项目
```bash
git clone https://github.com/cxzrdxy/video-parser-main.git
cd video-parser-main
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置必要的环境变量
```

4. 启动服务
```bash
# 启动后端 API (端口 5001)
python api.py

# 启动前端界面 (端口 7860)
python app.py
```

### Docker 部署

```bash
# 使用 docker-compose 启动
docker-compose up -d
```

服务地址:
- Gradio 前端: http://localhost:7860
- FastAPI 后端: http://localhost:5001

## 项目结构

```
video-parser-main/
├── api.py                    # FastAPI 后端服务
├── app.py                    # Gradio 前端界面
├── qwen3vl.py                # Qwen3-VL 视频分析
├── configs/                  # 配置文件
│   ├── business_config.json
│   ├── general_constants.py
│   └── logging_config.py
├── src/
│   ├── api/                  # API 接口模块
│   ├── database/             # 数据库管理
│   └── downloaders/          # 视频下载器
├── utils/                    # 工具函数
├── test_client/              # 测试客户端
└── Dockerfile                # Docker 配置
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/parse` | POST | 解析视频链接 |
| `/download` | POST | 下载视频 |
| `/login` | POST | 用户登录 |
| `/records` | GET | 获取下载记录 |
| `/ranking` | GET | 获取排行榜 |

## 配置说明

主要环境变量：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `QWEN_API_KEY` | ModelScope API 密钥 | - |
| `QWEN_MODEL_ID` | Qwen 模型 ID | Qwen/Qwen3-VL-8B-Instruct |
| `MAX_FRAMES` | 视频分析提取帧数 | 6 |
| `DB_HOST` | 数据库地址 | localhost |
| `DB_PASSWORD` | 数据库密码 | - |

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/)
- [Gradio](https://gradio.app/)
- [Qwen](https://www.qwenlm.ai/)

---

Star ⭐ 欢迎issues和PR！
