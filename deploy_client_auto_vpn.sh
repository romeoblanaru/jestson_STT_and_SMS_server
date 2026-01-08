#!/bin/bash
# Automated WireGuard Client Deployment with VPN Tunnel Configuration
# Primary method: Configure through existing VPN tunnel (for cloned systems)
# Fallback method: SSH with temporary key

set -e

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run this script with sudo:"
    echo "sudo $0"
    exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "Automated Multi-Client Deployment"
echo "VPN Tunnel Method with SSH Fallback"
echo "========================================="

# Configuration file for persistent settings
CONFIG_FILE="/home/rom/.deploy_config"
TEMP_KEY_PATH="/dev/shm/temp_ssh_key_$$"  # Use RAM disk for extra security
TEMP_SSH_DIR="/dev/shm/temp_ssh_$$"
VPN_WEBHOOK_URL="http://10.100.0.1:8090/api/wireguard/add_peer"
USE_VPN_METHOD=false
USE_SSH_METHOD=false

# Cleanup function - ALWAYS runs on exit
cleanup() {
    if [ "$USE_SSH_METHOD" = "true" ]; then
        echo ""
        echo -e "${YELLOW}Cleaning up temporary SSH key...${NC}"
        
        # Securely delete the temporary key
        if [ -f "$TEMP_KEY_PATH" ]; then
            shred -vfz -n 3 "$TEMP_KEY_PATH" 2>/dev/null || rm -f "$TEMP_KEY_PATH"
            echo -e "${GREEN}✅ Temporary SSH key securely deleted${NC}"
        fi
        
        # Remove temporary SSH directory
        if [ -d "$TEMP_SSH_DIR" ]; then
            rm -rf "$TEMP_SSH_DIR"
            echo -e "${GREEN}✅ Temporary SSH directory removed${NC}"
        fi
        
        # Clear SSH agent if we added keys
        ssh-add -D 2>/dev/null || true
    fi
}

# Set trap to ensure cleanup runs even if script fails
trap cleanup EXIT INT TERM

