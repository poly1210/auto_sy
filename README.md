
[//]: # (说明)

2、安装依赖： pip install -r requirements.txt
3、在 config/config.yml 中配置账号、密码
4、运行用例： pytest testCase/ --html=reports/report.html

[//]: # (可能需要用到的命令)
----------------------------------
导入所有依赖到文件： pip freeze > requirements.txt
安装当前目录下的Python包： pip install -e .