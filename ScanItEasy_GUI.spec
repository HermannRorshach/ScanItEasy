# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ScanItEasy_GUI.py'],
    pathex=[],
    binaries=[],
    datas=[('light.png', '.'), ('dark.png', '.'), ('doc_decorations/Красная лента. Первая страница.png', 'doc_decorations'), ('doc_decorations/Синяя лента. Первая страница.png', 'doc_decorations'), ('doc_decorations/Уголок с красной лентой.png', 'doc_decorations'), ('doc_decorations/Уголок с синей лентой.png', 'doc_decorations')],
    hiddenimports=[],
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
    name='ScanItEasy_GUI',
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
)
