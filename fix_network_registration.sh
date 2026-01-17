#!/bin/bash
# Fix EC25 network registration

PORT="/dev/ttyUSB_AT"

echo "Checking SIM and network status..."

# Configure serial port
stty -F $PORT 115200 raw -echo 2>/dev/null

# Check SIM status
echo "1. Checking SIM status..."
echo -e "AT+CPIN?\r" > $PORT
sleep 1
timeout 2 cat < $PORT

# Check network operator
echo -e "\n2. Checking network operator..."
echo -e "AT+COPS?\r" > $PORT
sleep 1
timeout 2 cat < $PORT

# Check signal quality
echo -e "\n3. Checking signal quality..."
echo -e "AT+CSQ\r" > $PORT
sleep 1
timeout 2 cat < $PORT

# Check registration status
echo -e "\n4. Checking registration status..."
echo -e "AT+CREG?\r" > $PORT
sleep 1
timeout 2 cat < $PORT

# Try to force registration (automatic mode)
echo -e "\n5. Forcing automatic network registration..."
echo -e "AT+COPS=0\r" > $PORT
sleep 5
timeout 2 cat < $PORT

# Check if it worked
echo -e "\n6. Verifying registration..."
echo -e "AT+CREG?\r" > $PORT
sleep 1
timeout 2 cat < $PORT

echo -e "\nDone! Check output above."
