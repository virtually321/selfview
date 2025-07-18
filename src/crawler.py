#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬取 http://rihou.cc:555/gggg.nzk/ 中的 m3u / m3u8，
保留源文件里的 group-title，筛出 CCTV、凤凰、中天、寰宇、东森，
生成统一 playlist.m3u
"""

import re
import sys
import pathlib
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ROOT_URL = "http://rihou.cc:555/gggg.nzk/"
OUTPUT_FILE = pathlib.Path(__file__).resolve().parent.parent / "playlist.m3u"
HEADERS = {"User-Agent": "Mozilla/5.0 (PlaylistBot)"}
TIMEOUT = 10

# 关键字正则
PATTERNS = [
    r"CCTV[-\s]?\d{1,2}",          # CCTV-1 … CCTV-17
    r"(凤凰|Phoenix)",             # 凤凰
    r"(中天|CTi)",                 # 中天
    r"(寰宇|Global)",              # 寰宇
    r"(东森|ETTV)"                 # 东森
]
KEY_RE = re.compile("|".join(PATTERNS), re.I)

def fetch(url):
    res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    res.raise_for_status()
    res.encoding = res.apparent_encoding
    return res.text

def discover_links(html, base):
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        yield urljoin(base, a["href"].strip())

def is_playlist(url):
    return url.lower().endswith((".m3u", ".m3u8"))

def parse_m3u(content):
    """
    从播放列表文本提取 (group, name, url) 三元组
    """
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF"):
            # 解析 group-title
            m_group = re.search(r'group-title="([^"]+)"', line, re.I)
            group = m_group.group(1).strip() if m_group else "未知分组"
            # 解析频道显示名
            name = line.split(",", 1)[-1].strip()
            # 下一行是真实链接
            if i + 1 < len(lines) and not lines[i + 1].startswith("#"):
                url = lines[i + 1]
                yield group, name, url
            i += 2
        else:
            i += 1

def crawl():
    visited_html = set()
    done_playlist = set()
    results = []                           # [(group, name, url), …]

    def dfs(url):
        if url in visited_html:
            return
        visited_html.add(url)

        try:
            html = fetch(url)
        except Exception as e:
            print(f"[WARN] {url} -> {e}", file=sys.stderr)
            return

        # 在当前 HTML 里先找 *.m3u8? 直接文字出现（不少网页直接列出来）
        for link in re.findall(r"http[^\"'<> ]+\.m3u8?", html, re.I):
            if link not in done_playlist:
                handle_playlist_link(link)

        # 再递归子页面
        for link in discover_links(html, url):
            if is_playlist(link):
                if link not in done_playlist:
                    handle_playlist_link(link)
            else:
                if urlparse(link).netloc == urlparse(ROOT_URL).netloc:
                    dfs(link)

    def handle_playlist_link(link):
        done_playlist.add(link)
        try:
            txt = fetch(link)
        except Exception as e:
            print(f"[WARN] playlist {link} -> {e}", file=sys.stderr)
            return

        # 如果文件里包含 #EXTINF 就按列表解析，否则当作单串流
        if "#EXTINF" in txt:
            for group, name, stream in parse_m3u(txt):
                if KEY_RE.search(group) or KEY_RE.search(name):
                    results.append((group, name, stream))
        else:
            # 直接流：尝试用 url 判断
            if KEY_RE.search(link):
                # 用文件名当频道名
                name = link.rsplit("/", 1)[-1]
                results.append(("未知分组", name, link))

    dfs(ROOT_URL)
    return results

def generate_m3u(items):
    """
    items: [(group, name, url), …]
    """
    lines = ["#EXTM3U"]
    seen = set()        # 防止重复 (name,url)

    for group, name, url in items:
        key = (name, url)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f'#EXTINF:-1 group-title="{group}", {name}')
        lines.append(url)

    return "\n".join(lines) + "\n"

def main():
    print("[INFO] Crawling…")
    items = crawl()
    print(f"[INFO] 收到 {len(items)} 条流")
    playlist_text = generate_m3u(items)
    OUTPUT_FILE.write_text(playlist_text, encoding="utf-8")
    print(f"[INFO] 写入 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
