import requests

url = "http://rihou.cc:555/gggg.nzk/"  # 请确保这个网址是有效的

def fetch_webpage(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = r.apparent_encoding
        r.raise_for_status()
        return r.text
    except Exception as e:
        print("请求失败：", e)
        return ""

def parse_channels(text):
    """
    解析输入文本，保留所有频道和节目链接。
    先全部读入，再过滤掉含“肥羊”的频道，如果组频道全被删，该组也删除。
    """
    groups = {}
    current_group = None

    # 按行解析文本，先全部保存
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        
        # 识别组行（带,且带#genre#）
        if ',' in line and '#genre#' in line:
            current_group = line.split(',', 1)[0].strip()
            if current_group not in groups:
                groups[current_group] = []
            continue
        
        # 组内频道行
        if current_group is not None and ',' in line:
            channel_name, stream_url = line.split(',', 1)
            channel_name = channel_name.strip()
            stream_url = stream_url.strip()
            groups[current_group].append((channel_name, stream_url))

    # 过滤操作：去除含“肥羊”的频道，空组删除
    filtered_groups = {}
    for group, channels in groups.items():
        filtered_channels = [
            (name, url) for (name, url) in channels
            if "肥羊" not in name and "肥羊" not in url
        ]
        if filtered_channels:
            filtered_groups[group] = filtered_channels

    return filtered_groups

def save_m3u(groups, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n\n")
        for group_name, channels in groups.items():
            if channels:
                f.write(f"#{group_name}\n")
                for channel_name, stream_url in channels:
                    f.write(f'#EXTINF:-1 group-title="{group_name}", {channel_name}\n')
                    f.write(stream_url + "\n")
    print(f"写入文件 {filename} 完成，节目总数：{sum(len(ch) for ch in groups.values())} 条。")

def main():
    print(f"开始抓取 URL: {url}")
    html = fetch_webpage(url)
    if not html:
        print("抓取失败，退出。")
        return

    groups = parse_channels(html)
    if not groups:
        print("解析后无有效节目，退出。")
        return

    save_m3u(groups, "playlist.m3u")

if __name__ == '__main__':
    main()
