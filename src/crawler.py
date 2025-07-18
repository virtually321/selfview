#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬取 http://rihou.cc:555/gggg.nzk/ 中的 m3u / m3u8，
保留源文件里的 group-title，筛出 CCTV、凤凰、中天、寰宇、东森，
生成统一 playlist.m3u
"""

#!/usr/bin/env python3
"""
通用爬虫示例
- 默认抓取 https://httpbin.org/get 做连通性测试
- 可通过环境变量 TARGET_URL 指定真正要抓的站点
- 支持 HTTP(S)_PROXY 环境变量
"""

import os
import sys
import time
import logging
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# -------------------- 日志配置 --------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("crawler")

# -------------------- 参数读取 --------------------
TARGET_URL: str = os.getenv("TARGET_URL", "https://httpbin.org/get")
PROXIES: dict[str, str] = {
    "http": os.getenv("HTTP_PROXY", ""),
    "https": os.getenv("HTTPS_PROXY", ""),
}
# 去掉空字符串，避免 requests 把 "" 当成代理地址
PROXIES = {k: v for k, v in PROXIES.items() if v}

# -------------------- 会话初始化 --------------------
session = requests.Session()
session.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (compatible; SelfViewBot/1.0; +https://github.com/yourname/selfview)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.