# Function to check if we have an active VPN connection
check_vpn_connection() {
    echo ""
    echo -e "${BLUE}📡 Checking VPN connectivity...${NC}"
    
    # Check if wg0 interface exists
    if ! ip link show wg0 &>/dev/null; then
        echo -e "${YELLOW}⚠️  No WireGuard interface found${NC}"
        return 1
    fi
    
    # Get current VPN IP
    CURRENT_VPN_IP=$(ip addr show wg0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
    if [ -z "$CURRENT_VPN_IP" ]; then
        echo -e "${YELLOW}⚠️  WireGuard interface has no IP${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Current VPN IP: $CURRENT_VPN_IP${NC}"
    
    # Test connectivity to VPS through VPN
    if ping -c 1 -W 2 10.100.0.1 &>/dev/null; then
        echo -e "${GREEN}✅ Can reach VPS through VPN tunnel${NC}"
        
        # Test if webhook is accessible
        if curl -s -m 5 -o /dev/null -w "%{http_code}" "$VPN_WEBHOOK_URL" 2>/dev/null | grep -q "^[234]"; then
            echo -e "${GREEN}✅ VPN webhook is accessible${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  VPN webhook not accessible at $VPN_WEBHOOK_URL${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  Cannot reach VPS through VPN${NC}"
        return 1
    fi
}

# Function to configure via VPN tunnel
configure_via_vpn() {
    local new_ip="$1"
    local new_public_key="$2"
    local phone="$3"
    local name="$4"
    local current_ip="$5"
    
    echo ""
    echo -e "${BLUE}📡 Configuring new peer via VPN tunnel...${NC}"
    echo "Using existing connection from $current_ip"
    
    # Prepare JSON payload (matching actual webhook format)
    JSON_PAYLOAD=$(cat <<EOF
{
    "new_ip": "$new_ip",
    "public_key": "$new_public_key",
    "phone": "$phone",
    "name": "$name",
    "auth_token": "394c2b67cf7b87efa8fdb01ac75118bfac1c95b99893f40723ed4b452183bf10"
}
EOF
)
    
    echo "Sending configuration to VPS webhook..."
    
    # Send request to VPS webhook
    RESPONSE=$(curl -s -X POST "$VPN_WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "$JSON_PAYLOAD" 2>/dev/null)
    
    # Check response
    if echo "$RESPONSE" | grep -q '"status":"success"'; then
        echo -e "${GREEN}✅ VPS configuration successful via VPN tunnel${NC}"
        return 0
    else
        echo -e "${RED}❌ VPS configuration failed${NC}"
        echo "Response: $RESPONSE"
        return 1
    fi
}

# Function to securely input SSH key
get_ssh_key() {
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}SSH KEY AUTHENTICATION SETUP (FALLBACK METHOD)${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "The VPN tunnel method failed or is not available."
    echo "Falling back to SSH configuration method."
    echo ""
    echo -e "${GREEN}What will happen:${NC}"
    echo "1. You paste your SSH private key"
    echo "2. Script uses it to configure VPS"
    echo "3. Key is AUTOMATICALLY DELETED when done"
    echo ""
    echo -e "${RED}Security notes:${NC}"
    echo "• Key is stored in RAM (/dev/shm) not on disk"
    echo "• Key is shredded with 3-pass overwrite when deleted"
    echo "• Key is deleted even if script fails (trap handler)"
    echo "• No permanent trace left on this Pi"
    echo ""
    echo -e "${YELLOW}Please paste your SSH private key below.${NC}"
    echo "It should start with '-----BEGIN ... PRIVATE KEY-----'"
    echo "and end with '-----END ... PRIVATE KEY-----'"
    echo ""
    echo "Paste the key, then press Enter and Ctrl-D when done:"
    echo -e "${YELLOW}────────────────────────────────────────────────────${NC}"
    
    # Read the key securely
    cat > "$TEMP_KEY_PATH"
    
    # Set secure permissions immediately
    chmod 600 "$TEMP_KEY_PATH"
    
    echo -e "${YELLOW}────────────────────────────────────────────────────${NC}"
    
    # Validate the key format
    if ! grep -q "BEGIN.*PRIVATE KEY" "$TEMP_KEY_PATH"; then
        echo -e "${RED}❌ Invalid key format! No 'BEGIN PRIVATE KEY' found${NC}"
        exit 1
    fi
    
    if ! grep -q "END.*PRIVATE KEY" "$TEMP_KEY_PATH"; then
        echo -e "${RED}❌ Invalid key format! No 'END PRIVATE KEY' found${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ SSH key received and secured${NC}"
    echo ""
    
    # Create temporary SSH config
    mkdir -p "$TEMP_SSH_DIR"
    chmod 700 "$TEMP_SSH_DIR"
    cp "$TEMP_KEY_PATH" "$TEMP_SSH_DIR/id_rsa"
    
    USE_SSH_METHOD=true
}

# Function to execute SSH commands with temporary key
ssh_with_temp_key() {
    local host="$1"
    shift
    ssh -i "$TEMP_SSH_DIR/id_rsa" \
        -o StrictHostKeyChecking=accept-new \
        -o UserKnownHostsFile=/dev/null \
        -o PasswordAuthentication=no \
        -o LogLevel=ERROR \
        "$host" "$@"
}

# Function to load or set webhook domain
get_webhook_domain() {
    local saved_domain=""
    
    # Check if we have a saved domain
    if [ -f "$CONFIG_FILE" ]; then
        saved_domain=$(grep "^WEBHOOK_DOMAIN=" "$CONFIG_FILE" 2>/dev/null | cut -d'=' -f2)
    fi
    
    # Default domain
    local default_domain="my-bookings.co.uk"
    
    echo ""
    echo "📝 Webhook Server Configuration"
    echo "================================"
    
    if [ ! -z "$saved_domain" ]; then
        echo "Previously used domain: $saved_domain"
        echo ""
        read -p "Use this domain? (y/n/change): " choice
        case "$choice" in
            y|Y) 
                WEBHOOK_DOMAIN="$saved_domain"
                ;;
            n|N)
                WEBHOOK_DOMAIN="$default_domain"
                ;;
            *)
                read -p "Enter new domain: " WEBHOOK_DOMAIN
                ;;
        esac
    else
        echo "Default domain: $default_domain"
        read -p "Press Enter to use default or type new domain: " user_input
        if [ -z "$user_input" ]; then
            WEBHOOK_DOMAIN="$default_domain"
        else
            WEBHOOK_DOMAIN="$user_input"
        fi
    fi
    
    # Test the domain
    echo ""
    echo "Testing connection to $WEBHOOK_DOMAIN..."
    TEST_URL="https://$WEBHOOK_DOMAIN/webhooks/check_ip.php?list=all"
    
    TEST_RESULT=$(curl -s -L -m 10 "$TEST_URL" 2>/dev/null)
    TEST_STATUS=$(echo "$TEST_RESULT" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    
    if [ "$TEST_STATUS" != "success" ]; then
        echo -e "${RED}❌ Cannot connect to $WEBHOOK_DOMAIN or invalid response${NC}"
        echo "Response: $TEST_RESULT"
        echo ""
        echo "Please check:"
        echo "1. Domain is correct"
        echo "2. Server is online"
        echo "3. Webhooks are configured"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Successfully connected to $WEBHOOK_DOMAIN${NC}"
    
    # Save the working domain
    echo "WEBHOOK_DOMAIN=$WEBHOOK_DOMAIN" > "$CONFIG_FILE"
    
    # Display existing associations
    echo ""
    echo "📋 Existing Client Associations:"
    echo "================================="
    
    # Parse and display the list - looking for "results" array, not "data"
    if echo "$TEST_RESULT" | grep -q '"results":\['; then
        # Extract results array and format it
        echo "$TEST_RESULT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'results' in data:
        clients = []
        for item in data['results']:
            ip = item.get('ip_address', '')
            phone = item.get('phone_number', '')
            name = item.get('client_name', item.get('notes', ''))
            if ip:
                last_octet = int(ip.split('.')[-1])
                clients.append((last_octet, ip, phone, name))
        clients.sort()
        for _, ip, phone, name in clients:
            print(f'  {ip:<15} | {phone:<20} | {name}')
    else:
        print('  No existing clients found')
except:
    print('  Error parsing client list')
" 2>/dev/null || {
        # Fallback to basic parsing if Python fails
        echo "$TEST_RESULT" | grep -o '"ip_address":"[^"]*"' | cut -d'"' -f4 | while read ip; do
            echo "  $ip"
        done
    }
    else
        echo "  No existing clients found"
    fi
    
    echo "================================="
    echo ""
}

