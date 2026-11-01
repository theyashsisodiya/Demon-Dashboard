#!/usr/bin/env python3
"""
Demon-Devil Local Server & Key Management Dashboard
Compatible with Demon-devil Android APK and libdarkxazan.so
"""

import http.server
import socketserver
import urllib.parse
import json
import sqlite3
import datetime
import os
import secrets
import string
import socket

PORT = int(os.environ.get("PORT", 8080))
DB_FILE = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys.db"))
DARK_ZIP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dark.zip")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_string TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            duration_days INTEGER NOT NULL,
            device_serial TEXT,
            max_devices INTEGER DEFAULT 1,
            is_active INTEGER DEFAULT 1,
            notes TEXT DEFAULT '',
            last_used_at TEXT DEFAULT '',
            last_ip TEXT DEFAULT ''
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            client_ip TEXT NOT NULL,
            key_string TEXT NOT NULL,
            device_serial TEXT DEFAULT '',
            status TEXT NOT NULL,
            details TEXT DEFAULT ''
        )
    ''')
    
    # Check if a sample key exists, if not create one
    c.execute('SELECT COUNT(*) FROM keys')
    if c.fetchone()[0] == 0:
        now = datetime.datetime.now()
        exp = now + datetime.timedelta(days=365)
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        exp_str = exp.strftime("%Y-%m-%d %H:%M:%S")
        c.execute('''
            INSERT INTO keys (key_string, created_at, expires_at, duration_days, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', ("DEMON-VIP-2026", now_str, exp_str, 365, "Default VIP key (1 Year)"))
        conn.commit()
    conn.close()

def generate_key_string(prefix="DEMON"):
    part1 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    part2 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    return f"{prefix}-{part1}-{part2}"

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Format custom console logs
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {args[0]} - {args[1]}")

    def send_json_response(self, data, status_code=200):
        body = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path == "/dark.zip" and os.path.exists(DARK_ZIP_PATH):
            file_size = os.path.getsize(DARK_ZIP_PATH)
            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Length', str(file_size))
            self.end_headers()
        elif path == "/version.txt":
            content = b"1.12"
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
        else:
            self.send_response(200)
            self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            html_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html")
            if os.path.exists(html_file):
                with open(html_file, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "Dashboard HTML not found")
            return

        elif path == "/version.txt":
            # Version endpoint for Downtwo.Version()
            content = b"1.12"
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        elif path == "/dark.zip":
            # Payload download for Downtwo.Link()
            if os.path.exists(DARK_ZIP_PATH):
                file_size = os.path.getsize(DARK_ZIP_PATH)
                self.send_response(200)
                self.send_header('Content-Type', 'application/zip')
                self.send_header('Content-Length', str(file_size))
                self.end_headers()
                with open(DARK_ZIP_PATH, 'rb') as f:
                    while chunk := f.read(65536):
                        self.wfile.write(chunk)
            else:
                self.send_error(404, "dark.zip not found on server")
            return

        elif path == "/server/config.json":
            self.send_json_response({"status": "ok", "version": "1.12", "server": "Demon-Devil Local Server"})
            return

        elif path == "/api/keys":
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM keys ORDER BY id DESC')
            rows = [dict(r) for r in c.fetchall()]
            conn.close()
            self.send_json_response({"status": "success", "keys": rows})
            return

        elif path == "/api/logs":
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM access_logs ORDER BY id DESC LIMIT 50')
            rows = [dict(r) for r in c.fetchall()]
            conn.close()
            self.send_json_response({"status": "success", "logs": rows})
            return

        elif path == "/api/system-info":
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM keys')
            total = c.fetchone()[0]
            c.execute('SELECT COUNT(*) FROM keys WHERE is_active = 1')
            active = c.fetchone()[0]
            c.execute('SELECT COUNT(*) FROM keys WHERE device_serial IS NOT NULL AND device_serial != ""')
            devices = c.fetchone()[0]
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute('SELECT COUNT(*) FROM keys WHERE expires_at < ?', (now_str,))
            expired = c.fetchone()[0]
            conn.close()

            info = {
                "local_ip": LOCAL_IP,
                "port": PORT,
                "server_time": now_str,
                "total_keys": total,
                "active_keys": active,
                "expired_keys": expired,
                "bound_devices": devices,
                "auth_endpoint": f"http://{LOCAL_IP}:{PORT}/jangam/connect"
            }
            self.send_json_response({"status": "success", "info": info})
            return

        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else ""

        # Check if incoming request is from the Android App
        # Endpoints: /jangam/connect, /connect, /api/connect
        if path in ["/jangam/connect", "/connect", "/api/connect"]:
            self.handle_auth_request(raw_body)
            return

        # Dashboard Admin APIs
        try:
            data = json.loads(raw_body) if raw_body else {}
        except Exception:
            data = urllib.parse.parse_qs(raw_body)
            data = {k: v[0] for k, v in data.items()}

        if path == "/api/keys/generate":
            key_name = data.get("key", "").strip()
            prefix = data.get("prefix", "DEMON").strip().upper()
            duration_days = int(data.get("days", 30))
            notes = data.get("notes", "").strip()

            if not key_name:
                key_name = generate_key_string(prefix)

            now = datetime.datetime.now()
            if duration_days > 0:
                exp = now + datetime.timedelta(days=duration_days)
            else:
                # Custom date or 10 years for lifetime
                custom_date = data.get("custom_exp", "")
                if custom_date:
                    exp = datetime.datetime.strptime(custom_date, "%Y-%m-%d %H:%M:%S")
                else:
                    exp = now + datetime.timedelta(days=3650) # 10 years

            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            exp_str = exp.strftime("%Y-%m-%d %H:%M:%S")

            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            try:
                c.execute('''
                    INSERT INTO keys (key_string, created_at, expires_at, duration_days, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (key_name, now_str, exp_str, duration_days, notes))
                conn.commit()
                conn.close()
                self.send_json_response({"status": "success", "message": "Key created", "key": key_name, "expires_at": exp_str})
            except sqlite3.IntegrityError:
                conn.close()
                self.send_json_response({"status": "error", "message": "Key already exists"}, 400)
            return

        elif path == "/api/keys/delete":
            key_id = data.get("id")
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('DELETE FROM keys WHERE id = ?', (key_id,))
            conn.commit()
            conn.close()
            self.send_json_response({"status": "success", "message": "Key deleted"})
            return

        elif path == "/api/keys/reset-device":
            key_id = data.get("id")
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('UPDATE keys SET device_serial = NULL WHERE id = ?', (key_id,))
            conn.commit()
            conn.close()
            self.send_json_response({"status": "success", "message": "Device binding cleared"})
            return

        elif path == "/api/keys/toggle-status":
            key_id = data.get("id")
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('UPDATE keys SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?', (key_id,))
            conn.commit()
            conn.close()
            self.send_json_response({"status": "success", "message": "Status updated"})
            return

        else:
            self.send_error(404, "API Not Found")

    def handle_auth_request(self, raw_body):
        """
        Handles Android App Authentication Request:
        Body format from LogAct.java:
        game=PUBG&user_key=<KEY>&serial=<DEVICE_UUID>
        """
        client_ip = self.client_address[0]
        params = {}
        try:
            # First try parsing as urlencoded
            parsed_params = urllib.parse.parse_qs(raw_body)
            for k, v in parsed_params.items():
                params[k] = v[0]
        except Exception:
            pass

        # If empty, try JSON
        if not params and raw_body:
            try:
                params = json.loads(raw_body)
            except Exception:
                pass

        user_key = params.get("user_key", "").strip()
        serial = params.get("serial", "").strip()
        game = params.get("game", "PUBG")
        now_dt = datetime.datetime.now()
        now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n[AUTH ATTEMPT] Key: '{user_key}' | Serial: '{serial}' | Client: {client_ip} | Time: {now_str}")

        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        def log_access(status, details):
            c.execute('''
                INSERT INTO access_logs (timestamp, client_ip, key_string, device_serial, status, details)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (now_str, client_ip, user_key, serial, status, details))
            conn.commit()

        if not user_key:
            log_access("DENIED", "Empty Key")
            conn.close()
            self.send_json_response({"status": "false", "error": "Please enter a key"})
            return

        c.execute('SELECT * FROM keys WHERE key_string = ?', (user_key,))
        row = c.fetchone()

        if not row:
            log_access("DENIED", "Key does not exist")
            conn.close()
            print(f"[AUTH RESULT] FAILED: Key not found in database")
            self.send_json_response({"status": "false", "error": "Key Invalid"})
            return

        key_data = dict(row)

        if key_data["is_active"] != 1:
            log_access("DENIED", "Key is disabled / revoked")
            conn.close()
            print(f"[AUTH RESULT] FAILED: Key is deactivated")
            self.send_json_response({"status": "false", "error": "Key has been disabled by admin"})
            return

        # Check expiration
        expires_at_str = key_data["expires_at"]
        try:
            exp_dt = datetime.datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
            if now_dt > exp_dt:
                log_access("DENIED", f"Key expired on {expires_at_str}")
                conn.close()
                print(f"[AUTH RESULT] FAILED: Key expired ({expires_at_str})")
                self.send_json_response({"status": "false", "error": f"Key Expired on {expires_at_str}"})
                return
        except Exception as e:
            print(f"[WARN] Date parse exception: {e}")

        # Check HWID / Device Serial binding
        bound_serial = key_data.get("device_serial")
        if bound_serial and bound_serial.strip():
            if bound_serial.strip() != serial:
                log_access("DENIED", f"Device serial mismatch (Bound: {bound_serial})")
                conn.close()
                print(f"[AUTH RESULT] FAILED: Device mismatch (Bound: {bound_serial}, Sent: {serial})")
                self.send_json_response({"status": "false", "error": "Key is registered to another device"})
                return
        else:
            # Bind to this device on first login
            if serial:
                c.execute('UPDATE keys SET device_serial = ? WHERE id = ?', (serial, key_data["id"]))
                print(f"[AUTH] Bound key to device UUID: {serial}")

        # Update last login info
        c.execute('''
            UPDATE keys SET last_used_at = ?, last_ip = ? WHERE id = ?
        ''', (now_str, client_ip, key_data["id"]))
        log_access("SUCCESS", f"Authorized until {expires_at_str}")
        conn.commit()
        conn.close()

        print(f"[AUTH RESULT] SUCCESS! Authorized for device {serial} until {expires_at_str}")

        # Send response exactly formatted as expected by LogAct.java and libdarkxazan.so:
        # {
        #   "status": "success",
        #   "data": {
        #     "EXP": "YYYY-MM-DD HH:MM:SS"
        #   }
        # }
        response_payload = {
            "status": "success",
            "data": {
                "EXP": expires_at_str,
                "exp": expires_at_str,
                "Exp": expires_at_str
            },
            "message": "Login Successful"
        }
        self.send_json_response(response_payload)

def run():
    init_db()
    server_address = ('0.0.0.0', PORT)
    httpd = socketserver.ThreadingTCPServer(server_address, RequestHandler)
    print("=" * 65)
    print(f" DEMON-DEVIL LOCAL DASHBOARD & AUTH SERVER RUNNING")
    print("=" * 65)
    print(f" Web Dashboard URL : http://localhost:{PORT}")
    print(f" Network Access URL : http://{LOCAL_IP}:{PORT}")
    print(f" Auth API Endpoint  : http://{LOCAL_IP}:{PORT}/jangam/connect")
    print(f" Payload Endpoint   : http://{LOCAL_IP}:{PORT}/dark.zip")
    print(f" Version Endpoint   : http://{LOCAL_IP}:{PORT}/version.txt")
    print("=" * 65)
    print(" Press Ctrl+C to stop the server\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()

if __name__ == '__main__':
    run()
