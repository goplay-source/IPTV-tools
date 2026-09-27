# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ip2region_master/data/ip2region.xdb', 'ip2region_master/data'),
    ],
    hiddenimports=[
        'ip2region_master.binding.python.iptest',
        'ip2region_master.binding.python.xdbSearcher',
    ],
    excludes=[
        'pandas', 'openpyxl', 'adddata', 'matplotlib', 'numpy',
        'IPython', 'jupyter', 'notebook',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='IPTVTester',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,       # 带控制台，方便看错误
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
