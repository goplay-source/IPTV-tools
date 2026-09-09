"""
IPTV 直播源测试逻辑层
开发维护: https://iptv-search.com

IPTV 直播源测试逻辑层
从原脚本提取核心检测逻辑，适配桌面UI调用。
"""

import os
import sys
import re
import time
import json
import threading
import socket
from urllib.parse import urlparse, urljoin, quote
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

# ── 路径适配（PyInstaller 兼容性）─────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    _BASE_DIR = sys._MEIPASS
else:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_ip2region_path = os.path.join(_BASE_DIR, "ip2region_master")
if _ip2region_path not in sys.path:
    sys.path.insert(0, _ip2region_path)

try:
    from binding.python.iptest import searchWithContent, load_xdb_file
    _XDB_LOADED = False
except ImportError as e:
    print(f"⚠️ ip2region 导入失败: {e}")
    searchWithContent = None
    load_xdb_file = None
    _XDB_LOADED = False


# ── 配置数据类 ────────────────────────────────────────────────────────────────
@dataclass
class TestConfig:
    """测试参数配置"""
    max_workers: int = 4
    min_fluency_score: int = 10
    timeout: int = 15
    check_fluency: bool = True
    check_live: bool = True
    quick_live_check: bool = False
    strict_validation: bool = True
    data_source_whitelist: List[str] = field(default_factory=lambda: [
        "http://REDACTED",
        "http://REDACTED",
    ])
    domain_blacklist: List[str] = field(default_factory=lambda: [
        "sc2022.stream-link.org", "live.v1.mk", "epg.pw", "em.21dtv.com", "cfss.cc",
        "dp.sxtv.top", "180.142.179.15", "histar.zapi.us.kg", "zw9999.cnstream.top:80",
        '117.27.190.42', 'tv.sd.cn', 'www.372583307.top', "103.95.24.37",
        "146.56.153.245", "hikvision.city", "hls.szsummer.cn", "cloud.yumixiu768.com",
        "ww.hanliu8.cn:9847", 'zy.otioi.cn', '61.10.2.141', '27.222.3.214',
        'tvbox6.com', 'aktv.top', '38.64.72.148:80', 'cdn.iptv8k.top', 'ku9.fr.to',
        'd2e1asnsl7br7b.cloudfront.net', 'wouu.net:9977', '122.152.202.33',
        'wo.xiang.lai.ge.bi.jiao.chang.de.yu.ming.wan.wan.jie.xi.bu.zhi.dao.ke.bu.ke.xing.hk3.345888.xyz.cdn.cloudflare.net',
        'www.freetv.top', '222.128.55.152', '61.221.215.25', 'l.cztvcloud.com',
        'live_bin.m16tv.cfd', '37.27.111.214', 'stream1.freetv.fun', '8.138.7.223',
        'ottiptv.cc', 'hebtv.com', 'event.pull.hebtv.com', 'ali-m-l.cztv.com',
        'www.douzhicloud.site', 'migu.188766.xyz', 'xtvantsc.xyz', 'tmxk.pp.ua',
        'breezy-audrie-zspace-7524863c.koyeb.app', 'mgev.188766.xyz', '115.150.63.77',
        'satellitepull.cnr.cn', '107.150.60.122', 'r.jdshipin.com', '74.91.26.218',
        '4gtv.cnlive.club', 'jnzq.ohoyee.com', 'docker.digital8.top'
    ])
    link_blacklist_patterns: List[str] = field(default_factory=list)
    allowed_ports: List[int] = field(default_factory=list)


# ── 频道数据类 ────────────────────────────────────────────────────────────────
@dataclass
class Channel:
    """频道基础信息"""
    name: str
    link_str: str
    group_name: str
    extvlcopt_lines: List[str] = field(default_factory=list)
    extinf_headers: Dict[str, str] = field(default_factory=dict)
    raw_extinf_line: Optional[str] = None
    page_url: str = ""

    # 测试结果
    is_valid: bool = False
    response_time: str = ""
    codec: Optional[str] = None
    final_url: str = ""
    fluency_score: Optional[int] = None
    fluency_level: Optional[str] = None
    bitrate_kbps: Optional[float] = None
    is_smooth: Optional[bool] = None
    location: str = "未测试"


# ── 全局状态 ─────────────────────────────────────────────────────────────────
_xdb_lock = threading.Lock()
_xdb_initialized = False


def init_xdb():
    """初始化 ip2region 数据库（线程安全）"""
    global _xdb_initialized
    if _xdb_initialized or load_xdb_file is None:
        return
    with _xdb_lock:
        if _xdb_initialized:
            return
        try:
            load_xdb_file()
            _xdb_initialized = True
        except Exception as e:
            print(f"⚠️ XDB 初始化失败: {e}")


# ════════════════════════════════════════════════════════════════════════════
# 以下代码从「新建 文本文档.txt」原脚本移植，未做功能修改
# ════════════════════════════════════════════════════════════════════════════

import random
import datetime
import gc
import tracemalloc
from collections import defaultdict

try:
    import zhconv
    HAS_ZHCONV = True
except ImportError:
    HAS_ZHCONV = False


def to_simplified(text):
    if not text or not HAS_ZHCONV:
        return text
    try:
        return zhconv.convert(text, 'zh-cn')
    except:
        return text


