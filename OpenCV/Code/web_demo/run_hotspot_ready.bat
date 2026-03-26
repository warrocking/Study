@echo off
setlocal
set PY=C:\Study\OpenCV\.venv\Scripts\python.exe
set SCRIPT=C:\Study\OpenCV\Code\web_demo\run_hotspot_ready.py
if not exist "%PY%" (
  echo [ERROR] Python venv not found: %PY%
  pause
  exit /b 1
)
"%PY%" "%SCRIPT%"
endlocal
