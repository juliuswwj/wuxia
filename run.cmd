set PYTHONUTF8=1
cd \work\wuxia
:start
  adb disconnect
  python3 wait.py 4:30 8:30 12:30 16:30 20:30 00:30
  python3 main.py >>x:\wuxia.txt 2>&1
  if %errorlevel% neq 0 (
    taskkill /F /IM HD-Player.exe
    timeout 30
    python3 main.py >>x:\wuxia.txt 2>&1
  )
  if %errorlevel% neq 0 (
    taskkill /F /IM HD-Player.exe
    timeout 30
    python3 main.py >>x:\wuxia.txt 2>&1
  )
  taskkill /F /IM HD-Player.exe
  timeout 300
goto start
