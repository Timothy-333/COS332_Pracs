import os
import socket
import threading
import logging
import email as email_lib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# The username and password for the proxy server
PROXY_USERNAME = os.getenv('PROXY_USERNAME')
PROXY_PASSWORD = os.getenv('PROXY_PASSWORD')

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

# Real POP3 server credentials and address
POP3_SERVER_ADDR = (os.getenv('POP3_SERVER_ADDR'), int(os.getenv('POP3_SERVER_PORT', 110)))
POP3_USERNAME = os.getenv('POP3_USERNAME')
POP3_PASSWORD = os.getenv('POP3_PASSWORD')

def authenticate(client_sock):
    # Read the username and password from the client
    client_sock.send(b"+OK POP3 proxy ready\r\n")
    data = client_sock.recv(1024).decode("utf-8").strip()
    if data.upper() == "CAPA":
            handle_capa_command(client_sock)
            data = client_sock.recv(1024).decode("utf-8").strip()
    if data.upper().startswith("USER"):
        username = data.split()[1]
        logging.info("Received username: %s", username)
        client_sock.send(b"+OK\r\n")
    else:
        client_sock.send(b"-ERR Invalid command\r\n")
        return False

    data = client_sock.recv(1024).decode("utf-8").strip()
    if data.upper().startswith("PASS"):
        password = data.split()[1]
        logging.info("Received password")
        if username == PROXY_USERNAME and password == PROXY_PASSWORD or (username == ADMIN_USERNAME and password == ADMIN_PASSWORD):
            client_sock.send(b"+OK Proxy authentication successful\r\n")
            print("Proxy authentication successful")
            return username
        else:
            client_sock.send(b"-ERR Proxy authentication failed\r\n")
            print("Proxy authentication failed")
            return none
    else:
        client_sock.send(b"-ERR Invalid command\r\n")
        return False

def handle_capa_command(client_sock):
    capa_response = (
        "+OK Capability list follows\r\n"
        "USER\r\n"
        "RESP-CODES\r\n"
        "LOGIN-DELAY\r\n"
        "TOP\r\n"
        "UIDL\r\n"
        ".\r\n"
    )
    client_sock.send(capa_response.encode("utf-8"))

def connect_to_pop3_server():
    # Create a socket and connect to the POP3 server
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.connect(POP3_SERVER_ADDR)
    
    # Read the server greeting
    server_sock.recv(1024)

    # Authenticate with the POP3 server
    server_sock.send(f"USER {POP3_USERNAME}\r\n".encode("utf-8"))
    server_sock.recv(1024)
    server_sock.send(f"PASS {POP3_PASSWORD}\r\n".encode("utf-8"))
    server_sock.recv(1024)

    return server_sock

def relay_messages(client_sock, server_sock, username):
    try:
        while True:
            client_msg = client_sock.recv(1024)
            if not client_msg:
                break
            logging.info("Client -> Server: %s", client_msg.strip())

            # Only allow the user to delete emails if they have the correct username
            if client_msg.upper().startswith(b"DELE") and username != "admin":
                client_sock.send(b"-ERR You don't have permission to delete emails\r\n")
                continue

            server_sock.send(client_msg)
            
            server_msg = server_sock.recv(1024)
            if not server_msg:
                break
            logging.info("Server -> Client: %s", server_msg.strip())

            if server_msg.startswith(b"+OK") and b"\r\n.\r\n" in server_msg:
                # Parse the email
                email = email_lib.message_from_bytes(server_msg)

                # Check if the subject line contains 'Confidential'
                if "Confidential" in email["Subject"]:
                    # Replace the email with a cover email
                    email = email_lib.message_from_string("Subject: Just testing\r\n\r\nJust testing")
                    server_msg = email.as_bytes()

                # Add 'Handled by <username>' to the body of the email
                if email.is_multipart():
                    for part in email.get_payload():
                        if part.get_content_type() == "text/plain":
                            part.set_payload(part.get_payload() + "\n\nHandled by " + username)
                else:
                    email.set_payload(email.get_payload() + "\n\nHandled by " + username)

                server_msg = email.as_bytes()
            client_sock.send(server_msg)
    except Exception as e:
        logging.error("Error relaying messages: %s", e)

def handle_client(client_sock):
    try:
        # Authenticate the client
        username = authenticate(client_sock)
        if not username:
            client_sock.close()
            return
        
        # Connect to the POP3 server
        server_sock = connect_to_pop3_server()

        # Relay messages between the client and the POP3 server
        relay_messages(client_sock, server_sock, username)
    except Exception as e:
        logging.error("Error handling client: %s", e)
    finally:
        client_sock.close()
        if 'server_sock' in locals():
            server_sock.close()

def start_server():
    # Create a server socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(("localhost", 55555))
    server_sock.listen(5)
    logging.info("POP3 proxy server listening on port 55555")

    try:
        while True:
            client_sock, client_addr = server_sock.accept()
            logging.info("Accepted connection from %s:%s", client_addr[0], client_addr[1])
            threading.Thread(target=handle_client, args=(client_sock,)).start()
    except KeyboardInterrupt:
        logging.info("Shutting down server")
    finally:
        server_sock.close()

if __name__ == "__main__":
    start_server()
