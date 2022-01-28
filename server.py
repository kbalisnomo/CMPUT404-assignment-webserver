#  coding: utf-8 
import socketserver
import os
import mimetypes

CWD = os.getcwd() + "/"

# Copyright 2022 Abram Hindle, Eddie Antonio Santos, Kyle Philip Balisnomo
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    allowed_methods = ["GET"]
    
    # In order to check if a directory is a sub directory of another one
    # https://stackoverflow.com/questions/3812849/how-to-check-whether-a-directory-is-a-sub-directory-of-another-directory
    def in_server_directory(self, file, directory):
        # Make both absolute
        directory = os.path.join(os.path.realpath(directory), '')
        file = os.path.realpath(file)
        return os.path.commonprefix([file, directory]) == directory or file == directory[:-1]

    def read_file_contents(self, file_path):
        with open(file_path) as f:
            return f.read()

    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.parse_request(self.data)

    def return_200(self, host, path, protocol):
        # Paths which end in / should serve index.html
        if path[-1] == "/":
            path = path + "index.html"
        
        status = protocol + " 200 OK"
        host, port = self.request.getsockname()
        location_header = "Location: http://{}:{}{}".format(host, port, path) + "/"
        server_path = CWD + "www" + path
        content_type_header = "Content-Type: " + mimetypes.guess_type(server_path)[0]
        body = self.read_file_contents(server_path) + "\r\n"

        response = "\r\n".join([status, location_header, content_type_header, "", body]).encode()
        self.request.sendall(response)

    def return_301(self, host, path, protocol):
        status = protocol + " 301 Moved Permanently"
        host, port = self.request.getsockname()
        location_header = "Location: http://{}:{}{}".format(host, port, path) + "/"
        response = ("\r\n".join([status, location_header]) + "\r\n").encode()
        self.request.sendall(response)

    def return_404(self, host, path, protocol):
        response = (protocol + " 404 Not Found\r\n").encode()
        self.request.sendall(response)

    def return_405(self, host, path, protocol):
        response = (protocol + " 405 Method Not Allowed\r\n").encode()
        self.request.sendall(response)

    def parse_request(self, request):
        request_list = request.decode().split("\r\n") # Split request into parts
        request_type_path_protocol = request_list[0].split()
        request_type = request_type_path_protocol[0]
        request_path = request_type_path_protocol[1]
        request_protocol = request_type_path_protocol[2]
        request_host = request_list[1].split()[1]
        
        server_directory = CWD + "www"
        server_path = server_directory + request_path

        if request_type not in self.allowed_methods:
            self.return_405(request_host, request_path, request_protocol)
        elif not os.path.exists(server_path):
            self.return_404(request_host, request_path, request_protocol)
        elif not self.in_server_directory(server_path, server_directory):
            self.return_404(request_host, request_path, request_protocol)
        elif os.path.isdir(server_path):
            if request_path[-1] != "/":
                self.return_301(request_host, request_path, request_protocol)
            else:
                self.return_200(request_host, request_path, request_protocol)
        else:
            self.return_200(request_host, request_path, request_protocol)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
