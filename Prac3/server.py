import http.server
import socketserver
import subprocess

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        response = handle_http_request(self.path)
        if response.startswith('HTTP/1.1 200 OK'):
            self.send_response(200)
        elif response.startswith('HTTP/1.1 404 Not Found'):
            self.send_response(404)
        elif response.startswith('HTTP/1.1 500 Internal Server Error'):
            self.send_response(500)
        else:
            self.send_response(500)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(response, "utf8"))
        return

def handle_http_request(request):
    if request == '/prev':
        executable = './prev'
    elif request == '/next':
        executable = './next'
    else:
        return 'HTTP/1.1 404 Not Found\r\n\r\n'

    result = subprocess.run([executable], capture_output=True, text=True)

    # Check if the C++ executable ran successfully
    if result.returncode != 0:
        return 'HTTP/1.1 500 Internal Server Error\r\n\r\n'

    return 'HTTP/1.1 200 OK\r\n' + result.stdout

PORT = 55555
Handler = MyHttpRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()