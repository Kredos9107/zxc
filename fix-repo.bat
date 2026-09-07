@echo off
setlocal
title FIX repo - drop large files from local history

set GIT=git
where git >nul 2>&1 || set GIT="C:\Program Files\Git\bin\git.exe"

cd /d "%~dp0"

echo ================================================
echo   FIX REPO
echo.
echo   GitHub refuses files over 100 MB.
echo   The folder "uchebniki" got into local commits
echo   and blocks every push.
echo.
echo   This script will:
echo     1. squash ALL local unpushed commits into one
echo     2. untrack everything listed in .gitignore
echo     3. make one clean commit
echo.
echo   Your files on disk are NOT deleted - only
echo   removed from git tracking.
echo ================================================
echo.

if not exist ".gitignore" (
    echo ERROR: .gitignore not found in %CD%
    echo Put it there first.
    pause
    exit /b 1
)

set "ANS="
set /p ANS="Proceed? (y/n): "
if /i not "%ANS%"=="y" (
    echo Aborted.
    pause
    exit /b 1
)

echo.
echo --- current local commits not on the remote ---
%GIT% fetch origin
%GIT% --no-pager log --oneline origin/main..HEAD
echo.

echo --- squashing them (files on disk untouched) ---
%GIT% reset --soft origin/main
if errorlevel 1 goto :fail

echo --- rebuilding the index with .gitignore applied ---
%GIT% rm -r --cached . -q
if errorlevel 1 goto :fail
%GIT% add -A
if errorlevel 1 goto :fail

echo.
echo --- what will be committed ---
%GIT% --no-pager diff --cached --stat
echo.

%GIT% commit -m "clean up: ignore large files, add lab 3.2.6"
if errorlevel 1 goto :fail

echo.
echo ================================================
echo   DONE. Now run push.bat
echo ================================================
echo.
pause
exit /b 0

:fail
echo.
echo ------------------------------------------------
echo   Something went wrong. Nothing was pushed.
echo   Open Git Bash and check:  git status
echo ------------------------------------------------
echo.
pause
exit /b 1
