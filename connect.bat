@echo off
title CONNECT - ssh-agent + Git Bash (Kredos9107/zxc)

set "GITDIR=C:\Program Files\Git"
if not exist "%GITDIR%\git-bash.exe" (
    echo ERROR: Git for Windows not found at "%GITDIR%".
    echo Edit GITDIR at the top of this file.
    pause
    exit /b 1
)

cd /d "%~dp0"

start "" "%GITDIR%\git-bash.exe" --cd="%CD%" -c "./connect.sh; exec bash -i"

exit /b 0
