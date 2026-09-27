# IPTV Tools — 免费直播源测试与 M3U 同步工具

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
