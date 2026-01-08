#!/usr/bin/env python3
"""
Check NeMo's N-gram Language Model Fusion API
to understand how to properly configure fusion_models for TDT greedy decoder
"""
import inspect
from nemo.collections.asr.parts.submodules.rnnt_decoding import NGramGPULanguageModel

print("=" * 80)
print("NGramGPULanguageModel Inspection")
print("=" * 80)

# Check class signature
print("\nClass signature:")
print(inspect.signature(NGramGPULanguageModel))

# Check docstring
if NGramGPULanguageModel.__doc__:
    print("\nDocstring:")
    print(NGramGPULanguageModel.__doc__)

# Check init method
print("\n" + "=" * 80)
print("__init__ method source:")
print("=" * 80)
try:
    init_source = inspect.getsource(NGramGPULanguageModel.__init__)
    print(init_source[:1000])  # First 1000 chars
except Exception as e:
    print(f"Could not get source: {e}")

# Check for configuration
print("\n" + "=" * 80)
print("Checking for config dataclass:")
print("=" * 80)

try:
    from nemo.collections.asr.parts.submodules.rnnt_decoding import NGramGPULanguageModelConfig
    print(f"Found NGramGPULanguageModelConfig: {NGramGPULanguageModelConfig}")
    print(f"\nSignature: {inspect.signature(NGramGPULanguageModelConfig)}")

    # Try to create instance to see defaults
    try:
        config = NGramGPULanguageModelConfig()
        print("\nDefault config attributes:")
        for attr in dir(config):
            if not attr.startswith('_'):
                try:
                    val = getattr(config, attr)
                    if not callable(val):
                        print(f"  {attr}: {val}")
                except:
                    pass
    except Exception as e:
        print(f"Could not create config: {e}")

except ImportError as e:
    print(f"NGramGPULanguageModelConfig not found: {e}")

# Check what parameters the decoding strategy expects
print("\n" + "=" * 80)
print("Checking RNNTBPEDecodingConfig for fusion_models:")
print("=" * 80)

try:
    from nemo.collections.asr.parts.submodules.rnnt_decoding import RNNTBPEDecodingConfig
    from omegaconf import OmegaConf

    # Try to find fusion-related attributes
    config_instance = RNNTBPEDecodingConfig()
    print("\nFusion-related attributes in RNNTBPEDecodingConfig:")
    for attr in dir(config_instance):
        if 'fusion' in attr.lower() or 'ngram' in attr.lower() or 'lm' in attr.lower():
            try:
                val = getattr(config_instance, attr)
                if not callable(val):
                    print(f"  {attr}: {val}")
            except:
                pass

except Exception as e:
    print(f"Error checking RNNTBPEDecodingConfig: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Conclusion")
print("=" * 80)
print("\nTo enable n-gram fusion, we need to:")
print("1. Understand the expected input format for NGramGPULanguageModel")
print("2. Check if it supports ARPA/KenLM binary format")
print("3. Configure fusion_models in decoding config")
print("4. Set appropriate fusion_models_alpha values")
