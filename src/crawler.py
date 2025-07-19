import requests
import re

url = "http://rihou.cc:555/gggg.nzk/"  # 替换为你的真实URL

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

def parse_m3u_content(text):
    """
    解析格式示例：
    #分组名
    #EXTINF:-1 group-title="分组名", 频道名
    url
    ...
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    current_group = None
    playlist = []

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('#') and not line.startswith('#EXTINF'):
            # 新分组名，比如 "#特闽 AKtv"
            current_group = line.lstrip('#').strip()
            i += 1
            continue
        elif line.startswith('#EXTINF'):
            # 解析EXTINF行的分组、频道名
            match = re.match(r'#EXTINF:-1 group-title="([^"]+)",\s*(.+)', line)
            if not match:
                print(f"无法解析行：{line}")
                i += 1
                continue
            group_title = match.group(1)
            channel_name = match.group(2)

            # 下一行是URL
            if i + 1 >= len(lines):
                print("缺少直播地址，跳过")
                break
            stream_url = lines[i + 1]

            # 优先用EXTINF的group-title，否则用当前分组名
            group = group_title if group_title else current_group

            playlist.append((group, channel_name, stream_url))
            i += 2
        else:
            # 其他行忽略
            i += 1

    return playlist

def save_playlist(items, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n\n")
        for group, channel_name, stream_url in items:
            f.write(f'#EXTINF:-1 group-title="{group}",{channel_name}\n')
            f.write(f'{stream_url}\n')

def main():
    html = fetch_webpage(url)
    if not html:
        print("获取网页失败")
        return

    playlist = parse_m3u_content(html)
    if not playlist:
        print("未找到任何直播源")
        return

    save_playlist(playlist, "playlist.m3u")
    print(f"成功写入 {len(playlist)} 条直播源到 playlist.m3u")

if __name__ == '__main__':
    main()
