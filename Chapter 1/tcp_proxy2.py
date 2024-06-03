# this is a dynamic tcp proxy that can handle http and https requests
# but there is some issue with the code, it is not working as expected
# I am working on it to fix the issue
# I will update the code as soon as I fix the issue
import sys
import socket
import threading
import ssl


ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.options |= ssl.OP_NO_SSLv2
ssl_context.options |= ssl.OP_NO_SSLv3


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

def resolve_hostname(hostname):
    try:
        return socket.gethostbyname(hostname)
    except socket.error as e:
        print(f"[!!] DNS resolution failed for {hostname}: {e}")
        return None

def server_loop(local_host, local_port):
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
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket,))
        proxy_thread.start()

def parse_http_request(buffer):
    headers = buffer.split(b"\r\n")
    if len(headers) == 0 or len(headers[0].split()) < 3:
        return None, None, None, None, None

    first_line = headers[0].decode()
    method, path, version = first_line.split()
    host = None
    port = 80
    for header in headers[1:]:
        if header.lower().startswith(b"host:"):
            host = header.split(b" ")[1].decode()
            if ':' in host:
                host, port = host.split(':')
                port = int(port)
            break
    return method, path, version, host, port

def proxy_handler(client_socket):
    request = receive_from(client_socket)
    method, path, version, host, port = parse_http_request(request)
    if host:
        print(f"[=>] Resolving hostname: {host}")
        remote_ip = resolve_hostname(host)
        if not remote_ip:
            print("[!!] Failed to resolve hostname.")
            client_socket.close()
            return

        print(f"[=>] Connecting to {host} ({remote_ip}):{port}")

        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            remote_socket.connect((remote_ip, port))
            if port == 443:
                remote_socket = ssl.wrap_socket(remote_socket)

            remote_socket.send(request)

            while True:
                remote_buffer = receive_from(remote_socket)
                if len(remote_buffer):
                    print(f"[<==] Received {len(remote_buffer)} bytes from {host}")
                    client_socket.send(remote_buffer)

                local_buffer = receive_from(client_socket)
                if len(local_buffer):
                    print(f"[==>] Received {len(local_buffer)} bytes from localhost")
                    remote_socket.send(local_buffer)

                if not len(remote_buffer) and not len(local_buffer):
                    client_socket.close()
                    remote_socket.close()
                    break
        except Exception as e:
            print(f"[!!] Error: {e}")
            remote_socket.close()
            client_socket.close()

def main():
    if len(sys.argv[1:]) != 2:
        print("Usage: python tcp_proxy.py [localhost] [localport]")
        print("Example: python tcp_proxy.py 127.0.0.1 8080")
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    server_loop(local_host, local_port)

if __name__ == "__main__":
    main()
