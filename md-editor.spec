# -*- mode: python ; coding: utf-8 -*-
# md-editor PyInstaller Configuration
# 打包配置说明：
# 1. 单文件模式：所有文件打包到一个 exe 中
# 2. 无窗口模式：不显示控制台窗口
# 3. 图标：使用 icon.png 作为程序图标

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src', 'src'),  # 包含前端文件
    ],
    hiddenimports=[
        # PyWebView 相关
        'pywebview',
        'pywebview.platforms.winforms',
        'pywebview.platforms.edgechromium',
        'pywebview.platforms.cef',
        # 系统托盘相关
        'pystray',
        # 图像处理相关
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        # 全局快捷键相关
        'pynput',
        'pynput.keyboard',
        'pynput.mouse',
        # PyQt5 相关
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.QtNetwork',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='md-editor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='md-editor',
)