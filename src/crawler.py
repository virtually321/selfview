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

# 使用正确的目标网址
ROOT_URL = "http://rihou.cc:555/gggg.nzk/"
OUTPUT_FILE = pathlib.Path(__file__).resolve().parent.parent / "playlist.m3u"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Referer': ROOT_URL,
}
TIMEOUT = 10

# 关键字正则
PATTERNS = [
    r"CCTV[-\s]?\d{1,2}",  # CCTV-1 … CCTV-17
    r"(凤凰|Phoenix)",      # 凤凰
    r"(中天|CTi)",          # 中天
    r"(寰宇|Global)",       # 寰宇
    r"(东森|ETTV)"          # 东森
]
KEY_RE = re.compile("|".join(PATTERNS), re.I)

def fetch(url):
    """获取URL内容，自动处理编码"""
    try:
        res = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        return res.text
    except Exception as e:
        print(f"[ERROR] 获取 {url} 失败: {e}")
        return None

def discover_links(html, base):
    """从HTML中发现所有链接"""
    if not html:
        return
        
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href and not href.startswith(("javascript:", "mailto:", "#")):
            yield urljoin(base, href)

def is_playlist(url):
    """检查是否是播放列表文件"""
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
                i += 1  # 跳过URL行
            i += 1
        else:
            i += 1

def crawl():
    visited_html = set()
    done_playlist = set()
    results = []  # [(group, name, url), …]
    print(f"[INFO] 开始爬取: {ROOT_URL}")

    def dfs(url):
        if url in visited_html:
            return
        visited_html.add(url)
        print(f"[DEBUG] 访问: {url}")

        html = fetch(url)
        if not html:
            return

        # 在当前HTML中查找.m3u/.m3u8链接
        for link in re.findall(r"https?://[^\"'<> ]+\.m3u8?", html, re.I):
            if link not in done_playlist:
                print(f"[DEBUG] 发现播放列表: {link}")
                handle_playlist_link(link)

        # 递归处理子页面
        for link in discover_links(html, url):
            if is_playlist(link):
                if link not in done_playlist:
                    print(f"[DEBUG] 发现播放列表: {link}")
                    handle_playlist_link(link)
            else:
                # 只处理相同域名的链接
                if urlparse(link).netloc == urlparse(ROOT_URL).netloc:
                    dfs(link)

    def handle_playlist_link(link):
        done_playlist.add(link)
        print(f"[INFO] 处理播放列表: {link}")
        content = fetch(link)
        if not content:
            return

        # 解析播放列表内容
        if "#EXTINF" in content:
            for group, name, stream in parse_m3u(content):
                if KEY_RE.search(group) or KEY_RE.search(name):
                    results.append((group, name, stream))
                    print(f"[ADD] 添加频道: {group} - {name}")
        else:
            # 直接流：尝试用URL判断
            if KEY_RE.search(link):
                name = link.rsplit("/", 1)[-1]
                results.append(("直接流", name, link))
                print(f"[ADD] 添加直接流: {name}")

    try:
        dfs(ROOT_URL)
    except KeyboardInterrupt:
        print("[WARN] 用户中断爬取")
    return results

def generate_m3u(items):
    """生成M3U播放列表"""
    lines = ["#EXTM3U"]
    seen = set()  # 防止重复 (name,url)

    for group, name, url in items:
        key = (name, url)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f'#EXTINF:-1 group-title="{group}", {name}')
        lines.append(url)

    return "\n".join(lines) + "\n"

def main():
    print("[INFO] 开始爬取过程...")
    items = crawl()
    print(f"[INFO] 找到 {len(items)} 个电视频道")
    
    if items:
        playlist_text = generate_m3u(items)
        OUTPUT_FILE.write_text(playlist_text, encoding="utf-8")
        print(f"[SUCCESS] 播放列表已保存至: {OUTPUT_FILE}")
    else:
        print("[WARNING] 未找到任何电视频道，跳过文件写入")

if __name__ == "__main__":
    main()
