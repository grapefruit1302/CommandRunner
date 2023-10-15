import re
import time
import paramiko
import sys

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




def process_commands(filename):
    try:
        with open(filename, 'r') as file:
            commands = file.read().splitlines()
        return commands
    except Exception as e:
        print(f'Error reading commands file: {e}')
        sys.exit(1)

def main():
    ssh_host = input('Enter SSH host address: ')
    ssh_port = int(input('Enter SSH port: '))
    ssh_username = input('Enter SSH username: ')
    ssh_password = input('Enter SSH password: ')
    telnet_username = ssh_username
    telnet_password = ssh_password

    switches_file = input('Enter the path to the file with switch data: ')
    commands_file = input('Enter the path to the file with commands: ')
    check = input('Enter check string to verify command execution: ')

    try:
        with open(switches_file, 'r') as file:
            text = file.read()
    except Exception as e:
        print(f'Error reading switches file: {e}')
        sys.exit(1)

    commands = process_commands(commands_file)

    pattern = r'sw-\S+'
    matches = re.findall(pattern, text)

    print("Start!!!")

    for i in matches:
        client = SSHAndTelnetClient(ssh_host, ssh_port, ssh_username, ssh_password, i + ".te.clb", telnet_username, telnet_password)
        client.connect_ssh()
        client.connect_telnet()
        res = ""

        start_time = time.time()


        for command in commands:
            if command == commands[-1]:
                res += client.send_telnet_command(command)
            else:
                res += client.send_telnet_command(command)

        client.send_telnet_command("")
        end_time = time.time()
        execution_time = round(end_time - start_time, 2)
        if check in res:
            res2 = str(i + " - Good |" + str(execution_time) + " seconds")
            print(res2)
        else:
            res2 = str(i + " - BAD!!!")
            print(res2)
        client.close_connections()

    print("Done!!!")

if __name__ == '__main__':
    main()
