set PYTHONIOENCODING=utf-8

adb disconnect
python3 main.py >>..\wuxia.txt 2>&1
if %errorlevel% neq 0 (
taskkill /F /IM HD-Player.exe
timeout 30
python3 main.py >>..\wuxia.txt 2>&1
)
if %errorlevel% neq 0 (
taskkill /F /IM HD-Player.exe
timeout 30
python3 main.py >>..\wuxia.txt 2>&1
)
taskkill /F /IM HD-Player.exe
