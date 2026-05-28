@echo off
SET GIT_PATH="C:\Program Files\Git\bin\git.exe"
echo [CULTIA Architect] Starting GitHub Sync...

%GIT_PATH% add .
%GIT_PATH% commit -m "update: enhanced cultural data and system logic"
%GIT_PATH% branch -M main
%GIT_PATH% push -u origin main

echo [CULTIA Architect] Sync Complete!
pause
