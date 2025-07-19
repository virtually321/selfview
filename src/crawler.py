import requests
import re

url = "http://rihou.cc:555/gggg.nzk/"  # 你的链接

keywords = ['凤凰', '央视', 'cctv', '东森', '寰宇', '中天', '财经频道']

headers = {
    "User-Agent": "Mozilla/5.0",
}

def fetch_webpage(url):
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = resp.apparent_encoding
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def parse_playlist(text):
    """
    支持如下格式：
    - 分组行通常包含 "#genre#"，例如："欣赏频道,#genre#"
    - 分组名后面是若干(频道名, 直播地址)条目
    - 直播条目格式：频道名,直播地址
    - 连续读取直到遇到新的分组名或文件结尾    
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    group = "默认分组"
    playlist = []
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        # 判断是否是分组名行
        if '#genre#' in line:
            # 切出分组名称，例“欣赏频道,#genre#”取“欣赏频道”
            group = line.split(',')[0].strip()
            idx += 1
            continue

        # 解析直播条目，判断格式 "频道名,直播地址"
        parts = line.split(',', maxsplit=1)
        if len(parts) == 2:
            channel_name = parts[0].strip()
            stream_url = parts[1].strip()
        else:
            # 如果当前行不是直播条目格式，尝试和下一行合并，部分站流地址在下一行？
            if idx + 1 < len(lines):
                channel_name = line
                stream_url = lines[idx + 1]
                idx += 1
            else:
                # 无效数据跳过
                idx += 1
                continue

        # 关键词过滤
        if any(kw.lower() in channel_name.lower() for kw in keywords):
            playlist.append((group, channel_name, stream_url))
        idx += 1
    return playlist

def save_playlist(items, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n\n")
        last_group = None
        for group, channel_name, stream_url in items:
            if group != last_group:
                last_group = group
            # 写入带分组名的播放项格式
            f.write(f'#EXTINF:-1 group-title="{group}",{channel_name}\n')
            f.write(f'{stream_url}\n')

def main():
    html = fetch_webpage(url)
    if not html:
        print("获取网页失败")
        return

    playlist = parse_playlist(html)
    if not playlist:
        print("没有符合条件的直播源")
        return

    save_playlist(playlist, "playlist.m3u")
    print(f"共写入 {len(playlist)} 条直播源到 playlist.m3u")

if __name__ == '__main__':
    main()
