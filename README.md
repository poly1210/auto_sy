
# auto_sy

## 项目说明

这是一个基于 Python + PySide6 的 ERP 自动化工具，主要用于销售、采购、生产等流程的接口自动化执行。

## 启动依赖

建议先安装项目所需依赖：

```powershell
python -m pip install -r requirements.txt
```

如果你的环境是 Python 3.13，而 `requirements.txt` 中的某些版本安装失败，优先补齐当前项目启动所需的核心依赖：

```powershell
python -m pip install PySide6==6.9.1 pandas==2.3.1 openpyxl==3.1.5 PyMySQL==1.1.2 PyYAML==6.0.2 ruamel.yaml==0.18.10 ruamel.yaml.clib==0.2.12 anyio==4.9.0
```

## 运行前配置

1. 在 `config/config.yml` 中配置账号、密码和数据库信息。
2. 确认 `config/token.yml` 可读写，程序登录后会自动写入 token。
3. 准备好销售订单或采购订单 Excel 文件，格式需与 `src/read_xlsx/` 下的读取逻辑一致。

## 运行命令

启动 GUI：

```powershell
python main.py
```

如果需要先验证当前解释器和依赖环境，可以执行：

```powershell
python --version
python -m pip --version
```

## 常用命令

导出当前环境依赖：

```powershell
pip freeze > requirements.txt
```

以可编辑模式安装当前目录下的 Python 包：

```powershell
pip install -e .
```