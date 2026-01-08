#!/bin/bash
# Decode phone number from PDU format

pdu="$1"
if [[ -z "$pdu" ]]; then
    echo "Usage: $0 <pdu_hex>"
    exit 1
fi

# Extract number type and digits (looking for type 91 or 81 followed by number)
# In PDU: 0B=length, 91=international type, then number in swapped nibbles
number_part=$(echo "$pdu" | grep -oE '0[A-F]91[0-9A-F]{10,14}' | sed 's/^..//')
if [[ -n "$number_part" ]]; then
    type_code="${number_part:0:2}"
    number_hex="${number_part:2}"
    
    # Decode swapped nibbles
    decoded=""
    for ((i=0; i<${#number_hex}; i+=2)); do
        char2=${number_hex:$i:1}
        char1=${number_hex:$((i+1)):1}
        decoded="${decoded}${char1}${char2}"
    done
    
    # Remove padding F and any trailing non-digits
    decoded=$(echo "$decoded" | sed 's/F.*//' | sed 's/[^0-9]*$//')
    
    # Add + for international
    if [[ "$type_code" == "91" ]]; then
        echo "+$decoded"
    else
        echo "$decoded"
    fi
else
    echo "No number found in PDU"
fi