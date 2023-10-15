from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
import sys
import re
import time
import paramiko

class Worker(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, ssh_host, ssh_port, ssh_username, ssh_password, telnet_username, telnet_password, text, commands, check):
        super(Worker, self).__init__()
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_username = ssh_username
        self.ssh_password = ssh_password
        self.telnet_username = telnet_username
        self.telnet_password = telnet_password
        self.text = text
        self.commands = commands
        self.check = check

    def run(self):
        self.connect_to_switches()

    def connect_to_switches(self):
        pattern = r'sw-\S+'
        matches = re.findall(pattern, self.text)   #відфільтровані комутатори

        for i in matches:
            client = SSHAndTelnetClient(self.ssh_host, self.ssh_port, self.ssh_username, self.ssh_password, i + ".te.clb", self.telnet_username, self.telnet_password)
            client.connect_ssh()
            client.connect_telnet()
            res = ""

            start_time = time.time()

            for command in self.commands:
                if command == self.commands[len(self.commands) - 1]:
                    res += client.send_telnet_command(command)
                
                else:
                    res += client.send_telnet_command(command)

            client.send_telnet_command("")
            end_time = time.time()
            execution_time = round(end_time - start_time, 2)
            if self.check in res:
                res2 = str(i + " - Good |" + str(execution_time) + " seconds")
                self.update_signal.emit(res2)
            else:
                res2 = str(i + " - BAD!!!")
                self.update_signal.emit(res2)
        self.update_signal.emit("Done!!!")

class SSHAndTelnetClient:  
    def __init__(self, ssh_host, ssh_port, ssh_username, ssh_password, telnet_host, telnet_username, telnet_password):
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_username = ssh_username
        self.ssh_password = ssh_password
        self.telnet_host = telnet_host
        self.telnet_username = telnet_username
        self.telnet_password = telnet_password

    def connect_ssh(self):  
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(self.ssh_host, port=self.ssh_port, username=self.ssh_username, password=self.ssh_password)
        except Exception as e:
            print(f'Error connecting via SSH: {e}')
            exit(1)

    def connect_telnet(self):  
        try:
            self.telnet_channel = self.ssh_client.invoke_shell()
            self.telnet_channel.send("telnet " + self.telnet_host + "\n")
            time.sleep(1) 
            self.telnet_channel.send(self.telnet_username + "\n")
            self.telnet_channel.send(self.telnet_password + "\n")
            response = self.telnet_channel.recv(4096).decode('utf-8')
        except Exception as e:
            print(f'Error connecting via Telnet: {e}')
            self.ssh_client.close()
            exit(1)

    def send_telnet_command(self, command):  
        try:
            self.telnet_channel.send(command + "\n")
            time.sleep(1)  
            response = self.telnet_channel.recv(4096).decode('utf-8')
        except Exception as e:
            print(f'Error sending Telnet command: {e}')
        return response

    def close_connections(self):
        self.telnet_channel.close()
        self.ssh_client.close()
        print('Connections closed.')

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi('CommandRun.ui', self)
        self.setFixedSize(1070, 666)
        self.pushButton.clicked.connect(self.run_command)
        self.worker = None
    
    def add_log(self, message):
        self.textEdit_3.append(message)
        cursor = QTextCursor(self.textEdit_3.document())
        cursor.movePosition(QTextCursor.End)
        self.textEdit_3.setTextCursor(cursor)

    def update_results(self, result):
        self.add_log(result)

    def run_command(self):
        if not self.lineEdit.text().strip() or not self.lineEdit_2.text().strip() or not self.lineEdit_3.text().strip() or not self.lineEdit_4.text().strip() or not self.lineEdit_5.text().strip():
            self.add_log("Please fill in all the required fields.")
            return
        self.add_log("Starting...")
        self.add_log("Detectable switches:")

        ssh_host = self.lineEdit.text()
        ssh_port = int(self.lineEdit_4.text())
        ssh_username = self.lineEdit_3.text()
        ssh_password = self.lineEdit_2.text()
        check = self.lineEdit_5.text()
        telnet_username = ssh_username
        telnet_password = ssh_password
        text = self.textEdit.toPlainText()
        commands_1 = self.textEdit_2.toPlainText()

        commands = commands_1.splitlines()
        self.worker = Worker(ssh_host, ssh_port, ssh_username, ssh_password, telnet_username, telnet_password, text, commands, check)
        self.worker.update_signal.connect(self.update_results)
        self.worker.start()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())