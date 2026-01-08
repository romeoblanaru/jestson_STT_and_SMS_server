#!/usr/bin/env python3
"""
Response Tokenizer Module
Splits LLM responses into smaller parts for better TTS conversation flow

Split criteria:
1. After punctuation: ? ! , .
2. Before separator words (language-specific)
3. Exception handling (e.g., "dvs." in Romanian)
"""

import os
import re
import time


def load_separators(language):
    """Load separator words for specified language"""
    separators_file = f"/home/rom/transcription_separators/separators_{language}"
    separator_words = []

    if os.path.exists(separators_file):
        try:
            with open(separators_file, 'r', encoding='utf-8') as f:
                separator_words = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Warning: Failed to load separator words: {e}")

    return separator_words


def load_exceptions(language):
    """Load exception patterns for specified language"""
    exceptions_file = f"/home/rom/transcription_separators/exceptions_{language}"
    exceptions = []

    if os.path.exists(exceptions_file):
        try:
            with open(exceptions_file, 'r', encoding='utf-8') as f:
                exceptions = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Warning: Failed to load exceptions: {e}")

    return exceptions


def tokenize_response(text, language, call_id=None, save_debug=True):
    """
    Tokenize response text into smaller parts for better TTS flow

    Args:
        text (str): Text to tokenize
        language (str): Language code ('ro', 'lt', etc.)
        call_id (str, optional): Call ID for debug file naming
        save_debug (bool): Whether to save debug output to disk

    Returns:
        list: List of text tokens

    Split criteria:
    1. After punctuation: ? ! , .
    2. Before separator words (loaded from file based on language)
    3. Exceptions: Don't split if pattern found in exceptions file
    """

    # Load separator words and exceptions for this language
    separator_words = load_separators(language)
    exceptions = load_exceptions(language)

    # Process text character by character
    tokens = []
    current_token = ""
    i = 0

    while i < len(text):
        char = text[i]
        current_token += char
        should_split = False

        # 1. Check for punctuation split (after: ? ! , .)
        if char in '?!,.':
            # Check if this is an exception (e.g., "dvs." in Romanian)
            is_exception = False
            for exception in exceptions:
                if current_token.rstrip().endswith(exception):
                    is_exception = True
                    break

            if not is_exception:
                if i + 1 >= len(text) or text[i + 1] in ' \n\t':
                    should_split = True

        # 2. Check for separator word split (before word)
        if not should_split and separator_words:
            remaining_text = text[i + 1:]
            for separator_word in separator_words:
                pattern = r'^\s+(' + re.escape(separator_word) + r')(\s|[?!,.]|$)'
                match = re.match(pattern, remaining_text, re.IGNORECASE)
                if match:
                    should_split = True
                    break

        # Perform split if needed
        if should_split:
            token = current_token.strip()
            if token:
                tokens.append(token)
            current_token = ""

        i += 1

    # Add remaining text as final token
    if current_token.strip():
        tokens.append(current_token.strip())

    if not tokens:
        tokens = [text.strip()]

    # Save debug info if requested
    if save_debug and call_id:
        try:
            os.makedirs("/home/rom/transcriptions", exist_ok=True)
            debug_file = f"/home/rom/transcriptions/{call_id}_tokenization.txt"
            with open(debug_file, 'a', encoding='utf-8') as f:
                timestamp = time.strftime('%H:%M:%S')
                f.write(f"\n[{timestamp}] Original text:\n")
                f.write(f"  {text}\n\n")
                f.write(f"  Split into {len(tokens)} tokens:\n")
                for idx, token in enumerate(tokens, 1):
                    f.write(f"    {idx}. {token}\n")
        except Exception as e:
            print(f"Warning: Failed to save tokenization debug: {e}")

    return tokens
