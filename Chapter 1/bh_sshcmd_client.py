# ssh client using python

import threading
import paramiko
import sys
import subprocess
from getpass import getpass

def ssh_command(ip, username, passwd, command):
    client = paramiko.SSHClient()
    # client.load_host_keys('/home/tests/.ssh/known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=username, password=passwd)
    print("Connected to %s" % ip)
    session = client.get_transport().open_session()

    if session.active:
        session.exec_command(command)
        print(command)
        print(session.recv(1024))
    
    return

def main():
    if len(sys.argv[1:]) != 1:
        print("Usage: python bh_sshcmd_client.py <target_ip>")
        sys.exit(0)
    
    target_ip = sys.argv[1]
    username = input("please enter username: ")
    password = getpass()
    
    while True:
        command = input("<Shell:#> ")
        if command == 'exit':
            break
        else:
            ssh_command(target_ip, username, password, command)

if __name__ == '__main__':
    main()
