@echo off
setlocal enabledelayedexpansion
title PUSH to github Kredos9107/zxc

set GIT=git
where git >nul 2>&1 || set GIT="C:\Program Files\Git\bin\git.exe"

rem the buttons live in a subfolder - the repo is one level up
cd /d "%~dp0.."

for /f "delims=" %%b in ('%GIT% rev-parse --abbrev-ref HEAD') do set BRANCH=%%b

echo ================================================
echo   PUSH
echo   repo   : %CD%
echo   branch : %BRANCH%
echo   remote : github.com/Kredos9107/zxc
echo ================================================
echo.

%GIT% status --short
echo.

rem ---- anything to commit? (tracked changes OR untracked files) ----
set "DIRTY="
for /f "delims=" %%s in ('%GIT% status --porcelain') do set DIRTY=1

if not defined DIRTY (
    echo No local changes to commit.
    echo Checking for unpushed commits...
    echo.
    goto :dopush
)

set "MSG="
set /p MSG="Commit message (Enter = auto): "
if "!MSG!"=="" (
    for /f "tokens=1-3 delims=. " %%a in ("%DATE%") do set STAMP=%%a.%%b.%%c
    set MSG=update !STAMP! !TIME:~0,5!
)

echo.
%GIT% add -A
%GIT% commit -m "!MSG!"
if errorlevel 1 (
    echo.
    echo   Commit failed. Nothing was pushed.
    echo.
    pause
    exit /b 1
)
echo.

:dopush
%GIT% push origin %BRANCH% 2>"%TEMP%\pusherr.txt"
set PUSHCODE=%ERRORLEVEL%
type "%TEMP%\pusherr.txt"
if %PUSHCODE%==0 goto :ok

rem ---- which failure is it? ----
findstr /i /c:"exceeds GitHub's file size limit" "%TEMP%\pusherr.txt" >nul
if not errorlevel 1 goto :toobig
findstr /i /c:"GH001" "%TEMP%\pusherr.txt" >nul
if not errorlevel 1 goto :toobig
findstr /i /c:"Permission denied (publickey)" "%TEMP%\pusherr.txt" >nul
if not errorlevel 1 goto :nokey
findstr /i /c:"Could not read from remote repository" "%TEMP%\pusherr.txt" >nul
if not errorlevel 1 goto :nokey
findstr /i /c:"fetch first" "%TEMP%\pusherr.txt" >nul
if not errorlevel 1 goto :behind
findstr /i /c:"non-fast-forward" "%TEMP%\pusherr.txt" >nul
if not errorlevel 1 goto :behind

echo.
echo ------------------------------------------------
echo   Push failed for a reason this script does not
echo   recognise. Read the message above.
echo ------------------------------------------------
echo.
pause
exit /b 1

:nokey
echo.
echo ------------------------------------------------
echo   REJECTED: GitHub did not accept the SSH key.
echo   Run connect.bat and check what it prints,
echo   then run push.bat again.
echo ------------------------------------------------
echo.
pause
exit /b 1

:toobig
echo.
echo ------------------------------------------------
echo   REJECTED: a file over 100 MB is in the commits.
echo   GitHub will never accept it.
echo.
echo   Find the file in the message above, then in
echo   Git Bash untrack it (the file stays on disk):
echo       git rm --cached "path/to/big.pdf"
echo       git commit --amend -C HEAD
echo   Then run push.bat again.
echo ------------------------------------------------
echo.
pause
exit /b 1

:behind
echo.
echo ------------------------------------------------
echo   REJECTED: the remote has commits you do not
echo   have locally.
echo ------------------------------------------------
echo.
set "ANS="
set /p ANS="Rebase local commits on top of remote and retry? (y/n): "
if /i not "!ANS!"=="y" (
    echo Aborted. Nothing was changed.
    echo.
    pause
    exit /b 1
)

echo.
%GIT% pull --rebase origin %BRANCH%
if errorlevel 1 (
    echo.
    echo   REBASE STOPPED - conflicts. Open Git Bash:
    echo       git rebase --abort      to roll back
    echo.
    pause
    exit /b 1
)

echo.
%GIT% push origin %BRANCH%
if errorlevel 1 (
    echo.
    echo   Push failed again. Open Git Bash and look manually.
    echo.
    pause
    exit /b 1
)

:ok
echo.
echo ================================================
echo   DONE. Last commits:
echo ================================================
%GIT% --no-pager log --oneline -5
echo.
pause
