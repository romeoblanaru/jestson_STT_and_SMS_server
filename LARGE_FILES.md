# Large Files Excluded from Repository

This document describes large model files (over 300MB) that are excluded from the git repository.

## Speech-to-Text Models

### 1. Faster-Whisper Model
- **Location**: `.cache/faster-whisper/models--Systran--faster-whisper-small/`
- **Size**: ~300MB+
- **Description**: Faster-Whisper small model for speech recognition
- **Download**: Automatically downloaded by faster-whisper library on first use
- **Command**: Models are cached when running the STT service

### 2. Whisper.cpp Models
- **Location**: `whisper.cpp/models/`
- **Files**:
  - `ggml-large-v3-turbo.bin` (~1.5GB)
  - `ggml-large-v3-turbo-q5_0.bin` (~1GB)
- **Description**: Whisper.cpp quantized models for efficient inference
- **Download**:
  ```bash
  cd whisper.cpp/models
  bash download-ggml-model.sh large-v3-turbo
  bash download-ggml-model.sh large-v3-turbo-q5_0
  ```

### 3. NVIDIA Riva Parakeet Model
- **Location**: `riva_quickstart_v2.19.0/model_repository/prebuilt/`
- **File**: `asr_parakeet_1.1b_universal_streaming_embedded.tar.gz` (~1.2GB)
- **Description**: NVIDIA Riva ASR Parakeet model for streaming speech recognition
- **Download**: Included with NVIDIA Riva QuickStart deployment
- **Documentation**: https://docs.nvidia.com/deeplearning/riva/

### 4. Parakeet TDT Model
- **Location**: `parakeet-tdt-0.6b-v3/`
- **File**: `parakeet-tdt-0.6b-v3.nemo` (~600MB)
- **Description**: NVIDIA Parakeet TDT (Token and Duration Transducer) model
- **Download**: Available from NVIDIA NGC catalog
- **Command**:
  ```bash
  wget https://api.ngc.nvidia.com/v2/models/nvidia/nemo/parakeet_tdt_0.6b/versions/v3/files/parakeet-tdt-0.6b-v3.nemo
  ```

## Hugging Face Cache
- **Location**: `.cache/huggingface/`
- **Description**: Cached models from Hugging Face Hub
- **Note**: Models are automatically downloaded and cached when needed

## How to Setup Models on New Machine

1. **Install required libraries**: Follow the main README.md for installation instructions
2. **Run STT service**: Models will be automatically downloaded on first use
3. **For manual download**: Use the commands listed above for specific models
4. **For Riva models**: Follow NVIDIA Riva QuickStart documentation

## Disk Space Requirements

- Minimum: 5GB for basic models
- Recommended: 10GB for all models
- With cache: 15GB total
