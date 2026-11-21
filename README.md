# Python Honeypot

A simple, educational honeypot with three fake services -- SSH, FTP, and an
HTTP login page -- that look real enough to attract scanners and bots, but
implement zero real functionality. Every connection attempt, command, and
login attempt is logged in structured JSON so you can analyze attacker
behavior afterward.

## How it works

```
Attacker connects --> fake service sends a realistic banner/page
                  --> whatever the attacker sends (commands, credentials) is captured
                  --> logger.py records it as a JSON line (timestamp, service, IP, details)
                  --> service replies with a generic failure and disconnects
```

No real authentication, file access, or command execution ever happens --
these services exist purely to look interesting and record activity.

## Setup

Requires Python 3.9+

## Configuring

Edit `config.json`:

```json
{
  "services": {
    "ssh":  {"enabled": true, "port": 2222, "banner": "SSH-2.0-OpenSSH_7.4"},
    "ftp":  {"enabled": true, "port": 2121, "banner": "220 (vsFTPd 3.0.3)"},
    "http": {"enabled": true, "port": 8080, "fake_page_title": "Employee Portal Login"}
  },
  "log_file": "honeypot.log",
  "bind_host": "0.0.0.0"
}
```

- Toggle any service off with `"enabled": false`.
- Ports default to non-privileged numbers (2222, 2121, 8080) so you don't need root to run it. You *can* set them to the real well-known ports (22, 21, 80) to look more convincing to scanners, but that requires root/admin and means the real service can't also run on that port.
- Set `bind_host` to `127.0.0.1` while testing locally so nothing outside your machine can reach it.

## Running it

```bash
python main.py
```

Stop anytime with `Ctrl+C`.

## Testing it

# HTTP honeypot(Windows)
curl http://127.0.0.1:8080/admin

Invoke-WebRequest -Uri "http://127.0.0.1:8080/login" -Method POST -Body "username=admin&password=hunter2"
```

Watch `honeypot.log` fill up with structured events like:

```json
{"timestamp": "2026-07-18T09:56:58Z", "service": "ftp", "src_ip": "127.0.0.1", "src_port": 53644, "event_type": "login_attempt", "details": {"username": "admin", "password": "hunter2"}}
```
