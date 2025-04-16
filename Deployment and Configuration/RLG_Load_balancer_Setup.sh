#!/bin/bash
# RLG_Load_balancer_Setup.sh
# ----------------------------
# RLG Load Balancer Setup Script
# Author: RLG Team
#
# Description:
#   This script sets up a load balancer for RLG Data & RLG Fans using Nginx and
#   Keepalived. It distributes traffic across backend servers and configures
#   automatic failover. This setup supports the full suite of integrated services,
#   including scraping, compliance monitoring, AI analysis, reporting, monetization,
#   newsletter distribution, the RLG Agent Chat Bot, and the RLG Super Tool.
#
#   Note:
#     Regional pricing rules (including Special Region pricing for Israel and SADC tiers)
#     are applied within the backend services. Ensure those modules are integrated.
#
# Usage:
#   To set up the load balancer, run this script with root privileges.
# ----------------------------

set -e  # Exit on any error
set -o pipefail

LOG_FILE="/var/log/rlg_load_balancer_setup.log"

log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "$LOG_FILE"
}

# Update system and install necessary packages: nginx and keepalived
log "[INFO] Updating system and installing Nginx and Keepalived..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx keepalived || { log "[ERROR] Package installation failed!"; exit 1; }

# Configure Nginx Load Balancer
log "[INFO] Configuring Nginx for load balancing..."
sudo tee /etc/nginx/conf.d/rlg_load_balancer.conf > /dev/null <<'EOF'
upstream rlg_backend {
    server rlg_backend_1:8000;
    server rlg_backend_2:8000 backup;
}

server {
    listen 80;
    server_name rlgdata.com;

    location / {
        proxy_pass http://rlg_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

log "[INFO] Testing Nginx configuration..."
sudo nginx -t || { log "[ERROR] Nginx configuration test failed!"; exit 1; }

log "[INFO] Restarting Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

log "[INFO] Nginx load balancer setup completed."

# Configure Keepalived for High Availability
log "[INFO] Setting up Keepalived for automatic failover..."
sudo tee /etc/keepalived/keepalived.conf > /dev/null <<'EOF'
vrrp_instance RLG_VIP {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass RLGsecure123
    }
    virtual_ipaddress {
        192.168.1.100/24
    }
}
EOF

log "[INFO] Restarting Keepalived..."
sudo systemctl restart keepalived
sudo systemctl enable keepalived

log "[INFO] Keepalived high availability setup completed."

# Final Summary
log "[INFO] RLG Load Balancer successfully configured!"
log "[INFO] - Nginx: Traffic distribution across backend servers configured."
log "[INFO] - Keepalived: Automatic failover enabled with VIP 192.168.1.100/24."
log "[INFO] - Integration: Load balancer supports all backend services including scraping, compliance, AI analysis, reporting, monetization, RLG Newsletter, RLG Agent Chat Bot, and the RLG Super Tool."
log "[INFO] - Pricing tiers (including Special Region pricing for Israel and SADC tiers) will be enforced by the backend logic after user registration and location lock."

exit 0
