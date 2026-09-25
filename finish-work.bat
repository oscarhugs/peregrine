@echo off
cd /d "%~dp0"
echo Staging changes...
git add -A
git status
echo.
set /p msg="Commit message (or press Enter for default): "
if "%msg%"=="" set msg=Update work session
git commit -m "%msg%"
git push
echo.
echo Done. Press any key to close.
pause >nul
