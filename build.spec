# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for YouTube MP3 GUI Downloader
Packages the app + all dependencies + FFmpeg binaries into a directory distribution.
"""

import sys
from pathlib import Path

block_cipher = None

# ── Collect all source files ──────────────────────────────────────────────────
a = Analysis(
    ['main.py'],
    pathex=['.', 'src'],
    binaries=[],
    datas=[
        # Bundle FFmpeg binaries inside _internal/ffmpeg/
        ('ffmpeg/ffmpeg.exe',   'ffmpeg'),
        ('ffmpeg/ffplay.exe',   'ffmpeg'),
        ('ffmpeg/ffprobe.exe',  'ffmpeg'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.extractor.youtube',
        'yt_dlp.postprocessor',
        'yt_dlp.postprocessor.ffmpeg',
        'packaging',
        'requests',
        'tqdm',
        'psutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'pytest_cov', 'coverage'],
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
    name='youtube-mp3-gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # No terminal window on launch
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='youtube-mp3-gui',
)
