# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

IPTV直播源测试工具 — CustomTkinter 桌面应用，整合「新建 文本文档.txt」完整检测逻辑。支持 M3U/TXT 播放列表导入、链接有效性检测、直播流判定、流畅度评分、IP归属地查询，结果可筛选/排序/导出 M3U。

## 运行

```bash
pip install -r requirements.txt
python main.py
```

## 打包

```bash
pyinstaller build.spec
# 输出：dist/IPTVTester.exe（~22MB，含所有依赖）
```

## 文件结构

```
main.py              — 入口，CTk 启动，主题设置
test_logic.py        — 纯逻辑层：网络请求、m3u8分析、流畅度测试、播放列表解析
gui.py               — CustomTkinter 三 Tab UI（导入源/测试结果/配置）
requirements.txt     — 依赖声明：customtkinter, requests, fake-useragent, tqdm
build.spec           — PyInstaller 打包配置（含 ip2region.xdb 数据文件）
config.json          — 自动生成的运行时配置（程序首次运行创建）
ip2region_master/    — 归属地库（含 xdb 数据文件，不变）
```

## 核心架构

- `test_logic.py`：从原脚本移植完整检测逻辑（`enhanced_test_link_with_redirect`、`StreamAnalyzer`、`test_hls_fluency` 等），移除 `adddata.py` 数据库依赖和 Excel 输出。GUI 通过 `test_channel_via_config(channel, config)` 调用单个频道测试，通过 `parse_source(content, page_url)` 解析播放列表。
- `gui.py`：`IPTVApp` 类管理三 Tab UI，测试结果通过 `ThreadPoolExecutor` 在后台线程运行，结果通过 `master.after(0, callback)` 回主线程更新 UI。
- `ip2region_master` 路径通过 `__file__` 相对定位，PyInstaller 打包后兼容。

## 关键设计

- 线程安全：所有网络请求在工作线程，UI更新在主线程（`after(0, ...)`）
- 配置持久化：`config.json` 存储线程数、超时、开关等，程序启动自动加载
- 筛选/排序：客户端实现，不影响原始 `self.results` 列表
- CTkProgressBar 使用 `.set(value)` 而非 `.configure(value=...)`（customtkinter 6.0 API 差异）
