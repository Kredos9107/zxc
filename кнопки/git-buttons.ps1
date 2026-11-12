param([ValidateSet('push','pull','help')][string]$Mode='help')
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Windows.Forms
$repo=Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $repo
$git=(Get-Command git -ErrorAction Stop).Source
$env:GIT_SSH_COMMAND='"'+$env:SYSTEMROOT.Replace('\','/')+'/System32/OpenSSH/ssh.exe" -o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=15 -o ServerAliveCountMax=3 -i "'+$env:USERPROFILE.Replace('\','/')+'/.ssh/id_rsa" -o UserKnownHostsFile="'+$env:USERPROFILE.Replace('\','/')+'/.ssh/known_hosts"'
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
  if($script:output -match 'publickey'){ $reason='GitHub не принял SSH-ключ. Открой настройки ключей GitHub и добавь публичный ключ этого ноутбука. Приватный ключ никому не отправляй.' }
  if($script:output -match 'Host key verification|REMOTE HOST IDENTIFICATION'){ $reason='Не удалось проверить подлинность GitHub. Проверку безопасности мы не отключаем. Открой справку GitHub о SSH и проверь запись known_hosts.' }
  if($script:output -match 'GH001|file size limit'){ $reason='В истории есть файл больше лимита GitHub. Простое удаление файла не уберёт его из старых коммитов. Отправка остановлена, локальная работа сохранена. Открой GitHub Desktop для просмотра неотправленных коммитов.' }
  $x=Menu 'Проблема подключения или отправки' ($reason+"`r`n`r`nПодробности:`r`n"+$script:output) @('Повторить','Открыть настройки SSH GitHub','Закрыть — локальная работа сохранится')
  if($x -eq 1){Start-Process 'https://github.com/settings/keys'; continue}
  if($x -ne 0){throw 'Операция отменена. Локальные файлы сохранены.'}
 }
}
try {
 if($Mode -eq 'help') {
  [void](Menu 'Как пользоваться кнопками' "PUSH — сохранить изменения ноутбука и отправить на GitHub.`r`nPULL — получить изменения GitHub. Если есть свои правки, предложит сохранить их локально перед объединением.`r`n`r`nПри конфликте выбирай версию отдельно для каждого файла: «ноутбук» или «GitHub». Остальные изменения объединяются автоматически. Если сомневаешься — отменяй: обе версии сохранятся.`r`n`r`nПри незавершённом rebase кнопка предложит резервную копию и отмену старой операции.`r`n`r`nРезервные копии лежат рядом с zxc в папке zxc-backups. Их можно открыть в Проводнике и скопировать нужные файлы обратно. Папку .git вручную не переносить.`r`n`r`nОшибка сети — включи интернет / проверь VPN и нажми «Повторить». Ошибка ключа — открой настройки GitHub из окна ошибки.`r`n`r`nНекоторые ошибки доступа и большие файлы в старой истории требуют отдельного исправления. Кнопки не удаляют историю автоматически." @('Понятно')); exit
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
 $done=if($Mode -eq 'push'){'Изменения отправлены на GitHub.'}else{'Файлы обновлены. Локальные коммиты не отправлялись; для отправки нажми PUSH.'}
 if($script:backup){$done+="`r`nРезервная копия: "+$script:backup}
 [void](Menu 'Готово' $done @('Закрыть'))
} catch {
 $x=Menu 'Операция остановлена' ($_.Exception.Message+"`r`n`r`nНе удаляй папку .git. Можно открыть папку проекта или резервные копии. Для повторной попытки снова нажми PUSH / PULL.") @('Открыть папку проекта','Открыть резервные копии','Закрыть')
 if($x -eq 0){Start-Process explorer.exe -ArgumentList ('"'+$repo+'"')}
 if($x -eq 1){$b=Join-Path (Split-Path $repo -Parent) 'zxc-backups'; if(Test-Path $b){Start-Process explorer.exe -ArgumentList ('"'+$b+'"')}}
 exit 1
}
