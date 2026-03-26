@echo off
setlocal
set PY=C:\Study\OpenCV\.venv\Scripts\python.exe
set APP=C:\Study\OpenCV\Code\server_app\app.py
if not exist "%PY%" (
  echo [ERROR] Python not found: %PY%
  pause
  exit /b 1
)
set SERVER_HOST=0.0.0.0
set SERVER_PORT=5000
"%PY%" "%APP%"
endlocal
