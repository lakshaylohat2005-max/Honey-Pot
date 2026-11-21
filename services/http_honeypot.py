from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs


def make_handler(page_title: str, logger):
    class HoneypotHTTPHandler(BaseHTTPRequestHandler):
        server_version = "Apache/2.4.41"  # fake Server header, looks like a real Apache box
        sys_version = ""

        def log_message(self, format, *args):
            pass  # silence default stderr logging; we log our own structured events

        def _client_ip_port(self):
            return self.client_address[0], self.client_address[1]

        def _login_page_html(self, error: str = ""):
            error_html = f'<p style="color:red;">{error}</p>' if error else ""
            return f"""<!DOCTYPE html>
<html>
<head><title>{page_title}</title></head>
<body style="font-family:sans-serif;max-width:400px;margin:80px auto;">
  <h2>{page_title}</h2>
  {error_html}
  <form method="POST" action="/login">
    <label>Username:</label><br>
    <input type="text" name="username"><br><br>
    <label>Password:</label><br>
    <input type="password" name="password"><br><br>
    <input type="submit" value="Log In">
  </form>
</body>
</html>"""

        def do_GET(self):
            ip, port = self._client_ip_port()
            logger.log_event("http", ip, port, "get_request", {"path": self.path})

            body = self._login_page_html().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            ip, port = self._client_ip_port()
            length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(length).decode("utf-8", errors="replace")
            fields = parse_qs(raw_body)

            username = fields.get("username", [""])[0]
            password = fields.get("password", [""])[0]

            logger.log_event(
                "http", ip, port, "login_attempt",
                {"path": self.path, "username": username, "password": password},
            )

            body = self._login_page_html(error="Invalid username or password.").encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return HoneypotHTTPHandler


def start_http_honeypot(host: str, port: int, page_title: str, logger):
    handler_class = make_handler(page_title, logger)
    server = ThreadingHTTPServer((host, port), handler_class)
    print(f"[http] fake HTTP login honeypot listening on {host}:{port}")
    server.serve_forever()
