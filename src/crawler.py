import requests
import re

url = "http://rihou.cc:555/gggg.nzk/"  # 替换成你的地址

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
    解析文本，格式示例：
    #分组名
    #EXTINF:-1 group-title="分组名", 频道名
    直播地址
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    groups = dict()
    current_group = None
    i = 0
    while i < len(lines):
        line = lines[i]

        # 分组名行，必须 # 开头且不是 #EXTINF，否则跳过
        if line.startswith("#") and not line.startswith("#EXTINF"):
            current_group = line.lstrip("#").strip()
            print(f"解析到分组：{current_group}")
            if current_group not in groups:
                groups[current_group] = []
            i += 1
            continue

        # 解析节目 #EXTINF
        if line.startswith("#EXTINF"):
            m = re.match(r'#EXTINF:-1 group-title="([^"]+)",\s*(.+)', line)
            if not m:
                print(f"警告：无法解析EXTINF行: {line}")
                i += 1
                continue
            group_title = m.group(1).strip()
            channel_name = m.group(2).strip()

            if i + 1 >= len(lines):
                print("错误：直播地址缺失，跳过节目")
                break
            stream_url = lines[i + 1]

            # 按照 #EXTINF 中的 group-title 分组，会覆盖当前分组
            if group_title not in groups:
                groups[group_title] = []

            print(f"  添加节目: 分组={group_title}, 频道={channel_name}")

            groups[group_title].append((channel_name, stream_url))
            i += 2
            continue

        i += 1

    return groups

def save_with_group_line(groups, filename):
    total_count = sum(len(v) for v in groups.values())
    print(f"开始写入文件 {filename}，共 {total_count} 个节目，{len(groups)} 个分组")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        for group in groups:
            f.write(f"#{group}\n")
            for (channel_name, stream_url) in groups[group]:
                f.write(f'#EXTINF:-1 group-title="{group}",{channel_name}\n')
                f.write(f"{stream_url}\n")
    print("写入完成！")

def main():
    print(f"开始抓取 URL: {url}")
    html = fetch_webpage(url)
    if not html:
        print("抓取失败，程序退出")
        return

    print("抓取成功，开始解析")
    groups = parse_and_group(html)

    if not groups:
        print("未解析出任何分组和节目，程序退出")
        return

    save_with_group_line(groups, "playlist.m3u")

if __name__ == "__main__":
    main()
