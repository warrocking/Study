@echo off
setlocal
set PY=C:\Study\OpenCV\.venv\Scripts\python.exe
set SCRIPT=C:\Study\OpenCV\Code\server_client\publish_latest_result_to_server.py
if not exist "%PY%" (
  echo [ERROR] Python not found: %PY%
  pause
  exit /b 1
)
rem If server is running on another machine/domain, change this value.
set GAME_SERVER_URL=http://127.0.0.1:5000
set SHARE_EXPIRE_MINUTES=1440
"%PY%" "%SCRIPT%"
endlocal
