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
    解析输入文本，根据节目源动态提取分组名。
    仅保留特定的频道，每个分组名不合并。
    """
    filter_keywords = ['肥羊', '咪咕']
    # 仅保留的频道名称
    valid_channels = [
        "CCTV", "凤凰", "中天", "寰宇", "东森",
        "无线", "RTHK", "TVBS", "江苏卫视",
        "东方卫视", "浙江卫视", "上海新闻", "财经"
    ]

    groups = {}

    parts = text.split('\n')
    for part in parts:
        part = part.strip()
        # 检查是否包含内容并且有逗号
        if not part or ',' not in part:
            continue
        
        channel_name, stream_url = part.split(',', 1)
        channel_name = channel_name.strip()
        stream_url = stream_url.strip()

        # 过滤掉包含禁止词的频道名和流地址
        if any(k in channel_name for k in filter_keywords):
            print(f"过滤频道名包含禁止词: {channel_name}")
            continue
        if any(k in stream_url for k in filter_keywords):
            print(f"过滤地址包含禁止词: {stream_url}")
            continue

        # 检查频道名是否在有效频道列表中
        if any(valid_channel in channel_name for valid_channel in valid_channels):
            # 提取分组名
            if "#" in channel_name:
                group_name = channel_name.split('#')[0].strip()  # 从频道名中提取分组名
            else:
                group_name = "其他"  # 如果没有分组名，给它一个默认分组
            
            # 将频道添加到对应的分组
            if group_name not in groups:
                groups[group_name] = []  # 创建新的分组
            groups[group_name].append((channel_name, stream_url))  # 添加到分组

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
    print("抓取内容：", html[:200], "...")  # 观察前200字符

    groups = parse_channels(html)
    if not groups or all(not v for v in groups.values()):
        print("解析后无有效节目，退出。")
        return

    save_m3u(groups, "playlist.m3u")

if __name__ == '__main__':
    main()
