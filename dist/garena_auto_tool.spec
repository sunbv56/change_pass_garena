# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['garena_auto_tool.py'],
    pathex=[],
    binaries=[],
    datas=[('bin', 'bin'), ('C:\\Users\\Acer\\AppData\\Local\\Programs\\Python\\Python311\\Lib\\site-packages\\customtkinter', 'customtkinter')],
    hiddenimports=[
                 'customtkinter', 
                 'requests',
                 'urllib3',
                 'charset_normalizer',
                 'idna',
                 'certifi'
             ],
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
    name='garena_auto_tool',
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
    icon=['icon.ico'],
)
