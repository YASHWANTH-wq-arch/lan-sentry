import os
import subprocess
from flask import Flask, render_template_string
from datetime import datetime

app = Flask(__name__)

IP = "YOUR_PHONE_LAN_IP"  # Replace with your phone's IP
LOG = "/tmp/phone.log"

def get_recent_logs(n=15):
    """Read last n lines from the log file."""
    if not os.path.exists(LOG):
        return []
    try:
        with open(LOG, 'r') as f:
            lines = f.readlines()
            return [line.strip() for line in lines[-n:]]
    except:
        return []

def check_phone_status():
    """Quick ping + UPnP check."""
    ping_status = "DOWN"
    upnp_status = "unknown"
    
    # Ping check
    try:
        result = subprocess.run(['ping', '-c', '1', '-W', '2', IP], 
                              capture_output=True, timeout=3)
        ping_status = "UP" if result.returncode == 0 else "DOWN"
    except:
        ping_status = "DOWN"
    
    # UPnP check
    try:
        result = subprocess.run(['sudo', 'timeout', '3', 'nmap', '-sU', '-p1900', IP],
                              capture_output=True, text=True, timeout=5)
        if '1900/udp' in result.stdout:
            upnp_status = result.stdout.split('1900/udp')[1].split()[0]
    except:
        upnp_status = "unknown"
    
    return ping_status, upnp_status

@app.route('/')
def dashboard():
    ping, upnp = check_phone_status()
    logs = get_recent_logs(15)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LAN-Sentry Dashboard</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body { font-family: Arial, sans-serif; background: #1e1e1e; color: #00ff00; padding: 20px; }
            .container { max-width: 900px; margin: 0 auto; }
            h1 { color: #00ff00; }
            .status { padding: 15px; background: #2d2d2d; border-left: 4px solid #00ff00; margin: 10px 0; }
            .up { border-left-color: #00ff00; }
            .down { border-left-color: #ff0000; }
            .logs { background: #0a0a0a; padding: 15px; border-radius: 5px; max-height: 400px; overflow-y: auto; }
            .log-entry { padding: 5px; border-bottom: 1px solid #333; font-family: monospace; font-size: 12px; }
            table { width: 100%; }
            td { padding: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>LAN-Sentry Dashboard</h1>
            <p>Monitoring: <strong>""" + IP + """</strong></p>
            
            <div class="status """ + ("up" if ping == "UP" else "down") + """">
                <table>
                    <tr><td><strong>Ping Status:</strong></td><td>""" + ping + """</td></tr>
                    <tr><td><strong>UPnP (1900/udp):</strong></td><td>""" + upnp + """</td></tr>
                    <tr><td><strong>Last Check:</strong></td><td>""" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</td></tr>
                </table>
            </div>
            
            <h2>Recent Logs (Last 15)</h2>
            <div class="logs">
    """
    
    if logs:
        for log in logs:
            html += f'<div class="log-entry">{log}</div>'
    else:
        html += '<div class="log-entry" style="color: #ff9900;">[No logs yet. Start phone.sh first]</div>'
    
    html += """
            </div>
            <p style="margin-top: 20px; font-size: 12px; color: #888;">
                Auto-refreshing every 5 seconds. Ensure phone.sh is running.
            </p>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=False)
