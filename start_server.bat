@echo off
REM Переход в директорию, где находится скрипт сервера
cd /d %~dp0

REM Проверка, установлен ли Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python не установлен или не добавлен в PATH.
    pause
    exit /b
)

REM Проверка, установлены ли необходимые библиотеки
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo Библиотека FastAPI не установлена. Устанавливаем...
    pip install fastapi
)

pip show uvicorn >nul 2>&1
if %errorlevel% neq 0 (
    echo Библиотека Uvicorn не установлена. Устанавливаем...
    pip install uvicorn
)

pip show mysql-connector-python >nul 2>&1
if %errorlevel% neq 0 (
    echo Библиотека mysql-connector-python не установлена. Устанавливаем...
    pip install mysql-connector-python
)

REM Запуск сервера
echo Запуск сервера FastAPI...
uvicorn main:app --reload

REM Ожидание нажатия клавиши перед закрытием окна
pause