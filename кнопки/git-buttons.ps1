param([ValidateSet('push','pull','help','setup')][string]$Mode='help')
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Windows.Forms
$repo=Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $repo
$git=(Get-Command git -ErrorAction Stop).Source
# --- аккаунт и репозиторий: менять только в файле github.conf рядом с этим скриптом ---
$cfg=@{}
Get-Content -LiteralPath (Join-Path $PSScriptRoot 'github.conf') -Encoding UTF8 | ForEach-Object { if($_ -match '^\s*([A-Z_]+)\s*=\s*(.*?)\s*$'){ $cfg[$matches[1]]=$matches[2] } }
$ghUser=$cfg['GH_USER']; $ghRepo=$cfg['GH_REPO']; $keyName=$cfg['SSH_KEY']
$remoteUrl="git@github.com:$ghUser/$ghRepo.git"
$sshDir=Join-Path $env:USERPROFILE '.ssh'
$key=Join-Path $sshDir $keyName
$knownHosts=Join-Path $sshDir 'known_hosts'
$sshExe=Join-Path $env:SYSTEMROOT 'System32\OpenSSH\ssh.exe'
# IdentitiesOnly: предлагать GitHub только ключ этого аккаунта (старый id_rsa привязан к другому аккаунту)
$env:GIT_SSH_COMMAND='"'+$sshExe.Replace('\','/')+'" -o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -o IdentitiesOnly=yes -i "'+$key.Replace('\','/')+'" -o UserKnownHostsFile="'+$knownHosts.Replace('\','/')+'"'
$env:GIT_TERMINAL_PROMPT='0'
$env:GIT_MERGE_AUTOEDIT='no'
function Menu($title,$message,$choices) {
 $f=New-Object Windows.Forms.Form
 $f.Text=$title; $f.Width=760; $f.Height=500; $f.StartPosition='CenterScreen'
 $t=New-Object Windows.Forms.TextBox
 $t.Multiline=$true; $t.ReadOnly=$true; $t.ScrollBars='Vertical'; $t.SetBounds(15,15,710,250); $t.Text=$message
 $f.Controls.Add($t)
 $f.Tag=-1
 for($i=0;$i -lt $choices.Count;$i++) {
  $b=New-Object Windows.Forms.Button; $b.Text=$choices[$i]; $b.Tag=$i; $b.SetBounds(15,275+40*$i,710,35)
  $b.Add_Click({$this.FindForm().Tag=$this.Tag; $this.FindForm().Close()}); $f.Controls.Add($b)
 }
 [void]$f.ShowDialog(); $answer=[int]$f.Tag; $f.Dispose(); return $answer
}
function GitRun([string[]]$a) {
 $old=$ErrorActionPreference; $ErrorActionPreference='Continue'
 $script:output=(& $git -c core.quotepath=false @a 2>&1 | Out-String)
 $script:code=$LASTEXITCODE; $ErrorActionPreference=$old
}
function Must([string[]]$a) { GitRun $a; if($script:code -ne 0){throw $script:output} }
function Backup {
 $dest=Join-Path (Split-Path $repo -Parent) ('zxc-backups\'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
 [void](New-Item -ItemType Directory -Path $dest -Force)
 & robocopy $repo $dest /E /XJ /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
 if($LASTEXITCODE -ge 8){throw 'Не удалось сделать резервную копию. Изменения остановлены.'}
 $script:backup=$dest
 return $dest
}
function Network([string[]]$a) {
 while($true) {
  GitRun $a; if($script:code -eq 0){return}
  $reason='Не удалось связаться с GitHub. Проверь интернет и VPN, затем нажми «Повторить».'
  if($script:output -match 'Repository not found|does not appear to be a git repository'){ $reason="На GitHub нет репозитория $ghUser/$ghRepo или у ключа нет к нему доступа. Создай пустой репозиторий $ghRepo в аккаунте $ghUser (github.com/new) и нажми «Повторить»." }
  if($script:output -match 'publickey'){ $reason="GitHub не принял SSH-ключ для аккаунта $ghUser. Нажми «Настроить ключ» — ключ создастся (если его нет), скопируется, и откроется страница GitHub для добавления." }
  if($script:output -match 'Host key verification|REMOTE HOST IDENTIFICATION'){ $reason='Не удалось проверить подлинность GitHub. Проверку безопасности мы не отключаем. Открой справку GitHub о SSH и проверь запись known_hosts.' }
  if($script:output -match 'GH001|file size limit'){ $reason='В истории есть файл больше лимита GitHub. Простое удаление файла не уберёт его из старых коммитов. Отправка остановлена, локальная работа сохранена. Открой GitHub Desktop для просмотра неотправленных коммитов.' }
  $x=Menu 'Проблема подключения или отправки' ($reason+"`r`n`r`nПодробности:`r`n"+$script:output) @('Повторить','Настроить ключ (setup)','Закрыть — локальная работа сохранится')
  if($x -eq 1){Setup; continue}
  if($x -ne 0){throw 'Операция отменена. Локальные файлы сохранены.'}
 }
}
function Setup {
 if(!(Test-Path -LiteralPath $sshDir)){[void](New-Item -ItemType Directory -Path $sshDir -Force)}
 if(!(Test-Path -LiteralPath $key)) {
  $kg=Join-Path $env:SYSTEMROOT 'System32\OpenSSH\ssh-keygen.exe'
  $p=Start-Process -FilePath $kg -ArgumentList ('-q -t ed25519 -C "'+$ghUser+'@zxc" -N "" -f "'+$key+'"') -Wait -NoNewWindow -PassThru
  if($p.ExitCode -ne 0 -or !(Test-Path -LiteralPath ($key+'.pub'))){throw 'Не удалось создать SSH-ключ.'}
 }
 $pub=(Get-Content -LiteralPath ($key+'.pub') -Raw).Trim()
 [Windows.Forms.Clipboard]::SetText($pub)
 Start-Process 'https://github.com/settings/ssh/new'
 $msg="Открылась страница GitHub «Add new SSH key».`r`n`r`n1. Проверь, что вошёл в аккаунт $ghUser (аватар справа вверху).`r`n2. Title — любое название, например «ноутбук».`r`n3. Key — нажми Ctrl+V: публичный ключ уже скопирован.`r`n4. Нажми «Add SSH key» и вернись сюда.`r`n`r`nПубличный ключ (его показывать можно; файл без .pub — секретный, его никому не отправляй):`r`n$pub"
 while($true) {
  $x=Menu 'Настройка SSH-ключа' $msg @('Ключ добавлен — проверить','Открыть страницу ещё раз','Закрыть')
  if($x -eq 1){[Windows.Forms.Clipboard]::SetText($pub); Start-Process 'https://github.com/settings/ssh/new'; continue}
  if($x -ne 0){return}
  $old=$ErrorActionPreference; $ErrorActionPreference='Continue'
  $out=(& $sshExe -o BatchMode=yes -o ConnectTimeout=15 -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$knownHosts" -i "$key" -T git@github.com 2>&1 | Out-String)
  $ErrorActionPreference=$old
  if($out -match ('Hi '+[regex]::Escape($ghUser)+'!')){[void](Menu 'Готово' "Ключ работает: GitHub узнал аккаунт $ghUser.`r`nТеперь можно нажимать PUSH / PULL." @('Закрыть')); return}
  if($out -match 'Hi ([^!]+)!'){$msg="Этот ключ привязан к другому аккаунту: $($matches[1]). Удали его там (Settings → SSH keys) и добавь в $ghUser.`r`n`r`n"+$out; continue}
  $msg="GitHub пока не принял ключ. Проверь, что он добавлен в аккаунт $ghUser, и нажми «проверить» ещё раз.`r`n`r`nПодробности:`r`n"+$out
 }
}
function EnsureRemote {
 GitRun @('remote','get-url','origin')
 if($script:code -ne 0){Must @('remote','add','origin',$remoteUrl); $script:note="Добавлен адрес репозитория: $remoteUrl"}
 elseif($script:output.Trim() -ne $remoteUrl){$was=$script:output.Trim(); Must @('remote','set-url','origin',$remoteUrl); $script:note="Адрес репозитория изменён:`r`nбыло  $was`r`nстало $remoteUrl"}
}
try {
 if($Mode -eq 'setup'){Setup; exit}
 if($Mode -eq 'help') {
  [void](Menu 'Как пользоваться кнопками' "Репозиторий: github.com/$ghUser/$ghRepo (аккаунт и имя меняются в файле кнопки\github.conf).`r`n`r`nSETUP — один раз на новом компьютере: создаёт SSH-ключ для аккаунта $ghUser, копирует его и открывает страницу GitHub, куда его вставить.`r`nPUSH — сохранить изменения ноутбука и отправить на GitHub.`r`nPULL — получить изменения GitHub. Если есть свои правки, предложит сохранить их локально перед объединением.`r`n`r`nПри конфликте выбирай версию отдельно для каждого файла: «ноутбук» или «GitHub». Остальные изменения объединяются автоматически. Если сомневаешься — отменяй: обе версии сохранятся.`r`n`r`nПри незавершённом rebase кнопка предложит резервную копию и отмену старой операции.`r`n`r`nРезервные копии лежат рядом с zxc в папке zxc-backups. Их можно открыть в Проводнике и скопировать нужные файлы обратно. Папку .git вручную не переносить.`r`n`r`nОшибка сети — включи интернет / проверь VPN и нажми «Повторить». Ошибка ключа — открой настройки GitHub из окна ошибки.`r`n`r`nНекоторые ошибки доступа и большие файлы в старой истории требуют отдельного исправления. Кнопки не удаляют историю автоматически." @('Понятно')); exit
 }
 Must @('rev-parse','--git-dir'); $gd=$script:output.Trim()
 foreach($state in @('rebase-merge','rebase-apply','MERGE_HEAD','CHERRY_PICK_HEAD','REVERT_HEAD')) {
  if(Test-Path (Join-Path $gd $state)) {
   $x=Menu 'Предыдущая операция не закончилась' "Git остановился во время $state. Можно сохранить полную копию репозитория и отменить эту операцию. Правки, сделанные при разрешении конфликтов, останутся в резервной копии." @('Создать копию и отменить старую операцию','Закрыть, ничего не менять')
   if($x -ne 0){exit}; $null=Backup
   $op=switch -Regex ($state) {'^rebase' {'rebase'} '^MERGE' {'merge'} '^CHERRY' {'cherry-pick'} '^REVERT' {'revert'}}
   Must @($op,'--abort'); break
  }
 }
 Must @('symbolic-ref','--quiet','--short','HEAD'); $branch=$script:output.Trim()
 EnsureRemote
 if(!(Test-Path -LiteralPath $key)){
  $x=Menu 'Нет SSH-ключа' "Для аккаунта $ghUser на этом компьютере ещё нет ключа ($key). Создать его сейчас?" @('Создать и настроить ключ','Закрыть')
  if($x -ne 0){exit}; Setup; if(!(Test-Path -LiteralPath $key)){exit}
 }
 Network @('fetch','origin')
 Must @('status','--porcelain'); $dirty=$script:output
 if($dirty.Trim()) {
  $x=Menu 'Есть изменения на ноутбуке' ("Сохранить эти изменения локальным коммитом перед продолжением? PUSH затем отправит их, PULL только объединит с GitHub.`r`n`r`n"+$dirty) @('Сохранить изменения и продолжить','Отмена — оставить файлы как есть')
  if($x -ne 0){exit}
  $null=Backup
  Must @('add','-A'); Must @('commit','-m',('update '+(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')))
 }
 GitRun @('show-ref','--verify',('refs/remotes/origin/'+$branch)); $remoteExists=$script:code -eq 0
 if(!$remoteExists -and $Mode -eq 'pull'){throw "Ветки $branch нет на GitHub. Открой PUSH, чтобы опубликовать её, или выбери нужную ветку в редакторе."}
 if($remoteExists) {
  Must @('rev-parse','HEAD'); $before=$script:output.Trim()
  GitRun @('-c','merge.autoStash=false','merge','--no-edit',('origin/'+$branch))
  if($script:code -ne 0) {
   if(!(Test-Path (Join-Path $gd 'MERGE_HEAD'))){throw $script:output}
   try {
    Must @('diff','--name-only','--diff-filter=U'); $files=@($script:output.TrimEnd() -split "`r?`n" | Where-Object {$_})
    foreach($file in $files) {
     $x=Menu 'Один файл изменён с двух сторон' ("Файл: $file`r`n`r`nВыбери, какую ПОЛНУЮ версию этого файла оставить. Выбор применяется только к этому файлу. Для объединения текста вручную выбери отмену и воспользуйся редактором.`r`n`r`nДругие файлы объединяются автоматически. Исходные версии остаются в истории Git.") @('Оставить версию ноутбука','Взять версию GitHub','Отменить всё объединение')
     if($x -notin @(0,1)){throw 'Объединение отменено. Можно повторить PULL позже.'}
     $side=if($x -eq 0){'2'}else{'3'}
     GitRun @('cat-file','-e',(':'+ $side+':'+$file))
     if($script:code -eq 0){$flag=if($x -eq 0){'--ours'}else{'--theirs'}; Must @('checkout',$flag,'--',$file); Must @('add','--',$file)}
     else {Must @('rm','--',$file)}
    }
    Must @('commit','--no-edit')
   } catch {
    $problem=$_.Exception.Message; GitRun @('merge','--abort')
    if($script:code -ne 0){throw ($problem+"`r`nНе удалось отменить объединение: "+$script:output)}
    throw $problem
   }
  }
 }
 if($Mode -eq 'push'){Network @('push','--set-upstream','origin',$branch)}
 $done=if($Mode -eq 'push'){"Изменения отправлены на GitHub ($ghUser/$ghRepo)."}else{'Файлы обновлены. Локальные коммиты не отправлялись; для отправки нажми PUSH.'}
 if($script:note){$done+="`r`n`r`n"+$script:note}
 if($script:backup){$done+="`r`nРезервная копия: "+$script:backup}
 [void](Menu 'Готово' $done @('Закрыть'))
} catch {
 $x=Menu 'Операция остановлена' ($_.Exception.Message+"`r`n`r`nНе удаляй папку .git. Можно открыть папку проекта или резервные копии. Для повторной попытки снова нажми PUSH / PULL.") @('Открыть папку проекта','Открыть резервные копии','Закрыть')
 if($x -eq 0){Start-Process explorer.exe -ArgumentList ('"'+$repo+'"')}
 if($x -eq 1){$b=Join-Path (Split-Path $repo -Parent) 'zxc-backups'; if(Test-Path $b){Start-Process explorer.exe -ArgumentList ('"'+$b+'"')}}
 exit 1
}
