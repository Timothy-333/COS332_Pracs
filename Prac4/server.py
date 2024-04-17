import socket
import random
import threading
from urllib.parse import urlparse, parse_qs

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


def handle_client(conn, addr, questions):
    global score
    global current_questions
    request = conn.recv(1024).decode()
    headers = request.split('\n')
    get_line = headers[0]
    ip, port = addr
    if ' ' not in get_line:
        return
    line_parts = get_line.split(' ')
    method, path = line_parts[0], line_parts[1]
    if method == 'GET':
        # Parse the URL and the query parameters
        parsed_path = urlparse(path)
        params = parse_qs(parsed_path.query)

        if parsed_path.path == '/favicon.ico':
            return
        # Check if the 'answer' parameter is provided
        if 'answer' in params and questions and ip in current_questions:
            answer = params['answer'][0]
            # Check the answer and update the score
            if answer.upper() == current_questions[ip].answer:
                response_body = 'Congratulations!<br/>\r\n'
                score += 1
            else:
                response_body = 'Wrong answer. The correct answer is: ' + current_questions[ip].answer + '<br/>\r\n'
        else:
            response_body = ''

        # Select a question and remove it from the list
        if questions:
            question = random.choice(questions)
            questions.remove(question)
            current_questions[ip] = question

            # Construct the HTTP response
            response_body += (question.question + '<br/>\r\n' +
                              '<br/>\r\n'.join(question.options) + '<br/>\r\n' +
                              '<form method="get">\r\n' +
                              '<input type="text" name="answer" placeholder="Enter your answer">\r\n' +
                              '<input type="submit" value="Submit">\r\n' +
                              '</form>\r\n')
        else:
            response_body += 'Game over! Your score is: ' + str(score) + '/' + str(total) + '\r\n'
        response = ('HTTP/1.1 200 OK\r\n' +
                    'Content-type: text/html\r\n' +
                    'Content-Length: ' + str(len(response_body)) + '\r\n' +
                    '\r\n' +
                    response_body)

        conn.sendall(response.encode())
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
                thread = threading.Thread(target=handle_client, args=(conn, addr, questions))
                thread.start()
    except KeyboardInterrupt:
        print("Server is stopping...")

questions = load_questions('questions.txt')
current_questions = {}
total = len(questions)
score = 0
start_server(questions)