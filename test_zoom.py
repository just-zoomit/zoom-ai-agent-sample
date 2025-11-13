#!/usr/bin/env python3
"""
Test script for Zoom Team Chat integration.
"""
import json
import requests
import os
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

def test_zoom_webhook():
    """Test Zoom webhook endpoint locally."""
    
    # Test payload (simulating Zoom Team Chat event)
    test_payload = {
        "event": "bot_notification",
        "payload": {
            "plainToken": "Hello, bot! How are you?",
            "toJid": "test@example.com",
            "accountId": "test_account"
        }
    }
    
    # App mention test payload (simulating team_chat.app_mention)
    app_mention_payload = {
        "event": "team_chat.app_mention",
        "payload": {
            "cmd": "@bot What is the company's mission?",
            "plainToken": "@bot What is the company's mission?",
            "toJid": "channel_123@conference.example.com",
            "accountId": "test_account",
            "channelName": "general"
        }
    }
    
    # URL validation test payload
    validation_payload = {
        "event": "endpoint.url_validation",
        "payload": {
            "plainToken": "test_validation_token"
        }
    }
    
    webhook_url = "http://localhost:5000/zoom/webhook"
    headers = {
        "Content-Type": "application/json",
        "x-zm-signature": "dummy_signature"  # In real scenario, this would be properly signed
    }
    
    print("\n" + "="*50)
    print("🧪 TESTING ZOOM WEBHOOK ENDPOINTS")
    print("="*50)
    print(f"Webhook URL: {webhook_url}")
    print("="*50 + "\n")
    
    try:
        # Test health endpoint first
        health_response = requests.get("http://localhost:5000/health")
        if health_response.status_code == 200:
            print("✓ Health endpoint working\n")
        else:
            print("✗ Health endpoint failed\n")
            
        print("\n" + "-"*60)
        print("📝 SETUP INSTRUCTIONS")
        print("-"*60)
        setup_steps = [
            "Set up proper environment variables in .env",
            "Run: uv run python main.py",
            "Use ngrok or similar to expose localhost:5000",
            "Configure Zoom Team Chat app webhook URL to point to your public endpoint",
            "The webhook endpoint will be: https://your-domain.ngrok.io/zoom/webhook"
        ]
        for i, step in enumerate(setup_steps, 1):
            print(f"{i}. {step}")
        print("-"*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to webhook server")
        print("Make sure to run 'uv run python main.py' first\n")

if __name__ == "__main__":
    test_zoom_webhook()