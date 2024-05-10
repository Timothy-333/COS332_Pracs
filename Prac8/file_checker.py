import os
import hashlib
import ftplib
import time

# FTP server details
FTP_HOST = "ftp.example.com"
FTP_USER = "username"
FTP_PASS = "password"

# Local and remote file paths
LOCAL_FILE_PATH = "path/to/local/file.txt"
REMOTE_FILE_PATH = "path/to/remote/backup_file.txt"

# Function to calculate the hash of a file
def calculate_hash(file_path):
    with open(file_path, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()

# Function to download a file from the FTP server
def download_file(ftp, remote_file_path, local_file_path):
    with open(local_file_path, "wb") as f:
        ftp.retrbinary("RETR " + remote_file_path, f.write)

# Connect to the FTP server
ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)

# Infinite loop
while True:
    # Check if the local file exists
    if not os.path.exists(LOCAL_FILE_PATH):
        # If it doesn't, download the file from the FTP server
        download_file(ftp, REMOTE_FILE_PATH, LOCAL_FILE_PATH)
    else:
        # If it does, calculate its hash
        local_file_hash = calculate_hash(LOCAL_FILE_PATH)

        # Download the hash of the remote file from the FTP server
        remote_file_hash = ftp.sendcmd("MD5 " + REMOTE_FILE_PATH).split()[1]

        # If the local file hash doesn't match the remote file hash, download the file from the FTP server
        if local_file_hash != remote_file_hash:
            download_file(ftp, REMOTE_FILE_PATH, LOCAL_FILE_PATH)

    # Sleep for a minute
    time.sleep(60)