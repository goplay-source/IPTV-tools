<!-- SEO keywords: IPTV, M3U, M3U8, 免费IPTV, 免费直播源, CCTV直播, TVB海外, IPTV播放器, IPTV测试工具, free IPTV, IPTV playlist, live TV channels, IPTV checker, iptv-search.com, 频道搜索, 直播源测试, 测速, 归属地, 黑名单过滤, 周测试, 筛选M3U, IPTV channel directory, live stream testing -->

<p align="center">
  <img src="https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/.github/social-preview.png" alt="IPTV Tools — Free IPTV Source Tester & M3U Sync" width="1280">
</p>

# 📺 IPTV Tools
## 免费直播源测试工具 & 每周 M3U 订阅 / Free IPTV Source Tester & Weekly M3U Subscription

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Last Sync](https://img.shields.io/github/last-commit/goplay-source/IPTV-tools.svg)]()
[![Stars](https://img.shields.io/github/stars/goplay-source/IPTV-tools.svg?style=social)]()
[![Forks](https://img.shields.io/github/forks/goplay-source/IPTV-tools.svg?style=social)]()

</div>

> 🛰️ A local desktop tool for batch-testing IPTV / M3U8 live stream sources, with a built-in public M3U source tested weekly — all channels are published to the subscription file, playable ones first.

## ✨ Features

| Module | Description |
|------|------|
| 🖥️ **Desktop GUI** | CustomTkinter modern UI — Windows / macOS / Linux |
| 🔍 **Batch Source Testing** | Multi-threaded (1-50 threads), validate M3U / M3U8 / TXT playlists |
| 🎯 **Live Stream Detection** | m3u8 header + segment monitoring dual validation |
| ⚡ **Fluency Scoring** | 3-second speed test, 0-100 score with quality rating |
| 🌍 **Geo Lookup** | Offline ip2region database, no network required |
| 🚫 **Blacklist Filtering** | Domain + keyword dual-layer auto-filter |
| 🔄 **Weekly M3U Test** | GitHub Action tests the built-in data source weekly, publishes full M3U (playable-first) |
| 📦 **One-Click Build** | PyInstaller single-file .exe, no Python needed |

## 🚀 Quick Start

```bash
git clone https://github.com/goplay-source/IPTV-tools.git
cd IPTV-tools
pip install -r requirements.txt
python main.py
```

Windows users can also download the pre-built `.exe` from [Releases](https://github.com/goplay-source/IPTV-tools/releases) — double-click to run, no Python required.

## 📥 Weekly M3U

This repo runs a weekly automated test against a built-in public M3U source using the same detection logic as the desktop app (`test_logic.py`). All channels are published to the subscription file — playable ones come first in each group so players pick good links, and the rest follow for reference:

- **[channel.m3u](https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/channel.m3u)** — full M3U subscription, tested weekly, playable-first ordering, grouped by category
- **[test_report.json](https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/test_report.json)** — JSON statistics report (total channels, playable count, per-group counts)

Import `channel.m3u` into VLC / TVBox / Kodi and you're done.

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
| Timeout (sec) | 20 | Max wait per link |
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
├── test_logic.py         # Core detection logic layer
├── test_weekly.py        # Weekly M3U test pipeline
├── channel.m3u           # Weekly tested M3U (full, playable-first)
├── test_report.json      # Weekly test report (auto-published)
├── requirements.txt      # Python dependencies
├── build.spec            # PyInstaller config
└── .github/workflows/    # test-weekly.yml (weekly M3U test)
```

## 🤝 Contributing

Pull requests welcome:
1. Fork this repo
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: add something'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📚 Related Resources

- 🌐 **[iptv-search.com](https://iptv-search.com)** — companion online channel directory & live-stream search
- 🔎 **[Browse: CCTV1](https://iptv-search.com/search?type=channel&q=CCTV1)** — jump to live results
- 🔎 **[Browse: HBO](https://iptv-search.com/search?type=channel&q=HBO)** — jump to live results
- 🗺️ **[Sitemap](https://iptv-search.com/sitemap.xml)** — full page index

## 🙏 Acknowledgments

Built on the shoulders of giants:

- [ip2region](https://github.com/lionsoul2014/ip2region) — Offline IP-to-region database, fast in-memory lookup
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — Modern themed UI components on top of tkinter
- [requests](https://github.com/psf/requests) — HTTP for humans (connection pooling + streaming downloads)
- [PyInstaller](https://github.com/pyinstaller/pyinstaller) — Freezes Python apps into single-file executables

---

## 🌐 About This Project

**IPTV Tools** is an open-source desktop application for **batch-testing IPTV / M3U8 live stream sources** — it validates reachability, measures playback fluency, resolves geo-location, and filters dead or low-quality channels before you import them into TVBox / Kodi / VLC.

## 🌐 About [iptv-search.com](https://iptv-search.com)

**iptv-search.com** is a public, free online service for **IPTV channel search, browsing, and live-stream testing**:

- 🔎 **Channel search** — find channels by name, country, language, or category with sub-200 ms responses
- 🌍 **Live streaming** — browse and play live channels directly in the browser (no app install required)
- 📱 **Mobile-friendly** — fully responsive, works in any modern browser on phone, tablet, or desktop
- 🗺️ **Coverage** — indexes thousands of live channels across 170+ country and regional groups
- 🔄 **Auto-refresh** — the channel index is updated automatically every 6 hours via background crawlers

The weekly M3U published in this repo is independently tested by this project's own pipeline and is **not derived from any iptv-search.com endpoint** — it uses the built-in data source described above.

## 📜 License

MIT

---

🌐 **Maintained by [iptv-search.com](https://iptv-search.com)**

If this tool helped you, please ⭐ this repo!

---

## 中文版 / Chinese Version

## 🛰️ 免费 IPTV 直播源测试工具 & 每周 M3U 订阅

一款本地桌面应用，用于批量检测 IPTV / M3U8 直播源的有效性、流畅度和归属地，并附带每周自动测试一次的内置公开数据源，全量输出到订阅文件（可播频道排前）。

## ✨ 功能特性

| 模块 | 说明 |
|------|------|
| 🖥️ **桌面 GUI** | CustomTkinter 现代 UI，支持 Windows / macOS / Linux |
| 🔍 **批量源检测** | 多线程并发（1-50 线程），验证 M3U / M3U8 / TXT 播放列表 |
| 🎯 **直播流判定** | m3u8 头部特征 + 实时切片监控双重验证 |
| ⚡ **流畅度评分** | 3 秒测速，0-100 分 + 优秀/良好/一般/较差评级 |
| 🌍 **归属地查询** | 离线 ip2region 数据库，无需联网 |
| 🚫 **黑名单过滤** | 域名 + 关键词双层自动过滤 |
| 🔄 **每周 M3U 测试** | GitHub Action 每周测试一次内置数据源，发布全量 M3U（可播优先排序） |
| 📦 **一键打包** | PyInstaller 单文件 exe，免装 Python |

## 🚀 快速开始

```bash
git clone https://github.com/goplay-source/IPTV-tools.git
cd IPTV-tools
pip install -r requirements.txt
python main.py
```

Windows 用户也可以下载 [Releases](https://github.com/goplay-source/IPTV-tools/releases) 里的预编译 `.exe`，双击即用，无需 Python 环境。

## 📥 每周 M3U

本仓库每周自动对一份内置的公开 M3U 数据源执行一次测试（使用与桌面端相同的 `test_logic.py` 检测逻辑）。订阅文件保留全部频道——可播频道排在每组靠前位置方便播放器优先取到好线路，未通过测试的频道列在后面仅供参考：

- **[channel.m3u](https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/channel.m3u)** — 全量 M3U 订阅，每周测试更新，可播优先排序，按类别分组
- **[test_report.json](https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/test_report.json)** — 统计报告（总频道数、可播数、各组数量）

将 `channel.m3u` 导入 VLC / TVBox / Kodi 即可直接使用。

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
| 超时(秒) | 20 | 单链接最大等待 |
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
├── test_logic.py         # 核心检测逻辑层
├── test_weekly.py        # 每周 M3U 测试管道
├── channel.m3u           # 每周测试后的 M3U（全量，可播优先）
├── test_report.json      # 每周测试报告（自动发布）
├── requirements.txt      # Python 依赖
├── build.spec            # PyInstaller 配置
└── .github/workflows/    # test-weekly.yml（每周 M3U 测试）
```

## 🤝 贡献

欢迎 Pull Request：
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: 增加 XX 功能'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📚 相关资源

- 🌐 **[iptv-search.com](https://iptv-search.com)** — 配套的在线频道目录与直播流搜索
- 🔎 **[浏览: CCTV1](https://iptv-search.com/search?type=channel&q=CCTV1)** — 跳转落地页（带预填搜索词）
- 🔎 **[浏览: HBO](https://iptv-search.com/search?type=channel&q=HBO)** — 跳转落地页（带预填搜索词）
- 🗺️ **[站点地图](https://iptv-search.com/sitemap.xml)** — 完整页面索引

## 🙏 致谢

基于巨人的肩膀构建：

- [ip2region](https://github.com/lionsoul2014/ip2region) — 离线 IP 归属地数据库，高速内存查询
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — 现代化 tkinter 主题组件库
- [requests](https://github.com/psf/requests) — Python 生态最广泛使用的 HTTP 客户端
- [PyInstaller](https://github.com/pyinstaller/pyinstaller) — Python 应用打包为单文件可执行程序

---

## 🌐 关于本项目

**IPTV Tools** 是一个开源桌面应用，用于**批量测试 IPTV / M3U8 直播源**——验证可达性、测量播放流畅度、解析 IP 归属地、在导入 TVBox / Kodi / VLC 前过滤掉失效或低质量频道。

## 🌐 关于 [iptv-search.com](https://iptv-search.com)

**iptv-search.com** 是一个公开的、免费的在线**IPTV 频道搜索、浏览与直播流测试服务**：

- 🔎 **频道搜索** — 按名称、国家、语言或类别搜索频道，200ms 内返回结果
- 🌍 **在线直播** — 浏览器内直接浏览和播放直播频道，无需安装任何 App
- 📱 **移动端适配** — 完全响应式设计，手机 / 平板 / 桌面端均可使用
- 🗺️ **覆盖范围** — 索引了数千个直播频道，覆盖 170+ 国家和地区分组
- 🔄 **自动更新** — 频道索引每 6 小时自动刷新一次

本仓库每周发布的 M3U 是本项目自己的管道独立测试的结果，**不来自 iptv-search.com 的任何接口**——使用的是上面描述的内置数据源。

## 📜 许可证

MIT

---

🌐 **由 [iptv-search.com](https://iptv-search.com) 开发维护**

如果这个工具帮到了你，请给个 ⭐ Star 支持一下！
