@echo off
title Installation - WinScreen
echo ============================================
echo  Installation des dependances Python
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR : Python n'est pas installe ou pas dans le PATH.
    echo Telechargez Python sur https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Installation de customtkinter, Pillow, mss et pywin32...
pip install customtkinter pillow mss pywin32

echo.
echo ============================================
echo  Installation terminee !
echo  Lancez lancer.bat pour demarrer le logiciel
echo ============================================
pause
