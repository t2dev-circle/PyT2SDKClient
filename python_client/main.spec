# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('./3rd_license/PySide6 license', './3rd_license'),
	('./3rd_license/qtawesome license', './3rd_license'),
    ('./3rd_license/qt-material license', './3rd_license'),
    ('license.dat', '.'),
    ('t2_api.yaml', '.'),
	('_py_t2sdk_api.cp310-win_amd64.pyd', '.'),
    ('py_t2sdk_api.py', '.')],
    hiddenimports=['_py_t2sdk_api', 'py_t2sdk_api','charset_normalizer.md__mypyc', 'PySide6.QtGui', 'PySide6.QtCore', 'PySide6.QtWidgets', 'qt_material'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['markunsafe', 'tcl8', 'PySide6.QtNetwork'],
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
    name='PyT2SDKClient',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PyT2SDKClient',
)
