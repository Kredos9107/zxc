@echo off
rem Отдельная кнопка: сразу принудительный пулл.
rem Вся логика - в pull.bat, здесь только передаётся аргумент force.
call "%~dp0pull.bat" force
