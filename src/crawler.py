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
    只保留 .m3u8 格式的节目源。
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
        
        # 检查是否是分组名行，格式如 "央卫咪咕,#genre#"
        if ',' in line and '#genre#' in line:
            current_group = line.split(',')[0].strip()  # 获取分组名
            if current_group not in groups:
                groups[current_group] = []  # 初始化分组
            continue
        
        # 检查是否是节目行
        if current_group is not None:  # 有分组时才处理节目行
            if ',' in line:
                channel_name, stream_url = line.split(',', 1)
                channel_name = channel_name.strip()
                stream_url = stream_url.strip()
                
                # 过滤掉包含禁止词的频道名和流地址
                if any(k in channel_name for k in filter_keywords):
                    print(f"过滤频道名包含禁止词: {channel_name}")
                    continue
                if any(k in stream_url for k in filter_keywords):
                    print(f"过滤地址包含禁止词: {stream_url}")
                    continue

                # 检查流地址是否是 .m3u8 格式，且不以 tvbus:// 开头
                if not stream_url.endswith('.m3u8') or stream_url.startswith('tvbus://'):
                    print(f"过滤非 .m3u8 或以 tvbus:// 地址: {stream_url}")
                    continue

                # 只在频道名有效时才添加
                if any(valid_channel in channel_name for valid_channel in valid_channels):
                    # 将频道添加到当前分组中
                    groups[current_group].append((channel_name, stream_url))

    return groups

def save_m3u(groups, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n\n")
        for group_name, channels in groups.items():
            if channels:  # 只在分组不为空时写入
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
    if not groups or all(not v for v in groups.values()):
        print("解析后无有效节目，退出。")
        return

    save_m3u(groups, "playlist.m3u")

if __name__ == '__main__':
    main()
