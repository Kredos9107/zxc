#!/usr/bin/env bash
# Поднимает ssh-agent (один на все окна), кладёт в него ключ аккаунта из github.conf
# и проверяет GitHub. Запускается из connect.bat, но можно вызвать и руками:  ./connect.sh

HERE="$(cd "$(dirname "$0")" && pwd)"
# GH_USER, GH_REPO, SSH_KEY
eval "$(tr -d '\r' < "$HERE/github.conf" | grep -E '^[A-Z_]+=')"
KEY="$HOME/.ssh/$SSH_KEY"
URL="git@github.com:$GH_USER/$GH_REPO.git"
ENVF="$HOME/.ssh/agent.env"

# скрипт лежит в подпапке "кнопки" - работаем с репозиторием этажом выше
cd "$HERE/.." || exit 1

if [ ! -f "$KEY" ]; then
    echo "Нет ключа $KEY - сначала запусти setup.bat (он создаст ключ и откроет GitHub)."
    exit 1
fi

# адрес репозитория и ключ - как в github.conf (в т.ч. для VS Code и обычного git)
if [ "$(git remote get-url origin 2>/dev/null)" != "$URL" ]; then
    git remote set-url origin "$URL" 2>/dev/null || git remote add origin "$URL"
    echo "origin -> $URL"
fi
git config core.sshCommand "ssh -o IdentitiesOnly=yes -i ~/.ssh/$SSH_KEY"

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
    echo "OK: $URL отвечает, ключ принят"
else
    echo "ОШИБКА: GitHub не ответил. Проверь, что репозиторий $GH_USER/$GH_REPO существует"
    echo "и ключ добавлен в аккаунт $GH_USER (setup.bat). Подробности:  ssh -vT git@github.com"
fi

echo
echo "--- репозиторий ---"
git status -sb
echo
echo "Готово. Это обычный Git Bash в папке репозитория."
