# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

versao = Path(SPECPATH, 'VERSION').read_text(encoding='utf-8').strip()

a = Analysis(
    ['data_structurer_etl.py'],
    pathex=[],
    binaries=[],
    datas=[('Borboleta.ico', '.')],
    hiddenimports=['tkcalendar', 'tkcalendar.backends', 'tkcalendar.backends.std', 'Bio', 'Bio.SeqIO', 'pandas', 'openpyxl'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name=f'Data_Structurer_v{versao}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Borboleta.ico'],
)
