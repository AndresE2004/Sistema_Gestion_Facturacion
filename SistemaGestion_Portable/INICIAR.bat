@echo off
chcp 65001 >nul
cls
echo ==================================================
echo SISTEMA DE GESTION DE SUSCRIPTORES Y FINANZAS
echo ==================================================
echo.
echo Licencia: MIT (Software Libre)
echo Version: 1.0.0 - Portable
echo.
echo Iniciando sistema...
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    echo.
    echo Por favor, instale Python desde:
    echo https://python.org
    echo.
    echo Asegurese de marcar "Add Python to PATH"
    echo durante la instalacion.
    echo.
    pause
    exit /b 1
)

echo Python detectado
echo.

REM Iniciar la aplicacion
python app/main_simple_fixed.py

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo iniciar la aplicacion
    echo.
    echo Verifique que todos los archivos esten presentes
    echo y que Python este correctamente instalado.
    echo.
    pause
)
