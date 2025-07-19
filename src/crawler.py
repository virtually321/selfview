import requests
import re

url = "http://rihou.cc:555/gggg.nzk/"  # 替换为你的URL

keywords = ['凤凰', '央视', 'cctv', '东森', '寰宇', '中天', '财经频道']

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

def split_entries(text):
    """
    依据换行符或空白符拆分文本成条目。
    优先尝试按换行拆分，不多于1/3空行则认为是换行式，
    否则按空白符拆分。
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    empty_line_count = text.count('\n\n')
    if empty_line_count < len(lines) / 3:
        # 换行格式为主
        return lines
    else:
        # 空白分割为主
        return re.split(r'\s+', text.strip())

def parse_entry(entry):
    """
    从一条记录提取频道名和流地址。
    规则：
    - 频道名+URL之间至少有一个逗号
    - URL通常是 http 或 https 开头，可用URL开头分割
    - 尝试用URL分割，避免频道名中出现逗号导致切割错误
    """
    # 查找URL位置
    url_match = re.search(r'(https?://[^\s]+)', entry)
    if not url_match:
        return None
    stream_url = url_match.group(1)

    # 频道名 = entry中，去掉流地址部分(及其前面的逗号)
    name_part = entry[:url_match.start()].rstrip(', ').strip()

    if not name_part or not stream_url:
        return None

    return name_part, stream_url

def filter_items(items, keywords):
    filtered = []
    for name, url in items:
        if any(kw.lower() in name.lower() for kw in keywords):
            filtered.append((name, url))
    return filtered

def save_playlist(items, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n\n")
        for name, url in items:
            f.write(f'#EXTINF:-1,{name}\n')
            f.write(f'{url}\n')

def main():
    html = fetch_webpage(url)
    if not html:
        print("无法获取网页内容")
        return

    entries = split_entries(html)
    print(f"拆分得到 {len(entries)} 条条目")

    parsed_items = []
    for e in entries:
        r = parse_entry(e)
        if r:
            parsed_items.append(r)
        else:
            print(f"未能解析条目: {e}")

    if not parsed_items:
        print("没有有效直播源")
        return

    filtered = filter_items(parsed_items, keywords)

    if not filtered:
        print("筛选后无匹配的直播源")
        return

    save_playlist(filtered, "playlist.m3u")
    print(f"成功写入 {len(filtered)} 条直播源到 playlist.m3u")

if __name__ == '__main__':
    main()
