# -*- coding: utf-8 -*-

import sys
import yaml
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget,QComboBox,QLabel,QLineEdit,QPushButton,QTableWidget,QTableWidgetItem,QMessageBox,QHBoxLayout, QVBoxLayout, QGridLayout
from PySide6.QtCore import Qt, QSize
import qtawesome as qta

from py_t2sdk_api import *

'''
py_t2sdk_api包的调用方式：

api = T2Api()
api.init()
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
'''

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        #初始化布局
        self.init_layout()

        #加载功能号yaml文件（来源于恒生柜台接口文档）
        self.init_data()
        self.load_yaml()
        
        #初始化输入输出界面数据
        self.init_choose()
        self.init_input()
        self.init_output()

        self.init = True

    def load_yaml(self, file_name='t2_api.yaml'):
        with open(file_name, "r", encoding="utf-8") as f:
            self.apis = yaml.full_load(f)
            #print(self.apis)

    def init_layout(self):
        self.widget_base = QWidget(self)

        self.layout_base = QVBoxLayout()
        self.widget_base.setLayout(self.layout_base)

        self.widget_choose = QWidget()
        self.widget_choose.setObjectName("widget_choose")
        self.widget_choose.setFixedHeight(48)
        self.widget_choose.setStyleSheet("QWidget#widget_choose{border:1px solid; border-color:#4f5b62}")

        self.widget_input = QWidget()
        self.widget_input.setObjectName("widget_input")
        self.widget_input.setStyleSheet("QWidget#widget_input{border:1px solid; border-color:#4f5b62}")

        self.widget_output = QWidget()
        self.widget_output.setObjectName("widget_output")
        self.widget_output.setStyleSheet("QWidget#widget_output{border:1px solid; border-color:#4f5b62}")

        self.layout_base.addWidget(self.widget_choose)
        self.layout_base.addWidget(self.widget_input)
        self.layout_base.addWidget(self.widget_output)

        self.layout_choose = QHBoxLayout()
        self.combox_apis = QComboBox()
        self.combox_apis.setFixedWidth(256)
        self.combox_apis.setFixedHeight(28)
        self.combox_apis.setEditable(True)
        self.widget_blank = QWidget()
        self.btn_run = QPushButton("测试")
        self.btn_run.setFixedWidth(80)
        self.btn_run.setFixedHeight(28)
        self.layout_choose.addWidget(self.combox_apis)
        self.layout_choose.addWidget(self.widget_blank)
        self.layout_choose.addWidget(self.btn_run)
        self.widget_choose.setLayout(self.layout_choose)

        self.combox_apis.currentIndexChanged.connect(self.select_api)
        self.btn_run.clicked.connect(self.run_api)

        self.setCentralWidget(self.widget_base)

    def init_data(self):
        self.init = False
        self.max_input_fields = 30
        self.apis = None
        self.cur_api = None
        self.t2req = StringMap()
        self.input_field_info = {}

        self.t2api = T2Api()
        self.t2api.init()

    def init_choose(self):
        if self.apis is None:
            return
        
        first = True

        for api in self.apis:
            if first:
                self.cur_api = api
                #print(self.cur_api)

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

        #print('init:', len(self.input_field_info), self.input_field_info)
        self.reset_input()

    def reset_input(self):
        input_fields = self.cur_api["Input"]
        field_count = len(input_fields)

        for i in range(self.max_input_fields):
            field_info = self.input_field_info[i]
            if i < field_count:
                field_info[0].setVisible(True)
                field_info[1].setVisible(True)

                field_info[0].setText(input_fields[i][1])
                field_info[1].setText("")
            else:
                field_info[0].setVisible(False)
                field_info[1].setVisible(False)

    def init_output(self):
        layout_output = QHBoxLayout()
        self.widget_output.setLayout(layout_output)

        self.tbl_output = QTableWidget()
        layout_output.addWidget(self.tbl_output)

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
        func_no = text.split('-')[0]
        return func_no
    
    def get_api(self):
        result = ''

        func_no = self.get_func_no()

        for api in self.apis:
            if func_no == str(api['ID']):
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
        
        print('get_input：', func_no, self.t2req)

    def pack_req(self):
        self.t2req.clear()

        #获取入参
        self.get_input()

        print('pack_req:', end=' ')
        for key, value in self.t2req.items():
            print(key, '=', value, '|', end=' ')
        print('')

        return self.t2req
    
    def select_api(self):
        self.cur_api = self.get_api()
        
        if not self.init or self.cur_api is None:
            return

        self.reset_input()

    def run_api(self):
        if not self.t2api.connect():
            msg = self.t2api.getErrMsg()
            print(msg)
            QMessageBox.information(self, '提示', msg)
            return
        
        req = self.pack_req()
        
        if not self.t2api.send(req):
            msg = self.t2api.getErrMsg()
            print('send:',type(msg), msg)
            QMessageBox.information(self, '提示', msg)
            return
        
        if not self.t2api.recv():
            msg = self.t2api.getErrMsg()
            print('recv:',type(msg), msg)
            QMessageBox.information(self, '提示', msg)
            return
        
        records = self.t2api.getRecords()
        for record in records:
            for key, value in record.items():
                print(key, value)

        #更新输出列表信息
        self.update_output()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.setWindowTitle("T2SDK客户端 V1.0")
    window.setWindowIcon(qta.icon("mdi.api", color="#304ffe"))
    window.resize(1024, 768)
    window.show()

    sys.exit(app.exec())
