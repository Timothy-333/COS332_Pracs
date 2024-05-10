import os
import hashlib
import socket
import time

# FTP server details
FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = 21
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

# Local and remote file paths
LOCAL_FILE_PATH = "file.txt"
REMOTE_FILE_PATH = "file.txt"
REMOTE_HASH_PATH = "file.md5"


# Function to calculate the hash of a file
def calculate_hash(file_path):
    with open(file_path, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()

# Function to send a command to the FTP server
def send_command(sock, cmd):
    sock.sendall((cmd + "\r\n").encode())
    return sock.recv(1024).decode()

def set_pasv(sock):
    global ip_address, port_number, data_sock
    response = send_command(sock, "PASV")
    start = response.find("(") + 1
    end = response.find(")")
    numbers = list(map(int, response[start:end].split(",")))
    ip_address = ".".join(map(str, numbers[:4]))
    port_number = numbers[4]*256 + numbers[5]
    return socket.create_connection((ip_address, port_number))

# Function to download a file from the FTP server
def download_file(sock, remote_file_path, local_file_path):
    print("Downloading file from FTP server...")
    data_sock = set_pasv(sock)
    # Send the RETR command over the control connection
    print(send_command(sock, "RETR " + remote_file_path))
    # Receive the file data over the data connection
    with open(local_file_path, "wb") as f:
        while True:
            data = data_sock.recv(1024)
            if not data:
                break
            f.write(data)
    print("File downloaded successfully!")
    data_sock.close()

try:
    while True:
        sock = socket.create_connection((FTP_HOST, FTP_PORT))
        sock.recv(1024).decode()
        send_command(sock, "USER " + FTP_USER)
        send_command(sock, "PASS " + FTP_PASS)
        # Check if the local file exists
        if not os.path.exists(LOCAL_FILE_PATH):
            print("File was Deleted")
            download_file(sock, REMOTE_FILE_PATH, LOCAL_FILE_PATH)
        else:
            # If it does, calculate its hash
            data_sock = set_pasv(sock)
            local_file_hash = calculate_hash(LOCAL_FILE_PATH)
            send_command(sock, "RETR " + REMOTE_HASH_PATH)
            # Receive the file data over the data connection
            data = b""
            while True:
                chunk = data_sock.recv(1024)
                if not chunk:
                    break
                data += chunk
            # Convert the data to a string and strip leading/trailing whitespace
            remote_file_hash = data.decode().strip()
            parts = remote_file_hash.split()
            remote_file_hash = parts[0] if len(parts) > 1 else None
            print("Local file hash:", local_file_hash)
            print("Remote file hash:", remote_file_hash)
            data_sock.close()
            if local_file_hash != remote_file_hash:
                print("File was Edited")
                sock.close()
                sock = socket.create_connection((FTP_HOST, FTP_PORT))
                sock.recv(1024).decode()
                send_command(sock, "USER " + FTP_USER)
                send_command(sock, "PASS " + FTP_PASS)
                download_file(sock, REMOTE_FILE_PATH, LOCAL_FILE_PATH)
        sock.close()
        time.sleep(10)
finally:
    if data_sock:
        data_sock.close()  # Close the data connection
    sock.close()  # Close the control connection