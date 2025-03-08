@echo off
REM Запуск FastAPI сервера
echo Запуск FastAPI сервера...

REM Открываем Swagger UI в браузере
start http://127.0.0.1:8000/docs

REM Запуск сервера в текущем окне консоли
uvicorn main:app --host 0.0.0.0 --port 8000

echo Сервер запущен. Логи будут отображаться в этом окне.
pause