#!/usr/bin/env bash
# Вызывается из pull.bat, когда git пишет
#   "untracked working tree files would be overwritten by merge/checkout".
#
# Причина: на другом компе файл переименовали, поменяв только регистр
# (Анмех.pdf -> АНМЕХ.pdf). Windows считает это одним и тем же файлом,
# а git для кириллицы - разными, и отказывается писать новое имя поверх старого.
#
# Лечение: убрать с диска старое имя, НО только если его содержимое
# совпадает и с последним коммитом, и с файлом на GitHub. Тогда git
# сам запишет ровно те же байты под новым именем - ничего не теряется.
# Путь помечается skip-worktree, чтобы pull --rebase не считал
# отсутствие файла "незакоммиченным изменением". При переходе на версию
# с GitHub старый путь уходит из индекса, и флаг исчезает сам.
#
#   fix-case.sh <ветка>   - убрать старые имена
#   fix-case.sh --undo    - вернуть всё как было (если повторный pull упал)

cd "$(dirname "$0")/.." || exit 2
LIST="$(git rev-parse --git-dir)/fix-case-paths"

if [ "$1" = "--undo" ]; then
  [ -f "$LIST" ] || exit 0
  while IFS= read -r p; do
    [ -n "$p" ] || continue
    if git ls-files --error-unmatch -- "$p" >/dev/null 2>&1; then
      git update-index --no-skip-worktree -- "$p"
      git checkout -- "$p" && echo "  возвращён: $p"
    fi
  done < "$LIST"
  rm -f "$LIST"
  exit 0
fi

BRANCH="${1:-main}"

low() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed \
    's/А/а/g;s/Б/б/g;s/В/в/g;s/Г/г/g;s/Д/д/g;s/Е/е/g;s/Ё/ё/g;s/Ж/ж/g;s/З/з/g;s/И/и/g;s/Й/й/g;s/К/к/g;s/Л/л/g;s/М/м/g;s/Н/н/g;s/О/о/g;s/П/п/g;s/Р/р/g;s/С/с/g;s/Т/т/g;s/У/у/g;s/Ф/ф/g;s/Х/х/g;s/Ц/ц/g;s/Ч/ч/g;s/Ш/ш/g;s/Щ/щ/g;s/Ъ/ъ/g;s/Ы/ы/g;s/Ь/ь/g;s/Э/э/g;s/Ю/ю/g;s/Я/я/g'
}

: > "$LIST"
fixed=0
while IFS=$'\t' read -r st old new; do
  [ -n "$new" ] || continue
  [ "$(low "$old")" = "$(low "$new")" ] || continue
  [ -f "$old" ] || continue
  disk=$(git hash-object -- "$old")
  head=$(git rev-parse -q --verify "HEAD:$old")
  remote=$(git rev-parse -q --verify "origin/$BRANCH:$new")
  if [ "$disk" = "$head" ] && [ "$head" = "$remote" ]; then
    rm -f -- "$old"
    git update-index --skip-worktree -- "$old"
    printf '%s\n' "$old" >> "$LIST"
    echo "  убран старый вариант имени: $old  (придёт как: $new)"
    fixed=$((fixed+1))
  else
    echo "  НЕ ТРОГАЮ $old - содержимое отличается от GitHub, разберись руками"
  fi
done < <(git diff --name-status -M "HEAD" "origin/$BRANCH")

[ "$fixed" -gt 0 ] || { rm -f "$LIST"; exit 1; }
exit 0
