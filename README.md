# Demon-Dashboard

A lightweight, zero-dependency Python management dashboard, SQLite key authentication server, and asset distribution backend designed for the BGMI virtual space / loader.

---

## 🌟 Features

- **Zero External Dependencies:** Built entirely with Python's standard library (`http.server`, `sqlite3`, `socketserver`, `json`, `secrets`). No `pip install` required!
- **Device Hardware Binding (HWID):** Automatically binds a key to the device's hardware UUID on first login to prevent key sharing.
- **Key Lifecycle Management:**
  - Generate custom or random keys with custom prefixes (`DEMON-XXXX-XXXX`).
  - Set custom validity durations (1 day, 7 days, 30 days, 1 year, or lifetime).
  - Toggle key status (activate / deactivate).
  - Reset device binding with a single click.
- **Payload & Config Endpoints:**
  - Serves zip payloads (`/ZENIN.zip` and `/CreatOp/Technical-public/ZENIN.zip`).
  - Serves version checks (`/version.txt` returning `1.8`).
  - Serves remote server configurations (`/server/config.json`).
- **Real-Time Access Logs:** Tracks client IP, timestamp, key, device serial, and authentication status.
- **Web UI:** Responsive administrative interface with real-time stats and control panel.

---

## 📁 Repository Structure

```text
├── server.py             # Main HTTP server, API routes, and SQLite database handler
├── keys.db               # SQLite database storing keys, expirations, and access logs
├── ZENIN.zip             # Primary payload archive distributed to authorized clients
├── dark.zip              # Legacy payload archive fallback
├── Dockerfile            # Lightweight Alpine Docker container
├── docker-compose.yml    # One-click Docker Compose deployment
├── run_docker.bat        # Windows 1-click Docker runner
├── run_docker.sh         # Linux / VPS 1-click Docker runner
├── start_server.bat      # Windows batch script to launch the server locally
├── start_tunnel.bat      # Quick launcher for Cloudflare Tunnel
└── static/
    └── index.html        # Web dashboard UI
```

---

## 🚀 Running Locally

### Option 1: Quick Launch (Windows)
Double-click `start_server.bat` in the repository folder.

### Option 2: Manual Terminal Run (Windows / macOS / Linux)
```bash
python server.py
```

The server will automatically start on port `8080`:
- **Web Dashboard:** [http://localhost:8080](http://localhost:8080)
- **Local Network URL:** `http://<YOUR_LAN_IP>:8080`
- **Auth Endpoint:** `http://<YOUR_LAN_IP>:8080/jangam/connect`

> **Default Admin Key:** When `keys.db` is initialized, a default key `DEMON-VIP-2026` is created with a 1-year validity.

---

## 🌐 Public Tunneling (Expose to Mobile Devices)

To connect mobile devices outside your local Wi-Fi without manual port forwarding:

### 1. Using Cloudflare Tunnel (Free & HTTPS)
If you have `cloudflared` installed:
```bash
cloudflared tunnel --url http://localhost:8080
```
Or run `start_tunnel.bat`. Cloudflare will generate a public URL like:
`https://random-subdomain.trycloudflare.com`

Use `https://random-subdomain.trycloudflare.com/jangam/connect` as your loader's auth endpoint.

### 2. Using ngrok
```bash
ngrok http 8080
```

---

## ☁️ Deployment Guide

### Method A: Deploy on Linux VPS (Ubuntu / Debian) — Recommended for 24/7 Uptime

1. **Clone the repository:**
   ```bash
   git clone https://github.com/theyashsisodiya/Demon-Dashboard.git
   cd Demon-Dashboard
   ```

2. **Run as a Background Systemd Service:**
   Create a service file:
   ```bash
   sudo nano /etc/systemd/system/demon-dashboard.service
   ```

   Paste the configuration:
   ```ini
   [Unit]
   Description=Demon-Dashboard Auth Server
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/root/Demon-Dashboard
   ExecStart=/usr/bin/python3 /root/Demon-Dashboard/server.py
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

3. **Start and Enable Service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable demon-dashboard
   sudo systemctl start demon-dashboard
   ```

4. **Verify status:**
   ```bash
   sudo systemctl status demon-dashboard
   ```

---

### Method B: Deploy using Docker (One-Click)

1. **One-Click Launch:**
   - **Windows:** Double-click `run_docker.bat`
   - **Linux / macOS:** Run `chmod +x run_docker.sh && ./run_docker.sh`
   - **Manual CLI:**
     ```bash
     docker compose up -d --build
     ```

2. **Management & Logs:**
   ```bash
   # View real-time access logs
   docker logs -f demon-dashboard

   # Stop container
   docker compose down

   # Restart container
   docker compose restart
   ```
   *The `keys.db` database and `dark.zip` are mapped via volumes, preserving your keys and device bindings across updates and container restarts.*

---

### Method C: Deploy on Free Cloud PaaS (Render / Railway / Koyeb)

1. **Render.com:**
   - Link your GitHub repository.
   - Select **Web Service**.
   - Build Command: *(leave empty or `python --version`)*.
   - Start Command: `python server.py`.
   - Add an environment variable or attach a persistent disk for `keys.db` so database changes persist across restarts.

2. **Note on Vercel:**
   - Vercel is a serverless platform with a read-only filesystem where functions shut down between requests. SQLite files (`keys.db`) cannot be written to or persisted on Vercel. For serverless deployment on Vercel, connect the backend logic to a cloud database such as **Turso** (hosted libSQL/SQLite) or **Supabase** (PostgreSQL). For simple setup, use **Render**, **Railway**, or a standard **VPS**.

---

## 📡 API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Administrative Web Dashboard UI |
| `/api/system-info` | `GET` | Server metrics, active keys count, device count |
| `/api/keys` | `GET` | List all keys and device associations |
| `/api/logs` | `GET` | Recent authentication attempts and HWID verification logs |
| `/api/keys/generate` | `POST` | Generate new key with custom duration |
| `/api/keys/delete` | `POST` | Permanently remove a key |
| `/api/keys/reset-device` | `POST` | Clear HWID device lock on a key |
| `/api/keys/toggle-status`| `POST` | Enable / Disable access key |
| `/jangam/connect` | `POST` | Client authentication endpoint used by the Android loader |
| `/version.txt` or `/CreatOp/Technical-public/version.txt` | `GET` | Version check endpoint (returns `1.8`) |
| `/ZENIN.zip` or `/CreatOp/Technical-public/ZENIN.zip` | `GET` | Primary payload download endpoint |
| `/dark.zip` | `GET` | Legacy payload fallback endpoint |
| `/server/config.json` | `GET` | Remote server feature switch configuration |
