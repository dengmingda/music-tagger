#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Music Tagger - 一个自动获取并写入音乐元数据的工具
支持平台：网易云音乐、QQ音乐
支持格式：MP3, FLAC, Opus
"""
import sys
import requests
import re
import json
import os
import base64
import html
import datetime
from mutagen.flac import FLAC, Picture
from mutagen.oggopus import OggOpus
from mutagen.mp3 import MP3
from mutagen import id3

# 颜色和图标
SUCCESS = "\033[1;32m\U0001F60A "
ERROR = "\033[1;31m\u274c "
INFO = "\033[1;34m\u2139\ufe0f "
RESET = "\033[0m"

def get_netease_data(song_id):
    headers = {'User-Agent': 'Mozilla/5.0'}
    detail = requests.get(f"https://music.163.com/api/song/detail/?id={song_id}&ids=[{song_id}]", headers=headers).json()
    lrc_data = requests.get(f"https://music.163.com/api/song/media?id={song_id}", headers=headers).json()
    
    if not detail.get('songs'): return None
    song = detail['songs'][0]
    
    # 格式化具体日期
    pub_time = song['album'].get('publishTime', 0)
    release_date = datetime.datetime.fromtimestamp(pub_time/1000).strftime('%Y-%m-%d') if pub_time > 0 else ""
    
    return {
        'title': song['name'],
        'artist': song['artists'][0]['name'],
        'album': song['album']['name'],
        'cover_url': song['album']['picUrl'] + "?param=800z800",
        'date': release_date,
        'track': str(song.get('no', '1')),
        'genre': "Pop",
        'lyric': lrc_data.get('lyric', '')
    }

def get_qq_data(song_mid):
    api_url = f"https://u.y.qq.com/cgi-bin/musicu.fcg?data=%7B%22songinfo%22%3A%7B%22method%22%3A%22get_song_detail_yqq%22%2C%22module%22%3A%22music.pf_song_detail_svr%22%2C%22param%22%3A%7B%22song_mid%22%3A%22{song_mid}%22%7D%7D%7D"
    headers = {'Referer': 'https://y.qq.com/', 'User-Agent': 'Mozilla/5.0'}
    detail = requests.get(api_url, headers=headers).json()
    
    try:
        info = detail['songinfo']['data']['track_info']
        album_mid = info['album']['mid']
        # 获取歌词
        lrc_resp = requests.get("https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg", 
                               params={'songmid': song_mid, 'format': 'json', 'nobase64': 1, 'callback': 'getMusicLyric'}, headers=headers)
        lyric_json = json.loads(lrc_resp.text.replace('getMusicLyric(', '').rstrip(')'))
        
        return {
            'title': info['name'],
            'artist': info['singer'][0]['name'],
            'album': info['album']['name'],
            'cover_url': f"https://y.gtimg.cn/music/photo_new/T002R800x800M000{album_mid}.jpg",
            'date': info['album'].get('time_public', ''), # 已经是 YYYY-MM-DD
            'track': str(info['index_album']),
            'genre': info.get('genre', 'Pop'),
            'lyric': html.unescape(lyric_json.get('lyric', ''))
        }
    except: return None

def write_meta(file_path, meta):
    ext = os.path.splitext(file_path)[1].lower()
    img_data = requests.get(meta['cover_url']).content
    fields = {k: str(v) for k, v in meta.items() if k != 'cover_url'}

    if ext == '.mp3':
        audio = MP3(file_path, ID3=id3.ID3)
        try: audio.add_tags()
        except: pass
        audio.tags.add(id3.TIT2(encoding=3, text=fields['title']))
        audio.tags.add(id3.TPE1(encoding=3, text=fields['artist']))
        audio.tags.add(id3.TPE2(encoding=3, text=fields['artist'])) # 专辑艺术家
        audio.tags.add(id3.TCOM(encoding=3, text=fields['artist'])) # 作曲家
        audio.tags.add(id3.TALB(encoding=3, text=fields['album']))
        audio.tags.add(id3.TDRC(encoding=3, text=fields['date']))   # 具体日期
        audio.tags.add(id3.TRCK(encoding=3, text=fields['track']))
        audio.tags.add(id3.TCON(encoding=3, text=fields['genre']))
        audio.tags.add(id3.USLT(encoding=3, lang='eng', desc='Lyrics', text=fields['lyric']))
        audio.tags.add(id3.APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=img_data))
        audio.save()

    elif ext in ['.flac', '.opus']:
        audio = FLAC(file_path) if ext == '.flac' else OggOpus(file_path)
        audio["title"] = fields['title']
        audio["artist"] = fields['artist']
        audio["albumartist"] = fields['artist']
        audio["composer"] = fields['artist']
        audio["album"] = fields['album']
        audio["date"] = fields['date']       # 具体日期
        audio["tracknumber"] = fields['track']
        audio["genre"] = fields['genre']
        audio["lyrics"] = fields['lyric']
        p = Picture()
        p.data, p.type, p.mime, p.desc = img_data, 3, "image/jpeg", "front cover"
        if ext == '.flac':
            audio.clear_pictures(); audio.add_picture(p)
        else:
            audio["metadata_block_picture"] = [base64.b64encode(p.write()).decode('ascii')]
        audio.save()

    print(f"{SUCCESS}全字段（含具体日期 {fields['date']}）已写入: {fields['title']}{RESET}")

def main():
    if len(sys.argv) < 3: return
    file_path, url = sys.argv[1], sys.argv[2]
    meta = None
    if "163.com" in url:
        m = re.search(r'id=(\d+)', url)
        if m: meta = get_netease_data(m.group(1))
    elif "y.qq.com" in url:
        m = re.search(r'songmid=([a-zA-Z0-9]+)', url) or re.search(r'songDetail/([a-zA-Z0-9]+)', url)
        if m: meta = get_qq_data(m.group(1))
    if meta: write_meta(file_path, meta)

if __name__ == "__main__":
    main()
