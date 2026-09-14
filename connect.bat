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

start "" "%GITDIR%\git-bash.exe" --cd="%CD%" -c "eval $(ssh-agent -s) >/dev/null; ssh-add ~/.ssh/id_rsa; echo; echo '--- keys in agent ---'; ssh-add -l; echo; echo '--- github ---'; if git ls-remote origin >/dev/null 2>&1; then echo 'OK - GitHub reachable, key accepted'; else echo 'FAIL - GitHub refused the key'; fi; echo; echo '--- repo ---'; git status -sb; echo; exec bash -i"

exit /b 0
