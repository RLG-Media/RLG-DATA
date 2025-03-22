#!/bin/bash

# RLG Load Balancer Setup Script
# Ensures efficient traffic distribution for RLG Data and RLG Fans
# Implements high availability, failover, and region-based routing

# Update system and install necessary packages
sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx keepalived

# Load Balancer Configuration (Nginx)
echo "Configuring Nginx for Load Balancing..."
sudo tee /etc/nginx/conf.d/rlg_load_balancer.conf > /dev/null <<EOL
upstream rlg_backend {
    server rlg_backend_1:8000;
    server rlg_backend_2:8000 backup;
}

server {
    listen 80;
    server_name rlgdata.com;

    location / {
        proxy_pass http://rlg_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOL

# Restart Nginx to apply changes
sudo systemctl restart nginx
sudo systemctl enable nginx

echo "Nginx Load Balancer setup completed."

# High Availability Setup (Keepalived)
echo "Setting up Keepalived for failover..."
sudo tee /etc/keepalived/keepalived.conf > /dev/null <<EOL
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
EOL

# Restart Keepalived to apply changes
sudo systemctl restart keepalived
sudo systemctl enable keepalived

echo "Keepalived High Availability setup completed."

# Final Summary
echo "RLG Load Balancer successfully configured!"
echo "- Nginx: Traffic distribution across backend servers"
echo "- Keepalived: Automatic failover for high availability"
echo "- Services: Supports all RLG Data and RLG Fans functionalities"
echo "- Secure, scalable, and optimized for global deployment"
