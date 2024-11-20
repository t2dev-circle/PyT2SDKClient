# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import yaml
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QWidget,
    QComboBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction
import qtawesome as qta

from py_t2sdk_api import *

"""
py_t2sdk_api包的调用方式：

api = T2Api()
api.init("121.41.126.194:9359")
api.connect()

req = StringMap()
func_no = "330000"
req["func_no"] = func_no
req["op_branch_no"] = "1000"
req["op_entrust_way"] = "7"
req["op_station"] = "127.0.0.1"
api.send(req)

api.recv()

records = api.getRecords()
for record in records:
    for key, value in record.items():
        print(key, value)
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # 加载功能号yaml文件（来源于恒生柜台接口文档）
        self.init_data()
        self.load_config()
        self.load_yaml()

        # 初始化api
        self.init_api()

        # 初始化布局
        self.init_layout()

        # 初始化输入输出界面数据
        self.init_choose()
        self.init_input()
        self.init_output()

        self.init = True

    def load_config(self, file_name="t2_api.json"):
        path = os.path.join(os.path.split(__file__)[0], file_name)
        if not os.path.exists(path):
            print(path)
            return

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        if len(content) == 0:
            return

        self.config_field_info = json.loads(content)

        print(self.config_field_info)

    def save_config(self, file_name="t2_api.json"):
        path = os.path.join(os.path.split(__file__)[0], file_name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.config_field_info))

    def load_yaml(self, file_name="t2_api.yaml"):
        path = os.path.join(os.path.split(__file__)[0], file_name)
        with open(path, "r", encoding="utf-8") as f:
            self.apis = yaml.full_load(f)
            # print(self.apis)

    def init_layout(self):
        self.widget_base = QWidget(self)

        self.layout_base = QVBoxLayout()
        self.widget_base.setLayout(self.layout_base)

        self.widget_choose = QWidget()
        self.widget_choose.setObjectName("widget_choose")
        self.widget_choose.setFixedHeight(48)
        self.widget_choose.setStyleSheet(
            "QWidget#widget_choose{border:1px solid; border-color:#4f5b62}"
        )

        self.widget_input = QWidget()
        self.widget_input.setObjectName("widget_input")
        self.widget_input.setStyleSheet(
            "QWidget#widget_input{border:1px solid; border-color:#4f5b62}"
        )

        self.widget_output = QWidget()
        self.widget_output.setObjectName("widget_output")
        self.widget_output.setStyleSheet(
            "QWidget#widget_output{border:1px solid; border-color:#4f5b62}"
        )

        self.layout_base.addWidget(self.widget_choose)
        self.layout_base.addWidget(self.widget_input)
        self.layout_base.addWidget(self.widget_output)

        self.layout_choose = QHBoxLayout()
        self.layout_choose.setContentsMargins(16, 0, 16, 0)
        self.lbl_addr = QLabel("柜台地址：")
        self.lbl_addr.setFixedWidth(64)
        self.edt_addr = QLineEdit()
        self.edt_addr.setFixedWidth(156)
        self.edt_addr.setFixedHeight(28)
        self.edt_addr.setText(self.get_server_ip())
        self.edt_addr.textChanged.connect(self.on_addr_changed)
        self.addr_blank = QWidget()
        self.addr_blank.setFixedWidth(32)
        self.lbl_apis = QLabel("柜台功能：")
        self.lbl_apis.setFixedWidth(64)
        self.combox_apis = QComboBox()
        self.combox_apis.setFixedWidth(256)
        self.combox_apis.setFixedHeight(28)
        self.combox_apis.setEditable(True)
        self.widget_blank = QWidget()
        self.btn_run = QPushButton("测试")
        self.btn_run.setFixedWidth(80)
        self.btn_run.setFixedHeight(28)
        self.layout_choose.addWidget(self.lbl_addr)
        self.layout_choose.addWidget(self.edt_addr)
        self.layout_choose.addWidget(self.addr_blank)
        self.layout_choose.addWidget(self.lbl_apis)
        self.layout_choose.addWidget(self.combox_apis)
        self.layout_choose.addWidget(self.widget_blank)
        self.layout_choose.addWidget(self.btn_run)
        self.widget_choose.setLayout(self.layout_choose)

        self.combox_apis.currentIndexChanged.connect(self.select_api)
        self.btn_run.clicked.connect(self.run_api)

        self.toolbar = self.addToolBar("")
        action_setting = QAction(
            qta.icon("ri.settings-3-line", color="#2979ff"), "设置", self
        )
        action_setting.setShortcut("Ctrl+Shift+T")
        action_setting.triggered.connect(self.on_open_settting)
        self.toolbar.addAction(action_setting)

        action_about = QAction(
            qta.icon("mdi.information-variant", color="#2979ff"), "关于", self
        )
        action_about.setShortcut("Ctrl+Shift+I")
        action_about.triggered.connect(self.on_open_about)
        self.toolbar.addAction(action_about)

        self.setWindowTitle(self.title)
        self.setCentralWidget(self.widget_base)

    def init_data(self):
        self.title = "T2SDK客户端 V1.1.3"
        self.init = False
        self.addr_changed = False
        self.max_input_fields = 30
        self.config_field_info = {}
        self.apis = None
        self.cur_api = None
        self.t2req = StringMap()
        self.input_field_info = {}

    def init_api(self):
        self.t2api = T2Api()
        self.t2api.init(self.get_server_ip())

    def init_choose(self):
        if self.apis is None:
            return

        first = True

        for api in self.apis:
            if first:
                self.cur_api = api
                # print(self.cur_api)

                first = False

            id = api["ID"]
            desc = api["Desc"]
            title = str(id) + "-" + desc

            self.combox_apis.addItem(title)

        self.combox_apis.setCurrentIndex(0)

    def init_input(self):
        self.layout_input = QGridLayout()
        self.layout_input.setSpacing(0)
        self.widget_input.setLayout(self.layout_input)

        row = 1
        column = 0
        column_count = 4

        for i in range(self.max_input_fields):
            widget_base = QWidget()
            layout_base = QHBoxLayout()

            lbl_field_title = QLabel(str(i))
            lbl_field_title.setFixedWidth(100)
            layout_base.addWidget(lbl_field_title)

            edt_field_value = QLineEdit()
            edt_field_value.setFixedWidth(156)
            edt_field_value.setFixedHeight(28)
            layout_base.addWidget(edt_field_value)

            widget_blank = QWidget()
            layout_base.addWidget(widget_blank)

            widget_base.setLayout(layout_base)

            self.layout_input.addWidget(widget_base, row, column)

            self.input_field_info[i] = (lbl_field_title, edt_field_value)

            column += 1

            if column % column_count == 0:
                row += 1
                column = 0

        self.reset_input()

    def on_open_settting(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("设置")

        layout_dlg = QGridLayout()
        dlg.setLayout(layout_dlg)

        config = {
            "柜台地址": "server_ip",
            "客户号": "client_id",
            "资金账号": "fund_account",
            "交易密码": "password",
            "委托方式": "op_entrust_way",
            "操作营业部代码": "op_branch_no",
            "营业部代码": "branch_no",
            "站点地址": "op_station",
        }

        field_info = {}

        row = 1
        column = 0
        column_count = 2

        for title, field_name in config.items():
            widget_base = QWidget()
            layout_base = QHBoxLayout()

            lbl_field_title = QLabel(title)
            lbl_field_title.setFixedWidth(100)
            layout_base.addWidget(lbl_field_title)

            edt_field_value = QLineEdit()
            edt_field_value.setFixedWidth(156)
            edt_field_value.setFixedHeight(28)
            edt_field_value.setText(self.get_field_value(field_name))
            layout_base.addWidget(edt_field_value)

            field_info[title] = edt_field_value

            widget_blank = QWidget()
            layout_base.addWidget(widget_blank)

            widget_base.setLayout(layout_base)

            layout_dlg.addWidget(widget_base, row, column)

            column += 1

            if column % column_count == 0:
                row += 1
                column = 0

        widget_base = QWidget()
        layout_base = QHBoxLayout()

        lbl_field_title = QLabel()
        lbl_field_title.setFixedWidth(100)
        layout_base.addWidget(lbl_field_title)

        btn_action = QPushButton("确定")
        btn_action.setFixedWidth(156)
        btn_action.setFixedHeight(28)
        btn_action.clicked.connect(dlg.accept)
        layout_base.addWidget(btn_action)

        widget_blank = QWidget()
        layout_base.addWidget(widget_blank)

        widget_base.setLayout(layout_base)

        column = 0
        layout_dlg.addWidget(widget_base, row, column)

        widget_base = QWidget()
        layout_base = QHBoxLayout()

        btn_action = QPushButton("取消")
        btn_action.setFixedWidth(156)
        btn_action.setFixedHeight(28)
        btn_action.clicked.connect(dlg.reject)
        layout_base.addWidget(btn_action)

        lbl_field_title = QLabel()
        lbl_field_title.setFixedWidth(100)
        layout_base.addWidget(lbl_field_title)

        widget_blank = QWidget()
        layout_base.addWidget(widget_blank)

        widget_base.setLayout(layout_base)

        column += 1
        layout_dlg.addWidget(widget_base, row, column)

        print("before:", self.config_field_info)

        result = dlg.exec()
        if result == QDialog.Accepted:
            for title, edt_field_value in field_info.items():
                field_name = config.get(title)
                if field_name:
                    self.config_field_info[field_name] = edt_field_value.text()

            self.reset_input()

        print("after:", self.config_field_info)

    def on_open_about(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("关于")
        layout_dlg = QVBoxLayout()
        layout_dlg.addWidget(QLabel(""))
        layout_dlg.addWidget(QLabel(self.title))
        layout_dlg.addWidget(QLabel(""))
        layout_dlg.addWidget(QLabel(self.get_copyright()))
        layout_dlg.addWidget(QLabel(""))
        layout_dlg.addWidget(QLabel("Email: 1274994515@qq.com"))
        layout_dlg.addWidget(QLabel(""))
        dlg.setLayout(layout_dlg)

        dlg.exec()

    def closeEvent(self, e):
        self.save_config()

    def get_copyright(self):
        year = time.strftime("%Y", time.localtime(time.time()))
        return "Copyright © " + str(year) + " t2dev-circle. All rights reserved."

    def get_field_value(self, field_name):
        field_value = self.config_field_info.get(field_name)
        if field_value is None:
            field_value = ""

        return field_value

    def get_server_ip(self):
        server_ip = self.get_field_value("server_ip")
        if server_ip is None or len(server_ip) == 0:
            server_ip = "121.41.126.194:9359"

        return server_ip

    def set_field_value(self, field_name, edt_value):
        field_value = self.config_field_info.get(field_name)
        if field_value is None:
            field_value = ""

        edt_value.setText(field_value)

    def reset_input(self):
        input_fields = self.cur_api["Input"]
        field_count = len(input_fields)

        self.edt_addr.setText(self.get_server_ip())

        for i in range(self.max_input_fields):
            field_info = self.input_field_info[i]
            if i < field_count:
                field_info[0].setVisible(True)
                field_info[1].setVisible(True)

                field_name = input_fields[i][1]
                field_info[0].setText(field_name)
                self.set_field_value(field_name, field_info[1])
            else:
                field_info[0].setVisible(False)
                field_info[1].setVisible(False)
                field_info[1].setText("")

    def init_output(self):
        layout_output = QHBoxLayout()
        self.widget_output.setLayout(layout_output)

        self.tbl_output = QTableWidget()
        layout_output.addWidget(self.tbl_output)

        self.combox_apis.setFocus()

    def update_output(self):
        records = self.t2api.getRecords()
        if len(records) == 0:
            return

        first_record = records[0]
        if len(first_record) == 0:
            return

        self.tbl_output.setRowCount(len(records))
        self.tbl_output.setColumnCount(len(first_record.keys()))
        self.tbl_output.setHorizontalHeaderLabels(first_record.keys())

        row = 0

        for record in records:
            column = 0
            for _, value in record.items():
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags and (~Qt.ItemFlag.ItemIsEditable))
                self.tbl_output.setItem(row, column, item)

                column += 1

            row += 1

    def get_func_no(self):
        text = self.combox_apis.currentText()
        func_no = text.split("-")[0]
        return func_no

    def get_api(self):
        result = ""

        func_no = self.get_func_no()

        for api in self.apis:
            if func_no == str(api["ID"]):
                result = api
                break

        return result

    def get_input(self):
        func_no = self.get_func_no()
        self.t2req["func_no"] = func_no

        for key, value in self.input_field_info.items():
            lbl_field_name = value[0]
            edt_field_value = value[1]

            if not lbl_field_name.isVisible():
                break

            self.t2req[lbl_field_name.text()] = edt_field_value.text()

        print("get_input：", func_no, self.t2req)

    def pack_req(self):
        self.t2req.clear()

        # 获取入参
        self.get_input()

        print("pack_req:", end=" ")
        for key, value in self.t2req.items():
            print(key, "=", value, "|", end=" ")
        print("")

        return self.t2req

    def on_addr_changed(self, text):
        print(text)
        self.addr_changed = True

    def select_api(self):
        self.cur_api = self.get_api()

        if not self.init or self.cur_api is None:
            return

        self.reset_input()

    def run_api(self):
        if self.addr_changed:
            addr = self.edt_addr.text()
            # 柜台地址发生变化，需要释放上一个连接并重新初始化
            self.t2api.release()
            self.t2api.init(addr)

        if not self.t2api.connect():
            msg = self.t2api.getErrMsg()
            print(msg)
            QMessageBox.information(self, "提示", msg)
            return

        req = self.pack_req()

        if not self.t2api.send(req):
            msg = self.t2api.getErrMsg()
            print("send:", type(msg), msg)
            QMessageBox.information(self, "提示", msg)
            return

        if not self.t2api.recv():
            msg = self.t2api.getErrMsg()
            print("recv:", type(msg), msg)
            QMessageBox.information(self, "提示", msg)
            return

        records = self.t2api.getRecords()
        for record in records:
            for key, value in record.items():
                print(key, value)

        # 更新输出列表信息
        self.update_output()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.setWindowIcon(qta.icon("mdi.api", color="#304ffe"))
    window.resize(1024, 768)
    window.show()

    sys.exit(app.exec())
