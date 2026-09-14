@echo off
title CONNECT - ssh-agent + Git Bash (Kredos9107/zxc)

set "GITDIR=C:\Program Files\Git"
if not exist "%GITDIR%\git-bash.exe" (
    echo ERROR: Git for Windows not found at "%GITDIR%".
    echo Edit GITDIR at the top of this file.
    pause
    exit /b 1
)

rem bash starts in this folder (кнопки), runs the script, then steps up
rem into the repo itself and stays there as a normal interactive shell
start "" "%GITDIR%\git-bash.exe" --cd="%~dp0" -c "./connect.sh; cd ..; exec bash -i"

exit /b 0
