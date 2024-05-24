import socket
import os
import logging
from http import HTTPStatus

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define socket host and port
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000
DOCUMENT_ROOT = 'htdocs'

class HTTPServer:
    def __init__(self, host, port, document_root):
        self.host = host
        self.port = port
        self.document_root = document_root
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        logging.info(f'Listening on port {self.port} ...')

    def start(self):
        while True:
            try:
                client_connection, client_address = self.server_socket.accept()
                self.handle_request(client_connection)
            except Exception as e:
                logging.error(f"Error: {e}")

    def handle_request(self, client_connection):
        try:
            request = client_connection.recv(1024).decode()
            logging.info(f"Client request:\n{request}")

            headers = request.split('\n')
            if len(headers) == 0 or len(headers[0].split()) < 2:
                raise ValueError("Invalid HTTP request format")

            method, path, _ = headers[0].split()
            if method != 'GET':
                raise ValueError("Unsupported HTTP method")

            if path == '/':
                path = '/index.html'

            filepath = os.path.join(self.document_root, path.lstrip('/'))
            logging.info(f"Requested file path: {filepath}")

            if os.path.isdir(filepath):
                raise FileNotFoundError("Requested path is a directory")

            with open(filepath, 'r') as fin:
                content = fin.read()

            response = f'HTTP/1.0 {HTTPStatus.OK.value} {HTTPStatus.OK.phrase}\n\n{content}'

        except FileNotFoundError:
            response = f'HTTP/1.0 {HTTPStatus.NOT_FOUND.value} {HTTPStatus.NOT_FOUND.phrase}\n\nFile Not Found'
            logging.error("Error: File not found")
        except PermissionError:
            response = f'HTTP/1.0 {HTTPStatus.FORBIDDEN.value} {HTTPStatus.FORBIDDEN.phrase}\n\nPermission Denied'
            logging.error("Error: Permission denied")
        except ValueError as ve:
            response = f'HTTP/1.0 {HTTPStatus.BAD_REQUEST.value} {HTTPStatus.BAD_REQUEST.phrase}\n\nBad Request'
            logging.error(f"Error: Bad request {ve}")
        except Exception as e:
            response = f'HTTP/1.0 {HTTPStatus.INTERNAL_SERVER_ERROR.value} {HTTPStatus.INTERNAL_SERVER_ERROR.phrase}\n\nInternal Server Error'
            logging.error(f"Error: Internal server error {e}")

        client_connection.sendall(response.encode())
        client_connection.close()

    def stop(self):
        self.server_socket.close()

if __name__ == "__main__":
    server = HTTPServer(SERVER_HOST, SERVER_PORT, DOCUMENT_ROOT)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
        logging.info("Server stopped.")