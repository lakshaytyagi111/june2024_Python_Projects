# this is an improved version of the SSH server that we created in the previous section
# we have added logging to the server to log the events that occur in the server
# also we have added a function to execute the command that the client sends to the server
# the function will execute the command and send the output of the command to the client
#  the server is started at 127.0.0.1:22 by default
#  to stop the server, press Ctrl+C
#  use sudo to run the server
import socket
import paramiko
import threading
import subprocess

# Import logging module for improved logging capabilities
import logging

# Configure logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up host key for SSH server
HOST_KEY = paramiko.RSAKey(filename='test_rsa_key.key')

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
    
    def check_channel_request(self, kind, chanid):
        # Only accept session type channels
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_auth_password(self, username, password):
        # Very simple authentication, should be replaced with real auth in production
        if (username == 'admin') and (password == 'admin'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

def run_command(command):
    command = command.rstrip()

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except Exception as e:
        output = b"Failed to execute command.\r\n"

    return output

def handle_connection(client):
    try:
        # Create a new transport object for the client
        transport = paramiko.Transport(client)
        transport.add_server_key(HOST_KEY)
        
        server = Server()
        try:
            # Start the transport server
            transport.start_server(server=server)
        except paramiko.SSHException as e:
            logging.error("SSH negotiation failed: %s", str(e))
            return
        
        # Wait for an authenticated channel from the client
        chan = transport.accept(20)
        if chan is None:
            logging.error("No channel.")
            return
        
        logging.info("Authenticated!")
        chan.send("Welcome to the SSH server!\n")
        
        while True:
            try:
                # Read a command from the client
                command = chan.recv(1024).decode('utf-8').strip()
                if command.lower() == 'exit':
                    logging.info("Client requested exit.")
                    break
                # Execute the command and send the result back to the client
                logging.info("Executing command: %s", command)
                exec_result = run_command(command)
                print(exec_result)
                result = f"Executed command: {command}\n"
                chan.send(result)
            except Exception as e:
                logging.error("Exception: %s", str(e))
                break
        
        chan.close()
    except Exception as e:
        logging.error("Exception: %s", str(e))
    finally:
        client.close()

def start_server(host='127.0.0.1', port=22):
    # Create a socket to listen for incoming connections
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(100)
    
    logging.info(f"Listening for connection on {host}:{port}...")

    while True:
        client, addr = sock.accept()
        logging.info(f"Connection from {addr}")
        threading.Thread(target=handle_connection, args=(client,)).start()

def usage():
    print("Usage:")
    print("sudo python improved_ssh_server.py")
    print("The server listens on 127.0.0.1:22 by default.")
    print("To stop the server, press Ctrl+C.")

if __name__ == '__main__':
    usage()
    start_server()