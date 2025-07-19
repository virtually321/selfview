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
    解析输入文本，根据组名和节目链接归类频道。
    只保留 .m3u8 和 .flv 格式的节目源。
    """
    filter_keywords = ['肥羊', '咪咕']  # 需过滤的关键字
    valid_channels = [
        "CCTV", "凤凰", "中天", "寰宇", "东森", "无线",
        "RTHK", "TVBS", "江苏卫视", "东方卫视", "浙江卫视",
        "上海新闻", "财经", "新闻", "综艺", "娱乐"  # 你可添加更多的频道名称
    ]
    
    groups = {}
    current_group = None

    # 按行解析文本
    for line in text.splitlines():
        line = line.strip()
        # 跳过空行
        if not line:
            continue
        
        # 检查是否是分组名行，以 # 开头，并且不包含 EXTINF
        if line.startswith("#") and not line.startswith("#EXTINF"):
            current_group = line[1:].strip()  # 获取分组名
            if current_group not in groups:
                groups[current_group] = []  # 初始化分组
            continue
        
        # 检查是否是节目行
        if current_group is not None:  # 只有在有分组的情况下才处理节目行
            if line.startswith("#EXTINF:"):
                parts = line.split(",")
                if len(parts) < 2:
                    continue  # 如果没有有效的频道名称则跳过
                channel_name = parts[1].strip()
                
                # 获取下一个非空行作为流地址
                stream_url_line = next((next_line.strip() for next_line in text.splitlines() 
                                         if next_line.strip() and not next_line.startswith("#")), None)

                # 过滤掉包含禁止词的频道名和流地址
                if any(k in channel_name for k in filter_keywords):
                    print(f"过滤频道名包含禁止词: {channel_name}")
                    continue
                if stream_url_line and any(k in stream_url_line for k in filter_keywords):
                    print(f"过滤地址包含禁止词: {stream_url_line}")
                    continue

                # 检查流地址是否是 .m3u8 或 .flv 格式
                if not (stream_url_line.endswith('.m3u8') or stream_url_line.endswith('.flv')):
                    print(f"过滤非 .m3u8 或非 .flv 地址: {stream_url_line}")
                    continue

                # 只在频道名有效时才添加
                if any(valid_channel in channel_name for valid_channel in valid_channels):
                    # 将频道添加到当前分组中
                    groups[current_group].append((channel_name, stream_url_line))

    # 删除空节目组
    groups = {group: channels for group, channels in groups.items() if channels}

    return groups

def save_m3u(groups, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n\n")
        for group_name, channels in groups.items():
            f.write(f"#{group_name}\n")  # 输出分组名
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
    if not groups:
        print("解析后无有效节目，退出。")
        return

    save_m3u(groups, "playlist.m3u8")

if __name__ == '__main__':
    main()