class StreamAnalyzer:
    def __init__(self):
        self.error_keywords = [
            'tokenerror', 'error.m3u8', 'advertisement', 'advert',
            'placeholder', 'offline', 'expired', 'invalid'
        ]
        self.live_markers = [
            '#EXT-X-MEDIA-SEQUENCE', '#EXT-X-TARGETDURATION',
            '#EXT-X-PLAYLIST-TYPE:EVENT', '#EXT-X-ALLOW-CACHE:NO',
            '#EXT-X-VERSION:3', '#EXT-X-VERSION:4'
        ]
        self.cache = {}

    def analyze_m3u8_content(self, content: str) -> dict:
        if not content:
            return {}
        lines = content.strip().split('\n')
        segments = [line for line in lines if line and not line.startswith('#')]
        extinf_lines = [line for line in lines if line.startswith('#EXTINF:')]
        durations = []
        for line in extinf_lines:
            match = re.search(r'#EXTINF:([\d\.]+)', line)
            if match:
                durations.append(float(match.group(1)))
        has_sequential_numbering = self._detect_sequential_filenames(segments)
        features = {
            'total_lines': len(lines),
            'total_segments': len(segments),
            'unique_segments': len(set(segments)),
            'avg_duration': sum(durations) / len(durations) if durations else 0,
            'durations_variation': len(set(durations)),
            'has_endlist': '#EXT-X-ENDLIST' in content,
            'has_media_sequence': any(marker in content for marker in ['#EXT-X-MEDIA-SEQUENCE', 'EXT-X-MEDIA-SEQUENCE:']),
            'has_target_duration': any(marker in content for marker in ['#EXT-X-TARGETDURATION', 'EXT-X-TARGETDURATION:']),
            'has_playlist_type': any(marker in content for marker in ['#EXT-X-PLAYLIST-TYPE:EVENT', 'EXT-X-PLAYLIST-TYPE:EVENT']),
            'segment_urls': segments[:20],
            'is_master_playlist': '#EXT-X-STREAM-INF' in content,
            'contains_error_keywords': any(keyword in content.lower() for keyword in self.error_keywords),
            'has_sequential_numbering': has_sequential_numbering
        }
        return features

    def _detect_sequential_filenames(self, segments):
        if len(segments) < 3:
            return False
        numbers = []
        for seg in segments:
            nums = re.findall(r'(\d+)', os.path.basename(seg))
            if nums:
                numbers.append(int(nums[-1]))
        if len(numbers) < 3:
            return False
        for i in range(1, len(numbers)):
            if numbers[i] <= numbers[i-1]:
                return False
        return True

    def detect_stream_type(self, features: dict) -> tuple:
        score = 0
        reasons = []
        if features.get('is_master_playlist'):
            if not features.get('has_endlist'):
                return True, 10, "直播流（主播放列表无ENDLIST）", ["主播放列表", "无ENDLIST"]
            else:
                return False, 10, "点播流（主播放列表包含ENDLIST）", ["主播放列表", "有ENDLIST"]
        if features.get('has_media_sequence'):
            if features.get('has_sequential_numbering'):
                score += 5
                reasons.append("媒体序列号+切片递增")
            else:
                score += 2
                reasons.append("媒体序列号(无递增)")
        if features.get('has_target_duration') and features.get('avg_duration', 0) > 0:
            score += 2
            reasons.append("包含目标时长")
        if not features.get('has_endlist'):
            score += 2
            reasons.append("未结束列表（直播特征）")
        else:
            score -= 2
            reasons.append("已结束列表（点播特征）")
        total_segs = features.get('total_segments', 0)
        if total_segs > 10:
            score += 2
            reasons.append(f"片段数量多({total_segs})")
        elif 3 <= total_segs <= 10:
            score += 1
            reasons.append(f"片段数量适中({total_segs})")
        if total_segs > 0:
            uniqueness_ratio = features.get('unique_segments', 0) / total_segs
            if uniqueness_ratio < 0.3 and total_segs > 5:
                score -= 3
                reasons.append(f"片段重复率高({uniqueness_ratio:.2f})")
        if features.get('contains_error_keywords'):
            score -= 5
            reasons.append("包含错误关键词")
        if score >= 4:
            return True, score, "直播流", reasons
        elif score <= -2:
            return False, score, "固定切片（点播）", reasons
        else:
            return None, score, "不确定", reasons

    def monitor_stream_changes(self, m3u8_url: str, headers: dict = None,
                               interval: float = 2, checks: int = 2) -> tuple:
        try:
            previous_segments = set()
            changes_detected = 0
            all_segments = []
            for i in range(checks):
                try:
                    response = request_with_retry(m3u8_url, timeout=5, headers=headers, retry_ua=True)
                    content = response.text
                    if any(keyword in content.lower() for keyword in self.error_keywords):
                        return False, 0, f"检测到错误页面"
                    lines = content.strip().split('\n')
                    current_segments = set(line for line in lines if line and not line.startswith('#'))
                    all_segments.append(current_segments)
                    if i > 0 and previous_segments:
                        new_segments = current_segments - previous_segments
                        removed_segments = previous_segments - current_segments
                        if new_segments or removed_segments:
                            changes_detected += 1
                        if current_segments == previous_segments:
                            if len(current_segments) <= 3:
                                return False, 0, f"固定循环({len(current_segments)}个片段)"
                    previous_segments = current_segments
                    if i < checks - 1:
                        time.sleep(interval)
                except Exception as e:
                    return False, 0, f"监控失败: {str(e)}"
            if changes_detected >= 1:
                return True, changes_detected, f"检测到{changes_detected}次变化"
            else:
                if len(all_segments) >= 2:
                    all_same = all(all_segments[0] == seg for seg in all_segments[1:])
                    if all_same:
                        return False, 0, "内容无变化"
                return True, 0, "内容稳定"
        except Exception as e:
            return False, 0, f"监控异常: {str(e)}"

    def comprehensive_live_check(self, stream_url: str, headers: dict = None,
                                 quick_check: bool = True) -> dict:
        result = {
            'url': stream_url,
            'is_live': False,
            'is_valid_stream': False,
            'stream_type': 'unknown',
            'confidence': 0,
            'reasons': [],
            'features': {},
            'final_verdict': '未检测'
        }
        try:
            response = request_with_retry(stream_url, timeout=5, headers=headers, retry_ua=True)
            if response.status_code != 200:
                result['reasons'].append(f"HTTP错误: {response.status_code}")
                return result
            content = response.text
            final_url = response.url
            if not content.startswith('#EXTM3U'):
                result['reasons'].append("非m3u8格式")
                return result
            if any(keyword in final_url.lower() for keyword in self.error_keywords):
                result['reasons'].append(f"重定向到错误页面: {final_url}")
                result['stream_type'] = 'error_redirect'
                return result
            features = self.analyze_m3u8_content(content)
            result['features'] = features
            is_live, confidence, stream_type, reasons = self.detect_stream_type(features)
            result['confidence'] = confidence
            result['reasons'].extend(reasons)
            if quick_check:
                result['is_live'] = is_live
                result['stream_type'] = stream_type
                result['is_valid_stream'] = is_live if is_live is not None else False
                result['final_verdict'] = f"快速检查: {stream_type}"
                return result
            is_live_monitor, changes, monitor_reason = self.monitor_stream_changes(
                stream_url, headers, interval=2, checks=2
            )
            result['reasons'].append(f"监控结果: {monitor_reason}")
            if is_live is False or is_live_monitor is False:
                result['is_live'] = False
                result['stream_type'] = 'vod_or_fixed'
                result['is_valid_stream'] = False
                result['final_verdict'] = "固定切片或点播"
            elif is_live is True or is_live_monitor is True:
                result['is_live'] = True
                result['stream_type'] = 'live'
                result['is_valid_stream'] = True
                result['final_verdict'] = "直播流"
            else:
                result['is_live'] = True
                result['stream_type'] = 'likely_live'
                result['is_valid_stream'] = True
                result['final_verdict'] = "疑似直播流"
            return result
        except Exception as e:
            result['reasons'].append(f"检测异常: {str(e)}")
            return result


global_analyzer = StreamAnalyzer()


# ── 请求工具 ──────────────────────────────────────────────────────────────────
try:
    from fake_useragent import UserAgent
    _ua_factory = UserAgent()
except ImportError:
    _ua_factory = None

_default_ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'


class OptimizedSession:
    def __init__(self):
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=20,
            pool_maxsize=100,
            max_retries=2
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers.update({
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        })

    def get(self, url, **kwargs):
        kwargs.setdefault('timeout', (5, 10))
        if 'headers' in kwargs:
            headers = kwargs['headers']
            if 'User-Agent' not in headers:
                headers['User-Agent'] = _default_ua
        return self.session.get(url, **kwargs)

    def head(self, url, **kwargs):
        kwargs.setdefault('timeout', (3, 5))
        if 'headers' in kwargs:
            headers = kwargs['headers']
            if 'User-Agent' not in headers:
                headers['User-Agent'] = _default_ua
        return self.session.head(url, **kwargs)


import requests
global_session = OptimizedSession()


