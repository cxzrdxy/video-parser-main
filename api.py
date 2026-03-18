#!/usr/bin/env python3
"""
视频解析下载 API 服务 (FastAPI 版本)
支持抖音、哔哩哔哩、小红书、快手、好看视频等平台
"""

import os
import time
import asyncio
from typing import Optional
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException, ChunkedEncodingError, ConnectionError
from urllib3.util.retry import Retry
from fastapi import FastAPI, Header, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from configs.logging_config import logger
from configs.general_constants import (
    DOMAIN_TO_NAME, MINI_PROGRAM_LEGAL_DOMAIN,
    SAVE_VIDEO_PATH, DOMAIN, check_essential_dirs
)
from utils.web_fetcher import WebFetcher, UrlParser
from utils.vigenere_cipher import VigenereCipher
from src.downloader_factory import DownloaderFactory
from database import init_db, get_session, UserDataService


# ==================== Pydantic 模型 ====================

class ParseRequest(BaseModel):
    """解析请求模型"""
    text: str


class DownloadRequest(BaseModel):
    """下载请求模型"""
    video_url: str
    video_id: str


class APIResponse(BaseModel):
    """统一响应模型"""
    retcode: int
    retdesc: str
    data: Optional[dict] = None
    ranking: Optional[dict] = None
    succ: bool


class UserUpsertRequest(BaseModel):
    open_id: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: str = "unknown"
    country: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    wechat_id: Optional[str] = None
    status: str = "active"


class UserPointsAdjustRequest(BaseModel):
    open_id: str
    delta: int
    reason: str


class DownloadRecordCreateRequest(BaseModel):
    open_id: str
    video_id: str
    platform: Optional[str] = None
    title: Optional[str] = None
    source_url: Optional[str] = None
    download_url: Optional[str] = None
    points_cost: int = 0


# ==================== 工具函数 ====================

def make_response(retcode: int, retdesc: str, data: dict = None,
                  ranking: dict = None, succ: bool = False) -> dict:
    """生成统一的响应格式"""
    return {
        'retcode': retcode,
        'retdesc': retdesc,
        'data': data,
        'ranking': ranking,
        'succ': succ
    }


def model_to_dict(model_obj) -> dict:
    if hasattr(model_obj, "model_dump"):
        return model_obj.model_dump(mode="json")
    return model_obj.dict()


def validate_timestamp(request_timestamp: int) -> bool:
    """验证时间戳是否在合理的时间窗口内"""
    current_timestamp = int(time.time() * 1000)
    time_window = 5 * 60 * 1000  # 5分钟的时间窗口
    return abs(current_timestamp - request_timestamp) <= time_window


def validate_request_headers(
    x_timestamp: str,
    x_gclt_text: str,
    x_egct_text: str,
    *args
) -> Optional[dict]:
    """
    验证请求头和参数

    Returns:
        None 如果验证通过，否则返回错误响应字典
    """
    # 检查是否有缺失的参数
    missing_params = [param for param in args if not param]
    if missing_params:
        logger.error(f'Missing parameters in request')
        return make_response(400, 'Missing parameters in request', None, None, False)

    if not x_timestamp:
        logger.error('Missing timestamp in request')
        return make_response(400, 'Missing timestamp in request', None, None, False)

    try:
        if not validate_timestamp(int(x_timestamp)):
            logger.error('Invalid timestamp')
            return make_response(400, 'Invalid timestamp', None, None, False)
    except ValueError:
        logger.error('Invalid timestamp format')
        return make_response(400, 'Invalid timestamp format', None, None, False)

    if not VigenereCipher(x_timestamp).verify_decryption(x_egct_text, x_gclt_text):
        logger.error('Decryption verification failed')
        return make_response(400, 'Decryption verification failed', None, None, False)

    return None


# ==================== 线程池配置 ====================

# 创建线程池执行器，用于执行同步下载任务
download_executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="download_worker")


