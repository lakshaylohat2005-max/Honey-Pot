import socket
import threading


def _handle_client(conn: socket.socket, addr, banner: str, logger):
    remote_ip, remote_port = addr
    logger.log_event("ssh", remote_ip, remote_port, "connection_opened")

    try:
        conn.sendall((banner + "\r\n").encode())

        conn.settimeout(5)
        data = conn.recv(1024)
        if data:
            # Try to decode for logging; fall back to hex if it's binary garbage
            try:
                decoded = data.decode("utf-8", errors="replace").strip()
            except Exception:
                decoded = data.hex()
            logger.log_event("ssh", remote_ip, remote_port, "data_received", {"raw": decoded})
    except socket.timeout:
        logger.log_event("ssh", remote_ip, remote_port, "timeout_no_data")
    except Exception as e:
        logger.log_event("ssh", remote_ip, remote_port, "error", {"error": str(e)})
    finally:
        conn.close()
        logger.log_event("ssh", remote_ip, remote_port, "connection_closed")


def start_ssh_honeypot(host: str, port: int, banner: str, logger):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(20)

    print(f"[ssh]  fake SSH honeypot listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=_handle_client, args=(conn, addr, banner, logger), daemon=True)
        t.start()
