# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/ui/*', 'ui/'), ('src/languages/*', 'languages/'), ('src/icon/guu.png', 'icon'), ('C:/Program Files/OpenSSL-Win64/bin/libssl-1_1-x64.dll', '.'), ('C:/Program Files/OpenSSL-Win64/bin/libcrypto-1_1-x64.dll', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='guu',
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
    icon='src/icon/guu.ico',
)
