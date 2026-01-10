# LAN-Sentry: Passive Android Telemetry

LAN-Sentry is a lightweight, network-based monitoring tool that tracks an Android device's status via IP fingerprinting.  
No client-side software, root, or USB debugging is required on the phone.

This project shows the full path from raw Nmap experiments to a working monitoring dashboard that others can reproduce.

---

## 1. What this project does

- Treats an Android phone as a black box on the LAN.
- Identifies it by IP and UDP fingerprint (UPnP on UDP/1900).
- Continuously monitors:
  - Whether the phone is reachable (ping).
  - Whether UPnP on UDP/1900 is exposed.
- Logs every heartbeat to a file.
- Serves a simple Flask web dashboard that visualises the telemetry.

Use this only on networks and devices you own or are explicitly authorised to test.

---

## 2. Environment and tools

- Kali / Debian-based Linux
- Android phone on the same Wi‑Fi
- Tools:
  - `nmap`
  - `arp-scan` (optional, for MAC/vendor)
  - `python3`
  - `python3-flask`

Install:

```bash
sudo apt update
sudo apt install python3 python3-flask nmap arp-scan
3. Network reconnaissance steps (what was done)
These are the exact steps used to profile the phone before building the scripts.

Find phone IP

On Android: Wi‑Fi details → IP address (example 192.168.29.173).

Verify live host

bash
nmap -sn 192.168.29.0/24
Confirm that 192.168.29.173 appears as “Host is up”.

Try TCP OS detection (mostly blocked)

bash
sudo nmap -O -sV -A 192.168.29.173
On Android this commonly shows all 1000 TCP ports filtered and unreliable OS guesses.

Use UDP to fingerprint

bash
sudo nmap -sU --top-ports 20 -sV 192.168.29.173
Typical results for the phone:

1900/udp open|filtered upnp

4500/udp open|filtered nat-t-ike

This pattern is a strong indicator of an Android/consumer device.

Confirm UPnP with NSE

List scripts:

bash
ls /usr/share/nmap/scripts/ | grep -i "upnp"
Run targeted script:

bash
sudo nmap -sU -p 1900 --script upnp-info 192.168.29.173
Confirms that UDP/1900 is used for UPnP on that IP.

These reconnaissance steps are the foundation that phone.py automates.

4. Project structure
Inside the lan-sentry directory:

./phone.sh
Telemetry engine:

Pings the phone periodically.

Runs a quick nmap -sU -p1900 against the phone.

Optionally runs arp-scan over the local net and logs MAC/vendor.

Appends timestamped status lines to /tmp/phone.log and rotates the file.

dashboard.py
Flask web interface:

Reads /tmp/phone.log (last 15 entries).

Performs a fresh ping/UPnP check on each page load.

Shows ONLINE/OFFLINE state, UPnP status, and recent logs.

Auto-refreshes every few seconds.

README.md
This documentation.

.gitignore
Ignores logs, tmp files, and Python cache.

5. Configuration
Edit phone.py and dashboard.py and set the same IP:

python
IP = "YOUR_PHONE_LAN_IP"
Example:

python
IP = "192.168.29.173"
Ensure the log path is consistent (both use):

text
/tmp/phone.log
6. How to run
Start the telemetry engine (Terminal 1):

bash
./phone./sh
You should see lines such as:

text
2026-01-08 11:39:08 | Ping: UP | UPnP: open|filtered | MAC: aa:bb:cc:dd:ee:ff Vendor
Start the dashboard (Terminal 2):

bash
sudo python3 dashboard.py
Flask will report:

text
Running on http://127.0.0.1:8081
Running on http://YOUR_KALI_IP:8081
Open the dashboard in a browser:

text
http://localhost:8081
You should see:

Android Phone: <your IP>

ONLINE / OFFLINE status

UPnP 1900: Active or Filtered/Unknown

“Last 15 Logs” with your phone.py output

7. What someone else can learn from this repo
How to use Nmap (TCP and UDP) to fingerprint an Android device on a home LAN.

How to turn manual recon commands into an automated telemetry loop.

How to expose that telemetry over a very small Flask dashboard using only logs and simple shell tools.

This is intended as a compact, realistic “weekend project” for people learning:

Network scanning and host discovery on Kali.

Basic Bash/Python automation.

Building a small security-focused dashboard.

8. Future ideas
The project can be extended in several directions:

Discovery loop that automatically scans the subnet and identifies Android-like devices to monitor.

Support for monitoring multiple devices and rendering a table in the dashboard.

Alerts if the phone is offline for more than N minutes or changes IP.

Integration with Suricata or other IDS to inspect traffic related to the monitored IP.

9. Ethics
Only use LAN-Sentry on networks and devices you own or administer.

Scanning public or guest Wi‑Fi can violate terms of service and may be logged by IDS/IPS.

Always respect laws and organisational policies when performing any network scanning.


