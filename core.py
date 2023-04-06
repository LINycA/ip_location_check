import sys
import traceback
import time

import re
from threading import Thread

import requests

from ip_check_ui import Ui_MainWindow
from PyQt5 import QtCore,QtWidgets,QtGui

class ip_check_core(Ui_MainWindow):
    def __init__(self) -> None:
        super(ip_check_core).__init__()
        self.window = QtWidgets.QMainWindow()
        self.setupUi(self.window)
        self.window.show()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 HBPC/12.1.2.300',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/json'
        }
        self.api_url = self.read_api_addr()
        self.pushButton.clicked.connect(self.btn_event)

    # 读取接口配置文件
    def read_api_addr(self) -> (str or None):
        url = None
        try:
            with open('api.ini','r',encoding='utf-8') as f:
                url = f.read().strip()
        except:
            pass
        if not url or ('http://' not in url and 'https://' not in url) or 'ip_addr' not in url:
            self.textBrowser.append('ip地址配置文件不存在或错误，已生成案例文件api.ini')
            with open('api.ini','w',encoding='utf-8') as f:
                f.write('http://xxxxxxx?ip_addr')
            self.pushButton.setEnabled(False)
            return None
        else:
            return url

    def request_info(self,url):
        return requests.get(url=url,headers=self.headers,timeout=3)


    def check_ip(self,url:str):
        # 检测ip地址格式是否错误
        try:
            res = self.request_info(url=url).json()
            ip = res.get('data')[0].get('origip')
            lo = res.get('data')[0].get('location')
            self.textBrowser.append(ip+' | '+lo)
            self.pushButton.setEnabled(True)
            # self.textBrowser.append(res.text)
        except Exception as error_msg:
            self.pushButton.setEnabled(True)
            self.textBrowser.append(str(error_msg))

    def btn_event(self):
        self.textBrowser.clear()
        self.pushButton.setEnabled(False)
        def check_ip_value(ip:str):
            if len(re.findall(r'\.',ip)) < 3 or len(re.findall(r'\.',ip)) > 3:
                return True
            elif len(ip) > 15:
                return True
            else:
                value_check_list = [ord(str(i)) for i in range(10)] + [ord('.')]
                for i in ip:
                    if ord(i) not in value_check_list:
                        return True
                return False
        ip_value = self.ip_edit.text()
        if check_ip_value(ip=ip_value):
            self.textBrowser.append('ip地址错误')
        else:
            url = self.api_url.replace('ip_addr',ip_value)
            p = Thread(target=self.check_ip,args=(url,))
            p.start()
            # p.join()

        


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    program = ip_check_core()
    sys.exit(app.exec_())
