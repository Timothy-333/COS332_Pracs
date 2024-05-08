import socket
import poplib
import time
from email.parser import BytesParser
from email.policy import default
import os

# echo -e "Subject: test\nTo: root@localhost\nBcc: timothy@localhost\n\nHello World." | sendmail -t
# POP3 server details
pop3_server = os.getenv('POP3_SERVER')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

# SMTP server details
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = int(os.getenv('SMTP_PORT'))  # Convert to int because environment variables are loaded as strings


# Connect to the POP3 server and log in
pop3 = poplib.POP3(pop3_server)
pop3.user(username)
pop3.pass_(password)


try:
    while True:
        pop3 = poplib.POP3(pop3_server)
        print(f'Connected to {pop3_server}. Server says: {pop3.getwelcome().decode()}')

        response_message = pop3.user(username)
        print(f'Sent username. Server says: {response_message.decode()}')

        response_message = pop3.pass_(password)
        print(f'Sent password. Server says: {response_message.decode()}')
        response, email_list, _ = pop3.list()
        num_messages = len(email_list)
        if num_messages > 0:
            raw_email = b'\n'.join(pop3.retr(num_messages)[1])
            email = BytesParser(policy=default).parsebytes(raw_email)
            # Look for the 'Bcc' field
            if email["To"] and email["X-Original-To"] != email["To"]:
                # Extract the original email's subject
                original_subject = email['Subject']
                print(email["to"])
                print(email["X-Original-To"])
                # SMTP server details
                smtp_server = 'localhost'
                smtp_port = 25
                with socket.create_connection((smtp_server, smtp_port)) as server:
                    server.sendall(b'HELO localhost\r\n')
                    while True:
                        reply = server.recv(1024)
                        print("Response to HELO command:", reply)
                        if reply.startswith(b'220'):
                            break
                        elif not reply:
                            raise Exception('HELO failed: no response')

                    server.sendall(b'MAIL FROM:<warning@localhost>\r\n')
                    while True:
                        reply = server.recv(1024)
                        print('Response to MAIL FROM command:', reply)
                        if reply.startswith(b'250'):
                            break
                        elif not reply:
                            raise Exception('MAIL FROM failed: no response')

                    server.sendall(f'RCPT TO:<{username}>\r\n'.encode())
                    while True:
                        reply = server.recv(1024)
                        print('Response to RCPT TO command:', reply)
                        if reply.startswith(b'250'):
                            break
                        elif not reply:
                            raise Exception('RCPT TO failed: no response')

                    server.sendall(b'DATA\r\n')
                    while True:
                        reply = server.recv(1024)
                        print('Response to DATA command:', reply)
                        if reply.startswith(b'354'):
                            break
                        elif not reply:
                            raise Exception('DATA failed: no response')

                    message = f'Subject: [BCC Warning] {original_subject}\n\nYou have received a BCC email.'
                    server.sendall((message + '\r\n.\r\n').encode())
                    while True:
                        reply = server.recv(1024)
                        print('Response to email data:', reply)
                        if reply.startswith(b'250'):
                            break
                        elif not reply:
                            raise Exception('End of data marker failed: no response')

                    server.sendall(b'QUIT\r\n')
                    while True:
                        reply = server.recv(1024)
                        print('Response to QUIT command:', reply)
                        if reply.startswith(b'221'):
                            break
                        elif not reply:
                            raise Exception('QUIT failed: no response')
            pop3.quit()
            time.sleep(20)
finally:
    pop3.quit()