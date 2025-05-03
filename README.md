# CirrusCtrl 🌩️

> **The All-in-One System Monitoring & Control Dashboard**

**CirrusCtrl** is a powerful, web-based tool designed for system administrators, developers, and DevOps engineers to monitor, manage, and troubleshoot systems in real-time — all from a centralized dashboard.

From checking system health and running processes to executing custom commands or scanning ports, CirrusCtrl gives you full control through a clean, responsive interface.

🔗 **Live Website**: [https://cirrusctrl.cyberfascinate.com](https://cirrusctrl.cyberfascinate.com)

---

## 🧰 Features

- **🖥️ System Summary**: CPU, memory, disk usage, uptime, network interfaces, OS details
- **🌐 Network Tools**: Ping, traceroute, port scan, route mapping, adapter info
- **🔒 Firewall Control**: Enable/disable Windows/Linux firewall remotely
- **⚙️ Command Execution**: Run arbitrary shell/PowerShell commands directly from the UI
- **🗑️ Process Management**: View running processes and kill them by PID
- **💾 Disk Usage**: Monitor disk partitions and space utilization
- **📈 Historical Metrics**: Store and visualize historical CPU, memory, and disk usage
- **🌍 Remote Access**: Query another CirrusCtrl instance for remote system data
- **📄 Log Viewer**: View and download application logs in real time

---

## 📦 Requirements

Before running CirrusCtrl, ensure you have the following dependencies installed:

### Python Packages
```bash
pip install flask flask-sqlalchemy flask-socketio psutil requests
```

### Optional System Tools (Linux)
- `nmap` – For port scanning (`sudo apt install nmap`)
- `ufw` – For Linux firewall management

Windows users only need PowerShell for command execution.

---

## 🛠️ Setup Instructions

1. **Clone the repo:**
   ```bash
   git clone https://github.com/cyberfascinate/CirrusCtrl.git
   cd CirrusCtrl
   ```

2. **Install dependencies:**
   ```bash
   pip install flask flask-sqlalchemy flask-socketio psutil requests
   ```

3. **Run the server:**
   ```bash
   python app.py
   ```

4. **Access the dashboard:**
   Open your browser and go to:
   ```
   http://localhost:5000
   ```

---

## 🖥️ Interface Overview

- **Sidebar Navigation**: Categorized tools like Network, Firewall, Logs, Commands
- **Output Area**: Displays results of executed actions (e.g., ping output, process list)
- **Charts**: Real-time graphs showing CPU, memory, and uptime trends
- **Responsive Design**: Works on desktops, tablets, and mobile devices

---

## 📂 File Structure

```
CirrusCtrl/
│
├── app.py                  # Main backend logic
├── README.md               # Project overview
├── logs/
│   └── app.log             # Action logs
├── static/
│   ├── script.js           # Frontend JavaScript
│   └── style.css           # Styling
├── templates/
│   └── index.html          # Web interface
└── system.db               # SQLite database for metrics
```

---

## 💬 Feedback & Contributions

We welcome contributions! If you'd like to help improve CirrusCtrl, feel free to submit pull requests or open issues.

To get started:
1. Fork the repo
2. Create a new feature branch (`git checkout -b feature/new-tool`)
3. Commit your changes (`git commit -m 'Add new tool'`)
4. Push to your fork (`git push origin feature/new-tool`)
5. Submit a Pull Request

Have questions or suggestions?  
📧 Reach out at: **contact@cyberfascinate.com**

---

## 🏷️ License

MIT License – see [LICENSE](LICENSE) for details.

---

## ✅ Let's Build Together!

Whether you're a developer looking to contribute, a sysadmin wanting better visibility into your systems, or just curious about how it works — **welcome to CirrusCtrl**.

Let’s make system operations smarter, faster, and more intuitive together.

---

## 🚀 Download Stable Release

🔗 [Download CirrusCtrl v1.0](https://github.com/cyberfascinate/CirrusCtrl/releases/tag/1.0)
