#!/usr/bin/env python3
"""
占位爬虫：确保 CI 可通过 DNS + HTTPS 请求
默认抓取 httpbin.org，
后续把 URL 换成真实域名即可。
"""
import os
import sys
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("crawler")

def main() -> None:
    # 1. 可手动通过环境变量覆盖
    target = os.getenv("TARGET_URL", "https://httpbin.org/get")
    log.info("准备抓取: %s", target)

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        resp = session.get(target, timeout=10)
        resp.raise_for_status()
        log.info("成功抓取 %d bytes", len(resp.text))
        log.info("前 200 字符：\n%s", resp.text[:200])
    except requests.exceptions.RequestException as e:
        log.error("抓取失败：%s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
