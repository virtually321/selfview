import requests
import re

url = "http://rihou.cc:555/gggg.nzk/"

keywords = ['凤凰', '央视', 'cctv', '东森', '寰宇', '中天', '财经频道']

headers = {
    "User-Agent": "Mozilla/5.0",
}

def fetch_webpage(url):
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def parse_sources(html_text):
    pattern = re.compile(r'#EXTINF:-1\s+group-title="([^"]+)"\s*,\s*([^\n]+)\n(.+?m3u8?)', re.IGNORECASE)
    results = pattern.findall(html_text)

    filtered_list = []

    for group_title, channel_name, stream_url in results:
        if any(kw.lower() in channel_name.lower() for kw in keywords):
            filtered_list.append((group_title.strip(), channel_name.strip(), stream_url.strip()))

    return filtered_list

def save_playlist(sources, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")

        last_group = None
        for group_title, channel_name, stream_url in sources:
            if group_title != last_group:
                f.write(f"#{group_title}\n")
                last_group = group_title

            f.write(f'#EXTINF:-1 group-title="{group_title}", {channel_name}\n')
            f.write(f"{stream_url}\n")

def main():
    html = fetch_webpage(url)
    if not html:
        print("获取网页失败，退出")
        return

    sources = parse_sources(html)
    if not sources:
        print("没有找到匹配的直播源")
        return

    save_playlist(sources, "playlist.m3u")
    print(f"成功写入 {len(sources)} 条直播源到 playlist.m3u")

if __name__ == '__main__':
    main()
