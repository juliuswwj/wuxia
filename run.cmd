set PYTHONUTF8=1
cd \work\wuxia
:start
  python3 wait.py 8:30 16:30 00:30
  python3 main.py >>x:\wuxia.txt 2>&1
  if %errorlevel% neq 0 (
    timeout 30
    python3 main.py >>x:\wuxia.txt 2>&1
  )
  timeout 300
goto start
