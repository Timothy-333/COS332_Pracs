import socket
import threading
import logging

# The username and password for the proxy server
PROXY_USERNAME = "proxyuser"
PROXY_PASSWORD = "proxypass"

# The address and credentials for the POP3 server
POP3_SERVER_ADDR = ("pop3.server.com", 110)
POP3_USERNAME = "pop3user"
POP3_PASSWORD = "pop3pass"

def authenticate(client_sock):
    # Read the username and password from the client
    username = client_sock.recv(1024).decode("utf-8")
    password = client_sock.recv(1024).decode("utf-8")

    # Check if the username and password are correct
    if username == PROXY_USERNAME and password == PROXY_PASSWORD:
        return True
    else:
        return False

def connect_to_pop3_server():
    # Create a socket and connect to the POP3 server
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.connect(POP3_SERVER_ADDR)

    # Authenticate with the POP3 server
    server_sock.send(f"USER {POP3_USERNAME}\r\n".encode("utf-8"))
    server_sock.send(f"PASS {POP3_PASSWORD}\r\n".encode("utf-8"))

    return server_sock

def relay_messages(client_sock, server_sock):
    while True:
        # Read a message from the client and send it to the server
        client_msg = client_sock.recv(1024)
        if not client_msg:
            break
        server_sock.send(client_msg)

        # Read a message from the server and send it to the client
        server_msg = server_sock.recv(1024)
        if not server_msg:
            break
        client_sock.send(server_msg)

def handle_client(client_sock):
    # Authenticate the client
    if not authenticate(client_sock):
        client_sock.close()
        return

    # Connect to the POP3 server
    server_sock = connect_to_pop3_server()

    # Relay messages between the client and the POP3 server
    relay_messages(client_sock, server_sock)

    # Close the connections
    client_sock.close()
    server_sock.close()

def start_server():
    # Create a server socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(("localhost", 55555))
    server_sock.listen()

    while True:
        # Accept a client connection
        client_sock, client_addr = server_sock.accept()

        # Handle the client connection in a new thread
        threading.Thread(target=handle_client, args=(client_sock,)).start()

start_server()