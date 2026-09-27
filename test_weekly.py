"""
Weekly M3U test pipeline:
  1. Fetch built-in source: https://cdn.jsdelivr.net/gh/Guovin/iptv-api@gd/output/result.m3u
  2. Parse all channels with test_logic.parse_source
  3. Run batch tests via ThreadPoolExecutor + test_channel_via_config
  4. Output all channels (regardless of test result), grouped, with playable-first ordering
  5. Write full M3U → channel.m3u + stats → test_report.json
"""

import sys
import os
import re
import json
import time
import logging
from datetime import datetime
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

# ── paths ─────────────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    _BASE = os.path.dirname(sys.executable)
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))

# ── logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
)
log = logging.getLogger('weekly')

# ── constants ─────────────────────────────────────────────────────────────────
BUILT_IN_SOURCE = "https://cdn.jsdelivr.net/gh/Guovin/iptv-api@gd/output/result.m3u"
OUTPUT_FILE = "channel.m3u"
# ip2region xdb ships with the repo checkout (ip2region_master/data/ip2region.xdb)
MAX_WORKERS = 8          # 8 threads is safe for a GitHub Actions runner
TIMEOUT = 20             # seconds per link test
MIN_FLUENCY = 10         # same default as GUI
PAGE_URL = BUILT_IN_SOURCE   # used as the "source page" identifier
MAX_URLS_PER_CHANNEL = 2     # dedup cap: max 2 links per (name, group)


# ── helpers ───────────────────────────────────────────────────────────────────
def fetch_source(url: str, dest: str = "tmp_source.m3u") -> str:
    """Download the M3U source to a local file and return its text content."""
    log.info("Fetching source: %s", url)
    resp = requests.get(url, timeout=60, stream=True)
    resp.raise_for_status()
    content = resp.content.decode('utf-8', errors='replace')
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(content)
    log.info("Fetched %d bytes → %s", len(content), dest)
    return content


def strip_tvg_meta(extinf_line: str) -> str:
    """Remove tvg-id attribute from a #EXTINF line, keep tvg-logo and group-title."""
    if not extinf_line:
        return ""
    line = re.sub(r'\s*tvg-id="[^"]*"', '', extinf_line)
    return line.strip()


def run_tests(channels, test_config) -> list:
    """Test all channels concurrently; return list of Channel objects with is_valid set."""
    from test_logic import test_channel_via_config, init_xdb
    init_xdb()
    results = []
    done = 0
    total = len(channels)
    t0 = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(test_channel_via_config, ch, test_config): i for i, ch in enumerate(channels)}
        for fut in as_completed(futures):
            i = futures[fut]
            try:
                ch = fut.result()
            except Exception as e:
                log.warning("Channel %d (%s) raised: %s", i, channels[i].name, e)
                ch = channels[i]
                ch.is_valid = False
            ch._idx = i  # stash original index
            results.append(ch)
            done += 1
            if done % 200 == 0:
                elapsed = time.time() - t0
                log.info("Progress: %d/%d (%.1f/s) — %.0fs elapsed", done, total, done / max(1, elapsed), elapsed)

    elapsed = time.time() - t0
    valid = sum(1 for r in results if r.is_valid)
    log.info("Done in %.1fs: %d/%d playable (%.1f%%)", elapsed, valid, total, 100.0 * valid / total if total else 0)
    return results


