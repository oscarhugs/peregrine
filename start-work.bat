@echo off
cd /d "%~dp0"
echo Pulling latest state...
git pull
echo.
echo Starting Claude Code...
claude
