"""
IPTV 直播源测试工具 — tkinter/ttk UI
"""

import os
import json
import threading
import queue
from typing import List
from tkinter import ttk, filedialog, messagebox, scrolledtext, BooleanVar, StringVar

from test_logic import (
    TestConfig,
    Channel,
    parse_source,
    test_channel_via_config,
    init_xdb,
    is_valid_playlist_content,
)


def _config_path() -> str:
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "config.json")


def _load_config() -> dict:
    path = _config_path()
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_config(cfg: dict):
    path = _config_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def _default_config() -> dict:
    return {
        "max_workers": 4,
        "min_fluency_score": 10,
        "timeout": 15,
        "check_fluency": True,
        "check_live": True,
        "quick_live_check": False,
        "strict_validation": True,
        "data_source_whitelist": [
            "http://REDACTED",
            "http://REDACTED",
        ],
        "domain_blacklist": [],
        "source_history": [],
    }


def _merge_config() -> dict:
    saved = _load_config()
    default = _default_config()
    merged = {**default, **saved}
    return merged


class IPTVApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=6)
        self.master = master
        self.master.title("IPTV直播源测试工具 v2.0 - iptv-search.com")

        style = ttk.Style()
        style.theme_use('clam')

        self.pack(fill='both', expand=True)

        self.channels: List[Channel] = []
        self.results: List[Channel] = []
        self.config: dict = _merge_config()
        self.testing = False
        self._paused = False
        self._stopped = False
        self._pending_queue = None
        self._results_queue = None
        self._workers = []
        self._filter_status = "all"
        self._filter_min_fluency = 0
        self._filter_location = ""
        self._sort_col = None
        self._sort_asc = True
        self._sources_used: List[str] = []

        init_xdb()

        # ── 顶栏 ──────────────────────────────────────────────────────────
        header = ttk.Frame(self)
        header.pack(fill='x', pady=(0, 4))
        ttk.Label(header, text="📡 IPTV直播源测试工具 v2.0", font=('Microsoft YaHei', 13, 'bold')).pack(side='left')
        ttk.Label(header, text="by iptv-search.com", font=('Microsoft YaHei', 9), foreground='#888888').pack(side='left', padx=(20, 0))
        ttk.Button(header, text="关于", width=6, command=self._show_about).pack(side='right', padx=10)

        # ── Tab 按钮 ──────────────────────────────────────────────────────
        tab_frame = ttk.Frame(self)
        tab_frame.pack(fill='x', pady=(0, 4))

        ttk.Button(tab_frame, text="📥 导入源", width=12,
                    command=lambda: self._switch_tab("import")).pack(side='left', padx=2)
        ttk.Button(tab_frame, text="✅ 测试结果", width=14,
                    command=lambda: self._switch_tab("results")).pack(side='left', padx=2)
        ttk.Button(tab_frame, text="⚙️ 配置", width=10,
                    command=lambda: self._switch_tab("config")).pack(side='left', padx=2)

        # ── Tab 内容区 ────────────────────────────────────────────────────
        self.tab_container = ttk.Frame(self)
        self.tab_container.pack(fill='both', expand=True)

        self.tab_import = ttk.Frame(self.tab_container)
        self.tab_results = ttk.Frame(self.tab_container)
        self.tab_config = ttk.Frame(self.tab_container)

        self._build_import_tab()
        self._build_results_tab()
        self._build_config_tab()
        self._switch_tab("import")

        # ── 操作栏 ────────────────────────────────────────────────────────
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', pady=(4, 2))

        self.btn_start = ttk.Button(btn_frame, text="▶ 开始测试", width=12,
                                     command=self._on_start_test)
        self.btn_start.pack(side='left', padx=4)

        self.btn_pause = ttk.Button(btn_frame, text="⏸ 暂停", width=8,
                                     command=self._on_toggle_pause, state='disabled')
        self.btn_pause.pack(side='left', padx=4)

        self.btn_stop = ttk.Button(btn_frame, text="⏹ 停止", width=8,
                                    command=self._on_stop_test, state='disabled')
        self.btn_stop.pack(side='left', padx=4)

        ttk.Button(btn_frame, text="💾 导出 M3U", width=12,
                    command=self._on_export_m3u).pack(side='left', padx=4)
        ttk.Button(btn_frame, text="📋 复制 M3U", width=12,
                    command=self._on_copy_m3u).pack(side='left', padx=4)
        ttk.Button(btn_frame, text="🗑 清空结果", width=12,
                    command=self._on_clear_results).pack(side='left', padx=4)

        # ── 进度条 ────────────────────────────────────────────────────────
        prog_frame = ttk.Frame(self)
        prog_frame.pack(fill='x', pady=(2, 2))

        self.progress_label = ttk.Label(prog_frame, text="等待测试",
                                         font=('Microsoft YaHei', 9))
        self.progress_label.pack(side='left', padx=4)

        self.progress_bar = ttk.Progressbar(prog_frame, mode='determinate', length=400)
        self.progress_bar.pack(side='left', padx=4, fill='x', expand=True)

        # ── 日志区 ────────────────────────────────────────────────────────
        log_frame = ttk.LabelFrame(self, text="📝 运行日志", padding=4)
        log_frame.pack(fill='both', expand=True, pady=(2, 0))

        ttk.Button(log_frame, text="清空", width=8,
                    command=self._clear_log).pack(anchor='e', padx=4)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=8,
                                                   font=('Consolas', 9),
                                                   state='disabled',
                                                   bg='#1e1e1e', fg='#d4d4d4')
        self.log_text.pack(fill='both', expand=True, padx=4, pady=(0, 4))


    def _show_about(self):
        """显示关于对话框"""
        import webbrowser
        msg = """IPTV直播源测试工具 v2.0

由 iptv-search.com 开发和维护

功能特性:
• 支持 M3U/TXT 播放列表导入
• 批量测试频道链接有效性
• 直播流检测与流畅度评分
• IP归属地查询
• 结果筛选/排序/导出

官方网站: https://iptv-search.com
"""
        result = messagebox.showinfo("关于", msg)
        if result == 'ok':
            webbrowser.open("https://iptv-search.com")

    def _switch_tab(self, tab_name):
        self.tab_import.pack_forget()
        self.tab_results.pack_forget()
        self.tab_config.pack_forget()
        if tab_name == "import":
            self.tab_import.pack(fill='both', expand=True)
        elif tab_name == "results":
            self.tab_results.pack(fill='both', expand=True)
            self._render_results()
        elif tab_name == "config":
            self.tab_config.pack(fill='both', expand=True)

    def _build_import_tab(self):
        url_frame = ttk.LabelFrame(self.tab_import, text="源地址", padding=8)
        url_frame.pack(fill='x', padx=4, pady=4)
        ttk.Label(url_frame, text="每行一个 URL，或逗号分隔多个：").pack(anchor='w')
        self.url_text = scrolledtext.ScrolledText(url_frame, height=5, font=('Consolas', 10))
        self.url_text.pack(fill='x', pady=4)
        btn_frame = ttk.Frame(url_frame)
        btn_frame.pack(fill='x', pady=4)
        ttk.Button(btn_frame, text="📁 选择本地文件", width=16,
                    command=self._on_select_file).pack(side='left', padx=4)
        ttk.Button(btn_frame, text="🔍 预览解析", width=16,
                    command=self._on_preview).pack(side='left', padx=4)
        ttk.Button(btn_frame, text="📂 加载历史源", width=16,
                    command=self._on_load_history).pack(side='left', padx=4)
        self.parse_info_label = ttk.Label(self.tab_import, text="", foreground='#B8860B',
                                           font=('Microsoft YaHei', 9))
        self.parse_info_label.pack(anchor='w', padx=8, pady=4)
        hist_frame = ttk.LabelFrame(self.tab_import, text="最近使用的源", padding=4)
        hist_frame.pack(fill='x', padx=4, pady=4)
        self.hist_label = ttk.Label(hist_frame, text="暂无历史记录", font=('Microsoft YaHei', 9))
        self.hist_label.pack(anchor='w', padx=4)

    def _build_results_tab(self):
        filter_frame = ttk.Frame(self.tab_results)
        filter_frame.pack(fill='x', padx=4, pady=4)
        ttk.Label(filter_frame, text="状态:").pack(side='left', padx=4)
        self.filter_status = ttk.Combobox(filter_frame, values=["全部", "✅ 有效", "❌ 无效"],
                                           width=10, state='readonly')
        self.filter_status.set("全部")
        self.filter_status.pack(side='left', padx=4)
        self.filter_status.bind('<<ComboboxSelected>>', lambda e: self._on_filter_change())
        ttk.Label(filter_frame, text="流畅度≥:").pack(side='left', padx=4)
        self.filter_fluency = ttk.Combobox(filter_frame,
                                            values=[str(i) for i in range(0, 101, 5)],
                                            width=6, state='readonly')
        self.filter_fluency.set("0")
        self.filter_fluency.pack(side='left', padx=4)
        self.filter_fluency.bind('<<ComboboxSelected>>', lambda e: self._on_filter_change())
        ttk.Label(filter_frame, text="归属地:").pack(side='left', padx=4)
        self.filter_location = ttk.Entry(filter_frame, width=15)
        self.filter_location.pack(side='left', padx=4)
        self.filter_location.bind('<Return>', lambda e: self._on_filter_change())
        ttk.Button(filter_frame, text="重置", width=6,
                    command=self._reset_filters).pack(side='left', padx=8)

        results_frame = ttk.Frame(self.tab_results)
        results_frame.pack(fill='both', expand=True, padx=4, pady=4)
        cols = ("状态", "频道名", "分组", "响应时间", "流畅度", "归属地", "编码")
        self.result_tree = ttk.Treeview(results_frame, columns=cols, show='headings', height=15)
        for col in cols:
            self.result_tree.heading(col, text=col,
                                      command=lambda c=col: self._on_sort(c, None))
            self.result_tree.column(col, width=100, anchor='center')
        self.result_tree.column("频道名", width=150, anchor='w')
        self.result_tree.column("归属地", width=100, anchor='w')
        # 配置颜色标签
        self.result_tree.tag_configure('valid', foreground='green')
        self.result_tree.tag_configure('invalid', foreground='red')
        self.result_tree.tag_configure('timeout', foreground='orange')
        self.result_tree.pack(fill='both', expand=True)
        self.result_tree.bind('<Double-1>', self._on_double_click_result)

    def _build_config_tab(self):
        # 右侧留空或使用其他配置项
        right = ttk.Frame(self.tab_config)
        right.pack(side='left', fill='both', expand=True, padx=(0, 4))

        # 测试参数标签框
        cfg_frame = ttk.LabelFrame(right, text="测试参数", padding=8)
        cfg_frame.pack(fill='both', expand=True)
        row = 0
        self.cfg_workers_var = StringVar(value="4")
        ttk.Label(cfg_frame, text="线程数：").grid(row=row, column=0, sticky='w', pady=4)
        ttk.Spinbox(cfg_frame, from_=1, to=50, textvariable=self.cfg_workers_var,
                     width=8).grid(row=row, column=1, padx=4)
        row += 1
        self.cfg_fluency_var = StringVar(value="10")
        ttk.Label(cfg_frame, text="最小流畅度：").grid(row=row, column=0, sticky='w', pady=4)
        ttk.Spinbox(cfg_frame, from_=0, to=100, textvariable=self.cfg_fluency_var,
                     width=8).grid(row=row, column=1, padx=4)
        row += 1
        self.cfg_timeout_var = StringVar(value="15")
        ttk.Label(cfg_frame, text="超时(秒)：").grid(row=row, column=0, sticky='w', pady=4)
        ttk.Spinbox(cfg_frame, from_=3, to=60, textvariable=self.cfg_timeout_var,
                     width=8).grid(row=row, column=1, padx=4)
        row += 1
        # 使用自定义复选框（显示 ✓/□ 符号）
        self.cfg_fluency_switch = BooleanVar(value=True)
        self.cfg_fluency_label = StringVar(value="✓ 启用流畅度检测")
        def toggle_fluency():
            val = self.cfg_fluency_switch.get()
            self.cfg_fluency_label.set("✓ 启用流畅度检测" if val else "□ 启用流畅度检测")
        self.cfg_fluency_switch.trace_add('write', lambda *args: toggle_fluency())
        fluency_lbl = ttk.Label(cfg_frame, textvariable=self.cfg_fluency_label,
                                 font=('Microsoft YaHei', 9), cursor='hand2')
        fluency_lbl.grid(row=row, column=0, columnspan=2, sticky='w', pady=4)
        fluency_lbl.bind('<Button-1>', lambda e: self.cfg_fluency_switch.set(not self.cfg_fluency_switch.get()))
        row += 1
        self.cfg_live_switch = BooleanVar(value=True)
        self.cfg_live_label = StringVar(value="✓ 启用直播流检测")
        def toggle_live():
            val = self.cfg_live_switch.get()
            self.cfg_live_label.set("✓ 启用直播流检测" if val else "□ 启用直播流检测")
        self.cfg_live_switch.trace_add('write', lambda *args: toggle_live())
        live_lbl = ttk.Label(cfg_frame, textvariable=self.cfg_live_label,
                              font=('Microsoft YaHei', 9), cursor='hand2')
        live_lbl.grid(row=row, column=0, columnspan=2, sticky='w', pady=4)
        live_lbl.bind('<Button-1>', lambda e: self.cfg_live_switch.set(not self.cfg_live_switch.get()))
        row += 1
        self.cfg_quick_switch = BooleanVar(value=False)
        self.cfg_quick_label = StringVar(value="□ 快速直播检测模式")
        def toggle_quick():
            val = self.cfg_quick_switch.get()
            self.cfg_quick_label.set("✓ 快速直播检测模式" if val else "□ 快速直播检测模式")
        self.cfg_quick_switch.trace_add('write', lambda *args: toggle_quick())
        quick_lbl = ttk.Label(cfg_frame, textvariable=self.cfg_quick_label,
                               font=('Microsoft YaHei', 9), cursor='hand2')
        quick_lbl.grid(row=row, column=0, columnspan=2, sticky='w', pady=4)
        quick_lbl.bind('<Button-1>', lambda e: self.cfg_quick_switch.set(not self.cfg_quick_switch.get()))
        row += 1
        self.cfg_strict_switch = BooleanVar(value=True)
        self.cfg_strict_label = StringVar(value="✓ 严格验证")
        def toggle_strict():
            val = self.cfg_strict_switch.get()
            self.cfg_strict_label.set("✓ 严格验证" if val else "□ 严格验证")
        self.cfg_strict_switch.trace_add('write', lambda *args: toggle_strict())
        strict_lbl = ttk.Label(cfg_frame, textvariable=self.cfg_strict_label,
                                font=('Microsoft YaHei', 9), cursor='hand2')
        strict_lbl.grid(row=row, column=0, columnspan=2, sticky='w', pady=4)
        strict_lbl.bind('<Button-1>', lambda e: self.cfg_strict_switch.set(not self.cfg_strict_switch.get()))

        # 域名黑名单
        bl_frame = ttk.LabelFrame(right, text="域名黑名单（每行一个域名）", padding=8)
        bl_frame.pack(fill='both', expand=True, pady=4)
        self.cfg_blacklist = scrolledtext.ScrolledText(bl_frame, height=8, font=('Consolas', 9))
        self.cfg_blacklist.pack(fill='both', expand=True)

        # 保存按钮放在底部整行
        btn_frame = ttk.Frame(self.tab_config)
        btn_frame.pack(fill='x', pady=(8, 0))
        ttk.Button(btn_frame, text="💾 保存配置", width=14,
                    command=self._on_save_config).pack(side='left', padx=4)
        ttk.Button(btn_frame, text="🔄 重置默认", width=14,
                    command=self._on_reset_config).pack(side='left', padx=4)

    def _load_config_to_ui(self):
        cfg = self.config
        self.cfg_blacklist.delete("1.0", "end")
        self.cfg_blacklist.insert("1.0", "".join(cfg.get("domain_blacklist", [])))
        history = cfg.get("source_history", [])
        if history:
            self.hist_label.configure(text=", ".join(history[-10:]))
        else:
            self.hist_label.configure(text="暂无历史记录")

    def _read_ui_config(self) -> TestConfig:
        return TestConfig(
            max_workers=int(self.cfg_workers_var.get() or 4),
            min_fluency_score=int(self.cfg_fluency_var.get() or 10),
            timeout=int(self.cfg_timeout_var.get() or 15),
            check_fluency=bool(self.cfg_fluency_switch.get()),
            check_live=bool(self.cfg_live_switch.get()),
            quick_live_check=bool(self.cfg_quick_switch.get()),
            strict_validation=bool(self.cfg_strict_switch.get()),
            domain_blacklist=[line.strip() for line in self.cfg_blacklist.get("1.0", "end-1c").split(chr(10)) if line.strip()],
        )

    def _on_save_config(self):
        cfg = self.config
        cfg["max_workers"] = int(self.cfg_workers_var.get() or 4)
        cfg["min_fluency_score"] = int(self.cfg_fluency_var.get() or 10)
        cfg["timeout"] = int(self.cfg_timeout_var.get() or 15)
        cfg["check_fluency"] = bool(self.cfg_fluency_switch.get())
        cfg["check_live"] = bool(self.cfg_live_switch.get())
        cfg["quick_live_check"] = bool(self.cfg_quick_switch.get())
        cfg["strict_validation"] = bool(self.cfg_strict_switch.get())
        cfg["data_source_whitelist"] = [line.strip() for line in self.cfg_whitelist.get('1.0', 'end-1c').split('\n') if line.strip()]
        _save_config(cfg)
        self._append_log("✅ 配置已保存")
        messagebox.showinfo("保存成功", "配置已保存到 config.json")

    def _on_reset_config(self):
        self.config = _default_config()
        _save_config(self.config)
        self._load_config_to_ui()
        self._append_log("🔄 配置已重置为默认值")
        messagebox.showinfo("重置成功", "配置已重置为默认值")

    def _on_select_file(self):
        filenames = filedialog.askopenfilenames(
            title="选择播放列表文件",
            filetypes=[("直播源文件", "*.m3u *.txt"), ("所有文件", "*.*")]
        )
        if filenames:
            for fpath in filenames:
                self._append_log(f"📁 选择文件: {os.path.basename(fpath)}")
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    is_valid, fmt = is_valid_playlist_content(content)
                    if not is_valid:
                        self._append_log(f"  ⚠️ 文件格式不支持: {fmt}")
                        continue
                    parsed = parse_source(content, fpath)
                    self.channels.extend(parsed)
                    self._append_log(f"  ✓ 解析到 {len(parsed)} 个频道 (格式: {fmt})")
                    if fpath not in self._sources_used:
                        self._sources_used.append(fpath)
                except Exception as e:
                    self._append_log(f"  ❌ 文件读取失败: {e}")
            self._update_parse_info()

    def _on_preview(self):
        content = self.url_text.get('1.0', 'end-1c').strip()
        if not content:
            messagebox.showwarning("提示", "请先输入源地址或选择文件")
            return
        sources = [s.strip() for s in content.replace(',', '\n').split('\n') if s.strip()]
        total = 0
        for src in sources:
            try:
                if src.startswith(('http://', 'https://')):
                    import requests
                    resp = requests.get(src, timeout=15, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    resp.raise_for_status()
                    content = resp.text
                    self._append_log(f"  📡 获取远程源: {src[:60]}... ({len(content)} 字节)")
                else:
                    with open(src, 'r', encoding='utf-8') as f:
                        content = f.read()
                is_valid, fmt = is_valid_playlist_content(content)
                if not is_valid:
                    self._append_log(f"  ⚠️ 格式无效: {fmt}")
                    continue
                parsed = parse_source(content, src)
                total += len(parsed)
                self.channels.extend(parsed)
                self._append_log(f"  ✓ {fmt} 格式，解析 {len(parsed)} 个频道")
                if src not in self._sources_used:
                    self._sources_used.append(src)
            except Exception as e:
                self._append_log(f"  ❌ 失败: {src[:50]}... → {e}")
        self._update_parse_info()
        if total > 0:
            messagebox.showinfo("预览完成", f"共解析到 {total} 个频道")

    def _on_load_history(self):
        history = self.config.get("source_history", [])
        if not history:
            messagebox.showinfo("提示", "暂无历史源记录")
            return
        dialog = ttk.Toplevel(self.master)
        dialog.title("选择历史源")
        dialog.geometry("400x300")
        listbox = scrolledtext.ScrolledText(dialog, height=10, font=('Consolas', 10))
        listbox.pack(fill='both', expand=True, padx=10, pady=10)
        for item in history:
            listbox.insert('end', item + '\n')
        def on_ok():
            selected = [s.strip() for s in listbox.get('1.0', 'end-1c').split('\n') if s.strip()]
            if selected:
                self.url_text.delete('1.0', 'end')
                self.url_text.insert('1.0', '\n'.join(selected))
                self._append_log(f"📂 已加载 {len(selected)} 条历史源")
            dialog.destroy()
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill='x', padx=10, pady=8)
        ttk.Button(btn_frame, text="确定", width=8, command=on_ok).pack(side='left', padx=4)
        ttk.Button(btn_frame, text="取消", width=8,
                    command=lambda: dialog.destroy()).pack(side='left', padx=4)

    def _update_parse_info(self):
        count = len(self.channels)
        if count > 0:
            self.parse_info_label.configure(text=f"✅ 已解析 {count} 个频道，可切换到「测试结果」标签页查看或开始测试")
        else:
            self.parse_info_label.configure(text="")

    def _on_start_test(self):
        if self.testing:
            messagebox.showwarning("提示", "测试正在进行中，请稍候...")
            return
        if not self.channels:
            messagebox.showwarning("警告", "没有可测试的频道，请先导入源")
            return
        config = self._read_ui_config()
        self.testing = True
        self._paused = False
        self._stopped = False
        self.results = []
        total = len(self.channels)
        completed = [0]
        valid_count = [0]
        self._pending_channels = list(self.channels)  # 待测频道列表

        # 工作函数
        def worker(worker_id):
            while True:
                # 检查停止
                if self._stopped:
                    break
                # 检查暂停
                if self._paused:
                    time.sleep(0.2)
                    continue
                # 取下一个频道
                if not self._pending_channels:
                    break
                ch = self._pending_channels.pop(0)
                try:
                    result = test_channel_via_config(ch, config)
                    with threading.Lock():
                        self.results.append(result)
                        completed[0] += 1
                        if result.is_valid:
                            valid_count[0] += 1
                    # 在主线程更新 UI
                    self.master.after(0, self._update_after_result, result, completed[0], total, valid_count[0])
                except Exception as e:
                    with threading.Lock():
                        completed[0] += 1
                    self._append_log(f"  ❌ 测试异常: {ch.name} → {e}")
                    self.master.after(0, lambda c=completed[0], t=total, v=valid_count[0]: self._check_complete(c, t, v))
                # 检查是否全部完成
                with threading.Lock():
                    if completed[0] >= total:
                        break

        # 启动工作线程
        self._workers = []
        for i in range(config.max_workers):
            t = threading.Thread(target=worker, args=(i,), daemon=True)
            t.start()
            self._workers.append(t)

        self.btn_start.configure(state='disabled', text="⏳ 测试中...")
        self.btn_pause.configure(state='normal')
        self.btn_stop.configure(state='normal')
        # 确保 UI 立即刷新
        self.master.after_idle(self._refresh_button_states)
        self._append_log(f"🚀 开始测试，共 {total} 个频道，线程数: {config.max_workers}")

    def _check_complete(self, completed, total, valid):
        """检查是否全部完成"""
        if completed >= total or self._stopped:
            self._on_tests_complete(valid, total)

    def _refresh_button_states(self):
        """确保按钮状态立即反映到界面上"""
        if self.testing:
            self.btn_start.configure(state='disabled', text="⏳ 测试中...")
            self.btn_pause.configure(state='normal')
            self.btn_stop.configure(state='normal')

    def _update_after_result(self, result, completed, total, valid):
        """在主线程中更新进度和表格"""
        if self._stopped:
            return
        status = "✓" if result.is_valid else "✗"
        self._append_log(
            f"[{completed}/{total}] {status} {result.name} | "
            f"{result.response_time} | {result.location}"
        )
        pct = completed / total * 100
        self.progress_bar['value'] = pct
        self.progress_label.configure(text=f"进度: {completed}/{total}  有效: {valid}")
        self._render_results()
        # 检查是否全部完成
        if completed >= total:
            self._on_tests_complete(valid, total)

    def _on_toggle_pause(self):
        """切换暂停/继续"""
        self._paused = not self._paused
        if self._paused:
            self.btn_pause.configure(text="▶ 继续")
            self._append_log("⏸ 测试已暂停")
        else:
            self.btn_pause.configure(text="⏸ 暂停")
            self._append_log("▶ 测试已继续")

    def _on_stop_test(self):
        """停止测试"""
        self._stopped = True
        self._paused = False
        self.btn_start.configure(state='normal', text="▶ 开始测试")
        self.btn_pause.configure(state='disabled')
        self.btn_stop.configure(state='disabled')
        self.master.after_idle(self._refresh_button_states_idle)
        self.progress_label.configure(text="已停止")
        self._append_log("⏹ 测试已停止")
        self._render_results()

    def _on_tests_complete(self, valid: int, total: int):
        self.testing = False
        self._stopped = False
        self.btn_start.configure(state='normal', text="▶ 开始测试")
        self.btn_pause.configure(state='disabled')
        self.btn_stop.configure(state='disabled')
        self.master.after_idle(self._refresh_button_states_idle)
        self.progress_label.configure(text=f"测试完成！有效: {valid}/{total}")
        self._append_log(f"🎉 测试完成，有效频道: {valid}/{total}")
        self._render_results()
        messagebox.showinfo("完成", f"测试完成\n有效频道: {valid}/{total}")

    def _render_results(self):
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        filtered = self._apply_filters()
        sorted_results = self._apply_sort(filtered)
        for ch in sorted_results:
            status_icon = "✅" if ch.is_valid else "❌"
            fluency_text = (
                f"{ch.fluency_score}/{ch.fluency_level}"
                if ch.fluency_score is not None else "未测试"
            )
            # 根据状态选择颜色标签
            if ch.is_valid:
                tag = 'valid'
            elif ch.response_time == '' or '失败' in ch.location or '过滤' in ch.location:
                tag = 'invalid'
            else:
                tag = 'timeout'
            self.result_tree.insert('', 'end', values=(
                status_icon,
                ch.name[:20],
                ch.group_name[:12],
                ch.response_time,
                fluency_text,
                ch.location[:14],
                ch.codec or "",
            ), tags=(tag,))
        self._append_log(f"📊 结果已刷新: {len(sorted_results)} 条显示 ({len(self.results)} 条总计)")

    def _apply_filters(self) -> List[Channel]:
        results = self.results
        if self._filter_status == "✅ 有效":
            results = [c for c in results if c.is_valid]
        elif self._filter_status == "❌ 无效":
            results = [c for c in results if not c.is_valid]
        if self._filter_min_fluency > 0:
            results = [c for c in results if (c.fluency_score or 0) >= self._filter_min_fluency]
        if self._filter_location:
            kw = self._filter_location.lower()
            results = [c for c in results if kw in c.location.lower()]
        return results

    def _apply_sort(self, results: List[Channel]) -> List[Channel]:
        if not self._sort_col:
            return results
        reverse = not self._sort_asc
        key_map = {
            "响应时间": lambda c: self._speed_to_num(c.response_time),
            "流畅度": lambda c: c.fluency_score or 0,
            "频道名": lambda c: c.name,
        }
        key_fn = key_map.get(self._sort_col, key_map["频道名"])
        return sorted(results, key=key_fn, reverse=reverse)

    @staticmethod
    def _speed_to_num(s: str) -> float:
        try:
            return float(s.replace(" ms", "").strip())
        except (ValueError, AttributeError):
            return 999999

    def _on_sort(self, col_key: str, btn):
        if self._sort_col == col_key:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col_key
            self._sort_asc = True
        self._render_results()

    def _on_filter_change(self, *args):
        self._filter_status = self.filter_status.get()
        self._filter_min_fluency = int(self.filter_fluency.get() or 0)
        self._filter_location = self.filter_location.get()
        self._render_results()

    def _reset_filters(self):
        self.filter_status.set("全部")
        self.filter_fluency.set("0")
        self.filter_location.delete(0, 'end')
        self._filter_status = "all"
        self._filter_min_fluency = 0
        self._filter_location = ""
        self._render_results()

    def _on_double_click_result(self, event):
        selection = self.result_tree.selection()
        if selection:
            item = self.result_tree.item(selection[0])
            name = item['values'][1]
            for ch in self.results:
                if ch.name == name:
                    self._copy_url(ch.link_str)
                    break

    def _copy_url(self, url: str):
        try:
            self.master.clipboard_clear()
            self.master.clipboard_append(url)
            self._append_log(f"📋 已复制: {url[:60]}...")
        except Exception:
            pass

    def _on_export_m3u(self):
        results = self._apply_filters()
        if not results:
            messagebox.showwarning("提示", "没有可导出的结果")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".m3u",
            filetypes=[("M3U Playlist", "*.m3u"), ("所有文件", "*.*")],
            title="导出 M3U"
        )
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("#EXTM3U\n")
                for ch in results:
                    if ch.is_valid:
                        group = ch.group_name or "未分组"
                        extra = ""
                        if ch.fluency_score is not None:
                            extra += f' fluency_score="{ch.fluency_score}"'
                        if ch.response_time:
                            extra += f' response_time="{ch.response_time}"'
                        f.write(f'#EXTINF:-1 group-title="{group}"{extra}, {ch.name}\n')
                        f.write(f'{ch.final_url or ch.link_str}\n')
            self._append_log(f"💾 已导出 M3U: {path} ({len(results)} 个有效频道)")
            messagebox.showinfo("导出成功", f"已导出 {len(results)} 个有效频道到:\n{path}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

    def _on_copy_m3u(self):
        results = self._apply_filters()
        if not results:
            messagebox.showwarning("提示", "没有可复制的结果")
            return
        lines = ["#EXTM3U"]
        for ch in results:
            if ch.is_valid:
                group = ch.group_name or "未分组"
                extra = ""
                if ch.fluency_score is not None:
                    extra += f' fluency_score="{ch.fluency_score}"'
                if ch.response_time:
                    extra += f' response_time="{ch.response_time}"'
                lines.append(f'#EXTINF:-1 group-title="{group}"{extra}, {ch.name}')
                lines.append(f'{ch.final_url or ch.link_str}')
        content = "\n".join(lines)
        try:
            self.master.clipboard_clear()
            self.master.clipboard_append(content)
            self._append_log(f"📋 已复制 M3U 到剪贴板 ({len(results)} 个频道)")
            messagebox.showinfo("复制成功", f"已复制 {len(results)} 个频道到剪贴板")
        except Exception as e:
            messagebox.showerror("复制失败", str(e))

    def _on_clear_results(self):
        self.results = []
        self.channels = []
        self._render_results()
        self.progress_bar['value'] = 0
        self.progress_label.configure(text="已清空")
        self._append_log("🗑 结果已清空")

    def _append_log(self, msg: str):
        def _do():
            self.log_text.configure(state='normal')
            self.log_text.insert('end', msg + '\n')
            self.log_text.configure(state='disabled')
            self.log_text.see('end')
        self.master.after(0, _do)

    def _clear_log(self):
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.configure(state='disabled')
