<!-- SEO keywords: IPTV, M3U, M3U8, 免费IPTV, 免费直播源, CCTV直播, TVB海外, IPTV播放器, IPTV测试工具, free IPTV, IPTV playlist, live TV channels, IPTV checker -->

# IPTV Tools — 免费直播源测试与 M3U 同步工具 / Free IPTV Source Tester & M3U Sync

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Channels](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/stats.json&label=Channels&query=$.total_channels&color=blue)]()
[![Countries](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/stats.json&label=Countries&query=$.total_countries&color=green)]()
[![Last Sync](https://img.shields.io/github/last-commit/goplay-source/IPTV-tools.svg)]()
[![Stars](https://img.shields.io/github/stars/goplay-source/IPTV-tools.svg?style=social)]()
[![Forks](https://img.shields.io/github/forks/goplay-source/IPTV-tools.svg?style=social)]()

</div>

> 🛰️ A local desktop tool for batch-testing IPTV / M3U8 live stream sources, with an auto-synced global channel catalog updated every 6 hours.

## ✨ Features

| Module | Description |
|------|------|
| 🖥️ **Desktop GUI** | CustomTkinter modern UI — Windows / macOS / Linux |
| 🔍 **Batch Source Testing** | Multi-threaded (1-50 threads), validate M3U / M3U8 / TXT playlists |
| 🎯 **Live Stream Detection** | m3u8 header + segment monitoring dual validation |
| ⚡ **Fluency Scoring** | 3-second speed test, 0-100 score with quality rating |
| 🌍 **Geo Lookup** | Offline ip2region database, no network required |
| 🚫 **Blacklist Filtering** | Domain + keyword dual-layer auto-filter |
| 🔄 **M3U Auto-Sync** | GitHub Action pulls latest catalog every 6 hours |
| 📦 **One-Click Build** | PyInstaller single-file .exe, no Python needed |

## 🚀 Quick Start

```bash
git clone https://github.com/goplay-source/IPTV-tools.git
cd IPTV-tools
pip install -r requirements.txt
python main.py
```

Windows users can also download the pre-built `.exe` from [Releases](https://github.com/goplay-source/IPTV-tools/releases) — double-click to run, no Python required.

## 📥 Auto-Synced Channel Catalog

This repo auto-syncs the latest channel catalog from [iptv-search.com](https://iptv-search.com) every 6 hours:

- **[channel.m3u](https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/channel.m3u)** — **20 real playable channels per day** (refreshed daily, full M3U format you can import into VLC / TVBox / Kodi)
- **[catalog.json](https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/catalog.json)** — full channel metadata tree (16,000+ channels, 170+ groups)
- **[stats.json](https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/stats.json)** — live statistics

## 🛠️ Usage

### 1. Import sources
Open the **Import** tab → paste M3U/TXT content or load a local file → preview parse results.

### 2. Run batch test
Switch to **Results** tab → configure threads → click **Start Test**.

### 3. Filter and export
Filter by status / fluency / geo → export M3U → import into TVBox / Kodi / VLC / PotPlayer.

## ⚙️ Configuration

| Parameter | Default | Description |
|------|--------|------|
| Threads | 4 | 1-50, higher = faster but more bandwidth |
| Min fluency | 10 | Channels below this score are filtered |
| Timeout (sec) | 15 | Max wait per link |
| Live stream detection | ✅ | Segment monitoring |
| Quick detection | ❌ | Skip segment monitoring |
| Strict validation | ✅ | Extra segment reachability check |

## 🧰 Tech Stack

- **UI**: CustomTkinter 6.x
- **HTTP**: requests + connection pooling + User-Agent rotation
- **Stream analysis**: custom `StreamAnalyzer` (m3u8 protocol heuristics)
- **Speed test**: segmented download + bitrate / buffer analysis
- **Geo**: ip2region XDB (offline)
- **Packaging**: PyInstaller single-file deployment

## 📁 Project Structure

```
IPTV-tools/
├── main.py               # Entry point, DPI-aware
├── gui.py                # CTk three-tab interface
├── test_logic.py         # Core logic layer
├── channel.m3u           # Auto-synced daily 20 sample
├── catalog.json          # Auto-synced full catalog
├── stats.json            # Auto-synced live stats
├── requirements.txt      # Python dependencies
├── build.spec            # PyInstaller config
└── .github/workflows/    # M3U auto-sync
```

## 🤝 Contributing

Pull requests welcome:
1. Fork this repo
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: add something'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📚 Related Resources

- 🌐 **[iptv-search.com](https://iptv-search.com)** — Companion online channel directory
- 📺 **[Channel Showcase](https://iptv-search.com/showcase)** — Browse all channels with search
- 🤖 **[llms.txt](https://iptv-search.com/llms.txt)** — LLM-friendly channel summary
- 🗺️ **[Sitemap](https://iptv-search.com/sitemap.xml)** — Full page index

## 🙏 Acknowledgments

- [ip2region](https://github.com/lionsoul2014/ip2region) — IP geo library
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — Modern tkinter theme
- [iptv-search.com](https://iptv-search.com) — Channel catalog source

## 📜 License

MIT

---

🌐 **Maintained by [iptv-search.com](https://iptv-search.com)**

If this tool helped you, please ⭐ this repo!

---

# 中文版 / Chinese Version

## 🛰️ 免费 IPTV 直播源测试与 M3U 同步工具

一款本地桌面应用，用于批量检测 IPTV / M3U8 直播源的有效性、流畅度和归属地，并附带一个每 6 小时自动同步的全球频道目录。

## ✨ 功能特性

| 模块 | 说明 |
|------|------|
| 🖥️ **桌面 GUI** | CustomTkinter 现代 UI，支持 Windows / macOS / Linux |
| 🔍 **批量源检测** | 多线程并发（1-50 线程），验证 M3U / M3U8 / TXT 播放列表 |
| 🎯 **直播流判定** | m3u8 头部特征 + 实时切片监控双重验证 |
| ⚡ **流畅度评分** | 3 秒测速，0-100 分 + 优秀/良好/一般/较差评级 |
| 🌍 **归属地查询** | 离线 ip2region 数据库，无需联网 |
| 🚫 **黑名单过滤** | 域名 + 关键词双层自动过滤 |
| 🔄 **M3U 自动同步** | GitHub Action 每 6 小时拉取最新频道目录 |
| 📦 **一键打包** | PyInstaller 单文件 exe，免装 Python |

## 🚀 快速开始

```bash
git clone https://github.com/goplay-source/IPTV-tools.git
cd IPTV-tools
pip install -r requirements.txt
python main.py
```

Windows 用户也可以下载 [Releases](https://github.com/goplay-source/IPTV-tools/releases) 里的预编译 `.exe`，双击即用，无需 Python 环境。

## 📥 自动同步的频道目录

本仓库每 6 小时自动从 [iptv-search.com](https://iptv-search.com) 同步最新频道目录：

- **[channel.m3u](https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/channel.m3u)** — **每日 20 个真实可播放频道**（每日刷新，标准 M3U 格式，可导入 VLC / TVBox / Kodi）
- **[catalog.json](https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/catalog.json)** — 完整频道目录树（16,000+ 频道，170+ 分组）
- **[stats.json](https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/stats.json)** — 实时统计指标

## 🛠️ 使用方法

### 1. 导入源
打开「导入源」标签页 → 粘贴 M3U/TXT 内容或加载本地文件 → 预览解析结果。

### 2. 开始批量测试
切换到「测试结果」标签页 → 配置线程数 → 点击「开始测试」。

### 3. 筛选并导出
按状态 / 流畅度 / 归属地筛选 → 导出 M3U → 导入 TVBox / Kodi / VLC / PotPlayer。

## ⚙️ 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 线程数 | 4 | 1-50 可调，越高越快越占带宽 |
| 最小流畅度 | 10 | 低于此分过滤 |
| 超时(秒) | 15 | 单链接最大等待 |
| 直播流检测 | ✅ | 切片监控验证 |
| 快速检测 | ❌ | 跳过切片监控 |
| 严格验证 | ✅ | 额外验证切片可达性 |

## 🧰 技术栈

- **UI**: CustomTkinter 6.x
- **网络**: requests + 连接池 + User-Agent 轮换
- **流分析**: 自研 `StreamAnalyzer`（m3u8 协议特征）
- **测速**: 分段下载 + 比特率 / 缓冲比计算
- **归属地**: ip2region XDB（离线）
- **打包**: PyInstaller 单文件部署

## 📁 项目结构

```
IPTV-tools/
├── main.py               # 程序入口，DPI 适配
├── gui.py                # CustomTkinter 三 Tab 界面
├── test_logic.py         # 核心逻辑层
├── channel.m3u           # 自动同步的每日 20 个可播频道
├── catalog.json          # 自动同步的完整频道目录
├── stats.json            # 自动同步的实时统计
├── requirements.txt      # Python 依赖声明
├── build.spec            # PyInstaller 配置
└── .github/workflows/    # M3U 自动同步
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request：
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add something'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 发起 Pull Request

## 📚 相关资源

- 🌐 **[iptv-search.com](https://iptv-search.com)** — 配套在线频道目录
- 📺 **[频道展示](https://iptv-search.com/showcase)** — 浏览全部频道（支持搜索）
- 🤖 **[llms.txt](https://iptv-search.com/llms.txt)** — LLM 友好的频道摘要
- 🗺️ **[站点地图](https://iptv-search.com/sitemap.xml)** — 完整页面索引

## 🙏 致谢

- [ip2region](https://github.com/lionsoul2014/ip2region) — IP 定位库
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — 现代化 tkinter 主题
- [iptv-search.com](https://iptv-search.com) — 频道目录数据源

## 📜 许可证

MIT

---

🌐 **由 [iptv-search.com](https://iptv-search.com) 开发维护**

如果这个工具帮到了你，请给个 ⭐ Star 支持一下！
