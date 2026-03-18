# 🎵 Music-Tagger

一个基于 Python 的自动化音乐元数据（Metadata）补全工具，支持从主流平台获取高规格的专辑封面和完整标签。

## ✨ 功能特性

- **多平台支持**：自动识别并抓取网易云音乐、QQ 音乐的歌曲数据。
- **高规格封面**：强制获取 **800x800** 高清专辑封面（支持 MP3, FLAC, Opus）。
- **完整元数据**：包括标题、艺术家、专辑、**具体发行日期 (YYYY-MM-DD)**、音轨号、流派。
- **智能归类**：自动写入“专辑艺术家”与“作曲家”。
- **内嵌歌词**：自动下载并内嵌 LRC 格式歌词，播放器无需额外文件即可显示动态歌词。
- **全格式兼容**：完美支持 `.mp3`, `.flac`, `.opus`。

## 🚀 快速开始

### 1. 安装依赖
本项目依赖 `mutagen` 处理音频标签，以及 `requests` 进行 API 请求。
```bash
pip install mutagen requests
```
### 2. 下载脚本 
下载 `tagger.py` 到本地。

### 3. 使用方法
在终端执行以下命令：
```bash
python tagger.py "你的音乐文件路径" "歌曲链接"
```
示例
```bash
python tagger.py "/Users/dengmingda/Music/周杰伦\ -\ 七里香.opus" "https://y.qq.com/n/ryqq_v2/songDetail/004Z8Ihr0JIu5s"
```
### 🛠️ 建议配置 (macOS/Linux)
为了更方便地使用，建议在 `~/.zshrc` 或 `~/.bashrc` 中添加别名：
```bash
alias tagger='noglob /你的路径/venv/bin/python3 /你的路径/tagger.py'
```
### 📝 注意事项
本工具仅供个人学习及音乐库整理使用，请尊重版权。












