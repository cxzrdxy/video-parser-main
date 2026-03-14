# Video Parser - 多平台视频解析下载工具

一个强大的多平台视频解析和下载工具，支持无水印下载、在线播放和视频内容分析。

## ✨ 功能特性

### 支持的平台
- 📱 **抖音** - 支持抖音视频、图文、合集等
- 🎬 **哔哩哔哩** - 支持 B 站视频解析下载
- 📸 **小红书** - 支持小红书视频和图文
- 🎭 **快手** - 支持快手视频解析
- 🎪 **好看视频** - 百度旗下视频平台
- 📺 **梨视频** - 新闻资讯视频
- 🤣 **皮皮搞笑** - 短视频平台
- 📹 **微视** - 腾讯微视短视频

### 核心功能
- ✅ **无水印下载** - 下载各大平台的无水印视频
- ✅ **在线播放** - 支持下载后在线预览视频
- ✅ **API 服务** - 提供 RESTful API 接口
- ✅ **Web 界面** - 基于 Gradio 的友好用户界面
- ✅ **视频分析** - 集成 Qwen3-VL 多模态模型分析视频内容
- ✅ **数据持久化** - MySQL 数据库存储用户数据
- ✅ **Docker 部署** - 支持容器化部署

## 🚀 快速开始

### 方法一：Docker 部署（推荐）

1. **克隆仓库**
```bash
git clone https://github.com/cxzrdxy/video-parser-main.git
cd video-parser-main
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置必要的参数
```

3. **启动服务**
```bash
docker-compose up -d
```

4. **访问服务**
- Gradio Web 界面：http://localhost:7860
- FastAPI 文档：http://localhost:5001/docs

### 方法二：本地部署

1. **环境要求**
- Python 3.8+
- MySQL 8.0+
- Node.js (可选)

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置数据库**
```sql
-- 创建数据库和用户
CREATE DATABASE ucmao_parse CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER 'video_parser'@'localhost' IDENTIFIED BY 'video_parser_password';
GRANT ALL PRIVILEGES ON ucmao_parse.* TO 'video_parser'@'localhost';
FLUSH PRIVILEGES;

-- 导入表结构
source schema.sql
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件配置数据库连接等信息
```

5. **启动服务**
```bash
# 启动 API 服务
python api.py

# 启动 Gradio Web 界面
python app.py
```

## 📖 API 使用

### 主要接口

#### 1. 解析视频
```http
POST /api/parse
Content-Type: application/json

{
  "text": "视频链接或分享文本"
}
```

#### 2. 下载视频
```http
POST /api/download
Content-Type: application/json

{
  "video_url": "视频地址",
  "video_id": "视频 ID"
}
```

#### 3. 获取用户数据
```http
GET /api/user/{user_id}/videos
```

#### 4. 视频分析（使用 Qwen3-VL）
```http
POST /api/analyze-video
Content-Type: application/json

{
  "video_url": "视频地址",
  "analysis_type": "content"
}
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `QWEN_API_BASE_URL` | Qwen3-VL API 地址 | `https://api-inference.modelscope.cn/v1` |
| `QWEN_API_KEY` | ModelScope API 密钥 | - |
| `QWEN_MODEL_ID` | 模型 ID | `Qwen/Qwen3-VL-8B-Instruct` |
| `API_SERVER_URL` | 后端 API 地址 | `http://127.0.0.1:5001` |
| `DB_HOST` | MySQL 主机地址 | `localhost` |
| `DB_PORT` | MySQL 端口 | `3306` |
| `DB_USER` | 数据库用户名 | `video_parser` |
| `DB_PASSWORD` | 数据库密码 | `video_parser_password` |
| `DB_NAME` | 数据库名称 | `ucmao_parse` |

## 📁 项目结构

```
video-parser-main/
├── api.py                      # FastAPI 后端服务
├── app.py                      # Gradio Web 界面
├── qwen3vl.py                  # Qwen3-VL 视频分析模块
├── requirements.txt            # Python 依赖
├── schema.sql                  # 数据库表结构
├── Dockerfile                  # Docker 镜像配置
├── docker-compose.yml          # Docker 编排配置
├── configs/                    # 配置文件
│   ├── business_config.json    # 业务配置
│   ├── general_constants.py    # 通用常量
│   └── logging_config.py       # 日志配置
├── database/                   # 数据库模块
│   ├── models.py               # 数据模型
│   ├── service.py              # 数据服务
│   └── session.py              # 数据库会话
├── src/                        # 核心下载器
│   ├── downloader_factory.py   # 下载器工厂
│   └── downloaders/            # 各平台下载器
│       ├── base_downloader.py  # 基础下载器
│       ├── douyin_downloader.py
│       ├── bilibili_downloader.py
│       └── ...
├── utils/                      # 工具函数
│   ├── common_utils.py         # 通用工具
│   ├── web_fetcher.py          # 网页抓取
│   ├── vigenere_cipher.py      # 加密工具
│   └── douyin_utils/           # 抖音专用工具
└── test_client/                # 测试客户端
```

## 🔐 安全说明

- 请妥善保管 `.env` 文件，不要提交到版本控制
- API 密钥和数据库密码请使用强密码
- 生产环境建议配置 HTTPS
- 定期更新依赖包以修复安全漏洞

## 🛠️ 开发指南

### 添加新平台支持

1. 在 `src/downloaders/` 目录创建新的下载器类
2. 继承 `BaseDownloader` 基类
3. 实现平台特定的解析逻辑
4. 在 `DownloaderFactory` 中注册

### 测试

```bash
# 运行测试客户端
python test_client/client_douyin.py
python test_client/client_bilibili.py
```

## 📝 常见问题

### 1. 权限错误（WinError 5）
建议使用 Docker 部署或在 Linux 环境下运行。

### 2. 依赖安装失败
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 数据库连接失败
检查 MySQL 服务是否启动，确认 `.env` 文件中的数据库配置正确。

## 📄 许可证

MIT License

## 🙏 致谢

- [Qwen3-VL](https://modelscope.cn/models/Qwen/Qwen3-VL-8B-Instruct) - 视频内容分析
- [Gradio](https://gradio.app/) - Web 界面
- [FastAPI](https://fastapi.tiangolo.com/) - API 框架

## 📮 联系方式

如有问题或建议，请提交 Issue 或联系作者。

---

**注意**: 本项目仅供学习交流使用，请遵守相关平台的版权和使用条款。
