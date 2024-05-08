import socket
import poplib
from email.parser import BytesParser
from email.policy import default

# POP3 server details
pop3_server = 'pop3.server.com'
username = 'username'
password = 'password'

# Connect to the POP3 server and log in
pop3 = poplib.POP3(pop3_server)
pop3.user(username)
pop3.pass_(password)

# Retrieve the list of email messages
num_messages = len(pop3.list()[1])

for i in range(num_messages):
    # Download the headers for each email
    raw_email = b'\n'.join(pop3.retr(i+1)[1])
    email = BytesParser(policy=default).parsebytes(raw_email)

    # Look for the 'Bcc' field
    if 'Bcc' in email:
        # Extract the original email's subject
        original_subject = email['Subject']

        # SMTP server details
        smtp_server = 'localhost'
        smtp_port = 25

        # Connect to the SMTP server
        with socket.create_connection((smtp_server, smtp_port)) as server:
            server.sendall(b'HELO localhost\r\n')
            server.recv(1024)  # Ignore the response

            server.sendall(b'MAIL FROM:<quizmaster@localhost>\r\n')
            server.recv(1024)  # Ignore the response

            server.sendall(f'RCPT TO:<{username}>\r\n'.encode())
            server.recv(1024)  # Ignore the response

            server.sendall(b'DATA\r\n')
            server.recv(1024)  # Ignore the response

            # Compose a warning email
            subject = f'[BCC Warning] {original_subject}'
            body = 'You have received a BCC email.'
            msg = f'Subject: {subject}\n\n{body}\r\n.\r\n'
            server.sendall(msg.encode())

            server.recv(1024)  # Ignore the response
            server.sendall(b'QUIT\r\n')

# Log out from the POP3 server
pop3.quit()