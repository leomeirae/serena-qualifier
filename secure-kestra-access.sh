#!/bin/bash

# SECURE KESTRA ACCESS SCRIPT
# This script provides temporary secure access to Kestra for authorized users

echo "🔐 SECURE KESTRA ACCESS UTILITY"
echo "================================"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root" 
   exit 1
fi

# Function to get current IP
get_current_ip() {
    curl -s https://ipinfo.io/ip || curl -s https://icanhazip.com || echo "Unable to detect IP"
}

# Function to open temporary access
open_access() {
    local user_ip=$(get_current_ip)
    echo "🌐 Detected IP: $user_ip"
    
    if [[ "$user_ip" == "Unable to detect IP" ]]; then
        echo "❌ Could not detect your IP address"
        exit 1
    fi
    
    echo "🔓 Opening temporary access for IP: $user_ip"
    
    # Add temporary UFW rule
    ufw allow from $user_ip to any port 8080 comment "Temporary Kestra access"
    
    # Add temporary Hetzner Cloud firewall rule (requires hcloud CLI)
    # hcloud firewall add-rule kestra-security-firewall --direction in --source-ips $user_ip/32 --protocol tcp --port 8080
    
    echo "✅ Access granted for 1 hour. URL: https://kestra.darwinai.com.br"
    echo "🔑 Username: admin"
    echo "🔑 Password: SerenaSecure2025!"
    echo ""
    echo "⚠️  Access will be automatically revoked in 1 hour"
    echo "⚠️  Or run: $0 close"
    
    # Schedule automatic closure in 1 hour
    (sleep 3600; $0 close) &
}

# Function to close access
close_access() {
    echo "🔒 Closing Kestra access..."
    
    # Remove UFW rule
    ufw --force delete allow from any to any port 8080 comment "Temporary Kestra access" 2>/dev/null
    ufw status numbered | grep "8080" | cut -d']' -f1 | cut -d'[' -f2 | sort -nr | while read line; do
        ufw --force delete $line 2>/dev/null
    done
    
    echo "✅ Access closed successfully"
}

# Function to check current access status
check_status() {
    echo "📊 Current Kestra Access Status:"
    echo "================================"
    
    # Check UFW rules
    echo "🔧 UFW Rules:"
    ufw status numbered | grep "8080" || echo "   No UFW rules for port 8080"
    
    # Check Kestra container status
    echo ""
    echo "📦 Kestra Container:"
    docker ps --format 'table {{.Names}}\t{{.Status}}' | grep kestra || echo "   Kestra not running"
    
    # Check authentication
    echo ""
    echo "🔐 Authentication Status:"
    if docker exec $(docker ps --format '{{.Names}}' | grep kestra) grep -q "security:" /app/confs/application.yml 2>/dev/null; then
        echo "   ✅ Authentication ENABLED"
    else
        echo "   ❌ Authentication DISABLED"
    fi
}

# Main logic
case "$1" in
    "open")
        open_access
        ;;
    "close")
        close_access
        ;;
    "status")
        check_status
        ;;
    *)
        echo "Usage: $0 {open|close|status}"
        echo ""
        echo "Commands:"
        echo "  open   - Open temporary secure access (1 hour)"
        echo "  close  - Close all access immediately"
        echo "  status - Check current access status"
        echo ""
        echo "🔐 Kestra Credentials:"
        echo "   Username: admin"
        echo "   Password: SerenaSecure2025!"
        exit 1
        ;;
esac 