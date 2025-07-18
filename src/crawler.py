#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时抓取 http://rihou.cc:555/gggg.nzk/ 下的 m3u/m3u8 链接，
筛选 CCTV、凤凰、中天、寰宇、东森相关地址，生成 playlist.m3u
"""
import re
import sys
import pathlib
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# ------------------ 可自行调整 ------------------
ROOT_URL = "http://rihou.cc:555/gggg.nzk/"
OUTPUT_FILE = pathlib.Path(__file__).resolve().parent.parent / "playlist.m3u"
GROUP_TITLE = "特闽 AKtv"
TIMEOUT = 10
HEADERS = {"User-Agent": "Mozilla/5.0 (PlaylistBot)"}
# ------------------------------------------------

# 频道关键字，用于判断 title，如果想要更多频道自行扩充
KEYWORDS = {
    "CCTV": r"CCTV[-\s]?\d{1,2}",
    "凤凰": r"(凤凰|Phoenix)",
    "中天": r"(中天|CTi)",
    "寰宇": r"(寰宇|Global)",
    "东森": r"(东森|ETTV)",
}

def fetch(url):
    """下载网页，返回 str"""
    res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    res.raise_for_status()
    res.encoding = res.apparent_encoding
    return res.text

def discover_links(html, base):
    """从 html 中挖掘 href 链接并返回绝对地址"""
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        abs_url = urljoin(base, href)
        yield abs_url

def is_playlist(url):
    return url.lower().endswith((".m3u", ".m3u8"))

def classify_channel(text):
    """根据关键字匹配频道名，返回合适的 display name"""
    for k, pattern in KEYWORDS.items():
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(0).upper() if k == "CCTV" else m.group(0)
    return None

def crawl():
    visited = set()
    playlists = {}

    def dfs(url):
        if url in visited or len(visited) > 3000:  # 防炸站
            return
        visited.add(url)

        try:
            html = fetch(url)
        except Exception as e:
            print(f"[WARN] {url} => {e}", file=sys.stderr)
            return

        # 先提取当前页的播放列表
        for link in re.findall(r"http[^\"'<> ]+\.(?:m3u8?)", html, re.I):
            ch_name = classify_channel(link)
            if ch_name:
                playlists.setdefault(ch_name, link)

        # 再递归子链接
        for link in discover_links(html, url):
            # 同域名/同目录才继续
            if urlparse(link).netloc == urlparse(ROOT_URL).netloc:
                if is_playlist(link):
                    ch_name = classify_channel(link)
                    if ch_name:
                        playlists.setdefault(ch_name, link)
                else:
                    dfs(link)

    dfs(ROOT_URL)
    return playlists

def generate_m3u(playlists: dict):
    lines = ["#EXTM3U"]
    for ch_name in sorted(playlists.keys()):
        url = playlists[ch_name]
        # 统一『央视1套』之类命名：CCTV-1
        ch_display = ch_name.replace(" ", "").replace("CCTV-", "CCTV")
        line_info = f'#EXTINF:-1 group-title="{GROUP_TITLE}", {ch_display} AKtv'
        lines.append(line_info)
        lines.append(url)
    return "\n".join(lines) + "\n"

def main():
    print("[INFO] Start crawling...")
    data = crawl()
    print(f"[INFO] Got {len(data)} channels")
    content = generate_m3u(data)
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"[INFO] Write to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