# Main script starts here

# Check if this is a cloned system with active VPN
if check_vpn_connection; then
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}DETECTED: Active VPN Connection${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "This appears to be a cloned system with inherited VPN configuration."
    echo "Current VPN IP: $CURRENT_VPN_IP"
    echo ""
    echo -e "${GREEN}The script will use the VPN tunnel method:${NC}"
    echo "1. Generate new WireGuard keys locally"
    echo "2. Send configuration to VPS via VPN webhook"
    echo "3. Switch this Pi to new identity"
    echo ""
    echo -e "${YELLOW}IMPORTANT: Make sure the original Pi is DISCONNECTED${NC}"
    echo -e "${YELLOW}to avoid IP conflicts during configuration.${NC}"
    echo ""
    read -p "Use VPN tunnel method? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        USE_VPN_METHOD=true
    fi
fi

# Get webhook domain for database operations
get_webhook_domain

# Get client phone number
echo "Enter client phone number (this will be used as identifier)"
echo "Examples: +447700900123, +33612345678"
echo ""
read -p "Client phone number: " CLIENT_PHONE

# Store original for display
CLIENT_PHONE_ORIGINAL="$CLIENT_PHONE"

# Remove any spaces, dashes, parentheses from phone
CLIENT_PHONE=$(echo "$CLIENT_PHONE" | tr -d ' ()-')

# Create safe ID by removing + and prefixing with phone_
CLIENT_PHONE_SAFE=$(echo "$CLIENT_PHONE" | tr -d '+' | sed 's/^/phone_/')

if [ -z "$CLIENT_PHONE" ]; then
    echo -e "${RED}❌ Phone number is required!${NC}"
    exit 1
fi

# Manual IP selection only
echo ""
echo "📝 IP Address Selection"
echo "Available range: 10.100.0.10 to 10.100.0.250"
echo "Check the list above for already used IPs"
echo ""
echo -e "${YELLOW}Enter ONLY the last number (suffix) of the IP address${NC}"
echo "Examples: For 10.100.0.45, enter: 45"
echo "         For 10.100.0.123, enter: 123"
echo ""
read -p "Enter IP suffix number only (10-250): " IP_INPUT

# Handle if user enters full IP by mistake
if echo "$IP_INPUT" | grep -q "\."; then
    # Extract just the last octet if user entered full IP
    IP_SUFFIX=$(echo "$IP_INPUT" | awk -F. '{print $NF}')
    echo -e "${YELLOW}Note: Extracted suffix $IP_SUFFIX from $IP_INPUT${NC}"
else
    IP_SUFFIX="$IP_INPUT"
fi

# Remove any leading zeros
IP_SUFFIX=$((10#$IP_SUFFIX))

# Validate IP suffix
if [ "$IP_SUFFIX" -lt 10 ] || [ "$IP_SUFFIX" -gt 250 ]; then
    echo -e "${RED}❌ IP suffix must be between 10 and 250${NC}"
    echo "   Got: $IP_SUFFIX"
    exit 1
fi

CLIENT_IP="10.100.0.${IP_SUFFIX}"
CLIENT_ID="CLIENT_${CLIENT_PHONE_SAFE}"

# Validate IP and Phone uniqueness via webhooks
echo ""
echo "📝 Validating IP and phone number uniqueness..."

# Check if IP already exists
IP_CHECK_RESULT=$(curl -s -L "https://$WEBHOOK_DOMAIN/webhooks/check_ip.php?ip=${CLIENT_IP}")
IP_STATUS=$(echo "$IP_CHECK_RESULT" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
IP_FOUND=$(echo "$IP_CHECK_RESULT" | grep -o '"found":[^,}]*' | cut -d':' -f2)
IP_EXISTING_PHONE=$(echo "$IP_CHECK_RESULT" | grep -o '"result":"[^"]*"' | cut -d'"' -f4)

if [ "$IP_STATUS" = "success" ] && [ "$IP_FOUND" = "true" ]; then
    echo -e "${RED}❌ IP ${CLIENT_IP} already in use by phone: ${IP_EXISTING_PHONE}${NC}"
    echo ""
    echo "Please choose a different IP suffix."
    exit 1
fi
echo -e "${GREEN}✅ IP ${CLIENT_IP} is available${NC}"

# Check if phone number already exists
PHONE_CHECK_RESULT=$(curl -s -L "https://$WEBHOOK_DOMAIN/webhooks/check_ip.php?nr=${CLIENT_PHONE}")
PHONE_STATUS=$(echo "$PHONE_CHECK_RESULT" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
PHONE_FOUND=$(echo "$PHONE_CHECK_RESULT" | grep -o '"found":[^,}]*' | cut -d':' -f2)
PHONE_EXISTING_IP=$(echo "$PHONE_CHECK_RESULT" | grep -o '"result":"[^"]*"' | cut -d'"' -f4)

if [ "$PHONE_STATUS" = "success" ] && [ "$PHONE_FOUND" = "true" ]; then
    echo -e "${RED}❌ Phone ${CLIENT_PHONE_ORIGINAL} already registered with IP: ${PHONE_EXISTING_IP}${NC}"
    echo ""
    echo "This phone number is already configured. Cannot proceed."
    exit 1
fi
echo -e "${GREEN}✅ Phone ${CLIENT_PHONE_ORIGINAL} is available${NC}"

echo ""
read -p "Enter client name (e.g., 'Alpha Corp' or person name): " CLIENT_NAME
CLIENT_NAME=${CLIENT_NAME:-"Client_${CLIENT_PHONE}"}

# For SSH method, get VPS details
if [ "$USE_VPN_METHOD" != "true" ]; then
    echo ""
    echo "Enter VPS SSH connection details"
    echo "Format: user@ip or user@hostname"
    echo "Examples:"
    echo "  root@144.91.96.97"
    echo "  admin@vps.example.com"
    echo ""
    read -p "VPS SSH connection: " VPS_SSH
    
    # Validate SSH format
    if [[ ! "$VPS_SSH" =~ ^[^@]+@[^@]+$ ]]; then
        echo -e "${RED}❌ Invalid format! Use: user@ip or user@hostname${NC}"
        exit 1
    fi
    
    # Extract user and host
    VPS_SSH_USER=$(echo "$VPS_SSH" | cut -d'@' -f1)
    VPS_SSH_HOST=$(echo "$VPS_SSH" | cut -d'@' -f2)
else
    # For VPN method, we know the VPS details
    VPS_SSH="root@10.100.0.1"
    VPS_SSH_USER="root"
    VPS_SSH_HOST="10.100.0.1"
fi

echo ""
echo "Configuration Summary:"
echo "  Client Phone: $CLIENT_PHONE_ORIGINAL"
echo "  Client Name: $CLIENT_NAME"
echo "  Client IP: $CLIENT_IP"
echo "  Client ID: $CLIENT_ID"
if [ "$USE_VPN_METHOD" = "true" ]; then
    echo -e "  Method: ${GREEN}VPN Tunnel (Primary)${NC}"
    echo "  Current VPN IP: $CURRENT_VPN_IP"
else
    echo -e "  Method: ${YELLOW}SSH Key (Fallback)${NC}"
    echo "  VPS Connection: ${VPS_SSH_USER}@${VPS_SSH_HOST}"
fi
echo "  Webhook Domain: $WEBHOOK_DOMAIN"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Step 1: Generate new WireGuard keys
echo ""
echo "📝 Step 1: Generating WireGuard keys..."
# Work in /etc/wireguard directory with proper permissions
sudo rm -f /etc/wireguard/private_new.key /etc/wireguard/public_new.key
NEW_PRIVATE_KEY=$(sudo wg genkey | sudo tee /etc/wireguard/private_new.key)
NEW_PUBLIC_KEY=$(echo "$NEW_PRIVATE_KEY" | sudo wg pubkey | sudo tee /etc/wireguard/public_new.key)
NEW_PRIVATE_KEY=$(sudo cat /etc/wireguard/private_new.key)
NEW_PUBLIC_KEY=$(sudo cat /etc/wireguard/public_new.key)
echo -e "${GREEN}✅ Keys generated${NC}"
echo "   Public key: ${NEW_PUBLIC_KEY:0:20}..."

# Step 2: Get VPS public key
VPS_PUBLIC_KEY=""
if [ -f /etc/wireguard/vps_public.key ]; then
    VPS_PUBLIC_KEY=$(sudo cat /etc/wireguard/vps_public.key)
    echo -e "${GREEN}✅ Step 2: Using saved VPS public key${NC}"
elif [ "$USE_VPN_METHOD" = "true" ]; then
    # Extract from current config if using VPN method
    VPS_PUBLIC_KEY=$(sudo grep "^PublicKey = " /etc/wireguard/wg0.conf | cut -d' ' -f3)
    if [ ! -z "$VPS_PUBLIC_KEY" ]; then
        echo "$VPS_PUBLIC_KEY" | sudo tee /etc/wireguard/vps_public.key > /dev/null
        echo -e "${GREEN}✅ Step 2: Extracted VPS public key from current config${NC}"
    fi
fi

# If we still don't have VPS public key and not using VPN method, get via SSH
if [ -z "$VPS_PUBLIC_KEY" ] && [ "$USE_VPN_METHOD" != "true" ]; then
    echo ""
    echo "📝 Step 2: Getting VPS public key via SSH..."
    
    # Get SSH key for authentication
    get_ssh_key
    
    # Test SSH connection
    echo "Testing SSH connection to VPS..."
    if ssh_with_temp_key "$VPS_SSH" "echo 'SSH connection successful'" 2>/dev/null; then
        echo -e "${GREEN}✅ SSH connection successful${NC}"
    else
        echo -e "${RED}❌ Failed to connect to VPS with provided key${NC}"
        exit 1
    fi
    
    VPS_PUBLIC_KEY=$(ssh_with_temp_key "$VPS_SSH" \
        "sudo cat /etc/wireguard/public.key 2>/dev/null || sudo wg show wg0 public-key 2>/dev/null")
    
    if [ -z "$VPS_PUBLIC_KEY" ]; then
        echo -e "${RED}❌ Failed to get VPS public key${NC}"
        exit 1
    fi
    
    echo "$VPS_PUBLIC_KEY" | sudo tee /etc/wireguard/vps_public.key > /dev/null
    echo -e "${GREEN}✅ VPS public key saved${NC}"
fi

# Get VPS endpoint (IP:PORT) from current config if using VPN method
if [ "$USE_VPN_METHOD" = "true" ]; then
    VPS_ENDPOINT=$(sudo grep "^Endpoint = " /etc/wireguard/wg0.conf | cut -d' ' -f3)
    if [ -z "$VPS_ENDPOINT" ]; then
        VPS_ENDPOINT="${VPS_SSH_HOST}:51820"
    fi
else
    VPS_ENDPOINT="${VPS_SSH_HOST}:51820"
fi

# Step 3: Configure VPS (via VPN or SSH)
VPS_CONFIG_SUCCESS=false

if [ "$USE_VPN_METHOD" = "true" ]; then
    # Try VPN method first
    echo ""
    echo "📝 Step 3: Configuring VPS via VPN tunnel..."
    
    if configure_via_vpn "$CLIENT_IP" "$NEW_PUBLIC_KEY" "$CLIENT_PHONE_ORIGINAL" "$CLIENT_NAME" "$CURRENT_VPN_IP"; then
        VPS_CONFIG_SUCCESS=true
    else
        echo -e "${YELLOW}⚠️  VPN configuration failed, falling back to SSH method${NC}"
        USE_VPN_METHOD=false
    fi
fi

# If VPN method failed or wasn't used, try SSH
if [ "$VPS_CONFIG_SUCCESS" != "true" ]; then
    echo ""
    echo "📝 Step 3: Configuring VPS via SSH..."
    
    # Get SSH key if we don't have it yet
    if [ "$USE_SSH_METHOD" != "true" ]; then
        get_ssh_key
    fi
    
    # Create the peer config to add
    PEER_CONFIG="
[Peer]
# ${CLIENT_NAME} (Phone: ${CLIENT_PHONE_ORIGINAL})
PublicKey = ${NEW_PUBLIC_KEY}
AllowedIPs = ${CLIENT_IP}/32
PersistentKeepalive = 25"
    
    # SSH to VPS and add the peer
    ssh_with_temp_key "$VPS_SSH" << ENDSSH
echo "Adding peer for ${CLIENT_PHONE_ORIGINAL}..."

# Check if peer already exists
if grep -q "${CLIENT_IP}/32" /etc/wireguard/wg0.conf; then
    echo "Updating existing peer with IP ${CLIENT_IP}..."
    # Remove old peer config
    sudo sed -i "/AllowedIPs = ${CLIENT_IP}\/32/,/^$/d" /etc/wireguard/wg0.conf
fi

# Add new peer config
echo "${PEER_CONFIG}" | sudo tee -a /etc/wireguard/wg0.conf > /dev/null

# Add peer to running config
sudo wg set wg0 peer ${NEW_PUBLIC_KEY} allowed-ips ${CLIENT_IP}/32 persistent-keepalive 25

# Show status
sudo wg show wg0 | grep -A2 "${NEW_PUBLIC_KEY:0:20}"
echo "✅ Peer added successfully"
ENDSSH
    
    if [ $? -eq 0 ]; then
        VPS_CONFIG_SUCCESS=true
        echo -e "${GREEN}✅ VPS configured via SSH${NC}"
    else
        echo -e "${RED}❌ Failed to configure VPS${NC}"
        exit 1
    fi
fi

# Step 4: Update local WireGuard configuration
echo ""
echo "📝 Step 4: Updating local WireGuard configuration..."
sudo tee /etc/wireguard/wg0.conf > /dev/null << EOF
[Interface]
Address = ${CLIENT_IP}/32
PrivateKey = ${NEW_PRIVATE_KEY}
DNS = 8.8.8.8

[Peer]
PublicKey = ${VPS_PUBLIC_KEY}
Endpoint = ${VPS_ENDPOINT}
AllowedIPs = 10.100.0.0/24
PersistentKeepalive = 25
EOF

# Move new keys to permanent location
sudo mv /etc/wireguard/private_new.key /etc/wireguard/private.key
sudo mv /etc/wireguard/public_new.key /etc/wireguard/public.key
sudo chmod 600 /etc/wireguard/private.key

echo -e "${GREEN}✅ Local configuration updated${NC}"

# Step 5: Restart WireGuard with new identity
echo ""
echo "📝 Step 5: Switching to new VPN identity..."
echo -e "${YELLOW}Note: The current VPN connection will be terminated${NC}"
sudo systemctl stop wg-quick@wg0 2>/dev/null || true
sleep 2
sudo systemctl start wg-quick@wg0
sudo systemctl enable wg-quick@wg0

echo -e "${GREEN}✅ WireGuard restarted with new identity${NC}"

# Step 6: Test new connection
echo ""
echo "📝 Step 6: Testing new VPN connection..."
echo "Waiting for tunnel to establish..."
sleep 3

# Check if interface is up with new IP
NEW_CURRENT_IP=$(ip addr show wg0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
if [ "$NEW_CURRENT_IP" = "$CLIENT_IP" ]; then
    echo -e "${GREEN}✅ WireGuard interface has new IP: $CLIENT_IP${NC}"
else
    echo -e "${RED}❌ WireGuard interface IP mismatch${NC}"
    echo "Expected: $CLIENT_IP, Got: $NEW_CURRENT_IP"
fi

# Test ping to VPS
VPS_INTERNAL_IP="10.100.0.1"
if ping -c 3 -W 2 ${VPS_INTERNAL_IP} &>/dev/null; then
    echo -e "${GREEN}✅ Ping to VPS (${VPS_INTERNAL_IP}) successful${NC}"
else
    echo -e "${YELLOW}⚠️  Cannot ping VPS (${VPS_INTERNAL_IP})${NC}"
    echo "Note: Connection may still work if ICMP is blocked"
fi

# Check handshake
HANDSHAKE=$(sudo wg show wg0 latest-handshakes | grep "${VPS_PUBLIC_KEY:0:20}" | awk '{print $2}')
if [ ! -z "$HANDSHAKE" ] && [ "$HANDSHAKE" != "0" ]; then
    HANDSHAKE_AGO=$(( $(date +%s) - $HANDSHAKE ))
    echo -e "${GREEN}✅ Handshake established (${HANDSHAKE_AGO} seconds ago)${NC}"
else
    echo -e "${YELLOW}⚠️  No handshake yet (may be normal if no traffic sent)${NC}"
fi

# Step 7: Register in database
echo ""
echo "📝 Step 7: Registering client in database..."

# URL encode the parameters
ENCODED_PHONE=$(echo "$CLIENT_PHONE_ORIGINAL" | sed 's/+/%2B/g')
ENCODED_NAME=$(echo "$CLIENT_NAME" | sed 's/ /%20/g')

# Insert into database with the client's public key (notes only contains the name)
DB_INSERT_RESULT=$(curl -s -L -X POST \
  "https://$WEBHOOK_DOMAIN/webhooks/insert_vpn_ip.php" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d "ip_address=${CLIENT_IP}&phone_number=${ENCODED_PHONE}&vpn_public_key=${NEW_PUBLIC_KEY}&notes=${ENCODED_NAME}")

# Check if insertion was successful
DB_INSERT_STATUS=$(echo "$DB_INSERT_RESULT" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [ "$DB_INSERT_STATUS" != "success" ]; then
    echo -e "${YELLOW}⚠️  Warning: Could not register in database${NC}"
    echo "   Response: $DB_INSERT_RESULT"
else
    echo -e "${GREEN}✅ Client registered in database${NC}"
fi

# Step 8: Set environment variables
echo ""
echo "📝 Step 8: Setting environment variables..."
sudo grep -v "CLIENT_" /etc/environment > /tmp/environment.tmp || true
echo "CLIENT_ID=${CLIENT_ID}" >> /tmp/environment.tmp
echo "CLIENT_IP=${CLIENT_IP}" >> /tmp/environment.tmp
echo "CLIENT_PHONE=${CLIENT_PHONE_ORIGINAL}" >> /tmp/environment.tmp
echo "CLIENT_PHONE_SAFE=${CLIENT_PHONE_SAFE}" >> /tmp/environment.tmp
echo "CLIENT_NAME=\"${CLIENT_NAME}\"" >> /tmp/environment.tmp
sudo mv /tmp/environment.tmp /etc/environment
echo -e "${GREEN}✅ Environment configured${NC}"

# Step 8b: Create .env file for services
echo ""
echo "📝 Step 8b: Creating .env configuration file..."
cat > /home/rom/.env << EOF
# Pi Gateway Configuration
# Auto-generated on $(date)
# Client: ${CLIENT_NAME}

# WireGuard VPN Configuration
WG_VPN_IP=${CLIENT_IP}
WG_INTERFACE=wg0

# VPS Webhook Configuration
VPS_WEBHOOK_URL=http://10.100.0.1:8088/webhook/sms/receive
VPS_IP=10.100.0.1

# Client Information
CLIENT_NAME=${CLIENT_NAME}
CLIENT_PHONE=${CLIENT_PHONE_ORIGINAL}
CLIENT_ID=${CLIENT_ID}

# SMS Gateway Settings
SMS_MAX_RETRIES=3
SMS_RETRY_DELAY=5
EOF
chown rom:rom /home/rom/.env
chmod 644 /home/rom/.env
echo -e "${GREEN}✅ .env file created${NC}"

# Step 9: Save client mapping
echo ""
echo "📝 Step 9: Saving client mapping..."
sudo mkdir -p /etc/wireguard/clients
echo "${CLIENT_PHONE_ORIGINAL}:${CLIENT_IP}:${CLIENT_NAME}" | sudo tee "/etc/wireguard/clients/${CLIENT_PHONE_SAFE}.info" > /dev/null
echo -e "${GREEN}✅ Client mapping saved${NC}"

# Final status
echo ""
echo "========================================="
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo "========================================="
echo ""
echo "Client Configuration:"
echo "  Phone Number: ${CLIENT_PHONE_ORIGINAL}"
echo "  Name: ${CLIENT_NAME}"
echo "  IP: ${CLIENT_IP}"
echo "  ID: ${CLIENT_ID}"
echo ""
echo "Method Used:"
if [ "$VPS_CONFIG_SUCCESS" = "true" ]; then
    if [ "$USE_VPN_METHOD" = "true" ]; then
        echo -e "  ${GREEN}VPN Tunnel (Primary method)${NC}"
    else
        echo -e "  ${YELLOW}SSH Key (Fallback method)${NC}"
    fi
fi
echo ""
echo "WireGuard Status:"
sudo wg show wg0 | head -10
echo ""
echo "Connection Tests:"
echo -n "  Local IP: "
ip addr show wg0 | grep inet | awk '{print $2}'
echo -n "  VPN Status: "
ping -c 1 -W 1 10.100.0.1 &>/dev/null && echo -e "${GREEN}✅ Connected${NC}" || echo -e "${RED}❌ Not Connected${NC}"
echo ""

if [ "$USE_SSH_METHOD" = "true" ]; then
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}SECURITY NOTICE:${NC}"
    echo "The temporary SSH key has been automatically deleted."
    echo "No SSH keys remain on this Pi."
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
fi

# Create a summary file
CONFIG_METHOD="Unknown"
if [ "$VPS_CONFIG_SUCCESS" = "true" ]; then
    if [ "$USE_VPN_METHOD" = "true" ]; then
        CONFIG_METHOD="VPN Tunnel"
    else
        CONFIG_METHOD="SSH Key (Fallback)"
    fi
fi

cat > /home/rom/client_info.txt << EOI
Client Information
==================
Phone: ${CLIENT_PHONE_ORIGINAL}
Name: ${CLIENT_NAME}
IP: ${CLIENT_IP}
ID: ${CLIENT_ID}
Webhook Domain: ${WEBHOOK_DOMAIN}
Configuration Method: ${CONFIG_METHOD}
Configured: $(date)

WireGuard Public Key: ${NEW_PUBLIC_KEY}
EOI

echo ""
echo "Configuration saved to: /home/rom/client_info.txt"
echo ""
echo "Next Steps:"
echo "  1. Connect USB dongle when ready"
echo "  2. Test from VPS: ping ${CLIENT_IP}"
echo "  3. Test SMS API: curl http://${CLIENT_IP}:8090/api/sms/status"
echo ""
echo -e "${GREEN}Client ${CLIENT_PHONE_ORIGINAL} is ready!${NC}"