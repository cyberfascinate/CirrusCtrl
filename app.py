import os
import subprocess
import platform
import socket
import time
import datetime
import psutil
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///system.db'
db = SQLAlchemy(app)
socketio = SocketIO(app)

# Logging Setup
if not os.path.exists('logs'):
    os.makedirs('logs')
import logging
logging.basicConfig(filename='logs/app.log', level=logging.INFO)

# ========== Routes ==========

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/action', methods=['POST'])
def handle_action():
    global last_output
    action = request.form.get('action', '').strip()
    try:
        logging.info(f"Received action: {action}")
        out = ""
        if action == 'map_routes':
            out = subprocess.check_output(['netstat', '-rn'] if platform.system().lower() == 'linux' else ['route', 'print'], timeout=3).decode()
        elif action == 'adapter_info':
            out = get_network_info()
        elif action == 'enable_fw_win':
            subprocess.run(['netsh', 'advfirewall', 'set', 'allprofiles', 'state', 'on'], check=True)
            out = 'Windows Firewall enabled'
        elif action == 'disable_fw_win':
            subprocess.run(['netsh', 'advfirewall', 'set', 'allprofiles', 'state', 'off'], check=True)
            out = 'Windows Firewall disabled'
        elif action == 'enable_fw_linux':
            subprocess.run(['ufw', 'enable'], check=True)
            out = 'Linux Firewall enabled'
        elif action == 'disable_fw_linux':
            subprocess.run(['ufw', 'disable'], check=True)
            out = 'Linux Firewall disabled'
        elif action == 'system_summary':
            out = get_system_summary()
        elif action == 'view_logs':
            with open('logs/app.log', 'r') as file:
                out = file.read()
        elif action == 'scan_alert':
            out = get_open_ports()
        elif action == 'process_monitoring':
            out = get_process_info()
        elif action == 'disk_usage':
            data = get_disk_usage()
            out = json.dumps(data, indent=2)
        elif action == 'custom_cmd':
            cmd = request.form.get('command')
            if platform.system().lower() == 'windows':
                result = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=10)
            else:
                result = subprocess.run(['bash', '-c', cmd], capture_output=True, text=True, timeout=10)
            out = result.stdout + result.stderr
        elif action == 'kill_process':
            pid = int(request.form.get('pid'))
            p = psutil.Process(pid)
            p.terminate()
            out = f"Process {pid} terminated."
        elif action == 'ping_host':
            host = request.form.get('host')
            cmd = ['ping', '-c', '4', host] if platform.system().lower() != 'windows' else ['ping', host]
            out = subprocess.check_output(cmd).decode()
        elif action == 'traceroute':
            host = request.form.get('host')
            cmd = ['traceroute', host] if platform.system().lower() != 'windows' else ['tracert', host]
            out = subprocess.check_output(cmd).decode()
        elif action == 'port_scan':
            host = request.form.get('host')
            cmd = ['nmap', '-p-', '--min-rate=1000', host]
            out = subprocess.check_output(cmd).decode()
        elif action == 'history':
            data = Metric.query.order_by(Metric.timestamp.desc()).limit(100).all()
            out = json.dumps([{ 'timestamp': m.timestamp.isoformat(), 'cpu': m.cpu, 'memory': m.memory, 'disk': m.disk } for m in data], indent=2)
        elif action == 'remote_check':
            host = request.form.get('host')
            import requests
            response = requests.post(f'http://{host}:5000/action', data={'action': 'system_summary'}, timeout=5)
            out = response.text
        else:
            out = 'Invalid or unsupported action.'
        logging.info(f"Action '{action}' completed successfully.")
    except Exception as e:
        logging.error(f"Error during action '{action}': {e}")
        out = f"Error: {e}"
    last_output = out
    return jsonify({'output': out})


@app.route('/download_log')
def download_log():
    from flask import send_file
    return send_file('logs/app.log', as_attachment=True)


@app.route('/remote', methods=['POST'])
def remote_check():
    host = request.form.get('host')
    try:
        import requests
        response = requests.post(f'http://{host}:5000/action', data={'action': 'system_summary'}, timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)})

# ========== Helper Functions ==========

