import socket
import threading


def _handle_client(conn: socket.socket, addr, banner: str, logger):
    remote_ip, remote_port = addr
    logger.log_event("ftp", remote_ip, remote_port, "connection_opened")

    username = None

    try:
        conn.sendall((banner + "\r\n").encode())
        conn.settimeout(15)

        while True:
            data = conn.recv(1024)
            if not data:
                break

            line = data.decode("utf-8", errors="replace").strip()
            if not line:
                continue

            parts = line.split(" ", 1)
            command = parts[0].upper()
            arg = parts[1] if len(parts) > 1 else ""

            if command == "USER":
                username = arg
                logger.log_event("ftp", remote_ip, remote_port, "username_attempt", {"username": username})
                conn.sendall(b"331 Please specify the password.\r\n")

            elif command == "PASS":
                logger.log_event(
                    "ftp", remote_ip, remote_port, "login_attempt",
                    {"username": username, "password": arg},
                )
                conn.sendall(b"530 Login incorrect.\r\n")

            elif command == "QUIT":
                conn.sendall(b"221 Goodbye.\r\n")
                break

            else:
                logger.log_event("ftp", remote_ip, remote_port, "command_received", {"command": line})
                conn.sendall(b"502 Command not implemented.\r\n")

    except socket.timeout:
        logger.log_event("ftp", remote_ip, remote_port, "timeout_no_data")
    except Exception as e:
        logger.log_event("ftp", remote_ip, remote_port, "error", {"error": str(e)})
    finally:
        conn.close()
        logger.log_event("ftp", remote_ip, remote_port, "connection_closed")


def start_ftp_honeypot(host: str, port: int, banner: str, logger):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(20)

    print(f"[ftp]  fake FTP honeypot listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=_handle_client, args=(conn, addr, banner, logger), daemon=True)
        t.start()
