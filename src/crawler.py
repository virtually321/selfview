#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os
import subprocess
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 全局常量
URL = "http://rihou.cc:555/gggg.nzk/"  # 节目源地址
FILENAME = "playlist.m3u"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/58.0.3029.110 Safari/537.3"
)

def create_session_with_retries():
    """
    创建带重试策略的 requests Session，以应对网络波动和临时错误。
    支持 Python 版本和 urllib3 版本的兼容性处理。
    """
    session = requests.Session()
    retry_kwargs = dict(
        total=5,
        backoff_factor=1.0,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    try:
        # urllib3 1.26+ 的参数名
        retry = Retry(allowed_methods=["HEAD", "GET", "OPTIONS"], **retry_kwargs)
    except TypeError:
        # older urllib3 版本回退
        retry = Retry(method_whitelist=["HEAD", "GET", "OPTIONS"], **retry_kwargs)

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def fetch_webpage(url):
    headers = {
        "User-Agent": USER_AGENT
    }
    session = create_session_with_retries()
    try:
        # 连接超时 10s，读取超时 30s
        r = session.get(url, headers=headers, timeout=(10, 30))
        r.encoding = r.apparent_encoding
        r.raise_for_status()
        return r.text
    except requests.exceptions.ConnectTimeout as e:
        logging.error("连接超时：%s", e)
    except requests.exceptions.ReadTimeout as e:
        logging.error("读取超时：%s", e)
    except requests.exceptions.Timeout as e:
        logging.error("请求超时：%s", e)
    except requests.exceptions.HTTPError as e:
        logging.error("HTTP 错误：%s", e)
    except requests.exceptions.RequestException as e:
        logging.error("请求失败：%s", e)
    return ""

def parse_channels(text):
    groups = {}
    current_group = None

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # 识别组行（带,且带#genre#）
        if ',' in line and '#genre#' in line:
            current_group = line.split(',', 1)[0].strip()
            groups.setdefault(current_group, [])
            continue
        # 频道行
        if current_group and ',' in line:
            channel_name, stream_url = line.split(',', 1)
            channel_name = channel_name.strip()
            stream_url = stream_url.strip()
            if "肥羊" not in channel_name and "肥羊" not in stream_url:
                groups[current_group].append((channel_name, stream_url))

    return {g: chs for g, chs in groups.items() if chs}

def save_m3u(groups, filename):
    """生成M3U文件，组名保留，组内写频道"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n\n')
        for group, channels in groups.items():
            if not channels:
                continue
            f.write(f"#{group}\n")
            for channel_name, stream_url in channels:
                f.write(f'#EXTINF:-1 group-title="{group}", {channel_name}\n')
                f.write(stream_url + "\n")
    total = sum(len(channels) for channels in groups.values())
    logging.info("写入文件 %s 完成，节目总数：%d 条。", filename, total)

def git_commit_and_push(filename):
    """将文件添加到 Git，并提交和推送更改"""
    try:
        subprocess.run(["git", "add", filename], check=True)
        subprocess.run(["git", "commit", "-m", "更新 playlist.m3u"], check=True)
        subprocess.run(["git", "push"], check=True)
        logging.info("Git 提交并推送完成。")
    except subprocess.CalledProcessError as e:
        logging.warning("Git 操作失败：%s", e)

def main():
    # 日志初始化
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    filename = FILENAME

    # 每次运行前，删除旧的 playlist.m3u 文件（如果存在）
    if os.path.exists(filename):
        try:
            os.remove(filename)
        except OSError as e:
            logging.warning("删除旧文件失败：%s", e)

    logging.info("开始抓取节目源：%s", URL)
    m3u_text = fetch_webpage(URL)
    if not m3u_text:
        logging.error("节目源抓取失败，退出")
        return

    logging.info("解析节目源频道……")
    groups = parse_channels(m3u_text)
    if not groups:
        logging.error("无有效频道，退出")
        return

    logging.info("生成M3U文件……")
    save_m3u(groups, filename)

    # 提交并推送更改
    git_commit_and_push(filename)

if __name__ == '__main__':
    main()
