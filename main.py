import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QLineEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout, QComboBox, QFileDialog
)

from baseApi.base_api import AllApi

# 获取根目录路径
root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_path)

from src.configuration.configuration import Configuration  # 你的配置逻辑类

import requests



class ErpGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ERP自动化工具")
        self.resize(600, 400)  # 设置窗口初始尺寸
        self.api = AllApi()
        self.config = Configuration(self.api)  # 实例化配置类（注意不要漏了括号，如果需要实例）

        # ==== 输入组件 ====
        self.mrp_scheme_name_input = self._create_input_row("MRP运算方案名称：")
        self.mrp_scheme_id_input = self._create_input_row("MRP运算方案ID：")
        self.production_order_input = self._create_input_row("生产工单号：")
        self.warehouse_input = self._create_input_row("采购到货仓库名：")
        self.sale_order_path_input = self._create_input_row("销售订单文件地址：", with_button=True)
        self.buy_order_path_input = self._create_input_row("采购订单文件地址：", with_button=True)

        # ==== 方法选择 ====
        method_layout = QHBoxLayout()
        method_label = QLabel("选择方法：")
        self.method_combo = QComboBox()
        self.method_combo.addItems(["方法一", "方法二", "方法三"])
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.method_combo)
        method_layout.addStretch()

        # ==== 运行与日志输出 ====
        self.run_button = QPushButton("执行方法")
        self.run_button.clicked.connect(self.execute_selected_method)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)

        # ==== 总体布局 ====
        layout = QVBoxLayout()
        layout.addLayout(self.mrp_scheme_name_input['layout'])
        layout.addLayout(self.mrp_scheme_id_input['layout'])
        layout.addLayout(self.production_order_input['layout'])
        layout.addLayout(self.warehouse_input['layout'])
        layout.addLayout(self.sale_order_path_input['layout'])
        layout.addLayout(self.buy_order_path_input['layout'])
        layout.addLayout(method_layout)
        layout.addWidget(self.run_button)
        layout.addWidget(QLabel("执行结果："))
        layout.addWidget(self.result_box)

        self.setLayout(layout)

    def _create_input_row(self, label_text, with_button=False):
        """通用行布局方法，返回控件引用和布局"""
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
        """文件选择弹窗"""
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
        # try:
        #     response = requests.get("https://www.baidu.com", timeout=5)
        #     if response.status_code == 200:
        #         print("联网正常")
        #     else:
        #         print("联网异常")
        # except Exception as e:
        #     print(f"联网失败：{e}")
        """执行选中的方法"""
        # 读取输入值
        mrp_scheme_name = self.mrp_scheme_name_input["input"].text().strip()

        mrp_scheme_id_str = self.mrp_scheme_id_input["input"].text().strip()
        if mrp_scheme_id_str.strip():  # 判断不是空字符串
            mrp_scheme_id = int(mrp_scheme_id_str)


        production_order = self.production_order_input["input"].text().strip()
        warehouse = self.warehouse_input["input"].text().strip()
        sale_order_path = self.sale_order_path_input["input"].text().strip()
        buy_order_path = self.buy_order_path_input["input"].text().strip()

        selected_method = self.method_combo.currentText()

        try:
            if selected_method == "方法一":
                if not mrp_scheme_name or not mrp_scheme_id or not sale_order_path:
                    self.result_box.append("方法一：MRP运算方案名称 / ID / 销售订单路径不能为空")
                    return
                result = self.config.run_one(sale_order_path, mrp_scheme_id, mrp_scheme_name)

            elif selected_method == "方法二":
                if not buy_order_path or not warehouse:
                    self.result_box.append("方法二：采购订单路径 / 仓库名不能为空")
                    return
                result = self.config.run_two(buy_order_path, warehouse)

            elif selected_method == "方法三":
                if not production_order:
                    self.result_box.append("方法三：生产工单号不能为空")
                    return
                result = self.config.run_three(production_order)

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