# ==================== 应用生命周期 ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("Starting Video Parser API Service (FastAPI)...")
    check_essential_dirs()
    init_db()
    yield
    # 关闭时执行
    logger.info("Shutting down Video Parser API Service...")
    # 关闭线程池
    download_executor.shutdown(wait=True)
    logger.info("Download executor shutdown complete")


# ==================== 创建 FastAPI 应用 ====================

app = FastAPI(
    title="视频解析下载 API",
    description="支持抖音、哔哩哔哩、小红书、快手、好看视频等平台的视频解析下载服务",
    version="2.0.0",
    lifespan=lifespan
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ==================== API 路由 ====================

@app.get("/")
async def root():
    """根路由 - 健康检查"""
    return {"status": "ok", "message": "Video Parser API is running (FastAPI)"}


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "timestamp": int(time.time() * 1000)}


@app.post("/api/users/upsert")
async def upsert_user(body: UserUpsertRequest):
    try:
        with get_session() as session:
            service = UserDataService(session)
            user = service.create_or_update_user(
                open_id=body.open_id,
                nickname=body.nickname,
                avatar_url=body.avatar_url,
                gender=body.gender,
                country=body.country,
                province=body.province,
                city=body.city,
                wechat_id=body.wechat_id,
                status=body.status,
            )
            return JSONResponse(
                status_code=200,
                content=make_response(200, "成功", model_to_dict(user), None, True)
            )
    except Exception as e:
        logger.error(f"Upsert user error: {e}")
        return JSONResponse(
            status_code=500,
            content=make_response(500, "保存用户失败", None, None, False)
        )


@app.get("/api/users/{open_id}")
async def get_user(open_id: str):
    try:
        with get_session() as session:
            service = UserDataService(session)
            user = service.get_user(open_id)
            if not user:
                return JSONResponse(
                    status_code=404,
                    content=make_response(404, "用户不存在", None, None, False)
                )
            return JSONResponse(
                status_code=200,
                content=make_response(200, "成功", model_to_dict(user), None, True)
            )
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return JSONResponse(
            status_code=500,
            content=make_response(500, "查询用户失败", None, None, False)
        )


@app.post("/api/users/points/adjust")
async def adjust_user_points(body: UserPointsAdjustRequest):
    try:
        with get_session() as session:
            service = UserDataService(session)
            user = service.adjust_points(open_id=body.open_id, delta=body.delta, reason=body.reason)
            return JSONResponse(
                status_code=200,
                content=make_response(200, "成功", model_to_dict(user), None, True)
            )
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content=make_response(400, str(e), None, None, False)
        )
    except Exception as e:
        logger.error(f"Adjust points error: {e}")
        return JSONResponse(
            status_code=500,
            content=make_response(500, "积分操作失败", None, None, False)
        )


@app.post("/api/users/download-records")
async def create_download_record(body: DownloadRecordCreateRequest):
    try:
        with get_session() as session:
            service = UserDataService(session)
            record = service.create_download_record(
                open_id=body.open_id,
                video_id=body.video_id,
                platform=body.platform,
                title=body.title,
                source_url=body.source_url,
                download_url=body.download_url,
                points_cost=body.points_cost,
            )
            return JSONResponse(
                status_code=200,
                content=make_response(200, "成功", model_to_dict(record), None, True)
            )
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content=make_response(400, str(e), None, None, False)
        )
    except Exception as e:
        logger.error(f"Create download record error: {e}")
        return JSONResponse(
            status_code=500,
            content=make_response(500, "记录下载失败", None, None, False)
        )


