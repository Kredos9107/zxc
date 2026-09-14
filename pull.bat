@echo off
setlocal
title PULL from github Kredos9107/zxc

set GIT=git
where git >nul 2>&1 || set GIT="C:\Program Files\Git\bin\git.exe"

cd /d "%~dp0"

for /f "delims=" %%b in ('%GIT% rev-parse --abbrev-ref HEAD') do set BRANCH=%%b

echo ================================================
echo   PULL
echo   repo   : %CD%
echo   branch : %BRANCH%
echo   remote : github.com/Kredos9107/zxc
echo ================================================
echo.

rem --- refuse to pull over uncommitted changes to tracked files ---
%GIT% diff --quiet && %GIT% diff --cached --quiet
if errorlevel 1 (
    echo ------------------------------------------------
    echo   You have uncommitted local changes:
    echo ------------------------------------------------
    %GIT% status --short
    echo.
    echo   Run push.bat first to save them, then pull.
    echo.
    pause
    exit /b 1
)

%GIT% fetch origin
if errorlevel 1 (
    echo.
    echo ------------------------------------------------
    echo   Could not reach GitHub. Run connect.bat and
    echo   check the SSH key, then try again.
    echo ------------------------------------------------
    echo.
    pause
    exit /b 1
)
echo.
echo Incoming commits:
%GIT% --no-pager log --oneline HEAD..origin/%BRANCH%
echo.
echo Your local commits not yet on the remote:
%GIT% --no-pager log --oneline origin/%BRANCH%..HEAD
echo.

%GIT% pull --rebase origin %BRANCH%
if errorlevel 1 (
    echo.
    echo ------------------------------------------------
    echo   REBASE STOPPED - there are conflicts.
    echo   Open Git Bash in this folder and either
    echo   resolve them, or roll back with:
    echo       git rebase --abort
    echo ------------------------------------------------
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================
echo   DONE. Last commits:
echo ================================================
%GIT% --no-pager log --oneline -5
echo.
pause
