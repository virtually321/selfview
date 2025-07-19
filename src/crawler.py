url = "http://rihou.cc:555/gggg.nzk/"

import requests

def fetch_webpage(url):
    try:
        r = requests.get(url, timeout=15)
        r.encoding = r.apparent_encoding
        r.raise_for_status()
        return r.text
    except Exception as e:
        print("请求失败：", e)
        return ""

def parse_channels(text):
    """
    解析你提供的格式：
    - 以空格分割多个频道信息
    - 每个频道信息以逗号分割为频道名和地址
    - 过滤频道名或地址中含“肥羊”“咪咕”的内容
    - 由于无明显分组，全部放一个默认分组“默认分组”
    """
    filter_keywords = ['肥羊', '咪咕']
    text = text.strip()
    # 先去掉可能的 #genre# 这类开头
    if text.startswith('#'):
        idx = text.find(' ')
        if idx != -1:
            text = text[idx:].strip()

    parts = text.split(' ')
    groups = {"默认分组": []}

    for part in parts:
        if ',' not in part:
            continue
        channel_name, stream_url = part.split(',', 1)
        if any(k in channel_name for k in filter_keywords):
            print(f"过滤频道名包含禁止词: {channel_name}")
            continue
        if any(k in stream_url for k in filter_keywords):
            print(f"过滤地址包含禁止词: {stream_url}")
            continue
        groups["默认分组"].append((channel_name.strip(), stream_url.strip()))
    return groups

def save_m3u(groups, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n\n")
        for group_name, channels in groups.items():
            f.write(f"#{group_name}\n")
            for channel_name, stream_url in channels:
                f.write(f'#EXTINF:-1 group-title="{group_name}",{channel_name}\n')
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
