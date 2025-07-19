import requests
import re

url = "http://rihou.cc:555/gggg.nzk/"  # 替换为你的URL

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

def parse_and_group(text):
    """
    解析文本，结构化为：
    {
        "分组名1": [
            (频道名, 流地址),
            ...
        ],
        "分组名2": [
            ...
        ],
        ...
    }
    假设格式是：
    #分组名
    #EXTINF:-1 group-title="分组名", 频道名
    流地址
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    current_group = None
    groups = dict()

    i = 0
    while i < len(lines):
        line = lines[i]

        # 识别分组名行 (以#开头但不是#EXTINF)
        if line.startswith('#') and not line.startswith('#EXTINF'):
            current_group = line.lstrip('#').strip()
            if current_group not in groups:
                groups[current_group] = []
            i += 1
            continue

        # 识别节目行
        if line.startswith('#EXTINF'):
            # 正则提取group-title和频道名
            m = re.match(r'#EXTINF:-1 group-title="([^"]+)",\s*(.+)', line)
            if not m:
                print(f"无法解析EXTINF行: {line}")
                i += 1
                continue
            group_title = m.group(1).strip()
            channel_name = m.group(2).strip()

            if i + 1 >= len(lines):
                print("直播地址缺失，跳过")
                break
            stream_url = lines[i+1]

            # 通常group_title应与上面current_group一致，若不一致，也以group_title为准
            if group_title not in groups:
                groups[group_title] = []

            groups[group_title].append((channel_name, stream_url))
            i += 2
            continue

        # 其他行跳过
        i += 1

    return groups

def save_with_group_line(groups, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n\n")
        for group, channels in groups.items():
            # 写分组名行
            f.write(f"#{group}\n")
            for channel_name, stream_url in channels:
                f.write(f'#EXTINF:-1 group-title="{group}",{channel_name}\n')
                f.write(f'{stream_url}\n')

def main():
    html = fetch_webpage(url)
    if not html:
        print("获取网页失败")
        return

    groups = parse_and_group(html)
    if not groups:
        print("没有解析到任何分组和节目")
        return

    save_with_group_line(groups, "playlist.m3u")
    print(f"已写入 {sum(len(v) for v in groups.values())} 条节目到 playlist.m3u")

if __name__ == "__main__":
    main()
