import socket
import random
import threading

class Question:
    def __init__(self, question, options, answer):
        self.question = question
        self.options = options
        self.answer = answer

def load_questions(filename):
    questions = []
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('?'):
                if 'question' in locals():
                    if not hasAnswer:  # Check if a question without a correct answer was encountered
                        options.append(chr(count) + ". None of the above")
                        questions.append(Question(question, options, chr(count)))
                    elif correct_answers > 1:  # Check if a question with more than one correct answer was encountered
                        options.append(chr(count) + ". More than one of the above")
                        questions.append(Question(question, options, chr(count)))
                    else:
                        questions.append(Question(question, options, answer))
                question = line[1:].strip()
                options = []
                count = 65
                hasAnswer = False
                correct_answers = 0
            elif line.startswith('-'):
                options.append(chr(count) + ". " + line[1:].strip())
                count += 1
            elif line.startswith('+'):
                options.append(chr(count) + ". " + line[1:].strip())
                answer = chr(count)
                hasAnswer = True
                correct_answers += 1
                count += 1
        if not hasAnswer:  # Check if the last question in the file doesn't have a correct answer
            options.append(chr(count) + ". None of the above")
            questions.append(Question(question, options, chr(count)))
        elif correct_answers > 1:  # Check if the last question in the file has more than one correct answer
            options.append(chr(count) + ". More than one of the above")
            questions.append(Question(question, options, chr(count)))
        else:
            questions.append(Question(question, options, answer))
    return questions

def serve_question(conn, questions):
    global score
    if questions == []:
        conn.sendall((b'\r\nScore: ' + str(score).encode() + b'/' + str(total).encode() + b'\r\n'))
        return False
    question = random.choice(questions)
    questions.remove(question)
    conn.sendall(('\r\n' + question.question + '\r\n' +'\r\n'.join(question.options) + '\r\n').encode())
    data = conn.recv(1024)
    if data.decode().strip().upper() == question.answer:
        conn.sendall(b'\r\nCongratulations!\r\n')
        score += 1
    else:
        conn.sendall(('\r\nWrong answer. The correct answer is: ' + question.answer + '\r\n').encode())
    conn.sendall(b'\r\nDo you want to continue? (yes/no)\r\n')
    data = conn.recv(1024)
    return data.decode().strip().lower() == 'y'

def handle_client(conn, questions):
    while serve_question(conn, questions):
        pass
    conn.close()

def start_server(questions):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 55555))
            s.listen()
            s.settimeout(1)
            while True:
                try:
                    conn, addr = s.accept()
                except socket.timeout:
                    continue
                thread = threading.Thread(target=handle_client, args=(conn, questions.copy()))
                thread.start()
    except KeyboardInterrupt:
        print("Server is stopping...")

questions = load_questions('questions.txt')
total = len(questions)
score = 0
start_server(questions)