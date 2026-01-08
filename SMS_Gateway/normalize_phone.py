#!/usr/bin/env python3
"""
Phone number normalization using sms-normalize-eu.sh
Extracts country code from gateway's phone number and uses it as default
"""
import subprocess
import json
import re
import os

def extract_country_code(phone_number):
    """
    Extract country code from phone number
    Handles 2-digit (UK: +44) and 3-digit (Lithuania: +370) codes

    Args:
        phone_number: Phone number string (e.g., "+447511772308")

    Returns:
        Country code with + (e.g., "+44" or "+370")
    """
    if not phone_number:
        return "+44"  # Default to UK

    # Remove spaces and formatting
    clean = phone_number.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

    # Must start with +
    if not clean.startswith('+'):
        return "+44"  # Default

    # Extract country code after +
    # Try 3-digit codes first (e.g., +370, +371, +372, +373)
    three_digit_codes = ['370', '371', '372', '373', '374', '375', '376', '377', '378', '379',
                         '380', '381', '382', '383', '385', '386', '387', '389', '420', '421', '423']

    if len(clean) >= 4:  # At least +XXX
        potential_3digit = clean[1:4]
        if potential_3digit in three_digit_codes:
            return '+' + potential_3digit

    # Try 2-digit codes (most European countries)
    if len(clean) >= 3:  # At least +XX
        potential_2digit = clean[1:3]
        # Validate it's numeric
        if potential_2digit.isdigit():
            return '+' + potential_2digit

    return "+44"  # Fallback to UK


def normalize_phone_number(phone_number, default_country_code=None):
    """
    Normalize phone number using sms-normalize-eu.sh

    Args:
        phone_number: Phone number to normalize
        default_country_code: Default country code (e.g., "+44"), if None uses +44

    Returns:
        Normalized phone number in E.164 format (e.g., "+447504128961")
    """
    if not phone_number:
        return phone_number

    # If already in E.164 format (starts with + and looks valid), return as-is
    if phone_number.startswith('+') and len(phone_number) >= 10:
        return phone_number

    # Set default country code
    if default_country_code is None:
        default_country_code = "+44"

    # Ensure default_country_code has +
    if not default_country_code.startswith('+'):
        default_country_code = '+' + default_country_code

    # Clean the number first
    clean = phone_number.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

    # Handle international prefix 00 → +
    if clean.startswith('00'):
        return '+' + clean[2:]

    # Handle numbers starting with country code (44, 370, etc) without +
    # Check if it starts with a known country code
    cc_digits = default_country_code[1:]  # Remove + to get digits

    # Case 1: Starts with CC + extra 0 (e.g., 4407504... should be +447504...)
    if clean.startswith(cc_digits + '0') and len(clean) > len(cc_digits) + 1:
        # Remove the extra 0 and add +
        return '+' + cc_digits + clean[len(cc_digits) + 1:]

    # Case 2: Starts with CC directly (e.g., 447504... should be +447504...)
    if clean.startswith(cc_digits) and len(clean) > len(cc_digits):
        return '+' + clean

    # Case 3: Starts with just CC digits for other countries
    # Check common 2-digit codes
    for potential_cc in ['44', '49', '33', '34', '39', '31', '32', '41', '43', '45', '46', '47', '48']:
        if clean.startswith(potential_cc) and len(clean) >= 10:
            return '+' + clean

    # Check common 3-digit codes
    for potential_cc in ['370', '371', '372', '373', '374', '375', '376', '377', '378', '379',
                         '380', '381', '382', '383', '385', '386', '387', '389', '420', '421', '423']:
        if clean.startswith(potential_cc) and len(clean) >= 10:
            return '+' + clean

    try:
        # Create temp file with SMS format
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sms') as f:
            f.write(f"To: {phone_number}\n\nTest message")
            temp_file = f.name

        # Run sms-normalize-eu.sh with custom default country code
        env = os.environ.copy()
        env['DEFAULT_CC'] = default_country_code

        result = subprocess.run(
            ['/home/rom/SMS_Gateway/sms_normalize_eu/sms-normalize-eu.sh', temp_file],
            env=env,
            capture_output=True,
            timeout=2
        )

        # Read normalized number from file
        with open(temp_file, 'r') as f:
            content = f.read()
            # Extract To: header
            for line in content.split('\n'):
                if line.startswith('To:'):
                    normalized = line.split(':', 1)[1].strip()
                    os.unlink(temp_file)
                    return normalized

        # Cleanup
        os.unlink(temp_file)

    except Exception as e:
        # If normalization fails, try simple fallback
        clean = phone_number.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

        # If starts with 0 (UK local format), add country code
        if clean.startswith('0') and len(clean) == 11:
            return default_country_code + clean[1:]

        # If already has +, return as-is
        if clean.startswith('+'):
            return clean

        # If looks like country code is already there (no leading 0), add +
        if len(clean) >= 10 and not clean.startswith('0'):
            return '+' + clean

    return phone_number  # Return original if all else fails


def get_gateway_country_code():
    """
    Get country code from gateway's own phone number in voice_config.json

    Returns:
        Country code with + (e.g., "+44" or "+370")
    """
    try:
        config_file = '/home/rom/voice_config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                phone_number = config.get('phone_number')
                if phone_number:
                    return extract_country_code(phone_number)
    except:
        pass

    # Fallback: check .env file
    try:
        env_file = '/home/rom/.env'
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('CLIENT_PHONE='):
                        phone = line.split('=', 1)[1].strip()
                        return extract_country_code(phone)
    except:
        pass

    return "+44"  # Default to UK


if __name__ == "__main__":
    # Test
    import sys

    if len(sys.argv) > 1:
        test_number = sys.argv[1]
        default_cc = sys.argv[2] if len(sys.argv) > 2 else None

        print(f"Input: {test_number}")
        print(f"Default CC: {default_cc or get_gateway_country_code()}")
        print(f"Normalized: {normalize_phone_number(test_number, default_cc or get_gateway_country_code())}")
    else:
        # Test cases
        gateway_cc = get_gateway_country_code()
        print(f"Gateway country code: {gateway_cc}")
        print()

        tests = [
            "07504128961",      # UK local
            "+447504128961",    # UK E.164
            "447504128961",     # UK without +
            "86123456",         # Lithuanian local
            "+37086123456",     # Lithuanian E.164
        ]

        for test in tests:
            normalized = normalize_phone_number(test, gateway_cc)
            print(f"{test:20} → {normalized}")
