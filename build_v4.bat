@echo off
echo ==============================================
echo  BUILDING NEURAL HUB V5.0 (TRUE TECH)
echo ==============================================

if exist build rd /s /q build
if exist dist rd /s /q dist
if exist Neural_Hub_v5.spec del /q Neural_Hub_v5.spec

echo Compiling...
.\.venv\Scripts\pyinstaller.exe --noconfirm --onefile --windowed ^
--name "Neural Hub v5" ^
--icon "icone_novo.ico" ^
--add-data "icone_novo.ico;." ^
--add-data "organizar_musicas.py;." ^
--add-data ".env;." ^
--hidden-import "mutagen" ^
--hidden-import "mutagen.easyid3" ^
--hidden-import "mutagen.flac" ^
--hidden-import "mutagen.wave" ^
--hidden-import "mutagen.aiff" ^
--hidden-import "customtkinter" ^
--hidden-import "google.generativeai" ^
--hidden-import "dotenv" ^
--hidden-import "requests" ^
--hidden-import "shutil" ^
--hidden-import "queue" ^
--hidden-import "certifi" ^
"launcher.py"

echo ==============================================
echo  BUILD COMPLETE! Check 'dist' folder.
echo ==============================================
pause
