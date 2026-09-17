@echo off
setlocal enabledelayedexpansion
title PULL from github Kredos9107/zxc

set GIT=git
where git >nul 2>&1 || set GIT="C:\Program Files\Git\bin\git.exe"

rem the buttons live in a subfolder - the repo is one level up
cd /d "%~dp0.."

rem --- ssh: point it at the key explicitly ---
rem Started from Explorer, Git's ssh garbles a Cyrillic user folder name
rem and then finds neither the key nor known_hosts ("authenticity of host
rem can't be established"). The 8.3 short name of the folder is plain ASCII.
for %%I in ("%USERPROFILE%") do set "UP=%%~sI"
set "UP=%UP:\=/%"
set GIT_SSH_COMMAND=ssh -i "%UP%/.ssh/id_rsa" -o UserKnownHostsFile="%UP%/.ssh/known_hosts"

set "GITBASH=C:\Program Files\Git\bin\bash.exe"

for /f "delims=" %%b in ('%GIT% rev-parse --abbrev-ref HEAD') do set BRANCH=%%b

echo ================================================
echo   PULL
echo   repo   : %CD%
echo   branch : %BRANCH%
echo   remote : github.com/Kredos9107/zxc
echo ================================================
echo.

rem  pull.bat force   -> go straight to the hard-reset path
if /i "%~1"=="force" goto :askforce

rem --- are there uncommitted changes to tracked files? ---
%GIT% diff --quiet && %GIT% diff --cached --quiet
if errorlevel 1 goto :dirty

:normal
%GIT% fetch origin
if errorlevel 1 goto :netfail
echo.
echo Incoming commits:
%GIT% --no-pager log --oneline HEAD..origin/%BRANCH%
echo.
echo Your local commits not yet on the remote:
%GIT% --no-pager log --oneline origin/%BRANCH%..HEAD
echo.

set CASEFIXED=
:dopull
%GIT% pull --rebase origin %BRANCH% 2>"%TEMP%\pullerr.txt"
set PULLCODE=%ERRORLEVEL%
type "%TEMP%\pullerr.txt"
if %PULLCODE%==0 (
    if exist ".git\fix-case-paths" del ".git\fix-case-paths"
    goto :ok
)

rem --- a real rebase with conflicts is in progress ---
if exist ".git\rebase-merge" goto :rebasefail
if exist ".git\rebase-apply" goto :rebasefail

rem --- the retry after a case fix failed too: put the old files back ---
if defined CASEFIXED (
    echo.
    echo --- retry failed, restoring the old file names ---
    "%GITBASH%" "%~dp0fix-case.sh" --undo
    goto :pullfail
)

rem --- file renamed on the other PC by changing only letter case? ---
findstr /i /c:"untracked working tree files would be overwritten by" "%TEMP%\pullerr.txt" >nul
if not errorlevel 1 goto :casefix
goto :pullfail

:casefix
set CASEFIXED=1
echo.
echo ------------------------------------------------
echo   A file was renamed on the other PC by changing
echo   only the letter case. Windows sees the old and
echo   new name as the same file, so git refuses.
echo   Removing the old copies (only if they are
echo   byte-identical to GitHub) and retrying...
echo ------------------------------------------------
"%GITBASH%" "%~dp0fix-case.sh" %BRANCH%
if errorlevel 1 goto :pullfail
echo.
goto :dopull

:pullfail
echo.
echo ------------------------------------------------
echo   PULL FAILED before anything was changed.
echo   Read the message above.
echo ------------------------------------------------
echo.
echo   [1] leave it
echo   [2] FORCE - take GitHub's version as-is
echo.
set "ANS="
set /p ANS="Choose 1 or 2: "
if "!ANS!"=="2" goto :askforce
echo.
echo Left as is.
echo.
pause
exit /b 1

:netfail
echo.
echo ------------------------------------------------
echo   Could not reach GitHub. Run connect.bat and
echo   check the SSH key, then try again.
echo ------------------------------------------------
echo.
pause
exit /b 1

:dirty
echo ------------------------------------------------
echo   You have uncommitted local changes:
echo ------------------------------------------------
%GIT% status --short
echo.
echo   [1] cancel  - nothing happens (then run push.bat to save them)
echo   [2] FORCE   - throw local changes away, take GitHub's version
echo.
set "ANS="
set /p ANS="Choose 1 or 2: "
if "!ANS!"=="2" goto :askforce
echo.
echo Aborted. Nothing was changed.
echo.
pause
exit /b 1

:rebasefail
echo.
echo ------------------------------------------------
echo   REBASE STOPPED - there are conflicts.
echo ------------------------------------------------
echo.
echo   [1] leave it - fix by hand in Git Bash
echo                  (git rebase --abort  to roll back)
echo   [2] FORCE    - abort the rebase and take GitHub's
echo                  version as-is
echo.
set "ANS="
set /p ANS="Choose 1 or 2: "
if "!ANS!"=="2" (
    %GIT% rebase --abort >nul 2>&1
    goto :askforce
)
echo.
echo Left as is. Open Git Bash in this folder.
echo.
pause
exit /b 1

rem ================================================
rem   FORCE: make the working copy identical to GitHub
rem ================================================
:askforce
echo.
echo ################################################
echo #  FORCE PULL
echo #
echo #  This makes branch %BRANCH% byte-for-byte the
echo #  same as github.com/Kredos9107/zxc:
echo #
echo #    - uncommitted edits      =^> thrown away
echo #    - new files not in git   =^> DELETED from disk
echo #    - local commits          =^> dropped from %BRANCH%
echo #
echo #  A safety copy is made first:
echo #    * local commits  =^> branch backup-^<sha^>
echo #    * uncommitted    =^> git stash
echo #  so nothing is truly lost, but do not rely on it.
echo ################################################
echo.
set "CONF="
set /p CONF="Type  FORCE  (capitals) to confirm, anything else cancels: "
if not "!CONF!"=="FORCE" (
    echo.
    echo Aborted. Nothing was changed.
    echo.
    pause
    exit /b 1
)

echo.
echo --- fetching ---
%GIT% fetch origin
if errorlevel 1 goto :netfail

%GIT% rev-parse --verify --quiet origin/%BRANCH% >nul
if errorlevel 1 (
    echo.
    echo   ERROR: branch %BRANCH% does not exist on GitHub.
    echo   Nothing was changed.
    echo.
    pause
    exit /b 1
)

set "BACKUPBRANCH="
set "STASHED="

rem --- save local commits that GitHub does not have ---
set AHEAD=0
for /f "delims=" %%c in ('%GIT% rev-list --count origin/%BRANCH%..HEAD') do set AHEAD=%%c
if not "!AHEAD!"=="0" (
    for /f "delims=" %%h in ('%GIT% rev-parse --short HEAD') do set SHA=%%h
    set "BACKUPBRANCH=backup-!SHA!"
    echo --- saving !AHEAD! local commit^(s^) to branch !BACKUPBRANCH! ---
    %GIT% branch -f !BACKUPBRANCH! HEAD
)

rem --- save uncommitted work (tracked edits + untracked files) ---
set "DIRTY="
for /f "delims=" %%s in ('%GIT% status --porcelain') do set DIRTY=1
if defined DIRTY (
    echo --- stashing uncommitted work ---
    %GIT% stash push -u -m "before force pull" >nul
    if not errorlevel 1 set "STASHED=1"
)

echo --- resetting %BRANCH% to origin/%BRANCH% ---
%GIT% reset --hard origin/%BRANCH%
if errorlevel 1 (
    echo.
    echo   reset failed. Nothing else was done.
    echo.
    pause
    exit /b 1
)

echo --- removing leftover files that are not in the repo ---
%GIT% clean -fd

echo.
echo ================================================
echo   DONE. This folder is now exactly what is on
echo   GitHub for branch %BRANCH%.
echo ================================================
if defined BACKUPBRANCH (
    echo   Old local commits kept in branch : !BACKUPBRANCH!
    echo     look at them :  git log !BACKUPBRANCH!
    echo     delete later :  git branch -D !BACKUPBRANCH!
)
if defined STASHED (
    echo   Uncommitted work kept in the stash:
    echo     look at it   :  git stash list
    echo     get it back  :  git stash pop
)
echo.
%GIT% --no-pager log --oneline -5
echo.
pause
exit /b 0

:ok
echo.
echo ================================================
echo   DONE. Last commits:
echo ================================================
%GIT% --no-pager log --oneline -5
echo.
pause
