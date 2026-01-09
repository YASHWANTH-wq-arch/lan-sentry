IP="192.168.29.173"
LOG="/tmp/phone.log"
INTERVAL=10
USE_ARP_SCAN=true

if [ "$USE_ARP_SCAN" = true ]; then
    if ! command -v arp-scan >/dev/null 2>&1; then
        echo "[!] arp-scan not found. Install with: sudo apt install arp-scan"
        USE_ARP_SCAN=false
    fi
fi

echo "=== LAN-Sentry started for $IP at $(date) ===" | tee -a "$LOG"

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

    if ping -c1 -W2 "$IP" >/dev/null 2>&1; then
        PING="UP"
    else
        PING="DOWN"
    fi

    UPNP=$(sudo timeout 3 nmap -sU -p1900 "$IP" 2>/dev/null | awk '/1900\/udp/ {print $2}')
    UPNP=${UPNP:-unknown}

    if [ "$USE_ARP_SCAN" = true ]; then
        MAC_LINE=$(sudo arp-scan --localnet 2>/dev/null | grep " $IP$")
        MAC=$(echo "$MAC_LINE" | awk '{print $2}')
        VENDOR=$(echo "$MAC_LINE" | awk '{print $3}')
        [ -z "$MAC" ] && MAC="unknown" && VENDOR=""
    else
        MAC="unknown"
        VENDOR=""
    fi

    STATUS="$TIMESTAMP | Ping: $PING | UPnP: $UPNP | MAC: $MAC $VENDOR"
    echo "$STATUS"
    echo "$STATUS" >> "$LOG"

    if [ -f "$LOG" ] && [ "$(wc -l < "$LOG")" -gt 2000 ]; then
        tail -1000 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
    fi

    sleep "$INTERVAL"
done
