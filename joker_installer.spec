# -*- mode: python ; coding: utf-8 -*-
import shutil

block_cipher = None

# Check if UPX is available
has_upx = shutil.which('upx') is not None

# Explicitly list only the modules needed for the installer
hiddenimports = [
    'win32com.client',
    'win32com',
]

# Exclude unnecessary modules to reduce installer size
excludes = [
    # Scientific/Data packages
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'PIL',
    'Pillow',
    
    # Testing frameworks
    'pytest',
    'unittest',
    'test',
    'doctest',
    
    # IPython/Jupyter
    'IPython',
    'jupyter',
    'jupyter_client',
    'jupyter_core',
    'ipykernel',
    'jedi',
    'parso',
    'pygments',
    'traitlets',
    'decorator',
    'pickleshare',
    'wcwidth',
    'prompt_toolkit',
    'zmq',
    'tornado',
    
    # Not needed for installer
    'openai',
    'psutil',
    'pynput',
    'pyperclip',
    'tkinter',
    '_tkinter',
    
    # Documentation
    'pydoc',
    'pydoc_data',
    
    # Web frameworks
    'flask',
    'django',
]

a = Analysis(
    ['setup.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
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
    name='joker_installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=has_upx,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src\\icon.ico',
)
