import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys
import subprocess
from urllib.parse import quote
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog,
    QTextEdit, QLineEdit, QMessageBox, QListWidget, QStatusBar
)


class DufsMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("dufs GUI客户端 by Guo")
        self.setGeometry(100, 100, 600, 400)

        # 创建中心 widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 布局
        layout = QVBoxLayout(central_widget)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # IP地址输入框
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("输入服务器IP地址")
        layout.addWidget(self.ip_input)

        # 端口输入框
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("输入服务器端口")
        layout.addWidget(self.port_input)

        # 远程目录输入框
        self.remote_dir_input = QLineEdit()
        self.remote_dir_input.setPlaceholderText("输入远程目录路径")
        layout.addWidget(self.remote_dir_input)

        # 文件列表视图
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        # 按钮
        self.upload_button = QPushButton("上传文件")
        self.upload_button.clicked.connect(self.upload_file)
        layout.addWidget(self.upload_button)

        self.download_button = QPushButton("下载文件")
        self.download_button.clicked.connect(self.download_file)
        layout.addWidget(self.download_button)

        self.list_button = QPushButton("列出目录")
        self.list_button.clicked.connect(self.list_directory)
        layout.addWidget(self.list_button)

        # 输出框
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

    def get_base_url(self):
        """获取基础URL"""
        ip = self.ip_input.text().strip() if self.ip_input.text() else None
        port = self.port_input.text().strip() if self.port_input.text() else None
        if not ip or not port:
            QMessageBox.warning(self, "警告", "请输入服务器IP地址和端口")
            return None
        return f"http://{ip}:{port}"

    def upload_file(self):
        """上传文件到远程目录"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择要上传的文件")
        if file_path:
            base_url = self.get_base_url()
            if not base_url:
                return
            remote_dir = self.remote_dir_input.text().strip() if self.remote_dir_input.text() else None
            if not remote_dir:
                QMessageBox.warning(self, "警告", "请输入远程目录路径")
                return
            encoded_dir = quote(remote_dir.rstrip('/'))
            file_name = file_path.split('/')[-1]
            encoded_file = quote(file_name)
            url = f"{base_url}/{encoded_dir}/{encoded_file}"
            print(f"上传文件的 URL: {url}")
            command = ["curl", "-T", file_path, url]
            self.run_command(command)

    def download_file(self):
        """从远程目录下载文件"""
        selected_item = self.file_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "警告", "请先选择要下载的文件")
            return
        file_name = selected_item.text().strip() if selected_item.text() else None
        if not file_name:
            QMessageBox.warning(self, "警告", "请选择有效的文件")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "选择保存位置", file_name)
        if file_path:
            base_url = self.get_base_url()
            if not base_url:
                return
            remote_dir = self.remote_dir_input.text().strip() if self.remote_dir_input.text() else None
            if not remote_dir:
                QMessageBox.warning(self, "警告", "请输入远程目录路径")
                return
            encoded_dir = quote(remote_dir.rstrip('/'))
            encoded_file = quote(file_name)
            url = f"{base_url}/{encoded_dir}/{encoded_file}"
            print(f"下载文件的 URL: {url}")
            command = ["curl", "-o", file_path, url]
            self.run_command(command)

    def list_directory(self):
        """列出远程目录内容"""
        base_url = self.get_base_url()
        if not base_url:
            return
        remote_dir = self.remote_dir_input.text().strip() if self.remote_dir_input.text() else None
        if not remote_dir:
            QMessageBox.warning(self, "警告", "请输入远程目录路径")
            return
        encoded_dir = quote(remote_dir.rstrip('/'))
        url = f"{base_url}/{encoded_dir}?simple"
        print(f"列出目录的 URL: {url}")
        command = ["curl", url]
        output = self.run_command(command)
        if output:
            self.file_list.clear()
            for line in output.splitlines():
                self.file_list.addItem(line)

    def run_command(self, command):
        """执行命令并捕获输出"""
        try:
            # 使用encoding='utf-8'并忽略编码错误
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if result.returncode == 0:
                self.status_bar.showMessage("操作成功", 5000)
                self.text_edit.append(f"成功: {result.stdout}")
                return result.stdout
            else:
                self.status_bar.showMessage("操作失败", 5000)
                self.text_edit.append(f"错误: {result.stderr}")
                QMessageBox.warning(self, "警告", f"命令执行失败: {result.stderr}")
                return None
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发生异常: {str(e)}")
            return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DufsMainWindow()
    window.show()
    sys.exit(app.exec())