def request_with_retry(url, headers=None, timeout=None, stream=False, method='get', retry_ua=True, **kwargs):
    if headers is None:
        headers = {}
    if 'User-Agent' not in headers:
        headers['User-Agent'] = _default_ua
    if timeout is None:
        timeout = (5, 10) if method == 'get' else (3, 5)
    session_method = getattr(global_session.session, method)
    try:
        response = session_method(url, headers=headers, timeout=timeout, stream=stream, **kwargs)
        if response.status_code < 400:
            return response
        if retry_ua:
            backup_headers = headers.copy()
            backup_headers['User-Agent'] = 'OKhttp/1.31'
            response = session_method(url, headers=backup_headers, timeout=timeout, stream=stream, **kwargs)
            return response
        else:
            return response
    except Exception as e:
        if retry_ua:
            backup_headers = headers.copy()
            backup_headers['User-Agent'] = 'OKhttp/1.31'
            try:
                response = session_method(url, headers=backup_headers, timeout=timeout, stream=stream, **kwargs)
                return response
            except Exception as e2:
                raise e2
        else:
            raise e


# ── 过滤配置 ──────────────────────────────────────────────────────────────────
unwanted_terms = ["🫓","大象","节目_10086","ipv6","🦌","🏔️ ","🦌","🐼 ","🐮","镧","🍜","🐦‍🔥","影院","2⃣ ","🍒","🌶","影院","🐉","🌾","🏛️","🌊","🏙️","🐬","线路","剧场","综合","vester","🇨🇳","频道","📡","🏆", "👉", "天下", "春盈", "免费", "IPV6","公告","永久","专线","影视",'🌏','🍁','台','V6','v6','☘️','🎬','🎥','🏀','📽','🪁','📺','💰','📡','🌊','🎮','🎵','🏛','直播',]

channel_filter_keywords = ["作者",'J2','Final']

excluded_keywords = ["免费","公告","永久","电影","广播","堆堆","虎牙","斗鱼","春晚","影视","少儿",'自留','湾湾全网','巴黎奥运','2V6','北京移动','全网','国际频道','小品','D J 歌 曲','狂','雪中悍刀行','产科医生','神雕英雄传','铁齿铜牙纪晓岚','尘封十三载','赤焰锦衣卫','纪录片','剧场','歌星金曲','D J 音乐','埋堆','斗鱼','虎牙','YY','哔哩','更新时间','香港','易看电视','教育','音乐','戏曲','影视解说','游戏','综艺','记录','纪录','测试','"国际','埋堆堆','轮播','AKTV','其他','经典剧场','付费','特色直播','电视剧','音乐','专享源','优质个源','儿童','SPORTS','定制','英语','明星','主题片','国际','动画片','MTV','收音机','以家人之名','温馨提示','轮播','易看','Fast','国外','点播','广播','直播中国','剧','️综艺','新闻女王','留言','难哄','打赏','卧底','爱奇艺','俄罗斯','电影','猫TV','中超','全运','万千','万辉','贺岁','直播','电台','演唱','晚会','回放','网页','童年','亮剑','雪豹','修仙','论剑','三国','大时代','流星花园','还珠','甄嬛','大地','经典','陈真','霍东','射雕','神雕','视觉','欣赏','4Gtv','MYTV','抖音','TG',
'电影','综艺','电视剧','纪录片','游戏','音乐','动漫','短剧','小品','相声','听书','老年','监控','抖音','YY','爱奇艺','埋堆堆','球帝','蜘蛛','zuqiu','[三网1]咪视界','[三网2]咪视界','[移动]咪视界','KK','九秀','齐齐','瑜伽裤','模特','车模','女团','热舞','Ai','钓鱼','乡野','脱口秀','沙雕动画','API随机点播','周杰伦歌曲点播','歌手合集点播','[三网1]咪视界','[三网2]咪视界','[移动]咪视界','[移动]BestTV','[三网]NewTV','[移动]NewTV','加入','群','抖音','DJ','music','私密','酒店','电信','联通','iptv','JD','央视3','央视频5','咪咕标清','今天','昨天','明天','注意','赛','解说','天威']


def normalize_channel_name(channel_name):
    pattern = r'^[Cc][c][t][v][-\s]?(1[0-7]|[1-9])([-\s]?[一-龥A-Za-z0-9]*)?$'
    match = re.match(pattern, channel_name, re.IGNORECASE)
    return f'CCTV{match.group(1)}' if match else channel_name


def clean_group_name(group_name):
    if not group_name:
        return group_name
    emoji_pattern = re.compile(r'['
        r'\U0001F1E0-\U0001F1FF'
        r'\U0001F300-\U0001F5FF'
        r'\U0001F600-\U0001F64F'
        r'\U0001F680-\U0001F6FF'
        r'\U0001F700-\U0001F77F'
        r'\U0001F800-\U0001F8FF'
        r'\U0001F900-\U0001F9FF'
        r'\U0001FA00-\U0001FA6F'
        r'\U0001FA70-\U0001FAFF'
        r'\U00002702-\U000027B0'
        r'\U000024C2-\U000024C2'
        r'\U0001F200-\U0001F251'
    ']', flags=re.UNICODE)
    for term in unwanted_terms:
        term = term.strip()
        if term:
            pattern = rf'\s*{re.escape(term)}\s*'
            group_name = re.sub(pattern, '', group_name)
    group_name = emoji_pattern.sub(r'', group_name)
    group_name = re.sub(r'\s+', ' ', group_name)
    return group_name.strip()


def should_filter_channel(channel_name, page_url, white_list):
    if page_url in white_list:
        return False
    channel_name_lower = channel_name.lower()
    for keyword in channel_filter_keywords:
        if keyword.lower() in channel_name_lower:
            return True
    return False


def should_filter_by_link(link_str, domain_blacklist, link_blacklist_patterns, allowed_ports):
    if not link_str:
        return True
    try:
        parsed = urlparse(link_str)
    except:
        return True

    if parsed.scheme not in ['http', 'https', 'rtmp']:
        return True

    domain = parsed.netloc.split(':')[0]
    if domain in domain_blacklist:
        return True

    if allowed_ports:
        port = parsed.port
        if port is not None and port not in allowed_ports:
            return True

    url_lower = link_str.lower()
    for pattern in link_blacklist_patterns:
        if re.search(pattern, url_lower):
            return True

    return False


