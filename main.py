import argparse
import json
import sys
import threading
import time

from logger import EventLogger
from services.ssh_honeypot import start_ssh_honeypot
from services.ftp_honeypot import start_ftp_honeypot
from services.http_honeypot import start_http_honeypot


def parse_args():
    parser = argparse.ArgumentParser(description="A simple multi-service Python honeypot.")
    parser.add_argument("--config", default="config.json", help="Path to honeypot config JSON.")
    return parser.parse_args()


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def main():
    args = parse_args()

    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Config file not found: {args.config}")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to load config: {e}")
        sys.exit(1)

    logger = EventLogger(config.get("log_file", "honeypot.log"))
    host = config.get("bind_host", "0.0.0.0")
    services_cfg = config.get("services", {})

    threads = []

    ssh_cfg = services_cfg.get("ssh", {})
    if ssh_cfg.get("enabled"):
        t = threading.Thread(
            target=start_ssh_honeypot,
            args=(host, ssh_cfg["port"], ssh_cfg.get("banner", "SSH-2.0-OpenSSH_7.4"), logger),
            daemon=True,
        )
        threads.append(t)

    ftp_cfg = services_cfg.get("ftp", {})
    if ftp_cfg.get("enabled"):
        t = threading.Thread(
            target=start_ftp_honeypot,
            args=(host, ftp_cfg["port"], ftp_cfg.get("banner", "220 (vsFTPd 3.0.3)"), logger),
            daemon=True,
        )
        threads.append(t)

    http_cfg = services_cfg.get("http", {})
    if http_cfg.get("enabled"):
        t = threading.Thread(
            target=start_http_honeypot,
            args=(host, http_cfg["port"], http_cfg.get("fake_page_title", "Employee Portal Login"), logger),
            daemon=True,
        )
        threads.append(t)

    if not threads:
        print("No services enabled in config. Nothing to do.")
        sys.exit(0)

    for t in threads:
        t.start()

    print(f"\nHoneypot running with {len(threads)} fake service(s). Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down honeypot.")
        sys.exit(0)


if __name__ == "__main__":
    main()
