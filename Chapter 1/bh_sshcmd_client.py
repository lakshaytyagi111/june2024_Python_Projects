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
    print("Connected to server %s" % ip)

    # now we have a connection to the remote machine
    # open a session on the remote machine, means we can execute commands on the remote machine
    session = client.get_transport().open_session()

    if session.active:
        # sending bytes-like object
        # execute the command on the remote machine
        
        # converting the command to bytes-like object
        
        command = command.encode()
        session.send(command)
        # session.exec_command(command)
        print(command)
        print("Command sent")
        # getting the response from the remote machine till no more data is available to recieve from the remote machine
        while True:
            # recieving the response from the remote machine
            response = session.recv(1024)
            # converting the response to string
            response = response.decode()
            print(response)
            if not response:
                break
        
    
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
        command.rstrip()
        
        if command == 'exit':
            break
        else:
            ssh_command(target_ip, username, password, command)

if __name__ == '__main__':
    main()
