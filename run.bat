@echo off
echo Iniciando Moises Local...
call venv\Scripts\activate
uvicorn main:app --host 192.168.17.2 --reload