def get_system_summary():
    uname = platform.uname()
    cpu_info = f"CPU Usage: {psutil.cpu_percent(interval=1)}%\n"
    cpu_info += f"CPU Cores: {psutil.cpu_count(logical=False)} Physical Cores, {psutil.cpu_count(logical=True)} Logical Cores\n"
    cpu_info += f"CPU Frequency: {psutil.cpu_freq().current} MHz\n"
    # CPU temperature
    try:
        temps = psutil.sensors_temperatures()
        if 'coretemp' in temps:
            cpu_info += f"CPU Temperature: {temps['coretemp'][0].current}°C\n"
    except Exception as e:
        cpu_info += f"Error getting CPU temperature: {e}\n"

    memory_info = f"Memory Usage: {psutil.virtual_memory().percent}%\n"
    memory_info += f"Total RAM: {psutil.virtual_memory().total / 1024 ** 3:.2f} GB\n"
    memory_info += f"Used RAM: {psutil.virtual_memory().used / 1024 ** 3:.2f} GB\n"
    memory_info += f"Available RAM: {psutil.virtual_memory().available / 1024 ** 3:.2f} GB\n"
    memory_info += f"Swap Memory: {psutil.swap_memory().percent}% Used\n"

    disk_info = f"Disk Usage: {psutil.disk_usage('/').percent}%\n"
    disk_info += f"Total Disk: {psutil.disk_usage('/').total / 1024 ** 3:.2f} GB\n"
    disk_info += f"Used Disk: {psutil.disk_usage('/').used / 1024 ** 3:.2f} GB\n"
    disk_info += f"Free Disk: {psutil.disk_usage('/').free / 1024 ** 3:.2f} GB\n"
    disk_info += "\nDisk Partitions:\n"
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info += f"  {partition.device} ({partition.fstype}): {usage.percent}% Used\n"
        except PermissionError:
            continue

    network_info = "Network Interfaces:\n"
    for interface, addrs in psutil.net_if_addrs().items():
        network_info += f"  Interface: {interface}\n"
        for addr in addrs:
            if addr.family == socket.AF_INET:
                network_info += f"    IP Address: {addr.address}\n"
            elif addr.family == socket.AF_LINK:
                network_info += f"    MAC Address: {addr.address}\n"

    uptime = get_uptime()

    os_info = f"Operating System: {uname.system} {uname.release} {uname.version}\n"
    os_info += f"Machine: {uname.machine}\n"
    os_info += f"Architecture: {platform.architecture()[0]}\n"
    os_info += f"Uptime: {uptime}\n"

    return f"""
System Information:
-------------------------
{os_info}
{cpu_info}
{memory_info}
{disk_info}
{network_info}
"""


def get_uptime():
    uptime_seconds = time.time() - psutil.boot_time()
    return str(datetime.timedelta(seconds=uptime_seconds))


def get_network_info():
    out = ""
    for interface, addrs in psutil.net_if_addrs().items():
        out += f"Interface: {interface}\n"
        for addr in addrs:
            if addr.family == socket.AF_INET:
                out += f"  IP Address: {addr.address}\n"
            elif addr.family == socket.AF_LINK:
                out += f"  MAC Address: {addr.address}\n"
    return out


def get_open_ports():
    try:
        if platform.system().lower() == 'linux':
            open_ports = subprocess.check_output(['ss', '-tuln'], timeout=3).decode()
        else:
            open_ports = subprocess.check_output(['netstat', '-ano'], timeout=3).decode()
        return parse_ports(open_ports)
    except Exception as e:
        logging.error(f"Error retrieving open ports: {e}")
        return f"Error: {e}"


def parse_ports(output):
    lines = output.splitlines()
    ports = []
    for line in lines:
        if "LISTEN" in line or "ESTABLISHED" in line:
            parts = line.split()
            if platform.system().lower() == 'linux':
                ports.append(parts[4])  # For Linux ss output
            else:
                ports.append(parts[1])  # For Windows netstat output
    return "\n".join(ports) if ports else "No open ports found."


def get_process_info():
    processes = psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info'])
    return "\n".join([f"PID: {p.info['pid']} Name: {p.info['name']} CPU: {p.info['cpu_percent']}% Memory: {p.info['memory_info'].rss / 1024 ** 2}MB" for p in processes])


def get_disk_usage():
    partitions = []
    for p in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(p.mountpoint)
            partitions.append({
                "path": p.device,
                "mountPoint": p.mountpoint,
                "total": round(usage.total / (1024 ** 3), 1),
                "used": round(usage.used / (1024 ** 3), 1),
                "available": round(usage.free / (1024 ** 3), 1),
                "usedPercent": round(usage.percent, 1)
            })
        except PermissionError:
            continue
    return partitions


class Metric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    cpu = db.Column(db.Float)
    memory = db.Column(db.Float)
    disk = db.Column(db.Float)


def save_metrics(cpu, memory, disk):
    metric = Metric(cpu=cpu, memory=memory, disk=disk)
    db.session.add(metric)
    db.session.commit()


last_output = ""


# ========== Run App ==========

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    if not os.path.exists('logs'):
        os.makedirs('logs')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)