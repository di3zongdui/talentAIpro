#!/usr/bin/env python
"""Test SiliconFlow API Key"""
import httpx
import json
import sys

def test_api_key():
    api_key = 'sk-unpavlxvzzormhmxlpzlajqadfrgvybfzevprbjqphbzigtr'
    url = 'https://api.siliconflow.cn/v1/chat/completions'

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    data = {
        'model': 'Qwen/Qwen3-Omni-30B-A3B-Instruct',
        'messages': [{'role': 'user', 'content': 'Say hello in one word'}],
        'max_tokens': 50,
    }

    print(f"Testing SiliconFlow API...")
    print(f"URL: {url}")
    print(f"Model: Qwen/Qwen3-Omni-30B-A3B-Instruct")

    try:
        resp = httpx.post(url, json=data, headers=headers, timeout=60)
        print(f"\nStatus: {resp.status_code}")
        print(f"Response: {resp.text[:1000]}")
        return resp.status_code == 200
    except Exception as e:
        print(f"\nError: {e}")
        return False

if __name__ == "__main__":
    success = test_api_key()
    sys.exit(0 if success else 1)