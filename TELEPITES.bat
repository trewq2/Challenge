@echo off
title Palfy Python Challenge - Telepites
cd /d "%~dp0"

echo ==========================================
echo  PALFY PYTHON CHALLENGE - TELEPITES
echo ==========================================
echo.
echo A pygame csomag telepitese...
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    py -m pip install -r requirements.txt
) else (
    python -m pip install -r requirements.txt
)

echo.
echo Ha nem latsz hibauzenetet, a telepites kesz.
echo Ezutan inditsd el az INDITAS.bat fajlt.
echo.
pause
