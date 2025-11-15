import os
import requests
from typing import Dict, Any
from pprint import pprint


class ZoomClient:
    """Client for interacting with Zoom Team Chat API."""
    
    def __init__(self):
        self.client_id = os.environ.get("ZOOM_CLIENT_ID")
        self.client_secret = os.environ.get("ZOOM_CLIENT_SECRET")
        self.base_url = "https://api.zoom.us/v2"
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Missing ZOOM_CLIENT_ID or ZOOM_CLIENT_SECRET environment variables")
    
    def get_access_token(self) -> str:
        """Get OAuth2 access token for Zoom API."""
        auth_url = "https://zoom.us/oauth/token"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials"
        }
        
        response = requests.post(
            auth_url,
            headers=headers,
            data=data,
            auth=(self.client_id, self.client_secret)
        )
        
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            raise Exception(f"Failed to get access token: {response.text}")

    def send_message(self, to_jid: str, channel_id: str, user_jid: str, message: str, account_id: str = None, reply_to: str = None) -> Dict[Any, Any]:
        """Send a message to a Zoom Team Chat channel or user."""
        access_token = self.get_access_token()
        print("\n" + "="*60)
        print("🔑 ZOOM ACCESS TOKEN")
        print(access_token)
        print("="*60)

        print("\n" + "="*60)
        print("📱 SENDING MESSAGE TO ZOOM ")
        print("="*60)
        message_details = {
            "to_jid": to_jid,
            "user_jid": user_jid,
            "channel_id": channel_id,
            "message": message,
            "account_id": account_id,
            "reply_to": reply_to
        }
        pprint(message_details, width=80)
        print("="*60 + "\n")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        payload = {
            "robot_jid": os.environ.get("ZOOM_BOT_JID", ""),
            "to_jid":  channel_id+"@conference.xmpp.zoom.us",
            "user_jid": user_jid+"@xmpp.zoom.us",
            "account_id": account_id or "",
            "content": {
                "head": {
                    "text": "Hello World",
                    "style": {"bold": True}
                },
                "body": [
                    {
                        "type": "message",
                        "text": message
                    },
                    {
                        "type": "actions",
                        "items": [
                            {
                                "text": "Thumbsup",
                                "value": "thumbsup",
                                "style": "Thumbsup"
                            },
                            {
                                "text": "Thumbsdown", 
                                "value": "thumbsdown",
                                "style": "Thumbsdown"
                            }
                        ]
                    }
                ]
            }
           
        }
        
        if reply_to:
            payload["reply_to"] = reply_to
        
        url = f"{self.base_url}/im/chat/messages"
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to send message: {response.text}")