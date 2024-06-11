# ssh server that takes command from client and executes it

import socket
import paramiko
import threading
import sys
import subprocess
from getpass import getpass

# using the key from paramiko demo files
# the key is used to encrypt the data from the server to the client
# the key is used to decrypt the data from the client to the server
# to create custom key, use the following command: ssh-keygen -t rsa -f test_rsa_key.key

host_key = paramiko.RSAKey(filename='test_rsa_key.key')
def run_command(command):

    command = command.rstrip()

    # run the command and get the output back
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except Exception as e:
        output = b"Failed to execute command.\r\n"

    # send the output back to the client
    return output

class Server(paramiko.ServerInterface):
    def _init_(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, channel_id):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        else:
            return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
        
    def check_auth_password(self, username, password):
        if (username == 'h') and (password == 'h'):
            return paramiko.AUTH_SUCCESSFUL
        else:
            return paramiko.AUTH_FAILED
    
server = sys.argv[1]   
ssh_port = int(sys.argv[2])
# pythion bh_ssh_server.py [server] [port]
# server is the ip address of the server
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #  if i don't use setsockopt, i get error: OSError: [Errno 98] Address already in use
    #  this is because the socket is in TIME_WAIT state and can't be reused
    #  setsockopt allows the socket to be reused
    #  reuse means that the socket can be used by another process
    #  example: if i run the server and client on the same machine, i get the error
    #  but if i run the server on one machine and client on another, i don't get the error
    #  because the socket is not in TIME_WAIT state
    #  TIME_WAIT state is the state of the socket after it has been closed
    #  sol_socket is the level of the socket option
    #  so_reuseaddr is the option to reuse the address
    #  1 is the value of the option: 1 means reuse the address 
    # to set multiple options, use bitwise OR
    #  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR | socket.SO_REUSEPORT, 1)
    #  this will allow the socket to be reused and the port to be reused
    
    sock.bind((server, ssh_port))
    sock.listen(100)

    print('[+] listening for connection on %s:%d ....' % (server, ssh_port))
    client, addr = sock.accept()
except Exception as e:
    print('[-] listening failed: ' + str(e))
    sys.exit(1)

print('[+] Got a connection!')

try:
    # creating a transport object: this is the server side of the ssh connection
    #  transprt means the transport layer of the ssh connection
    # it is the layer that is responsible for the encryption and decryption of data, 
    # for the authentication of the client and server, and for the negotiation of the encryption algorithms
    # negotiation means the process of agreeing on the encryption algorithms to be used 
    bhSession = paramiko.Transport(client)
    # adding the server key to the transport object
    # the server key is the key that is used to encrypt the data from the server to the client
    bhSession.add_server_key(host_key)
    # creating the server object
    server = Server()

    try:
        # starting the server
        bhSession.start_server(server=server)
    except paramiko.SSHException as e:
        print('[-] SSH negotiation failed.')
    # accepting the connection from the client
    channel = bhSession.accept(20)
    print("[+] Autheticated")
    # checking if the channel is active
    # channel is the connection between the client and the server from the server side
    # the channel is used to send and receive data between the client and the server
    # channel.recv means the server is receiving data from the client
    # channel.send means the server is sending data to the client
    # print(channel.recv(1024).decode())
    # sending welcome message to client
    channel.send("Welcome to bh_ssh")

    while True:
        try:
            print("1")
            channel.send(b'[bh_ssh]$ ')
            # Caught exception: a bytes-like object is required, not 'str'
            # the error is because the command is a string and it needs to be a bytes-like object
            # to convert the string to bytes-like object, use the encode method
            #  command = command.encode()
            # getting the command from the client
            # recieve until line ends
            cmd_buffer = ""
            while True:
                print("2")
                cmd_byte = channel.recv(1024)
                print("3" + str(type(cmd_byte.decode())) )
                # we cannot concate bytes-like object with string
                # to concate bytes-like object with string, convert the bytes-like object to string
                cmd_byte = cmd_byte.decode()
                cmd_buffer += cmd_byte
                if len(cmd_byte) < 1024:
                    break
            
            
            print('command received: ' + cmd_byte)
            if cmd_buffer != 'exit':
                # the server is sending the command to the client
                output = run_command(cmd_buffer)
                # printing the output of the command
                channel.send(output)
                print('output: ' + output.decode())
            else:
                channel.send('exit')
                print('exiting')
                bhSession.close()
                raise Exception('exit')
        except KeyboardInterrupt:
            bhSession.close()
except Exception as e:
    print('[-] Caught exception: ' + str(e))
    try:
        bhSession.close()
    except:
        pass
    sys.exit(1)
    
# to run the server, use the following command: python bh_ssh_server.py
# to run the client, use the following command: python bh_sshcmd_client.py
#  if this returns not a valid RSA private key file, use the following command: ssh-keygen -t rsa -f test_rsa_key.key
# if still not working, use the following command: ssh-keygen -t rsa -f test_rsa_key.key -m PEM
# this will create a key in PEM format