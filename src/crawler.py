#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
替代方案：从预设播放列表URL获取内容
生成统一 playlist.m3u
"""

import re
import pathlib
import requests

# 预设播放列表URL
PLAYLIST_URLS = [
    "http://example.com/path/to/playlist1.m3u",
    "http://example.com/path/to/playlist2.m3u",
    # 添加更多播放列表URL...
]

OUTPUT_FILE = pathlib.Path(__file__).resolve().parent.parent / "playlist.m3u"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}

# 关键字正则
PATTERNS = [
    r"CCTV[-\s]?\d{1,2}",  # CCTV-1 … CCTV-17
    r"(凤凰|Phoenix)",      # 凤凰
    r"(中天|CTi)",          # 中天
    r"(寰宇|Global)",       # 寰宇
    r"(东森|ETTV)"          # 东森
]
KEY_RE = re.compile("|".join(PATTERNS), re.I)

def fetch_playlist(url):
    """获取播放列表内容"""
    try:
        print(f"[FETCH] 获取播放列表: {url}")
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        return res.text
    except Exception as e:
        print(f"[ERROR] 获取播放列表失败: {e}")
        return None

def parse_m3u(content):
    """
    从播放列表文本提取 (group, name, url) 三元组
    """
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    results = []
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
                url = lines[i + 1].strip()
                if KEY_RE.search(group) or KEY_RE.search(name):
                    results.append((group, name, url))
                i += 1  # 跳过URL行
            i += 1
        else:
            i += 1
    return results

def main():
    all_items = []
    
    for url in PLAYLIST_URLS:
        content = fetch_playlist(url)
        if content:
            items = parse_m3u(content)
            all_items.extend(items)
            print(f"[INFO] 从 {url} 找到 {len(items)} 个频道")
    
    print(f"[INFO] 总共找到 {len(all_items)} 个电视频道")
    
    if all_items:
        # 生成播放列表内容
        lines = ["#EXTM3U"]
        seen = set()
        
        for group, name, url in all_items:
            key = (name, url)
            if key not in seen:
                seen.add(key)
                lines.append(f'#EXTINF:-1 group-title="{group}", {name}')
                lines.append(url)
        
        playlist_text = "\n".join(lines) + "\n"
        OUTPUT_FILE.write_text(playlist_text, encoding="utf-8")
        print(f"[SUCCESS] 播放列表已保存至: {OUTPUT_FILE}")
    else:
        print("[WARNING] 未找到任何电视频道，跳过文件写入")

if __name__ == "__main__":
    main()
