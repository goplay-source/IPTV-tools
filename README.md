# IPTV 直播源测试工具

> 一款功能强大的本地桌面工具，用于批量检测 IPTV/M3U8 直播源的有效性、流畅度和归属地。支持 M3U/TXT 播放列表导入，自动筛选有效频道，导出可用播放列表。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-lightgrey.svg)]()

## 简介

IPTV 直播源测试工具是一款专为 IPTV 爱好者和内容创作者开发的桌面应用程序。它能够：

- **批量测试** — 从 M3U/TXT 播放列表中解析频道，批量检测所有链接有效性
- **直播流判定** — 智能区分直播流与点播流，识别无效源
- **流畅度评分** — 对有效直播流进行 3 秒测速，输出 0-100 分数和「优秀/良好/一般/较差」评级
- **IP 归属地查询** — 内置 ip2region 数据库，获取每个源站点的地理归属
- **智能过滤** — 自动过滤包含错误特征的源（如 token 过期、广告占位符等）
- **灵活导出** — 支持导出为标准 M3U 格式，可直接导入 TVBox、Kodi、VLC 等播放器

本项目由 **[iptv-search.com](https://iptv-search.com)** 开发维护，网站提供直播源搜索、订阅管理和在线测试等更多服务。

## 功能特性

| 功能 | 说明 |
|------|------|
| 📥 多格式导入 | 支持 `.m3u`、`.m3u8`、`.txt`（TVBox 格式）播放列表文件 |
| 🔗 批量检测 | 多线程并行测试，可自定义线程数（1-50） |
| 🎯 直播判定 | 基于 m3u8 头部特征 + 实时切片监控双重验证 |
| ⚡ 流畅度测试 | 下载测速 + 缓冲分析，综合评分 0-100 |
| 🌍 归属地查询 | 集成 ip2region，无需联网即可查询 IP 归属 |
| 🚫 黑名单过滤 | 可配置域名黑名单和关键词过滤，自动排除低质源 |
| 🔍 结果筛选 | 按状态、流畅度阈值、归属地多维度筛选排序 |
| 💾 导出分享 | 一键导出有效频道为 M3U 文件，支持复制到剪贴板 |

## 安装运行

### 方式一：源码运行

```bash
# 1. 克隆仓库
git clone https://github.com/goplay-source/IPTV-tools.git
cd IPTV-tools

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行程序
python main.py
```

### 方式二：直接使用编译版

下载最新 Windows 便携版 `.exe`，解压即用，无需安装 Python 环境。

### 方式三：自行打包

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包为单文件 exe（Windows）
pyinstaller build.spec

# 输出文件：dist/IPTVTester.exe
```

## 使用方法

### 第一步：导入源

1. 打开「导入源」标签页
2. 粘贴 M3U/TXT 格式的播放列表内容，或点击「选择本地文件」导入
3. 点击「预览解析」验证频道解析是否正确
4. 也可通过「加载历史源」快速使用之前的源地址

### 第二步：开始测试

1. 切换到「测试结果」标签页
2. 点击「开始测试」，工具将使用配置的线程数并行检测所有频道
3. 测试过程中可随时暂停/停止

### 第三步：查看结果

测试结果包含以下信息：

- **状态** — ✅ 有效 / ❌ 无效
- **响应时间** — 连接建立耗时（毫秒）
- **流畅度** — 评分及等级（优秀/良好/一般/较差）
- **归属地** — IP 地理位置（省/城市/运营商）
- **编码格式** — hls_live / hls / direct_stream 等

支持点击列标题排序，使用筛选条件快速定位优质频道。

### 第四步：导出使用

1. 根据需要筛选出高质量频道
2. 点击「导出 M3U」保存为文件，或「复制 M3U」直接粘贴到播放器
3. 导出的 M3U 文件可直接用于 TVBox、Kodi、VLC、PotPlayer 等播放软件

## 配置说明

在「配置」标签页中可调整以下参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 线程数 | 4 | 并发测试线程，越高越快但越占用带宽 |
| 最小流畅度 | 10 | 低于此分数的频道将被过滤 |
| 超时(秒) | 15 | 单个链接的最大等待时间 |
| 启用流畅度检测 | ✓ | 关闭后可跳过测速，大幅缩短测试时间 |
| 启用直播流检测 | ✓ | 开启后进行完整的直播判定 |
| 快速直播检测 | ✗ | 开启后跳过切片监控，仅分析头部特征 |
| 严格验证 | ✓ | 开启后会额外验证切片可达性 |
| 域名黑名单 | — | 每行一个域名，匹配则自动跳过 |

## 技术栈

- **UI 框架**: Python tkinter / ttk（CustomTkinter 风格主题）
- **网络请求**: requests + session 连接池 + User-Agent 轮换
- **直播分析**: 自研 `StreamAnalyzer` 类，基于 m3u8 协议特征分析
- **流畅度测试**: 分段下载测速，计算比特率和缓冲比
- **归属地查询**: ip2region XDB 数据库（离线查询）
- **打包工具**: PyInstaller（单文件部署）

## 项目结构

```
IPTV-tools/
├── main.py               # 程序入口，DPI 适配 + CTk 启动
├── gui.py                # tkinter/ttk UI，三 Tab 界面
├── test_logic.py         # 核心逻辑层，网络测试 + 直播分析
├── requirements.txt      # Python 依赖声明
├── build.spec            # PyInstaller 打包配置
├── config.json           # 运行时配置（自动生成）
├── ip2region_master/     # 归属地查询数据库
└── dist/                 # 编译输出目录
```

## 关联服务

- **🌐 [iptv-search.com](https://iptv-search.com)** — IPTV 直播源搜索引擎，提供全网源快速检索、订阅管理和在线可用性测试
- **💻 GitHub 仓库** — 本项目源码持续更新，欢迎 Star 和 Fork

## 常见问题

**Q: 测试速度很慢怎么办？**
A: 尝试增大「线程数」或关闭「流畅度检测」和「直播流检测」来加速。

**Q: 为什么有些频道显示「切片不可达」？**
A: 该链接的 m3u8 播放列表中的切片文件返回了 HTTP 错误，通常意味着源已失效或被限速。

**Q: 导出的 M3U 文件在哪里用？**
A: 可直接导入 TVBox（Android）、Kodi（多平台）、VLC、PotPlayer、IPE 等主流播放软件。

**Q: 归属地查询不准？**
A: ip2region 数据库默认更新频率约为每月一次，可在 [iptv-search.com](https://iptv-search.com) 获取最新数据文件替换。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## 致谢

- [ip2region](https://github.com/lionsoul2014/ip2region) — 开源 IP 定位库
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — 现代化 tkinter 主题
- 所有提供开源播放列表的社区贡献者

---

**由 [iptv-search.com](https://iptv-search.com) 开发维护** — 专注 IPTV 直播源检索与优化工具
