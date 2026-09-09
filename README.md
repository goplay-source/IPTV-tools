# IPTV 直播源测试工具

> 本地桌面工具，批量检测 IPTV/M3U8 直播源的有效性、流畅度与 IP 归属地，支持筛选与导出。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)]()

由 [iptv-search.com](https://iptv-search.com) 开发维护。

## 功能特性

- 📥 **多格式导入** — 支持 `.m3u` / `.m3u8` / `.txt`（TVBox 格式）播放列表
- 🔗 **批量检测** — 多线程并行测试，可自定义线程数（1–50）
- 🎯 **直播流判定** — 基于 m3u8 头部特征 + 实时切片监控双重验证
- ⚡ **流畅度评分** — 0–100 分 + 优秀/良好/一般/较差 评级
- 🌍 **IP 归属地查询** — 集成 ip2region XDB 离线数据库，无需联网
- 🚫 **黑名单过滤** — 域名黑名单 + 关键词过滤，自动排除低质源
- 🔍 **结果筛选排序** — 按状态、流畅度阈值、归属地多维度筛选
- 💾 **M3U 导出** — 一键导出有效频道，可直接导入 TVBox、Kodi、VLC

## 快速开始

### 源码运行

```bash
pip install -r requirements.txt
python main.py
```

### 自行打包（Windows）

```bash
pyinstaller build.spec
# 产物：dist/IPTVTester.exe（约 22 MB，单文件便携）
```

## 使用流程

1. **导入源** — 「导入源」标签页粘贴 M3U/TXT 内容，或选择本地文件 / 加载历史源
2. **开始测试** — 「测试结果」标签页点击「开始测试」，可随时暂停 / 停止
3. **查看结果** — 支持按列排序与多维筛选
4. **导出 M3U** — 一键保存或复制到剪贴板，导入 TVBox / Kodi / VLC / PotPlayer

## 结果字段

| 字段 | 说明 |
|------|------|
| 状态 | ✅ 有效 / ❌ 无效 |
| 响应时间 | 连接建立耗时（毫秒）|
| 流畅度 | 评分 + 评级 |
| 归属地 | 省 / 城市 / 运营商 |
| 编码格式 | hls_live / hls / direct_stream 等 |

## 配置参数

「配置」标签页可调整：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 线程数 | 4 | 并发数，越高越快但占用带宽 |
| 最小流畅度 | 10 | 低于此分数将被过滤 |
| 超时(秒) | 15 | 单个链接最大等待时间 |
| 启用流畅度检测 | ✓ | 关闭后可跳过测速 |
| 启用直播流检测 | ✓ | 开启后进行完整直播判定 |
| 快速直播检测 | ✗ | 跳过切片监控，仅分析头部特征 |
| 严格验证 | ✓ | 额外验证切片可达性 |
| 域名黑名单 | — | 每行一个域名，匹配则跳过 |

## 项目结构

```
IPTV-tools/
├── main.py              # 入口，CustomTkinter 启动 + 主题设置
├── gui.py               # 三 Tab UI（导入源 / 测试结果 / 配置）
├── test_logic.py        # 网络请求、m3u8 分析、流畅度测试、播放列表解析
├── requirements.txt     # customtkinter, requests, fake-useragent, tqdm
├── build.spec           # PyInstaller 打包配置
├── config.json          # 运行时配置（首次运行自动生成）
└── ip2region_master/    # IP 归属地库（含 xdb 数据文件）
```

## 技术栈

- **UI** — [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- **网络** — requests + Session 连接池 + User-Agent 轮换
- **直播分析** — 自研 `StreamAnalyzer`，基于 m3u8 协议特征
- **流畅度** — 分段下载测速 + 缓冲比分析
- **归属地** — [ip2region](https://github.com/lionsoul2014/ip2region) XDB 离线查询
- **打包** — PyInstaller 单文件部署

## 关联

- 🌐 [iptv-search.com](https://iptv-search.com) — IPTV 直播源搜索、订阅管理、在线测试

## 常见问题

**Q: 测试很慢怎么办？**
A: 增大「线程数」，或关闭「流畅度检测」和「直播流检测」加速。

**Q: 「切片不可达」是什么意思？**
A: m3u8 播放列表中的切片文件返回 HTTP 错误，通常是源失效或被限速。

**Q: 归属地不准确？**
A: ip2region 默认约每月更新一次，可到 [iptv-search.com](https://iptv-search.com) 获取最新数据替换。

## 致谢

- [ip2region](https://github.com/lionsoul2014/ip2region)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
