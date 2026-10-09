@echo off
title Palfy Python Challenge
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py game.py
) else (
    python game.py
)

if errorlevel 1 (
    echo.
    echo A jatek nem indult el.
    echo Ha a pygame nincs telepitve, futtasd eloszor a TELEPITES.bat fajlt.
    echo.
    pause
)