# ── 流畅度测试 ────────────────────────────────────────────────────────────────
def test_stream_fluency(stream_url, headers=None, test_duration=5, min_bitrate=200,
                        max_buffer_ratio=0.5, min_download_bytes=262144):
    try:
        start_time = time.time()
        total_bytes = 0
        buffer_time = 0
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
        parsed_url = urlparse(stream_url)
        path_lower = parsed_url.path.lower()
        if path_lower.endswith('.m3u8') or '#EXTM3U' in stream_url:
            return test_hls_fluency(stream_url, headers, test_duration, min_bitrate, min_download_bytes)

        response = request_with_retry(
            stream_url,
            headers=headers,
            timeout=test_duration + 15,
            stream=True,
            retry_ua=True
        )
        if response.status_code != 200:
            return False, 0, 0, "HTTP错误"

        download_start = time.time()
        last_received_time = download_start
        chunk_size = 8192
        while True:
            try:
                chunk = next(response.iter_content(chunk_size=chunk_size))
                if not chunk:
                    break
                total_bytes += len(chunk)
                current_time = time.time()
                if current_time - last_received_time > 0.5:
                    buffer_time += current_time - last_received_time - 0.1
                last_received_time = current_time
                if current_time - download_start >= test_duration:
                    break
            except StopIteration:
                break
            except Exception:
                break
        response.close()

        actual_duration = min(time.time() - download_start, test_duration)
        if actual_duration <= 0:
            return False, 0, 0, "测试时长过短"
        if total_bytes < min_download_bytes:
            if total_bytes > 0 and (total_bytes * 8 / actual_duration) / 1024 >= min_bitrate:
                pass
            else:
                return False, 0, 0, f"下载量不足 ({total_bytes} < {min_download_bytes})"

        bitrate_kbps = (total_bytes * 8 / actual_duration) / 1024
        buffer_ratio = buffer_time / actual_duration if actual_duration > 0 else 1
        is_smooth = (bitrate_kbps >= min_bitrate) and (buffer_ratio <= max_buffer_ratio)

        bitrate_score = min(bitrate_kbps / 2000 * 50, 50)
        buffer_score = 50 - (buffer_ratio * 50)
        fluency_score = int(bitrate_score + buffer_score)
        fluency_score = max(0, min(100, fluency_score))

        if fluency_score >= 80:
            fluency_level = "优秀"
        elif fluency_score >= 60:
            fluency_level = "良好"
        elif fluency_score >= 40:
            fluency_level = "一般"
        else:
            fluency_level = "较差"

        return is_smooth, bitrate_kbps, fluency_score, fluency_level
    except Exception as e:
        return False, 0, 0, f"测试出错: {str(e)}"


def test_hls_fluency(m3u8_url, headers, test_duration, min_bitrate, min_download_bytes=262144):
    try:
        response = request_with_retry(m3u8_url, headers=headers, timeout=5, retry_ua=True)
        if response.status_code != 200:
            return False, 0, 0, "无法获取播放列表"
        playlist_content = response.text

        if '#EXT-X-STREAM-INF' in playlist_content:
            lines = playlist_content.strip().split('\n')
            best_bitrate = 0
            best_url = None
            for i, line in enumerate(lines):
                if '#EXT-X-STREAM-INF' in line:
                    codecs_match = re.search(r'CODECS="([^"]+)"', line)
                    if codecs_match:
                        codecs = codecs_match.group(1).lower()
                        if not ('avc1' in codecs or 'hvc1' in codecs or 'hevc' in codecs):
                            continue
                    bandwidth_match = re.search(r'BANDWIDTH=(\d+)', line)
                    if bandwidth_match:
                        bitrate = int(bandwidth_match.group(1))
                        if bitrate > best_bitrate and i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            if next_line and not next_line.startswith('#'):
                                best_bitrate = bitrate
                                best_url = next_line
            if best_url:
                if not best_url.startswith(('http://', 'https://')):
                    best_url = urljoin(m3u8_url, best_url)
                return test_hls_media_fluency(best_url, headers, test_duration, min_bitrate, min_download_bytes)
            else:
                return test_hls_media_fluency(m3u8_url, headers, test_duration, min_bitrate, min_download_bytes)
        else:
            return test_hls_media_fluency(m3u8_url, headers, test_duration, min_bitrate, min_download_bytes)
    except Exception as e:
        return False, 0, 0, f"HLS测试出错: {str(e)}"


def test_hls_media_fluency(m3u8_url, headers, test_duration, min_bitrate, min_download_bytes=262144):
    IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.ico')
    try:
        response = request_with_retry(m3u8_url, headers=headers, timeout=5, retry_ua=True)
        if response.status_code != 200:
            return False, 0, 0, "无法获取媒体列表"
        playlist_content = response.text
        lines = playlist_content.strip().split('\n')

        is_live = '#EXT-X-MEDIA-SEQUENCE' in playlist_content

        segment_urls = []
        segment_durations = []

        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('#EXTINF:'):
                match = re.search(r'#EXTINF:([\d.]+)', line)
                if match:
                    duration = float(match.group(1))
                    segment_durations.append(duration)
            elif line and not line.startswith('#') and i > 0:
                if any(line.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                    continue
                if not line.startswith(('http://', 'https://')):
                    if line.startswith('/'):
                        base_dir = m3u8_url.rsplit('/', 1)[0] + '/'
                        line = urljoin(base_dir, line.lstrip('/'))
                    else:
                        line = urljoin(m3u8_url, line)
                segment_urls.append(line)

        if not segment_urls:
            return False, 0, 0, "无有效片段"

        total_bytes = 0
        total_time = 0
        buffer_time = 0
        successful_segments = 0
        max_segments = min(10, len(segment_urls))

        for i in range(max_segments):
            try:
                segment_start = time.time()
                response = request_with_retry(
                    segment_urls[i],
                    headers=headers,
                    timeout=10,
                    stream=True,
                    retry_ua=True
                )
                if response.status_code == 200:
                    segment_bytes = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        segment_bytes += len(chunk)
                    total_bytes += segment_bytes
                    segment_time = time.time() - segment_start
                    total_time += segment_time
                    if i < len(segment_durations) and segment_time > segment_durations[i] * 1.5:
                        buffer_time += segment_time - segment_durations[i]
                    successful_segments += 1
                    if total_time >= test_duration:
                        break
                    response.close()
                else:
                    break
            except Exception:
                continue

        if successful_segments == 0:
            return False, 0, 0, "所有片段测试失败"

        if total_time > 0:
            bitrate_kbps = (total_bytes * 8 / total_time) / 1024
        else:
            bitrate_kbps = 0

        if is_live:
            effective_min_bytes = 262144
            if successful_segments > 0:
                pass
            else:
                if total_bytes < effective_min_bytes:
                    return False, 0, 0, f"下载量不足 ({total_bytes} < {effective_min_bytes})"
        else:
            if total_bytes < min_download_bytes:
                return False, 0, 0, f"下载量不足 ({total_bytes} < {min_download_bytes})"

        buffer_ratio = buffer_time / total_time if total_time > 0 else 1
        is_smooth = (bitrate_kbps >= min_bitrate) and (buffer_ratio <= 0.3)

        bitrate_score = min(bitrate_kbps / 2000 * 50, 50)
        buffer_score = 50 - (buffer_ratio * 50)
        fluency_score = int(bitrate_score + buffer_score)
        fluency_score = max(0, min(100, fluency_score))

        if fluency_score >= 80:
            fluency_level = "优秀"
        elif fluency_score >= 60:
            fluency_level = "良好"
        elif fluency_score >= 40:
            fluency_level = "一般"
        else:
            fluency_level = "较差"

        return is_smooth, bitrate_kbps, fluency_score, fluency_level

    except Exception as e:
        return False, 0, 0, f"媒体列表测试出错: {str(e)}"


# ── 链接测试 ──────────────────────────────────────────────────────────────────
_STRICT_ERROR_SIGNATURES = [
    'tokenerror', 'error.m3u8', 'expired', 'advert', 'placeholder',
    'offline', 'invalid', 'noconnection', 'stream not found', 'access denied',
    '不在线', '已停止', '未授权', '请联系'
]

_NON_MEDIA_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.txt', '.html',
    '.htm', '.css', '.js', '.json', '.xml', '.csv', '.php', '.asp', '.aspx',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.7z', '.tar', '.gz'
)

