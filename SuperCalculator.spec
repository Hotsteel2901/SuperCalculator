# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# Detect platform and set correct binary name
if sys.platform == 'win32':
    calc_core_binary = ('calc_core.dll', '.')
elif sys.platform == 'darwin':
    # Check for architecture
    import platform
    arch = platform.machine()
    if arch in ('arm64', 'aarch64'):
        calc_core_binary = ('calc_core_aarch64.dylib', '.')
    else:
        calc_core_binary = ('calc_core_x86_64.dylib', '.')
else:  # Linux
    import platform
    arch = platform.machine()
    if arch in ('aarch64', 'arm64'):
        calc_core_binary = ('calc_core_aarch64.so', '.')
    else:
        calc_core_binary = ('calc_core_x86_64.so', '.')

a = Analysis(
    ['super_calc_bridged.py'],
    pathex=[],
    binaries=[calc_core_binary],
    datas=[],
    hiddenimports=[
        'numpy',
        'matplotlib',
        'tkinter',
        'calc_bridge',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SuperCalculator',
    debug=False,
    bootloader_ignore_signals=True,
    strip=False,
    upx=True,
    upx_exclude=['numpy', 'matplotlib', 'tkinter'],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='SuperCalculator.ico',
)
