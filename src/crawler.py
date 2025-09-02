import requests
import os
import subprocess

url = "http://rihou.cc:555/gggg.nzk/"  # 节目源地址

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
    groups = {}
    current_group = None

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # 识别组行（带,且带#genre#）
        if ',' in line and '#genre#' in line:
            current_group = line.split(',', 1)[0].strip()
            groups.setdefault(current_group, [])
            continue
        # 频道行
        if current_group and ',' in line:
            channel_name, stream_url = line.split(',', 1)
            channel_name = channel_name.strip()
            stream_url = stream_url.strip()
            if "肥羊" not in channel_name and "肥羊" not in stream_url:
                groups[current_group].append((channel_name, stream_url))

    return {g: chs for g, chs in groups.items() if chs}

def save_m3u(groups, filename):
    """生成M3U文件，组名保留，组内写频道"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n\n')
        for group, channels in groups.items():
            if not channels:
                continue
            f.write(f"#{group}\n")
            for channel_name, stream_url in channels:
                f.write(f'#EXTINF:-1 group-title="{group}", {channel_name}\n')
                f.write(stream_url + "\n")
    total = sum(len(ch) for ch in groups.values())
    print(f"写入文件 {filename} 完成，节目总数：{total} 条。")

def git_commit_and_push(filename):
    """将文件添加到 Git，并提交和推送更改"""
    subprocess.run(["git", "add", filename])
    subprocess.run(["git", "commit", "-m", "更新 playlist.m3u"])
    subprocess.run(["git", "push"])

def main():
    filename = "playlist.m3u"
    
    # 每次运行前，删除旧的 playlist.m3u 文件（如果存在）
    if os.path.exists(filename):
        os.remove(filename)
    
    print(f"开始抓取节目源：{url}")
    m3u_text = fetch_webpage(url)
    if not m3u_text:
        print("节目源抓取失败，退出")
        return

    print("解析节目源频道……")
    groups = parse_channels(m3u_text)
    if not groups:
        print("无有效频道，退出")
        return

    print("生成M3U文件……")
    save_m3u(groups, filename)
    
    # 提交并推送更改
    git_commit_and_push(filename)

if __name__ == '__main__':
    main()
