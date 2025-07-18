import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QLineEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout, QComboBox, QFileDialog
)

from baseApi.base_api import AllApi
from src.configuration.configuration import Configuration  # 配置逻辑类
import user_context
import json
import requests


class ErpGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ERP自动化工具")
        self.resize(600, 420)
        self.api = AllApi()
        self.config = Configuration(self.api)


        # 登录用户输入
        self.login_user_input = self._create_input_row("登录用户名（如 admin）：")

        # 输入组件
        self.mrp_scheme_name_input = self._create_input_row("MRP运算方案名称：")
        self.mrp_scheme_id_input = self._create_input_row("MRP运算方案ID：")
        self.production_order_input = self._create_input_row("生产工单号：")
        self.warehouse_input = self._create_input_row("采购到货仓库名：")
        self.inspector_input = self._create_input_row("质检人姓名：")
        self.time_offset_input = self._create_input_row("MRP运算时间间隔（天数）：")
        self.sale_order_path_input = self._create_input_row("销售订单文件地址：", with_button=True)
        self.buy_order_path_input = self._create_input_row("采购订单文件地址：", with_button=True)

        # 方法选择
        method_layout = QHBoxLayout()
        method_label = QLabel("选择方法：")
        self.method_combo = QComboBox()
        self.method_combo.addItems(["方法一", "方法二", "方法三"])
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.method_combo)
        method_layout.addStretch()

        # 执行按钮
        self.run_button = QPushButton("执行方法")
        self.run_button.clicked.connect(self.execute_selected_method)

        # 输出框
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)

        # 总体布局
        layout = QVBoxLayout()
        layout.addLayout(self.login_user_input["layout"])
        layout.addLayout(self.mrp_scheme_name_input["layout"])
        layout.addLayout(self.mrp_scheme_id_input["layout"])
        layout.addLayout(self.production_order_input["layout"])
        layout.addLayout(self.warehouse_input["layout"])
        layout.addLayout(self.inspector_input["layout"])
        layout.addLayout(self.time_offset_input["layout"])
        layout.addLayout(self.sale_order_path_input["layout"])
        layout.addLayout(self.buy_order_path_input["layout"])
        layout.addLayout(method_layout)
        layout.addWidget(self.run_button)
        layout.addWidget(QLabel("执行结果："))
        layout.addWidget(self.result_box)

        self.setLayout(layout)

    def _create_input_row(self, label_text, with_button=False):
        label = QLabel(label_text)
        input_field = QLineEdit()
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(input_field)

        if with_button:
            btn = QPushButton("浏览")
            layout.addWidget(btn)
            btn.clicked.connect(lambda: self._choose_file(input_field))

        return {"label": label, "input": input_field, "layout": layout}

    def _choose_file(self, input_field):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "选择文件",
            "",
            "Excel 文件 (*.xlsx *.xls);;所有文件 (*.*)"
        )
        if file_path:
            input_field.setText(file_path)

    def execute_selected_method(self):
        username = self.login_user_input["input"].text().strip()
        user_context.user_key = username
        if not username:
            self.result_box.append("请先输入登录用户名（如 admin / user1）")
            return

        try:
            # 实例化 AllApi，传入用户名

            # 登录
            self.api.send_login("admin-api/config.yml")
        except Exception as e:
            self.result_box.append(f"登录失败：{str(e)}")
            return

        # 读取参数
        mrp_scheme_name = self.mrp_scheme_name_input["input"].text().strip()
        mrp_scheme_id_str = self.mrp_scheme_id_input["input"].text().strip()
        production_order = self.production_order_input["input"].text().strip()
        warehouse = self.warehouse_input["input"].text().strip()
        inspector = self.inspector_input["input"].text().strip()
        time_offset_str = self.time_offset_input["input"].text().strip()
        sale_order_path = self.sale_order_path_input["input"].text().strip()
        buy_order_path = self.buy_order_path_input["input"].text().strip()
        selected_method = self.method_combo.currentText()

        try:
            if selected_method == "方法一":
                if not mrp_scheme_name or not mrp_scheme_id_str or not sale_order_path or not time_offset_str:
                    self.result_box.append("方法一：MRP运算方案名称 / ID / 销售订单路径 / 时间间隔不能为空")
                    return
                if not mrp_scheme_id_str.isdigit():
                    self.result_box.append("运算方案ID必须为纯数字")
                    return
                mrp_scheme_id = int(mrp_scheme_id_str)
                result = self.config.run_one(sale_order_path, mrp_scheme_id, mrp_scheme_name, time_offset_str)

            elif selected_method == "方法二":
                if not buy_order_path or not warehouse or not inspector:
                    self.result_box.append("方法二：采购订单路径 / 仓库名 / 质检人不能为空")
                    return
                result = self.config.run_two(buy_order_path, warehouse, inspector)

            elif selected_method == "方法三":
                if not production_order or not inspector:
                    self.result_box.append("方法三：生产工单号 / 质检人不能为空")
                    return
                result = self.config.run_three(production_order, inspector)

            else:
                result = "未知方法"

            self.result_box.append(f"执行结果：{result}")
        except Exception as e:
            self.result_box.append(f"执行异常：{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ErpGUI()
    window.show()
    sys.exit(app.exec())
