import sys
import socket
import threading


def hexdump(src, length=16):
    result = []
    digits = 4
    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = ' '.join([f"{x:02X}" for x in s])
        text = ''.join([chr(x) if 0x20 <= x < 0x7f else '.' for x in s])
        result.append(f"{i:04x}  {hexa:<{length*3}}  {text}")
    print('\n'.join(result))

def receive_from(connection):
    buffer = bytearray()
    connection.settimeout(2)

    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer.extend(data)
    except:
        pass
    return buffer

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f"[!!] Failed to listen on {local_host}:{local_port}")
        print(f"[!!] Exception: {e}")
        sys.exit(0)

    print(f"[*] Listening on {local_host}:{local_port}")
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        print(f"[=>] Received connection from {addr[0]}:{addr[1]}")
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        remote_buffer = response_handler(remote_buffer)
        if len(remote_buffer):
            client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print(f"[==>] Received {len(local_buffer)} bytes from localhost")
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote host")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print(f"[<==] Received {len(remote_buffer)} bytes from remote")
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost")

def request_handler(buffer):
    # Modify requests destined for the remote host
    return buffer

def response_handler(buffer):
    # Modify responses destined for the local host
    return buffer

def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: python tcp_proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        print("Example: python tcp_proxy.py 127.0.0.1 8001 10.12.132.1 8001 True")
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5].lower() == 'true'

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == "__main__":
    main()