def dedup_and_group(channels: list) -> OrderedDict:
    """
    Output ALL channels grouped by group title.
    Playable channels come first within each group; dead ones follow.
    Max 2 links per (name, group) for playable; dead channels keep all original links.
    Returns OrderedDict[group_name, list[Channel]].
    """
    # Split into playable / not-playable, keeping per-channel counts
    playable = [c for c in channels if c.is_valid]
    dead = [c for c in channels if not c.is_valid]

    # Playable: dedup by (name, group), keep at most MAX_URLS_PER_CHANNEL
    seen = {}  # key: (name_lower, group) → count kept
    playable_kept = []
    for ch in playable:
        key = (ch.name.lower(), ch.group_name)
        count = seen.get(key, 0)
        if count < MAX_URLS_PER_CHANNEL:
            seen[key] = count + 1
            playable_kept.append(ch)
        # else: already at cap, skip the extra duplicate link

    # Dead: keep all, grouped
    all_channels_grouped = OrderedDict()

    for ch in playable_kept:
        all_channels_grouped.setdefault(ch.group_name, []).append(ch)

    for ch in dead:
        all_channels_grouped.setdefault(ch.group_name, []).append(ch)

    # Sort groups: playable count desc, then name
    group_stats = {g: (sum(1 for c in lst if c.is_valid), len(lst)) for g, lst in all_channels_grouped.items()}
    ordered = OrderedDict()
    for g, lst in sorted(all_channels_grouped.items(),
                        key=lambda kv: (-group_stats[kv[0]][0], kv[0].lower())):
        # Within group: playable first, then dead, both in original relative order
        group_playable = [c for c in lst if c.is_valid]
        group_dead = [c for c in lst if not c.is_valid]
        ordered[g] = group_playable + group_dead
    return ordered


def write_m3u(groups: OrderedDict, out_path: str, source: str, stats: dict):
    """Write the full M3U file (all channels, playable-first ordering)."""
    total = sum(len(v) for v in groups.values())
    lines = [
        '#EXTM3U',
        f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}',
        f'# Source: {source}',
        f'# Channels: {total} total — {stats["playable"]} playable, {total - stats["playable"]} unverified',
        f'# Playable channels are listed first within each group',
        f'# Groups: {len(groups)}',
    ]
    for group, chs in groups.items():
        for ch in chs:
            raw = ch.raw_extinf_line or f'#EXTINF:-1 group-title="{group}",{ch.name}'
            cleaned = strip_tvg_meta(raw)
            lines.append(cleaned)
            lines.append(ch.link_str)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    log.info("Wrote %d channels across %d groups → %s", total, len(groups), out_path)


def _build_config():
    """Build TestConfig with built-in source whitelisted."""
    from test_logic import TestConfig
    config = TestConfig(
        max_workers=MAX_WORKERS,
        timeout=TIMEOUT,
        min_fluency_score=MIN_FLUENCY,
        check_fluency=True,
        check_live=True,
        strict_validation=True,
    )
    config.data_source_whitelist.append(BUILT_IN_SOURCE)
    config.data_source_whitelist.append("https://raw.githubusercontent.com/Guovin/iptv-api/gd/output/result.m3u")
    return config


def main():
    import test_logic

    # ── config ────────────────────────────────────────────────────────────────
    config = _build_config()

    # ── 1. fetch ──────────────────────────────────────────────────────────────
    content = fetch_source(BUILT_IN_SOURCE)

    # ── 2. parse ─────────────────────────────────────────────────────────────
    channels = test_logic.parse_source(content, PAGE_URL)
    log.info("Parsed %d channels from source", len(channels))

    if not channels:
        log.error("No channels parsed — aborting")
        sys.exit(1)

    # ── 3. test all ──────────────────────────────────────────────────────────
    results = run_tests(channels, config)

    # ── 4. dedup & group (output ALL, playable-first) ───────────────────────
    groups = dedup_and_group(results)

    total = sum(len(v) for v in groups.values())
    playable = sum(1 for g in groups.values() for c in g if c.is_valid)

    stats = {
        'total': total,
        'playable': playable,
        'dead': total - playable,
    }

    # ── 5. write M3U ─────────────────────────────────────────────────────────
    write_m3u(groups, OUTPUT_FILE, BUILT_IN_SOURCE, stats)

    # ── 6. JSON report ──────────────────────────────────────────────────────
    report = {
        'generated_at': datetime.now().isoformat(),
        'source': BUILT_IN_SOURCE,
        'stats': stats,
        'groups': {g: {'total': len(chs), 'playable': sum(1 for c in chs if c.is_valid)}
                   for g, chs in groups.items()},
    }
    with open('test_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    log.info("Report → test_report.json")

    # cleanup temp files
    for tmp in ('tmp_source.m3u',):
        if os.path.exists(tmp):
            os.remove(tmp)
            log.info("Removed %s", tmp)


if __name__ == '__main__':
    main()
