# -*- mode: python ; coding: utf-8 -*-
# Fichier généré automatiquement pour linux

block_cipher = None

a = Analysis(
    ['/home/jean-fred/Aligntester/AlignTester/scripts/launcher_standalone.py'],
    pathex=[],
    binaries=[],
    datas=[('/home/jean-fred/Aligntester/AlignTester/src/frontend/dist/index.html', 'frontend/dist'), ('/home/jean-fred/Aligntester/AlignTester/src/frontend/dist/assets/index-BukNB8xk.css', 'frontend/dist/assets'), ('/home/jean-fred/Aligntester/AlignTester/src/frontend/dist/assets/index-MenYDzCZ.js', 'frontend/dist/assets'), ('/home/jean-fred/Aligntester/AlignTester/src/frontend/dist/assets/react-KfUPlHYY.js', 'frontend/dist/assets'), ('/home/jean-fred/Aligntester/AlignTester/src/frontend/dist/assets/recharts-DoIYDS5t.js', 'frontend/dist/assets'), ('/home/jean-fred/Aligntester/AlignTester/src/frontend/dist/assets/vendors-B9ygI19o.js', 'frontend/dist/assets'), ('/home/jean-fred/Aligntester/AlignTester/src/backend/main.py', 'backend'), ('/home/jean-fred/Aligntester/AlignTester/src/backend/api/alignment_parser.py', 'backend/api'), ('/home/jean-fred/Aligntester/AlignTester/src/backend/api/alignment_state.py', 'backend/api'), ('/home/jean-fred/Aligntester/AlignTester/src/backend/api/diskdefs_parser.py', 'backend/api'), ('/home/jean-fred/Aligntester/AlignTester/src/backend/api/format_validator.py', 'backend/api'), ('/home/jean-fred/Aligntester/AlignTester/src/backend/api/greaseweazle.py', 'backend/api'), ('/home/jean-fred/Aligntester/AlignTester/src/backend/api/manual_alignment.py', 'backend/api'), ('/home/jean-fred/Aligntester/AlignTester/src/backend/api/routes.py', 'backend/api'), ('/home/jean-fred/Aligntester/AlignTester/src/backend/api/settings.py', 'backend/api'), ('/home/jean-fred/Aligntester/AlignTester/src/backend/api/track0_verifier.py', 'backend/api'), ('/home/jean-fred/Aligntester/AlignTester/src/backend/api/websocket.py', 'backend/api'), ('/home/jean-fred/Aligntester/AlignTester/src/backend/api/__init__.py', 'backend/api')],
    hiddenimports=[
        'uvicorn',
        'fastapi',
        'websockets',
        'pydantic',
        'pydantic_settings',
        'pyserial',
        'multipart',
    ],
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
    [],
    exclude_binaries=True,
    name='aligntester',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    name='aligntester',
)
