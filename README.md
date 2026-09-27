<!-- SEO keywords: IPTV, M3U, M3U8, 免费IPTV, 免费直播源, CCTV直播, TVB海外, IPTV播放器, IPTV测试工具, free IPTV, IPTV playlist, live TV channels, IPTV checker -->
<!-- topic: iptv-tools ip2region free-iptv m3u m3u8 live-tv china-iptv playlist ott -->

# IPTV Tools — 免费直播源测试与 M3U 同步工具 | Free IPTV Source Tester & M3U Playlist Auto-Sync

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

> 🛰️ 一款功能强大的本地桌面工具，用于批量检测 IPTV / M3U8 直播源的有效性、流畅度和归属地。仓库内每日同步**频道目录树**（频道名 + 分组 + logo），不包含真实播放 URL。
>
> **关键词**：免费IPTV直播源、M3U播放器、M3U8测试工具、CCTV直播源、TVB海外直播、凤凰卫视、ESPN、BBC、CNN、HBO、IPTV源验证、频道归属地查询、IPTV批量检测

## 🌍 iptv-search.com 在线频道目录

本工具配套的在线频道目录已在 [iptv-search.com](https://iptv-search.com/?ref=github) 上线，按国家/语言/类型整理 **16,000+ 直播频道**，每日自动同步更新：

- 🇨🇳 **[CCTV 频道大全](https://iptv-search.com/category/CCTV)** — CCTV-1 至 CCTV-17、4K/8K 高清
- 🇭🇰 **[港澳台频道](https://iptv-search.com/category/HongKong)** — TVB 翡翠台、明珠台、ViuTV、凤凰卫视
- 🇹🇼 **[台湾频道](https://iptv-search.com/category/Taiwan)** — 中视、华视、台视、民视、TVBS
- 🌍 **[国际频道](https://iptv-search.com/category/International)** — CNN、BBC、ESPN、HBO、Discovery
- ⚽ **[体育频道](https://iptv-search.com/category/Sports)** — CCTV5、五星体育、DAZN、爱尔达体育
- 📺 **[频道展示页](https://iptv-search.com/showcase)** — 浏览全部频道（按名称搜索）
- 🗺️ **[站点地图](https://iptv-search.com/sitemap.xml)** — 所有页面索引（SEO 友好）

### 💎 订阅 VIP 解锁完整功能

| 套餐 | 价格 | 时长 | 适用场景 |
|------|------|------|----------|
| **体验会员** | ¥0.1 | 1 天 | 试用 |
| **月度会员** | ¥19.9 | 30 天 | 短期使用 |
| **季度会员** | ¥49.9 | 90 天 | 中期使用（推荐） |
| **年度会员** | ¥168 | 365 天 | 长期使用 |
| **永久会员** | ¥299 | 永久 | 含持续更新 |

**VIP 权益**：
- ✅ 完整 **16,000+ 频道** M3U 订阅（每日自动更新）
- ✅ 4K / 8K 高清频道优先（**每日 20 个真实可播**频道在本仓库免费试看）
- ✅ 手机 / 平板 / 智能电视 / 电视盒子 / 投影仪 / 电脑多设备同步
- ✅ 失效源自动替换（无需手动维护）
- ✅ EPG 节目单
- ✅ 无广告播放
- ✅ 支持 APTV、Televizo、IPTV Smarters、TiviMate、KODI、VLC 等主流播放器

👉 **[立即订阅 VIP](https://iptv-search.com/subscription/?ref=github)** ｜ **[查看套餐详情](https://iptv-search.com/plans/?ref=github)**

## ✨ 项目亮点

| 模块 | 说明 |
|------|------|
| 🖥️ **桌面 GUI** | CustomTkinter 现代 UI，Windows / macOS / Linux 全平台 |
| 🔍 **批量源检测** | 多线程并发，支持 1-50 线程自定义 |
| 🎯 **直播流判定** | m3u8 头部特征 + 实时切片监控双重验证 |
| ⚡ **流畅度评分** | 3 秒测速 + 缓冲分析，0-100 分 + 优秀/良好/一般/较差评级 |
| 🌍 **归属地查询** | 离线 ip2region 数据库，无网也能用 |
| 🚫 **黑名单过滤** | 域名 / 关键词双层过滤，自动排除低质源 |
| 🔄 **M3U 自动同步** | GitHub Action 每 6 小时拉取最新全球播放列表 |
| 📦 **一键打包** | PyInstaller 单文件 exe，免 Python 环境 |

## 🚀 快速开始

```bash
git clone https://github.com/goplay-source/IPTV-tools.git
cd IPTV-tools
pip install -r requirements.txt
python main.py
```

Windows 用户也可下载 [Release](https://github.com/goplay-source/IPTV-tools/releases) 里的便携版 `.exe`，双击即用。

## 📥 每日同步的全球频道目录（不含播放 URL）

本仓库通过 GitHub Actions 每 6 小时自动从 [iptv-search.com](https://iptv-search.com/?ref=github) 同步**频道目录**（频道名 + 国家分组 + 台标），文件位于仓库根目录：

- **[channel.m3u](https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/channel.m3u)** — 8,700+ 频道 / 150+ 国家（**M3U 格式但 URL 全部为占位，需订阅获取真实地址**）
- **[catalog.json](https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/catalog.json)** — 完整目录树结构
- **[stats.json](https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/stats.json)** — 实时统计指标

> ⚠️ **商业说明**：本仓库仅同步公开目录树，**不包含真实播放 URL**。完整可播放的 M3U 需要在 [iptv-search.com](https://iptv-search.com/?ref=github) 订阅后获得。

## 🆓 免费版 vs 付费版

> 我们坚持开源免费，但为了持续运营提供同步基础设施，部分功能需要订阅。

| 功能 | 桌面工具（本仓库） | iptv-search.com 在线版 |
|------|--------------------|------------------------|
| 本地源批量测试 | ✅ | ✅ |
| 流畅度评分 | ✅ | ✅ |
| 归属地查询 | ✅ | ✅ |
| 全球 M3U 订阅 | ❌（目录树可见，播放 URL 需订阅） | ✅（每日自动更新，完整可播放） |
| 4K / 8K 频道优先 | ❌ | ✅ |
| 多设备同步订阅 | ❌ | ✅（手机 / 电视 / 盒子 / 网页） |
| 失效源自动替换 | ❌ | ✅ |
| EPG 节目单 | ❌ | ✅ |
| 24/7 在线客服 | ❌ | ✅ |
| 价格 | 免费 | ¥19.9/月 起 |

👉 **[立即试用付费版](https://iptv-search.com/?ref=github)** — 首月 0.1 元体验

## 🛠️ 使用方法

### 第一步：导入源
打开「导入源」标签页 → 粘贴 M3U/TXT 内容 → 预览解析。

### 第二步：批量测试
切换到「测试结果」页 → 配置线程数 → 开始测试。

### 第三步：筛选导出
按状态 / 流畅度 / 归属地筛选 → 导出 M3U → 导入播放器。

## ⚙️ 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 线程数 | 4 | 1-50 可调 |
| 最小流畅度 | 10 | 低于此分过滤 |
| 超时(秒) | 15 | 单链接最大等待 |
| 直播流检测 | ✅ | 切片监控验证 |
| 快速直播检测 | ❌ | 跳过切片监控 |
| 严格验证 | ✅ | 额外验证切片可达性 |

## 🧰 技术栈

- **UI**: CustomTkinter 6.x
- **网络**: requests + 连接池 + User-Agent 轮换
- **流分析**: 自研 `StreamAnalyzer`（基于 m3u8 协议特征）
- **测速**: 分段下载 + 比特率 / 缓冲比计算
- **归属地**: ip2region XDB（离线）
- **打包**: PyInstaller 单文件部署

## 📁 项目结构

```
IPTV-tools/
├── main.py               # 程序入口，DPI 适配
├── gui.py                # CTk 三 Tab 界面
├── test_logic.py         # 核心逻辑层
├── playlist.m3u          # 自动同步的全球播放列表
├── stats.json            # 实时统计
├── requirements.txt      # 依赖声明
├── build.spec            # PyInstaller 配置
└── .github/workflows/    # M3U 自动同步
```

## 🤝 贡献指南

欢迎提交 Issue 和 PR：
1. Fork 仓库
2. 创建 feature 分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add something'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 发起 Pull Request

## 🙏 致谢

- [ip2region](https://github.com/lionsoul2014/ip2region) — IP 定位库
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — 现代化 tkinter 主题
- [iptv-search.com](https://iptv-search.com/?ref=github) — 提供实时同步的全球播放列表源

## 📚 相关资源

**官方频道目录**：
- [CCTV 直播源](https://iptv-search.com/category/CCTV) ｜ [TVB 海外直播](https://iptv-search.com/category/HongKong) ｜ [体育频道](https://iptv-search.com/category/Sports) ｜ [全部频道](https://iptv-search.com/showcase)

**AI 爬虫友好入口**：
- [llms.txt](https://iptv-search.com/llms.txt) — LLM 摘要（GPT / Claude 可索引）
- [llms-full.txt](https://iptv-search.com/llms-full.txt) — 完整频道数据
- [sitemap.xml](https://iptv-search.com/sitemap.xml) — 站点地图

**使用指南**：
- [新手指南](https://iptv-search.com/tutorial/?ref=github) — IPTV 是什么 + 怎么用
- [APTV & CarPlay 配置](https://iptv-search.com/carplay-aptv/?ref=github) — Apple 设备配置
- [订阅与续费](https://iptv-search.com/subscription/?ref=github) — VIP 套餐详情

**API 文档**：
- `GET /api/channels/catalog.json` — 频道目录 + 每日 20 个真实可播频道
- `GET /api/public/config` — 前端配置

## 📜 License

MIT

---

<div align="center">

🛰️ **由 [iptv-search.com](https://iptv-search.com/?ref=github) 开发维护** — 专注 IPTV 直播源检索与订阅服务

如果这个工具帮到了你，请给个 ⭐ Star 支持一下！

</div>

---

# English Version

#<!-- SEO keywords: IPTV, M3U, M3U8, free IPTV, IPTV playlist, live TV channels, CCTV, TVB, IPTV checker, M3U editor, IPTV source validator -->

# IPTV Tools — Free Live Stream Tester & Auto-Synced M3U Playlist

> A powerful desktop GUI for batch-testing IPTV / M3U8 live stream sources, plus an auto-synced global playlist updated every 6 hours.
>
> **Keywords**: free IPTV, M3U player, M3U8 checker, IPTV playlist, live TV channels, CCTV streaming, TVB overseas, ESPN, BBC, CNN, HBO, IPTV source validator, IPTV bulk tester, M3U editor

## 🌍 Online Channel Catalog (iptv-search.com)

The companion online directory at [iptv-search.com](https://iptv-search.com/?ref=github) catalogs **16,000+ live TV channels** organized by country, language, and category, updated daily:

- 🇨🇳 **[CCTV Channels](https://iptv-search.com/category/CCTV)** — CCTV-1 through CCTV-17, 4K/8K HD
- 🇭🇰 **[Hong Kong & Taiwan](https://iptv-search.com/category/HongKong)** — TVB Jade, Pearl, ViuTV, Phoenix TV
- 🌍 **[International](https://iptv-search.com/category/International)** — CNN, BBC, ESPN, HBO, Discovery
- ⚽ **[Sports](https://iptv-search.com/category/Sports)** — CCTV5, DAZN, ESPN, beIN Sports
- 📺 **[Showcase](https://iptv-search.com/showcase)** — Browse all channels with search
- 🗺️ **[Sitemap](https://iptv-search.com/sitemap.xml)** — Full page index (SEO-friendly)

### 💎 VIP Subscription Plans

| Plan | Price | Duration | Best For |
|------|-------|----------|----------|
| **Trial** | ¥0.1 | 1 day | Try it out |
| **Monthly** | ¥19.9 | 30 days | Short-term |
| **Quarterly** | ¥49.9 | 90 days | Mid-term (recommended) |
| **Yearly** | ¥168 | 365 days | Long-term |
| **Lifetime** | ¥299 | Permanent | Permanent + free updates |

**VIP Benefits**:
- ✅ Full **16,000+ channels** M3U subscription (auto-updated daily)
- ✅ 4K / 8K priority channels (**20 daily playable channels free in this repo**)
- ✅ Multi-device sync — phone, tablet, smart TV, TV box, projector, PC
- ✅ Auto-replace dead sources (zero maintenance)
- ✅ EPG program guide
- ✅ Ad-free playback
- ✅ Works with APTV, Televizo, IPTV Smarters, TiviMate, KODI, VLC

👉 **[Subscribe VIP](https://iptv-search.com/subscription/?ref=github)** ｜ **[View Plans](https://iptv-search.com/plans/?ref=github)**

## Features

- **Batch Source Testing** — multi-threaded concurrent checks (1-50 threads)
- **Live Stream Detection** — m3u8 header + segment monitoring dual validation
- **Fluency Scoring** — 3-second speed test, 0-100 score with quality rating
- **Geo Lookup** — offline ip2region database, no network required
- **Blacklist Filtering** — domain + keyword dual-layer auto-filter
- **Auto-Synced M3U** — GitHub Actions pulls latest playlist every 6 hours
- **One-Click Build** — PyInstaller single-file .exe, no Python needed

## Quick Start

```bash
git clone https://github.com/goplay-source/IPTV-tools.git
cd IPTV-tools
pip install -r requirements.txt
python main.py
```

## Daily-Synced Global M3U Playlist

This repo auto-syncs the latest global playlist from [iptv-search.com](https://iptv-search.com/?ref=github) every 6 hours:

- **[channel.m3u](https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/channel.m3u)** — 8,700+ channels / 150+ countries (M3U format with **placeholder URLs**; subscribe for real playlist)
- **[catalog.json](https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/catalog.json)** — full catalog tree
- **[stats.json](https://raw.githubusercontent.com/goplay-source/IPTV-tools/main/stats.json)** — live statistics

> ⚠️ **Note**: This repo syncs the public catalog only (channel names + groups + logos), **without real play URLs**. The full playable M3U requires a subscription at [iptv-search.com](https://iptv-search.com/?ref=github).

## Free vs Pro

| Feature | Desktop Tool (this repo) | iptv-search.com Online |
|---------|--------------------------|------------------------|
| Local source batch testing | ✅ | ✅ |
| Fluency scoring | ✅ | ✅ |
| Geo lookup | ✅ | ✅ |
| Global M3U subscription | ❌ (catalog only, URLs gated) | ✅ (auto-updated, full URLs) |
| 4K / 8K priority channels | ❌ | ✅ |
| Multi-device subscription | ❌ | ✅ |
| Auto-replace dead sources | ❌ | ✅ |
| EPG program guide | ❌ | ✅ |
| 24/7 support | ❌ | ✅ |
| Price | Free | From ¥19.9/month |

👉 **[Try Pro Free for First Month](https://iptv-search.com/?ref=github)**

## Tech Stack

- UI: CustomTkinter
- HTTP: requests + connection pooling + UA rotation
- Stream analysis: custom `StreamAnalyzer` (m3u8 protocol heuristics)
- Speed test: segmented download + bitrate / buffer analysis
- Geo: ip2region XDB (offline)
- Packaging: PyInstaller

## License

MIT

## 📚 Related Resources

**Official Channel Catalog**:
- [CCTV Live Streams](https://iptv-search.com/category/CCTV) ｜ [TVB Overseas](https://iptv-search.com/category/HongKong) ｜ [Sports Channels](https://iptv-search.com/category/Sports) ｜ [All Channels](https://iptv-search.com/showcase)

**AI-Crawler Friendly**:
- [llms.txt](https://iptv-search.com/llms.txt) — LLM summary (indexable by GPT / Claude)
- [llms-full.txt](https://iptv-search.com/llms-full.txt) — Full channel data
- [sitemap.xml](https://iptv-search.com/sitemap.xml) — Site map

**User Guides**:
- [Beginner Tutorial](https://iptv-search.com/tutorial/?ref=github) — What is IPTV + how to use
- [APTV & CarPlay Setup](https://iptv-search.com/carplay-aptv/?ref=github) — Apple device config
- [Subscription Plans](https://iptv-search.com/subscription/?ref=github) — VIP pricing

**API Docs**:
- `GET /api/channels/catalog.json` — Channel catalog + 20 daily playable channels
- `GET /api/public/config` — Frontend config

---

🌐 **Maintained by [iptv-search.com](https://iptv-search.com/?ref=github)** — focused on IPTV source discovery & subscription services.

If this tool helped you, please ⭐ this repo!