@app.get("/api/users/{open_id}/download-records")
async def list_download_records(
    open_id: str,
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    try:
        with get_session() as session:
            service = UserDataService(session)
            records = service.list_download_records(open_id=open_id, limit=limit, offset=offset)
            total = service.get_total_download_count(open_id=open_id)
            return JSONResponse(
                status_code=200,
                content=make_response(
                    200,
                    "成功",
                    {
                        "items": [model_to_dict(item) for item in records],
                        "total": total,
                        "limit": limit,
                        "offset": offset,
                    },
                    None,
                    True,
                )
            )
    except Exception as e:
        logger.error(f"List download records error: {e}")
        return JSONResponse(
            status_code=500,
            content=make_response(500, "查询下载记录失败", None, None, False)
        )


@app.post("/api/parse")
async def parse_video(
    body: ParseRequest,
    x_timestamp: str = Header(default="", alias="X-Timestamp"),
    x_gclt_text: str = Header(default="", alias="X-GCLT-Text"),
    x_egct_text: str = Header(default="", alias="X-EGCT-Text"),
    wx_open_id: str = Header(default="Guest", alias="WX-OPEN-ID"),
):
    """
    解析视频链接

    从分享链接中提取视频信息，包括标题、封面、视频直链等
    """
    try:
        text = body.text

        # 验证请求
        validation_error = validate_request_headers(x_timestamp, x_gclt_text, x_egct_text, text)
        if validation_error:
            return JSONResponse(status_code=400, content=validation_error)

        # 提取URL
        extracted_url = UrlParser.get_url(text)
        logger.info(f'extracted_url: {extracted_url}')

        if not extracted_url:
            logger.error('No valid URL found in text')
            return JSONResponse(
                status_code=400,
                content=make_response(400, '未找到有效的视频链接', None, None, False)
            )

        # 获取重定向URL
        redirect_url = WebFetcher.fetch_redirect_url(extracted_url)
        logger.info(f'redirect_url: {redirect_url}')

        # 如果重定向失败，直接使用原始URL
        if not redirect_url:
            redirect_url = extracted_url
            logger.info(f'Using original URL: {redirect_url}')

        platform = DOMAIN_TO_NAME.get(UrlParser.get_domain(redirect_url))
        video_id = UrlParser.get_video_id(redirect_url)
        real_url = UrlParser.extract_video_address(redirect_url)
        logger.info(f'platform: {platform}, video_id: {video_id}, real_url: {real_url}')

        if not platform:
            logger.error(f'This link is not supported for extraction: {real_url}')
            return JSONResponse(
                status_code=400,
                content=make_response(400, '该链接尚未支持提取', None, None, False)
            )

        title = cover_url = video_url = None
        downloader = None

        # 小红书平台特殊处理（重试机制）
        if platform == '小红书':
            max_attempts = 5
            attempts = 0
            while attempts < max_attempts:
                downloader = DownloaderFactory.create_downloader(platform, real_url)
                title = downloader.get_title_content()
                video_url = downloader.get_real_video_url()
                cover_url = downloader.get_cover_photo_url()
                if video_url:
                    break
                attempts += 1
                logger.debug(f"Attempt {attempts} failed. Retrying...")
            if not video_url:
                logger.error("Failed to retrieve video URL after 5 attempts.")
        else:
            downloader = DownloaderFactory.create_downloader(platform, real_url)
            title = downloader.get_title_content()
            video_url = downloader.get_real_video_url()
            cover_url = downloader.get_cover_photo_url()

        # 转换为 HTTPS
        updated_video_url = UrlParser.convert_to_https(video_url)
        updated_cover_url = UrlParser.convert_to_https(cover_url)

        data_dict = {
            'video_id': video_id,
            'platform': platform,
            'title': title,
            'video_url': updated_video_url,
            'cover_url': updated_cover_url
        }

        # B站视频需要额外返回音频URL
        if platform == '哔哩哔哩' and downloader and hasattr(downloader, 'get_audio_url'):
            audio_url = downloader.get_audio_url()
            if audio_url:
                data_dict['audio_url'] = UrlParser.convert_to_https(audio_url)

        logger.debug(f'{wx_open_id} {platform} Parse Success')
        if wx_open_id and wx_open_id != "Guest":
            try:
                with get_session() as session:
                    service = UserDataService(session)
                    service.increase_parse_count(wx_open_id)
            except Exception as metric_error:
                logger.error(f"Increase parse count failed: {metric_error}")
        return JSONResponse(
            status_code=200,
            content=make_response(200, '成功', data_dict, None, True)
        )

    except Exception as e:
        logger.error(f"Parse error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content=make_response(500, '功能太火爆啦，请稍后再试', None, None, False)
        )


def sync_download_video(request_video_url: str, video_path: str, wx_open_id: str) -> dict:
    """
    同步下载视频的函数，在线程池中执行

    Returns:
        dict: {'success': bool, 'error_msg': str or None}
    """
    logger.info(f"[Thread] Starting download for {request_video_url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Referer': 'https://www.pearvideo.com/'
    }

    # 如果是梨视频，必须带 Referer
    if "pearvideo.com" in request_video_url:
        headers['Referer'] = 'https://www.pearvideo.com/'

    # 创建带重试机制的session
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        response = session.get(request_video_url, headers=headers, stream=True, timeout=120)
        response.raise_for_status()
    except (RequestException, ConnectionError) as e:
        logger.error(f'{wx_open_id} Failed to connect: {e}')
        return {'success': False, 'error_msg': 'connect_failed'}

    try:
        # 保存视频到服务器
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info(f"[Thread] Download completed: {video_path}")
        return {'success': True, 'error_msg': None}
    except (ChunkedEncodingError, IOError) as e:
        logger.error(f'{wx_open_id} Failed to save video: {e}')
        # 删除可能不完整的文件
        if os.path.exists(video_path):
            os.remove(video_path)
        return {'success': False, 'error_msg': 'save_failed'}


@app.post("/api/download")
async def download_video(
    body: DownloadRequest,
    x_timestamp: str = Header(default="", alias="X-Timestamp"),
    x_gclt_text: str = Header(default="", alias="X-GCLT-Text"),
    x_egct_text: str = Header(default="", alias="X-EGCT-Text"),
    wx_open_id: str = Header(default="Guest", alias="WX-OPEN-ID"),
):
    """
    获取视频下载链接

    对于某些平台，需要服务器端下载并返回可访问的链接
    使用线程池执行同步下载任务，避免阻塞事件循环
    """
    try:
        request_video_url = body.video_url
        request_video_id = body.video_id

        # 验证请求
        validation_error = validate_request_headers(x_timestamp, x_gclt_text, x_egct_text, request_video_url)
        if validation_error:
            return JSONResponse(status_code=400, content=validation_error)

        # 判断视频链接的域名是否为小程序的合法域名
        domain = UrlParser.get_domain(request_video_url)
        logger.debug(f'Checking domain: {domain}')

        if domain in MINI_PROGRAM_LEGAL_DOMAIN:
            # 如果是，直接返回视频链接
            logger.debug(f'{wx_open_id} 直接返回视频链接')
            return JSONResponse(
                status_code=200,
                content=make_response(200, '成功', {'download_url': request_video_url}, None, True)
            )
        else:
            # 如果不是，服务器端下载视频并保存
            video_filename = f'{request_video_id}.mp4'
            video_path = os.path.join(SAVE_VIDEO_PATH, video_filename)

            # 如果 DOMAIN 未配置，使用本地测试地址
            current_domain = DOMAIN or "http://localhost:5001"

            if not os.path.exists(video_path):
                # 使用线程池执行同步下载任务
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    download_executor,
                    sync_download_video,
                    request_video_url,
                    video_path,
                    wx_open_id
                )

                if not result['success']:
                    # 下载失败，返回原始链接
                    error_msg = '服务器下载失败，返回原始链接'
                    return JSONResponse(
                        status_code=200,
                        content=make_response(200, error_msg, {'download_url': request_video_url}, None, True)
                    )

            # 返回视频的 URL
            download_url = f'{current_domain}/static/videos/{video_filename}'
            logger.debug(f'{wx_open_id} 返回视频地址: {download_url}')
            return JSONResponse(
                status_code=200,
                content=make_response(200, '成功', {'download_url': download_url}, None, True)
            )

    except Exception as e:
        logger.error(f"Download error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content=make_response(500, '功能太火爆啦，请稍后再试', None, None, False)
        )


# ==================== 主程序入口 ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=5001,
        reload=True,
        log_level="info"
    )
