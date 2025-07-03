@echo off
REM 自动打包脚本 - ERP自动化工具
pyinstaller -F -w -i app_icon.ico ^
--add-data "config/config.yml;config" ^
--add-data "config/token.yml;config" ^
main.py

echo.
echo 打包完成！你的exe在 dist\ 目录下。
pause