_MEDIA_SYNC_BYTES = {
    b'\x47': 'TS',
    b'\x00\x00\x01\xba': 'MPEG-PS',
    b'\x00\x00\x01\xb3': 'MPEG',
    b'\x66\x74\x79\x70': 'MP4'
}


def _is_likely_binary_stream(content_bin):
    if len(content_bin) < 1024:
        return False
    for sync, name in _MEDIA_SYNC_BYTES.items():
        if content_bin.startswith(sync):
            return True
    printable = sum(0x20 <= b <= 0x7e for b in content_bin[:2048])
    ratio = printable / len(content_bin[:2048]) if len(content_bin) > 0 else 0
    if ratio > 0.9:
        return False
    non_zero = sum(b != 0 for b in content_bin[:1024])
    if non_zero > 200 and ratio < 0.8:
        return True
    return False


def _extract_first_segment_url(content, base_url):
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            if not line.startswith(('http://', 'https://')):
                line = urljoin(base_url, line)
            return line
    return None


def _normalize_url(url):
    parsed = urlparse(url)
    safe_chars = "/?&=:#+"
    path_escaped = ''.join(
        ch if ch in safe_chars or ch.isalnum() else quote(ch)
        for ch in parsed.path
    )
    query_escaped = parsed.query
    if query_escaped:
        query_escaped = ''.join(
            ch if ch in "&=?#" or ch.isalnum() else quote(ch)
            for ch in query_escaped
        )
    return parsed._replace(path=path_escaped, query=query_escaped).geturl()


