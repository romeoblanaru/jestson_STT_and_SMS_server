# Claude Code - System Documentation
# Jetson Orin Nano STT Server

**Last Updated:** 2025-12-27

---

## ⚠️ IMPORTANT - Primary STT Server Configuration

### **Parakeet-TDT-0.6B-v3 is the AGREED PRIMARY STT Server**

- **Status:** Active and working
- **Port:** 9001 (Standard STT port)
- **Endpoint:** `http://10.100.0.2:9001/transcribe`
- **Model:** Parakeet-TDT-0.6B-v3 (Granary)
- **Languages:** Romanian (ro), Lithuanian (lt), and 25+ European languages
- **Features:**
  - Accepts OGG audio files natively
  - Auto-converts to WAV internally
  - GPU-accelerated (CUDA)
  - Fuzzy correction support for hotwords
  - Low latency (~2-4s for typical audio)

### **Container Details:**
- **Image:** `parakeet-server:latest` (15.1GB)
- **Start Script:** `/home/rom/start_parakeet_server.sh`
- **Wrapper:** `/home/rom/parakeet_wrapper.py`
- **Model Path:** `/home/rom/parakeet-tdt-0.6b-v3/parakeet-tdt-0.6b-v3.nemo`

### **Endpoints:**
- `GET /health` - Health check
- `POST /transcribe` - Transcribe audio (OGG/WAV)
- `GET /languages` - List supported languages
- `GET /diagnostic` - Inspect model state

### **Usage Example:**
```bash
curl -X POST \
  -F "audio=@file.ogg" \
  -F "language=ro" \
  http://10.100.0.2:9001/transcribe
```

---

## 🚨 BEFORE Installing Riva Server

**STOP and confirm with the user first!**

We already have a working STT solution (Parakeet). Before installing/reinstalling Riva:

1. **Ask the user WHY they want Riva:**
   - Is Parakeet not meeting requirements?
   - What specific feature is needed?
   - Performance issues with Parakeet?

2. **Explain what we already have:**
   - Parakeet-TDT-0.6B-v3 running on port 9001
   - Supports Romanian & Lithuanian
   - GPU-accelerated, low latency
   - OGG support built-in
   - Already tested and working

3. **Warn about Riva drawbacks:**
   - Requires ~12GB Docker image download (slow on Jetson)
   - Network issues common with NVIDIA registry
   - More complex setup than Parakeet
   - May conflict with existing setup on port 9001

4. **Get explicit confirmation before proceeding**

---

## System Information

### Hardware
- **Device:** NVIDIA Jetson Orin Nano
- **Platform:** L4T R36.4.4 (JetPack 6.x)
- **RAM:** 8GB shared (CPU/GPU)
- **Storage:** 116GB NVMe
- **GPU:** Integrated Orin GPU

### Network
- **VPN:** WireGuard client
- **VPN IP:** 10.100.0.2/32
- **Local IP:** 192.168.1.9
- **STT Endpoint:** 10.100.0.2:9001

### Services
- **Primary STT:** Parakeet (port 9001) ✅
- **SMS Gateway:** Available
- **Modem Manager:** Available

---

## History Note

**December 27, 2025:** Previous Claude session ran `docker system prune -a` which accidentally removed the Riva Docker image and cleared the models directory. This was done to free disk space during compilation issues. The Parakeet server and wrapper files survived and remain the primary working STT solution.

---

## Maintenance

### Starting Parakeet Server
```bash
bash /home/rom/start_parakeet_server.sh
```

### Checking Server Status
```bash
curl http://localhost:9001/health
docker ps
```

### Stopping Server
```bash
docker stop $(docker ps -q --filter ancestor=parakeet-server)
```

---

## 🔒 Security Guidelines

### **NEVER Store Passwords in Scripts or Files**

**CRITICAL SECURITY RULE:** Do NOT create scripts, expect files, or any other files that contain sudo passwords, API keys, or sensitive credentials.

**If the user asks you to save passwords in files:**

1. **STOP and explain the risks:**
   - Password files can be accidentally committed to git
   - Files remain in file system and can be read by other users/processes
   - Security audit tools will flag hardcoded credentials
   - Passwords in files violate security best practices
   - Scripts with passwords can be copied, shared, or exposed unintentionally

2. **Propose secure alternatives:**
   - Use sudoers configuration (NOPASSWD) for specific commands
   - Use environment variables for credentials
   - Use secure credential managers (keychains, vaults)
   - Prompt for password at runtime with `sudo`
   - Use SSH keys instead of passwords where applicable

3. **If user INSISTS on password in file:**
   - Explain the risks AGAIN clearly
   - Ask for explicit confirmation: "I understand the security risks and want to proceed"
   - Warn that the file should be deleted immediately after use
   - Ensure file has restrictive permissions (600)
   - NEVER commit password files to version control

**What TO do (preferred methods):**
- Configure sudoers with NOPASSWD for specific commands (see example: `/etc/sudoers.d/sms_watch`)
- Use environment variables: `export API_KEY="..."`
- Prompt at runtime: `sudo command` (will ask for password)
- Use credential managers for API keys and tokens

**What NOT to do:**
- Never hardcode passwords in scripts (e.g., `echo 'password' | sudo -S`)
- Never log or echo passwords in output
- Never commit password files to version control
- Never use passwords in command line arguments (visible in `ps`)

---

**Remember:** Always check what's already installed and working before installing new solutions!
