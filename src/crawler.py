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
    filter_keywords = ["肥羊", "咪咕"]
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    groups = dict()
    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("#") and not line.startswith("#EXTINF"):
            current_group = line.lstrip("#").strip()
            if current_group not in groups:
                groups[current_group] = []
            i += 1
            continue

        if line.startswith("#EXTINF"):
            m = re.match(r'#EXTINF:-1 group-title="([^"]+)",\s*(.+)', line)
            if not m:
                i += 1
                continue
            group_title = m.group(1).strip()
            channel_name = m.group(2).strip()
            if i + 1 >= len(lines):
                break
            stream_url = lines[i + 1]

            if any(keyword in channel_name for keyword in filter_keywords):
                print(f"过滤掉频道: {channel_name} （关键词匹配）")
                i += 2
                continue
            if any(keyword in stream_url for keyword in filter_keywords):
                print(f"过滤掉链接: {stream_url} （关键词匹配）")
                i += 2
                continue

            if group_title not in groups:
                groups[group_title] = []
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
            # 先输出分组名行 -- 这就是你需要的那个“在第一行添加分组名”
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
