import http.server
import socketserver
import os

os.chdir(r"C:\Users\George Guo\WorkBuddy\20260422151119")

PORT = 8765
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