def enhanced_test_link_with_redirect(url, headers=None, max_redirects=5,
                                     strict_validation=False, check_fluency=False,
                                     check_live=True, quick_live_check=True):
    parsed = urlparse(url)
    if parsed.scheme in ('rtmp', 'rtmps'):
        start_time = datetime.datetime.now()
        host = parsed.hostname
        port = parsed.port or 1935
        try:
            sock = socket.create_connection((host, port), timeout=3)
            sock.close()
            end_time = datetime.datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            fluency_info = {'is_smooth': False, 'bitrate_kbps': 0, 'fluency_score': 0, 'fluency_level': 'RTMP连接成功', 'used_user_agent': None}
            return True, url, url, 'rtmp', f"{response_time:.2f} ms", fluency_info
        except Exception as e:
            end_time = datetime.datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            fluency_info = {'is_smooth': False, 'bitrate_kbps': 0, 'fluency_score': 0, 'fluency_level': f"RTMP连接失败: {e}", 'used_user_agent': None}
            return False, url, url, None, f"{response_time:.2f} ms", fluency_info
    try:
        original_url = url
        start_time = datetime.datetime.now()
        if headers is None:
            headers = {
                'User-Agent': 'OKhttp/1.31',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
        if 'Referer' not in headers:
            headers['Referer'] = urljoin(url, '/')
        if 'Origin' not in headers:
            headers['Origin'] = urljoin(url, '/').rstrip('/')

        normalized_url = _normalize_url(url)
        response = request_with_retry(
            normalized_url,
            headers=headers,
            timeout=(8, 15),
            stream=True,
            method='get',
            retry_ua=True,
            allow_redirects=True
        )
        final_url = response.url
        used_ua = headers.get('User-Agent')
        if not used_ua:
            used_ua = _default_ua

        if response.status_code != 200:
            end_time = datetime.datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            fluency_info = {'is_smooth': False, 'bitrate_kbps': 0, 'fluency_score': 0, 'fluency_level': "HTTP错误", 'used_user_agent': used_ua}
            return False, original_url, final_url, None, f"{response_time:.2f} ms", fluency_info

        parsed_final = urlparse(final_url.lower())
        path = parsed_final.path
        if any(path.endswith(ext) for ext in _NON_MEDIA_EXTENSIONS):
            end_time = datetime.datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            fluency_info = {'is_smooth': False, 'bitrate_kbps': 0, 'fluency_score': 0, 'fluency_level': "非媒体扩展名", 'used_user_agent': used_ua}
            return False, original_url, final_url, None, f"{response_time:.2f} ms", fluency_info

        content_type = response.headers.get('Content-Type', '').lower()
        video_content_types = [
            'video/mp4', 'video/x-matroska', 'video/x-msvideo', 'video/x-flv',
            'video/quicktime', 'video/x-ms-wmv', 'video/webm', 'video/mpeg',
            'video/mp2t', 'video/x-mpegts', 'video/vnd.dlna.mpeg-tts',
            'audio/aac', 'audio/mpeg', 'audio/mp4', 'audio/x-m4a'
        ]
        is_video_file = any(vct in content_type for vct in video_content_types)
        if not is_video_file:
            video_extensions = ['.ts', '.mp4', '.mkv', '.avi', '.flv', '.mov', '.wmv', '.webm', '.m4a', '.aac', '.m2ts']
            is_video_file = any(path.endswith(ext) for ext in video_extensions)
        if is_video_file:
            end_time = datetime.datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            fluency_info = {'is_smooth': False, 'bitrate_kbps': 0, 'fluency_score': 0, 'fluency_level': "媒体文件", 'used_user_agent': used_ua}
            return False, original_url, final_url, None, f"{response_time:.2f} ms", fluency_info

        MAX_READ = 65536
        content_chunks = []
        total_read = 0
        for chunk in response.iter_content(chunk_size=8192):
            content_chunks.append(chunk)
            total_read += len(chunk)
            if total_read >= MAX_READ:
                break
        response.close()
        content_bin = b''.join(content_chunks)
        try:
            content = content_bin.decode('utf-8', errors='ignore')
        except:
            content = ""

        is_valid_stream = False
        codec_name = None

        if '#EXTM3U' in content:
            lines = content.split('\n')
            non_comment_lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
            if not non_comment_lines:
                end_time = datetime.datetime.now()
                response_time = (end_time - start_time).total_seconds() * 1000
                fluency_info = {'is_smooth': False, 'bitrate_kbps': 0, 'fluency_score': 0, 'fluency_level': "无切片/子流", 'used_user_agent': used_ua}
                return False, original_url, final_url, None, f"{response_time:.2f} ms", fluency_info
            content_lower = content.lower()
            for sig in _STRICT_ERROR_SIGNATURES:
                if sig in content_lower:
                    end_time = datetime.datetime.now()
                    response_time = (end_time - start_time).total_seconds() * 1000
                    fluency_info = {'is_smooth': False, 'bitrate_kbps': 0, 'fluency_score': 0, 'fluency_level': f"包含错误特征({sig})", 'used_user_agent': used_ua}
                    return False, original_url, final_url, None, f"{response_time:.2f} ms", fluency_info
            first_seg = _extract_first_segment_url(content, final_url)
            if first_seg:
                try:
                    seg_resp = request_with_retry(first_seg, headers=headers, timeout=3, method='head', retry_ua=False)
                    if seg_resp.status_code >= 400:
                        end_time = datetime.datetime.now()
                        response_time = (end_time - start_time).total_seconds() * 1000
                        fluency_info = {'is_smooth': False, 'bitrate_kbps': 0, 'fluency_score': 0, 'fluency_level': "切片不可达", 'used_user_agent': used_ua}
                        return False, original_url, final_url, None, f"{response_time:.2f} ms", fluency_info
                except Exception:
                    end_time = datetime.datetime.now()
                    response_time = (end_time - start_time).total_seconds() * 1000
                    fluency_info = {'is_smooth': False, 'bitrate_kbps': 0, 'fluency_score': 0, 'fluency_level': "切片请求异常", 'used_user_agent': used_ua}
                    return False, original_url, final_url, None, f"{response_time:.2f} ms", fluency_info

        if not is_valid_stream:
            is_likely_direct_stream = False
            if any(vct in content_type for vct in ['application/octet-stream', 'video/mp2t', 'video/x-mpegts']):
                is_likely_direct_stream = True
            elif any(path.endswith(ext) for ext in ['.ts', '.m4s', '.mp4', '.mkv', '.m2ts']):
                is_likely_direct_stream = True
            elif not content.lstrip().startswith('#EXT'):
                if content_type.startswith('text/'):
                    is_likely_direct_stream = False
                elif path in ('/', '') and 'video/' not in content_type and 'audio/' not in content_type:
                    is_likely_direct_stream = False
                elif any(path.endswith(ext) for ext in _NON_MEDIA_EXTENSIONS):
                    is_likely_direct_stream = False
                else:
                    if _is_likely_binary_stream(content_bin):
                        is_likely_direct_stream = True
            if is_likely_direct_stream:
                if b'<html' not in content_bin.lower() and b'<!DOCTYPE' not in content_bin:
                    is_valid_stream = True
                    codec_name = "direct_stream"

        if not is_valid_stream and check_live and ('#EXTM3U' in content or '#EXTINF' in content):
            has_media_seq = '#EXT-X-MEDIA-SEQUENCE' in content
            if has_media_seq:
                is_valid_stream = True
                codec_name = "hls_live"
            else:
                live_check_result = global_analyzer.comprehensive_live_check(
                    final_url, headers, quick_check=quick_live_check
                )
                if live_check_result.get('is_valid_stream', False):
                    is_valid_stream = True
                    codec_name = "hls_live"
                else:
                    if ('#EXTM3U' in content and ('#EXTINF:' in content or '#EXT-X-STREAM-INF' in content)):
                        is_valid_stream = True
                        codec_name = "hls_vod"
                    else:
                        end_time = datetime.datetime.now()
                        response_time = (end_time - start_time).total_seconds() * 1000
                        fluency_info = {'is_smooth': False, 'bitrate_kbps': 0, 'fluency_score': 0, 'fluency_level': f"非直播({live_check_result.get('stream_type', 'unknown')})", 'used_user_agent': used_ua}
                        return False, original_url, final_url, None, f"{response_time:.2f} ms", fluency_info

        if not is_valid_stream:
            if '#EXTM3U' in content or '#EXTINF' in content:
                is_valid_stream = True
                codec_name = "hls"
                if strict_validation:
                    is_valid_stream = validate_playlist_by_testing_segments(final_url, headers, max_segments=1)
            elif '<html' not in content.lower() and '<body' not in content.lower():
                stream_content_types = ['video/', 'audio/', 'application/x-mpegurl', 'application/vnd.apple.mpegurl']
                if any(ct in content_type for ct in stream_content_types):
                    is_valid_stream = True
                    codec_name = "stream"
                else:
                    url_lower = final_url.lower()
                    stream_extensions = ['.m3u8', '.m3u']
                    if any(url_lower.endswith(ext) for ext in stream_extensions):
                        is_valid_stream = True
                        codec_name = "stream"

        end_time = datetime.datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000

        if is_valid_stream:
            if check_fluency:
                if codec_name in ("hls", "hls_live", "hls_vod"):
                    is_smooth, bitrate_kbps, fluency_score, fluency_level = test_hls_fluency(
                        final_url, headers, test_duration=3, min_bitrate=200
                    )
                else:
                    is_smooth, bitrate_kbps, fluency_score, fluency_level = test_stream_fluency(
                        final_url, headers=headers, test_duration=3,
                        min_bitrate=200, max_buffer_ratio=0.5
                    )
                fluency_info = {
                    'is_smooth': is_smooth,
                    'bitrate_kbps': round(bitrate_kbps, 2) if bitrate_kbps else 0,
                    'fluency_score': fluency_score,
                    'fluency_level': fluency_level,
                    'used_user_agent': used_ua
                }
                return True, original_url, final_url, codec_name, f"{response_time:.2f} ms", fluency_info
            else:
                fluency_info = {'is_smooth': None, 'bitrate_kbps': None, 'fluency_score': None, 'fluency_level': None, 'used_user_agent': used_ua}
                return True, original_url, final_url, codec_name, f"{response_time:.2f} ms", fluency_info
        else:
            fluency_info = {'is_smooth': False, 'bitrate_kbps': 0, 'fluency_score': 0, 'fluency_level': "无效流", 'used_user_agent': used_ua}
            return False, original_url, final_url, None, f"{response_time:.2f} ms", fluency_info
    except Exception as e:
        end_time = datetime.datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000
        fluency_info = {'is_smooth': False, 'bitrate_kbps': 0, 'fluency_score': 0, 'fluency_level': f"异常: {str(e)[:30]}", 'used_user_agent': None}
        return False, original_url, url, None, f"{response_time:.2f} ms", fluency_info


def validate_playlist_content(playlist_content, playlist_url):
    if not playlist_content:
        return False
    if '#EXTM3U' not in playlist_content:
        return False
    lines = playlist_content.strip().split('\n')
    has_extinf = any('#EXTINF:' in line for line in lines[:20])
    has_media_segments = any(
        line.strip() and not line.startswith('#') and '.' in line
        for line in lines[:30]
    )
    return has_extinf and has_media_segments


def validate_playlist_by_testing_segments(playlist_url, headers=None, max_segments=2):
    try:
        if headers is None:
            headers = {
                'User-Agent': _default_ua,
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
        response = request_with_retry(playlist_url, headers=headers, timeout=8, retry_ua=True)
        if response.status_code != 200:
            return False
        playlist_content = response.text
        if '#EXT-X-STREAM-INF' in playlist_content:
            lines = playlist_content.strip().split('\n')
            for i, line in enumerate(lines[:10]):
                if '#EXT-X-STREAM-INF' in line and i + 1 < len(lines):
                    sub_url = lines[i + 1].strip()
                    if sub_url and not sub_url.startswith('#'):
                        if not sub_url.startswith(('http://', 'https://')):
                            sub_url = urljoin(playlist_url, sub_url)
                        return validate_playlist_by_testing_segments(sub_url, headers, max_segments)
            return False
        lines = playlist_content.strip().split('\n')
        segment_urls = []
        for line in lines[:50]:
            line = line.strip()
            if line and not line.startswith('#'):
                if not line.startswith(('http://', 'https://')):
                    line = urljoin(playlist_url, line)
                segment_urls.append(line)
        if not segment_urls:
            return False
        test_count = min(max_segments, len(segment_urls))
        successful_tests = 0
        for i in range(test_count):
            try:
                seg_response = request_with_retry(segment_urls[i], headers=headers, timeout=3, method='head', retry_ua=False)
                if seg_response.status_code in [200, 301, 302, 303, 307, 308]:
                    successful_tests += 1
            except Exception:
                continue
        return successful_tests > 0
    except Exception:
        return False


def test_single_link_wrapper(link_part, extvlcopt_lines=None, extinf_headers=None,
                             strict_validation=False, check_fluency=False,
                             min_fluency_score=0, check_live=True, quick_live_check=True):
    headers = {}
    default_headers = {
        'User-Agent': _default_ua,
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    headers.update(default_headers)
    if extinf_headers:
        headers.update(extinf_headers)
    if extvlcopt_lines:
        for line in extvlcopt_lines:
            opt_headers = parse_extvlcopt_line(line)
            headers.update(opt_headers)
    if 'User-Agent' not in headers:
        headers['User-Agent'] = default_headers['User-Agent']
    return enhanced_test_link_with_redirect(
        link_part, headers=headers, strict_validation=strict_validation,
        check_fluency=check_fluency, check_live=check_live,
        quick_live_check=quick_live_check
    )


def parse_extvlcopt_line(line):
    headers = {}
    line = line.replace('#EXTVLCOPT:', '').strip()
    if 'http-user-agent=' in line:
        match = re.search(r'http-user-agent=([^,]+)', line)
        if match:
            headers['User-Agent'] = match.group(1).strip()
    if 'http-referrer=' in line:
        match = re.search(r'http-referrer=([^,]+)', line)
        if match:
            headers['Referer'] = match.group(1).strip()
    if 'http-header=' in line:
        match = re.search(r'http-header="([^"]+)"', line)
        if match:
            header_str = match.group(1)
            for header_line in header_str.split('\\r\\n'):
                if ':' in header_line:
                    key, value = header_line.split(':', 1)
                    headers[key.strip()] = value.strip()
    return headers


def parse_extinf_attributes(line):
    headers = {}
    if 'http-user-agent=' in line:
        match = re.search(r'http-user-agent="([^"]+)"', line)
        if match:
            headers['User-Agent'] = match.group(1)
    if 'http-referrer=' in line:
        match = re.search(r'http-referrer="([^"]+)"', line)
        if match:
            headers['Referer'] = match.group(1)
    return headers, line


# ── 解析器 ────────────────────────────────────────────────────────────────────
def parse_m3u_content(content, page_url):
    channels = []
    lines = content.splitlines()
    current_channel = None
    extvlcopt_lines = []
    raw_extinf_line = ""
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        if line.startswith('#EXTVLCOPT:'):
            extvlcopt_lines.append(line)
            continue
        if line.startswith('#EXTINF:'):
            if current_channel:
                current_channel['extvlcopt_lines'] = extvlcopt_lines.copy()
                channels.append(current_channel)
                extvlcopt_lines = []
            raw_extinf_line = line
            headers, cleaned_line = parse_extinf_attributes(line)
            channel_name = ""
            group_name = ""
            if ',' in cleaned_line:
                parts = cleaned_line.split(',', 1)
                channel_name = parts[1].strip()
                channel_name = to_simplified(channel_name)
                match = re.search(r'group-title="([^"]+)"', cleaned_line)
                if match:
                    group_name = match.group(1).strip()
                    group_name = to_simplified(group_name)
            current_channel = {
                'name': channel_name,
                'link_str': None,
                'group_name': group_name,
                'extvlcopt_lines': [],
                'page_url': page_url,
                'extinf_headers': headers,
                'raw_extinf_line': raw_extinf_line
            }
        elif not line.startswith('#') and current_channel:
            current_channel['link_str'] = line
            current_channel['extvlcopt_lines'] = extvlcopt_lines.copy()
            channels.append(current_channel)
            current_channel = None
            extvlcopt_lines = []
            raw_extinf_line = ""
    return channels


def parse_txt_content(content, page_url):
    channels = []
    lines = content.splitlines()
    group_name = ''
    for line in lines:
        line = line.strip()
        if '#genre#' in line:
            match = re.search(r'^(.*?),#', line)
            group_name = match.group(1).strip() if match else ''
            group_name = to_simplified(group_name)
        elif line.startswith('#'):
            continue
        elif line and ',' in line:
            line_parts = line.split(',')
            if len(line_parts) >= 2:
                name = normalize_channel_name(line_parts[0])
                name = to_simplified(name)
                link_str = line_parts[1].strip()
                channels.append({
                    'name': name,
                    'link_str': link_str,
                    'group_name': group_name,
                    'extvlcopt_lines': [],
                    'page_url': page_url,
                    'extinf_headers': {},
                    'raw_extinf_line': None
                })
    return channels


def is_valid_playlist_content(content):
    content = content.strip()
    if content.startswith('#EXTM3U'):
        lines = content.splitlines()
        has_extinf = any('#EXTINF:' in line for line in lines[:20])
        if has_extinf:
            return True, 'm3u'
    if '#genre#' in content:
        lines = content.splitlines()
        has_channels = any(',' in line and line.strip() and not line.startswith('#') for line in lines[:50])
        if has_channels:
            return True, 'txt'
    html_indicators = [
        '<!DOCTYPE html', '<html', '<body', '<head', '<meta', '<script',
        '<h1', '<title', 'html>', 'body>', '<div', 'cloudflare'
    ]
    content_lower = content.lower()
    for indicator in html_indicators:
        if indicator in content_lower:
            return False, 'html'
    if len(content) < 100:
        return False, 'too_short'
    return False, 'unknown'


# ── 频道处理入口 ──────────────────────────────────────────────────────────────
def process_channel_data(name, link_str, group_name, domain_blacklist, iptest_instance, page_url,
                         data_source_white_list, extvlcopt_lines=None, extinf_headers=None,
                         raw_extinf_line=None, max_workers=3, strict_validation=False,
                         check_fluency=False, min_fluency_score=0, check_live=True, quick_live_check=True):
    if page_url not in data_source_white_list:
        if should_filter_channel(name, page_url, data_source_white_list):
            return None
    if group_name:
        for keyword in excluded_keywords:
            if keyword in group_name:
                return None

    first_link = link_str.split('#')[0].strip() if '#' in link_str else link_str
    parsed_url = urlparse(first_link)
    domain = parsed_url.netloc.split(':')[0] if parsed_url.netloc else ''
    if domain in domain_blacklist:
        return None

    valid_links = split_and_test_links_parallel(
        link_str, extvlcopt_lines, extinf_headers, max_workers,
        strict_validation, check_fluency, min_fluency_score,
        check_live, quick_live_check,
        domain_blacklist=domain_blacklist
    )

    channel_extvlcopt_lines = []
    channel_extinf_headers = {}

    if not valid_links:
        return None

    link_info = valid_links[0]
    original_url = link_info['original_link']
    final_url = link_info['final_url']
    codec_name = link_info['codec_name']
    response_time_str = link_info['response_time_str']
    fluency_info = link_info.get('fluency_info', {})
    channel_extvlcopt_lines = link_info.get('extvlcopt_lines', [])
    channel_extinf_headers = link_info.get('extinf_headers', {})

    try:
        guishudi = iptest_instance.searchWithContent(final_url if final_url else original_url)
    except:
        guishudi = "未知"

    hk_keywords = ['港·澳·台', '中国港澳', 'HK', 'TW', '港', '澳', '湾', '全球', '體育', '加密', '国际体育', '港澳台','國會','戲劇','旅遊','運動','新聞','兒童','音樂','綜合','香港','Pdtv','特闽','特区','闽南','SXtv','Hktv','FYtv','Juli','NOW','风云','8528','mytv','央視','體育','綜合']
    is_hk_channel = any(k in group_name for k in hk_keywords)
    cleaned_name = clean_group_name(group_name)
    if is_hk_channel:
        cleaned_name = "中国港澳[可能需梯]"

    channel_data = {
        'name': name,
        'link': original_url,
        'final_link': final_url,
        'iptvgroup': cleaned_name,
        'speed': response_time_str,
        'check_date': datetime.datetime.now(),
        'codec': codec_name,
        'guishudi': guishudi,
        'is_hk_channel': is_hk_channel,
        'new_group_name': cleaned_name,
        'page_url': page_url,
        'extvlcopt_lines': channel_extvlcopt_lines,
        'extinf_headers': channel_extinf_headers,
        'raw_extinf_line': raw_extinf_line,
        'is_smooth': fluency_info.get('is_smooth'),
        'bitrate_kbps': fluency_info.get('bitrate_kbps'),
        'fluency_score': fluency_info.get('fluency_score'),
        'fluency_level': fluency_info.get('fluency_level')
    }
    return [channel_data]


def split_and_test_links_parallel(link_str, extvlcopt_lines=None, extinf_headers=None,
                                  max_workers=5, strict_validation=False, check_fluency=False,
                                  min_fluency_score=0, check_live=True, quick_live_check=True,
                                  domain_blacklist=None):
    valid_links = []
    if domain_blacklist is None:
        domain_blacklist = []

    if '#' in link_str:
        link_parts = [part.strip() for part in link_str.split('#') if part.strip()]
        filtered_parts = []
        for part in link_parts:
            if not should_filter_by_link(part, domain_blacklist, [], []):
                filtered_parts.append(part)
        if len(filtered_parts) > 5:
            filtered_parts = filtered_parts[:5]
        if not filtered_parts:
            return []
        with ThreadPoolExecutor(max_workers=min(max_workers, len(filtered_parts))) as executor:
            future_to_link = {
                executor.submit(test_single_link_wrapper, part, extvlcopt_lines,
                               extinf_headers, strict_validation, check_fluency,
                               min_fluency_score, check_live, quick_live_check): part
                for part in filtered_parts
            }
            for future in as_completed(future_to_link):
                link_part = future_to_link[future]
                try:
                    is_valid, original_url, final_url, codec_name, response_time_str, fluency_info = future.result()
                    if is_valid:
                        if check_fluency:
                            fluency_score = fluency_info.get('fluency_score', 0)
                            if fluency_score >= min_fluency_score:
                                valid_links.append({
                                    'original_link': original_url,
                                    'final_url': final_url,
                                    'is_valid': is_valid,
                                    'codec_name': codec_name,
                                    'response_time_str': response_time_str,
                                    'fluency_info': fluency_info,
                                    'extvlcopt_lines': extvlcopt_lines,
                                    'extinf_headers': extinf_headers
                                })
                                if len(valid_links) >= 1:
                                    break
                        else:
                            valid_links.append({
                                'original_link': original_url,
                                'final_url': final_url,
                                'is_valid': is_valid,
                                'codec_name': codec_name,
                                'response_time_str': response_time_str,
                                'fluency_info': fluency_info,
                                'extvlcopt_lines': extvlcopt_lines,
                                'extinf_headers': extinf_headers
                            })
                            if len(valid_links) >= 1:
                                break
                except Exception:
                    pass
    else:
        link_str = link_str.strip()
        if not link_str:
            return []
        if should_filter_by_link(link_str, domain_blacklist, [], []):
            return []
        is_valid, original_url, final_url, codec_name, response_time_str, fluency_info = test_single_link_wrapper(
            link_str, extvlcopt_lines, extinf_headers, strict_validation,
            check_fluency, min_fluency_score, check_live, quick_live_check
        )
        if is_valid:
            valid_links.append({
                'original_link': original_url,
                'final_url': final_url,
                'is_valid': is_valid,
                'codec_name': codec_name,
                'response_time_str': response_time_str,
                'fluency_info': fluency_info,
                'extvlcopt_lines': extvlcopt_lines,
                'extinf_headers': extinf_headers
            })
    return valid_links


# ════════════════════════════════════════════════════════════════════════════
# GUI 适配层
# ════════════════════════════════════════════════════════════════════════════

def test_channel_via_config(channel: Channel, config: TestConfig) -> Channel:
    """
    对单个频道执行完整测试，返回填充后的 Channel 对象。
    这是 GUI 调用的主要接口。
    """
    # 前置过滤
    if channel.group_name:
        for kw in excluded_keywords:
            if kw in channel.group_name:
                channel.is_valid = False
                channel.location = "被排除分组过滤"
                return channel

    first_link = channel.link_str.split('#')[0].strip() if '#' in channel.link_str else channel.link_str
    parsed = urlparse(first_link)
    domain = parsed.netloc.split(':')[0] if parsed.netloc else ''
    if domain in config.domain_blacklist:
        channel.is_valid = False
        channel.location = "域名黑名单"
        return channel

    # 调用核心测试
    result_list = process_channel_data(
        name=channel.name,
        link_str=channel.link_str,
        group_name=channel.group_name,
        domain_blacklist=config.domain_blacklist,
        iptest_instance=init_xdb(),
        page_url=channel.page_url,
        data_source_white_list=config.data_source_whitelist,
        extvlcopt_lines=channel.extvlcopt_lines,
        extinf_headers=channel.extinf_headers,
        raw_extinf_line=channel.raw_extinf_line,
        max_workers=2,
        strict_validation=config.strict_validation,
        check_fluency=config.check_fluency,
        min_fluency_score=config.min_fluency_score,
        check_live=config.check_live,
        quick_live_check=config.quick_live_check,
    )

    if not result_list:
        channel.is_valid = False
        channel.location = "测试失败/过滤"
        return channel

    data = result_list[0]
    channel.is_valid = True
    channel.response_time = data.get('speed', '')
    channel.codec = data.get('codec')
    channel.final_url = data.get('final_link', channel.link_str)
    channel.fluency_score = data.get('fluency_score')
    channel.fluency_level = data.get('fluency_level')
    channel.bitrate_kbps = data.get('bitrate_kbps')
    channel.is_smooth = data.get('is_smooth')
    channel.location = data.get('guishudi', '未知')
    return channel


def parse_source(content: str, page_url: str) -> List[Channel]:
    """解析播放列表内容，返回频道列表"""
    if '#EXTM3U' in content:
        raw = parse_m3u_content(content, page_url)
    else:
        raw = parse_txt_content(content, page_url)

    channels = []
    for r in raw:
        ch = Channel(
            name=r['name'],
            link_str=r['link_str'],
            group_name=r.get('group_name', ''),
            extvlcopt_lines=r.get('extvlcopt_lines', []),
            extinf_headers=r.get('extinf_headers', {}),
            raw_extinf_line=r.get('raw_extinf_line'),
            page_url=page_url,
        )
        channels.append(ch)
    return channels
