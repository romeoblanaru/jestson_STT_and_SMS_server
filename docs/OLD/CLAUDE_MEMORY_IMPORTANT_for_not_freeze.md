# CRITICAL RULES FOR CLAUDE - EC25 PROJECT

## ⚠️ NEVER USE `cat` ON SERIAL PORTS ⚠️

**FORBIDDEN:**
```bash
cat /dev/ttyUSB2
cat /dev/ttyUSB0
cat /dev/ttyUSB1
cat /dev/ttyUSB3
```

**WHY:** Using `cat` directly on serial ports causes **BLOCKING I/O** that:
- Freezes the Claude console completely
- Freezes the terminal process
- Requires force kill or system reboot
- Does NOT respect timeout commands properly

## ✅ CORRECT WAY TO READ FROM EC25 SERIAL PORTS

**Method 1 - Using picocom (PREFERRED):**
```bash
echo -e "AT+CSQ\r" | timeout 2 picocom -b 115200 -qrx 500 /dev/ttyUSB2 2>/dev/null
```

**Method 2 - Using bash with proper timeout:**
```bash
timeout 3 bash -c 'echo -e "ATI\r" > /dev/ttyUSB2; sleep 0.5; timeout 1 cat /dev/ttyUSB2' 2>/dev/null
```

**Key points:**
- Always use `timeout` command
- Always redirect stderr to `/dev/null`
- Use picocom with `-qrx` flags for non-blocking operation
- Keep timeout values reasonable (1-3 seconds)

## EC25 USB Audio Behavior

**When USB audio is enabled on EC25:**
- Serial ports may become unresponsive
- AT commands may timeout
- Reading from ports may block indefinitely
- **This is why `cat` is FORBIDDEN**

---

**Last updated:** 2025-10-10
**Project:** EC25 Voice Bot with USB Audio
**User:** rom
