@echo off
title KANA OMNI AGENT - Master Launcher
color 0B

echo ============================================================
echo    KANA OMNI AGENT: AUTO-SYNC & LAUNCHER
echo ============================================================

:: 1. Sinkronisasi Kode dari GitHub
echo [!] Sinkronisasi data dari GitHub...
git pull origin master --rebase
if %errorlevel% neq 0 (
    echo [!] Gagal pull data. Cek koneksi internet atau Token GitHub Anda.
)

:: 2. Proteksi & Perbaikan Venv
echo [!] Verifikasi Virtual Environment...
if not exist "venv\Scripts\activate.bat" (
    echo [!] Venv tidak ditemukan atau rusak. Membangun ulang...
    if exist venv ( rd /s /q venv )
    python -m venv venv
    call venv\Scripts\activate
    echo [!] Menginstal ulang dependensi (requirements.txt)...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

:: 3. Jalankan Aplikasi Utama
echo [!] Memulai KANA OMNI CLI...
echo ------------------------------------------------------------
python kana_cli.py

:: 4. Auto-Push setelah Exit (Opsional)
echo ------------------------------------------------------------
echo [!] Aplikasi ditutup. Apakah ingin menyimpan log/perubahan ke Cloud? (Y/N)
set /p push_choice="> "
if /i "%push_choice%"=="Y" (
    git add .
    git commit -m "Auto-update logs: %date% %time%"
    git push origin master
    echo [OK] Data tersimpan di GitHub.
)

echo [!] Selesai. Sampai jumpa di sesi berikutnya!
pause