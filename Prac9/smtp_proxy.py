import socket
import logging

# Configuration
SMTP_PROXY_HOST = "localhost"
SMTP_PROXY_PORT = 55556

REAL_SMTP_HOST = "localhost"
REAL_SMTP_PORT = 25

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SMTPProxyServer:
    def __init__(self):
        self.server_socket = None

    def handle_client(self, client_socket):
    logging.info("Client connected")

    try:
        # Connect to the real SMTP server and get its greeting
        with socket.create_connection((REAL_SMTP_HOST, REAL_SMTP_PORT)) as smtp_socket:
            server_greeting = smtp_socket.makefile('r').readline()
            logging.debug("Server greeting: %s", server_greeting.strip())

            # Send server greeting to client
            client_socket.sendall(server_greeting.encode())

            # Receive and forward subsequent commands and email data
            client_file = client_socket.makefile('r')
            smtp_file = smtp_socket.makefile('r')
            while True:
                command = client_file.readline()
                if not command:
                    break
                smtp_socket.sendall(command.encode())
                reply = smtp_file.readline()
                client_socket.sendall(reply.encode())

    except Exception as e:
        logging.error("Error handling client: %s", e)

    finally:
        client_socket.close()
        logging.info("Client disconnected")

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((SMTP_PROXY_HOST, SMTP_PROXY_PORT))
        self.server_socket.listen()

        logging.info("SMTP proxy server started on %s:%s", SMTP_PROXY_HOST, SMTP_PROXY_PORT)

        while True:
            client_socket, client_address = self.server_socket.accept()
            self.handle_client(client_socket)

    def stop_server(self):
        if self.server_socket:
            self.server_socket.close()
            logging.info("SMTP proxy server stopped")

def main():
    proxy_server = SMTPProxyServer()
    proxy_server.start_server()

if __name__ == "__main__":
    main()
