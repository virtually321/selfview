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
    """
    groups = {}
    current_group = None

    # 按行解析文本
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        
        if ',' in line and '#genre#' in line:
            current_group = line.split(',', 1)[0].strip()
            if current_group not in groups:
                groups[current_group] = []
            continue
        
        if current_group is not None and ',' in line:
            channel_name, stream_url = line.split(',', 1)
            channel_name = channel_name.strip()
            stream_url = stream_url.strip()
            # 不做任何过滤，直接添加所有节目
            groups[current_group].append((channel_name, stream_url))

    return groups

def save_m3u(groups, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n\n")
        for group_name, channels in groups.items():
            if channels:
                f.write(f"#{group_name}\n")
                for channel_name, stream_url in channels:
                    f.write(f'#EXTINF:-1 group-title="{group_name}", {channel_name}\n')
                    f.write(stream_url + "\n")
    print(f"写入文件 {filename} 完成，{sum(len(v) for v in groups.values())} 条节目。")

def main():
    print(f"开始抓取 URL: {url}")
    html = fetch_webpage(url)
    if not html:
        print("抓取失败，退出。")
        return

    groups = parse_channels(html)
    if not groups or all(not v for v in groups.values()):
        print("解析后无有效节目，退出。")
        return

    save_m3u(groups, "playlist.m3u")

if __name__ == '__main__':
    main()
