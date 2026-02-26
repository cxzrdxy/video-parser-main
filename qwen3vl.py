#!/usr/bin/env python3
"""
基于 Qwen3-VL 模型的视频内容分析工具
支持读取本地 MP4 视频文件并提取视频内容描述

由于 API 有大小限制，采用提取视频关键帧的方式进行分析
"""

import os
import sys
import base64
import argparse
import tempfile
import subprocess
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API 配置（从环境变量读取）
API_BASE_URL = os.getenv('QWEN_API_BASE_URL', 'https://api-inference.modelscope.cn/v1')
API_KEY = os.getenv('QWEN_API_KEY', '')
MODEL_ID = os.getenv('QWEN_MODEL_ID', 'Qwen/Qwen3-VL-8B-Instruct')

# 帧提取配置
MAX_FRAMES = int(os.getenv('MAX_FRAMES', '8'))  # 最多提取的帧数
FRAME_QUALITY = 85  # JPEG 质量


def get_video_files(directory: str = None) -> list:
    """
    获取指定目录下的所有 MP4 视频文件

    Args:
        directory: 目录路径，默认为当前项目的 downloads 和 cache 目录

    Returns:
        视频文件路径列表
    """
    video_files = []

    if directory:
        search_dirs = [directory]
    else:
        # 默认搜索目录
        base_dir = Path(__file__).parent
        search_dirs = [
            base_dir / 'downloads',
            base_dir / 'cache',
            base_dir / 'static' / 'videos'
        ]

    for search_dir in search_dirs:
        if Path(search_dir).exists():
            for file in Path(search_dir).glob('*.mp4'):
                video_files.append(str(file))

    return video_files


def get_video_duration(video_path: str) -> float:
    """获取视频时长（秒）"""
    try:
        result = subprocess.run(
            [
                'ffprobe', '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ],
            capture_output=True,
            text=True
        )
        return float(result.stdout.strip())
    except Exception:
        return 0


def extract_frames(video_path: str, num_frames: int = MAX_FRAMES) -> list:
    """
    从视频中提取关键帧

    Args:
        video_path: 视频文件路径
        num_frames: 要提取的帧数

    Returns:
        帧图片路径列表
    """
    duration = get_video_duration(video_path)
    if duration <= 0:
        print("警告: 无法获取视频时长，使用默认间隔")
        duration = 60  # 默认假设60秒

    # 计算时间间隔
    interval = duration / (num_frames + 1)

    frames = []
    temp_dir = tempfile.mkdtemp(prefix='video_frames_')

    print(f"视频时长: {duration:.1f}秒，提取 {num_frames} 帧...")

    for i in range(num_frames):
        timestamp = interval * (i + 1)
        output_path = os.path.join(temp_dir, f'frame_{i:03d}.jpg')

        try:
            subprocess.run(
                [
                    'ffmpeg', '-y',
                    '-ss', str(timestamp),
                    '-i', video_path,
                    '-vframes', '1',
                    '-q:v', str(int((100 - FRAME_QUALITY) / 10) + 1),
                    output_path
                ],
                capture_output=True,
                check=True
            )

            if os.path.exists(output_path):
                frames.append(output_path)
                print(f"  提取帧 {i+1}/{num_frames} @ {timestamp:.1f}s")

        except subprocess.CalledProcessError as e:
            print(f"  帧 {i+1} 提取失败: {e}")

    return frames


def image_to_base64(image_path: str) -> str:
    """将图片转换为 base64 编码"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode('utf-8')


def analyze_video(video_path: str, prompt: str = None, stream: bool = True, num_frames: int = MAX_FRAMES) -> str:
    """
    使用 Qwen3-VL 模型分析视频内容

    Args:
        video_path: 视频文件路径
        prompt: 分析提示词
        stream: 是否使用流式输出
        num_frames: 提取的帧数

    Returns:
        视频内容描述
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"视频文件不存在: {video_path}")

    file_size = os.path.getsize(video_path) / (1024 * 1024)
    print(f"正在读取视频文件: {video_path} ({file_size:.1f}MB)")

    # 提取视频帧
    frames = extract_frames(video_path, num_frames)

    if not frames:
        raise RuntimeError("无法提取视频帧，请确保已安装 ffmpeg")

    print(f"成功提取 {len(frames)} 帧")

    # 默认提示词
    if not prompt:
        prompt = f"""这是从一个视频中提取的 {len(frames)} 帧关键画面。
请根据这些画面，详细描述这个视频的内容，包括：
1. 视频中出现的人物或物体
2. 发生的事件或动作
3. 场景环境
4. 视频的主题或表达的意思
5. 视频的整体叙事或故事线"""

    # 构建消息内容
    content = [{'type': 'text', 'text': prompt}]

    for frame_path in frames:
        frame_base64 = image_to_base64(frame_path)
        content.append({
            'type': 'image_url',
            'image_url': {
                'url': f'data:image/jpeg;base64,{frame_base64}'
            }
        })

    # 创建 API 客户端
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY,
    )

    print(f"正在分析视频...")
    print("-" * 50)

    # 调用 API
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[{
            'role': 'user',
            'content': content,
        }],
        stream=stream
    )

    # 处理响应
    result = ""
    if stream:
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                chunk_content = chunk.choices[0].delta.content
                print(chunk_content, end='', flush=True)
                result += chunk_content
        print()  # 换行
    else:
        result = response.choices[0].message.content
        print(result)

    # 清理临时文件
    for frame_path in frames:
        try:
            os.remove(frame_path)
        except Exception:
            pass

    try:
        os.rmdir(os.path.dirname(frames[0]))
    except Exception:
        pass

    return result


