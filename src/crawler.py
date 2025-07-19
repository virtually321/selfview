import requests
import re

url = "http://rihou.cc:555/gggg.nzk/"

# 筛选关键词
keywords = ['凤凰', '央视', 'cctv', '东森', '寰宇', '中天', '财经频道']

headers = {
    "User-Agent": "Mozilla/5.0",
}

def fetch_webpage(url):
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def parse_sources(html_text):
    """
    解析示例：

    假设文本里有m3u格式内容，比如：
    #EXTINF:-1 group-title="央卫湖北", 凤凰中文
    http://live.sxrtv.com/iptv/fhzw.m3u8

    正则抽取 group-title, 频道名 和 后面 URL

    """
    # 匹配 #EXTINF:-1 group-title="分组", 频道名 \n url
    pattern = re.compile(r'#EXTINF:-1\s+group-title="([^"]+)"\s*,\s*([^\n]+)\n(.+?m3u8?)', re.IGNORECASE)

    results = pattern.findall(html_text)

    filtered_list = []

    for group_title, channel_name, stream_url in results:
        # 关键词筛选
        if any(kw.lower() in channel_name.lower() for kw in keywords):
            filtered_list.append((group_title.strip(), channel_name.strip(), stream_url.strip()))

    return filtered_list

def save_playlist(sources, filename):
    """
    根据分组写文件，分组前加 #分组名换行
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")

        last_group = None

        for group_title, channel_name, stream_url in sources:
            if group_title != last_group:
                # 新分组，写分组行
                f.write(f"#{group_title}\n")
                last_group = group_title

            f.write(f'#EXTINF:-1 group-title="{group_title}", {channel_name}\n')
            f.write(f"{stream_url}\n")

def main():
    html = fetch_webpage(url)
    if not html:
        return

    sources = parse_sources(html)

    if not sources:
        print("未找到符合条件的直播源")
        return

    save_playlist(sources, "playlist.m3u")
    print(f"成功写入 {len(sources)} 条直播源到 playlist.m3u")

if __name__ == '__main__':
    main()
