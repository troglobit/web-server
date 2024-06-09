# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

# Ensure WINDIR is set
windir = os.environ.get('WINDIR', 'C:\\Windows')
system32 = os.path.join(windir, 'System32')

# Platform-specific pathex and binaries
if sys.platform == 'win32':
    pathex = [system32]
    binaries = [
        (os.path.join(system32, 'api-ms-win-core-path-l1-1-0.dll'), '.'),
        (os.path.join(system32, 'python312.dll'), '.')
    ]
else:
    pathex = []
    binaries = []

a = Analysis(
    ['webby.py'],
    pathex=pathex,
    binaries=binaries,
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='webby',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=True,
    upx_exclude=[],
    name='webby',
)