def list_videos():
    """列出项目中所有可用的视频文件"""
    video_files = get_video_files()

    if not video_files:
        print("未找到任何视频文件")
        return

    print("=" * 60)
    print("项目中的视频文件:")
    print("=" * 60)

    for i, video_file in enumerate(video_files, 1):
        file_size = os.path.getsize(video_file) / (1024 * 1024)
        file_name = os.path.basename(video_file)
        duration = get_video_duration(video_file)
        duration_str = f"{duration:.1f}s" if duration > 0 else "未知"
        print(f"{i}. [{file_size:.1f}MB, {duration_str}] {file_name}")
        print(f"   路径: {video_file}")

    print("=" * 60)
    return video_files


def interactive_mode():
    """交互式模式，让用户选择视频进行分析"""
    video_files = list_videos()

    if not video_files:
        return

    print("\n请输入要分析的视频编号 (输入 q 退出):")

    while True:
        try:
            user_input = input("> ").strip()

            if user_input.lower() == 'q':
                print("退出程序")
                break

            index = int(user_input) - 1
            if 0 <= index < len(video_files):
                video_path = video_files[index]
                print(f"\n选择的视频: {os.path.basename(video_path)}")

                # 询问自定义提示词
                custom_prompt = input("输入自定义提示词 (直接回车使用默认): ").strip()

                print("\n" + "=" * 60)
                analyze_video(video_path, custom_prompt if custom_prompt else None)
                print("=" * 60)

                print("\n继续选择其他视频，或输入 q 退出:")
            else:
                print(f"无效的编号，请输入 1-{len(video_files)} 之间的数字")

        except ValueError:
            print("请输入有效的数字")
        except KeyboardInterrupt:
            print("\n退出程序")
            break
        except Exception as e:
            print(f"分析出错: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='基于 Qwen3-VL 模型的视频内容分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出所有视频文件
  python qwen3vl.py --list

  # 分析指定视频
  python qwen3vl.py --video downloads/video.mp4

  # 使用自定义提示词分析
  python qwen3vl.py --video video.mp4 --prompt "这个视频讲的是什么故事？"

  # 指定提取帧数
  python qwen3vl.py --video video.mp4 --frames 12

  # 交互式模式
  python qwen3vl.py --interactive
        """
    )

    parser.add_argument(
        '--video', '-v',
        type=str,
        help='要分析的视频文件路径'
    )

    parser.add_argument(
        '--prompt', '-p',
        type=str,
        default=None,
        help='自定义分析提示词'
    )

    parser.add_argument(
        '--frames', '-f',
        type=int,
        default=MAX_FRAMES,
        help=f'要提取的视频帧数 (默认: {MAX_FRAMES})'
    )

    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='列出项目中所有视频文件'
    )

    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='交互式模式'
    )

    parser.add_argument(
        '--no-stream',
        action='store_true',
        help='禁用流式输出'
    )

    args = parser.parse_args()

    # 如果没有任何参数，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n" + "=" * 60)
        list_videos()
        return

    if args.list:
        list_videos()
    elif args.interactive:
        interactive_mode()
    elif args.video:
        analyze_video(
            args.video,
            prompt=args.prompt,
            stream=not args.no_stream,
            num_frames=args.frames
        )
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
