@echo off
title GHCT - Generador de horarios (NO CERRAR mientras trabajas)
cd /d "%~dp0"
"%~dp0python\python.exe" "%~dp0aplicacion\iniciar.py"
echo.
echo La aplicacion se ha cerrado.
pause
