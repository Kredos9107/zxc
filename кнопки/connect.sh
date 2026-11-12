#!/usr/bin/env bash
# Поднимает ssh-agent (один на все окна), кладёт в него ключ и проверяет GitHub.
# Запускается из connect.bat, но можно вызвать и руками:  ./connect.sh

KEY="$HOME/.ssh/id_rsa"
ENVF="$HOME/.ssh/agent.env"

# скрипт лежит в подпапке "кнопки" - работаем с репозиторием этажом выше
cd "$(dirname "$0")/.." || exit 1

# подхватить уже запущенный агент, если он есть
[ -f "$ENVF" ] && . "$ENVF" >/dev/null 2>&1

if ! ssh-add -l >/dev/null 2>&1; then
    ssh-agent -s > "$ENVF"
    . "$ENVF" >/dev/null
    echo "запущен новый ssh-agent (PID $SSH_AGENT_PID)"
else
    echo "используется уже запущенный ssh-agent (PID $SSH_AGENT_PID)"
fi

ssh-add "$KEY"

echo
echo "--- ключи в агенте ---"
ssh-add -l

echo
echo "--- GitHub ---"
if git ls-remote origin >/dev/null 2>&1; then
    echo "OK: git@github.com:Kredos9107/zxc.git отвечает, ключ принят"
else
    echo "ОШИБКА: GitHub не принял ключ."
    echo "Посмотреть подробности:  ssh -vT git@github.com"
fi

echo
echo "--- репозиторий ---"
git status -sb
echo
echo "Готово. Это обычный Git Bash в папке репозитория."
