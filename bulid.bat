@echo off
echo 正在清理旧的打包文件...
rmdir /s /q build
rmdir /s /q dist
del /q main.spec

echo 正在打包...
pyinstaller -F -w -i app_icon.ico --add-data "config/config.yml;config" main.py

echo 正在复制 token.yml 到 dist 目录...
copy config\token.yml dist\token.yml

echo 打包完成！dist 目录已包含 exe 和 token.yml
pause
