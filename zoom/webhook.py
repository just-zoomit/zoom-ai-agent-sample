import os
import hmac
import hashlib
import json
from flask import Flask, request, jsonify
from langchain_core.messages import HumanMessage
from .client import ZoomClient
from pprint import pprint


class ZoomWebhookHandler:
    """Handles Zoom Team Chat webhook events."""
    
    def __init__(self, agent):
        self.agent = agent
        self.zoom_client = ZoomClient()
        self.webhook_secret = os.environ.get("ZOOM_WEBHOOK_SECRET_TOKEN")
        
        if not self.webhook_secret:
            raise ValueError("Missing ZOOM_WEBHOOK_SECRET_TOKEN environment variable")
    
    def verify_webhook(self, payload: str, signature: str) -> bool:
        """Verify webhook signature from Zoom."""
        hash_for_verify = hmac.new(
            self.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        expected_signature = f"v0={hash_for_verify}"
        
        return hmac.compare_digest(signature, expected_signature)
    
    def process_message(self, event_data: dict) -> None:
        """Process incoming message from Zoom Team Chat."""
        try:
            # Extract message information
            message_content = event_data.get("payload", {}).get("plainToken", "")
            sender_jid = event_data.get("payload", {}).get("toJid", "")
            account_id = event_data.get("payload", {}).get("accountId")
            
            # Skip if no message content
            if not message_content.strip():
                return
            
            # Process with AI agent
            state = {"messages": [HumanMessage(content=message_content)]}
            response = self.agent.invoke(state)
            response_text = response["messages"][-1].content
            
            # Send response back to Zoom
            self.zoom_client.send_message(
                to_jid=sender_jid,
                message=response_text,
                account_id=account_id
            )
            
        except Exception as e:
            print(f"\n❌ ERROR processing Zoom message: {e}\n")
    
    def process_app_mention(self, event_data: dict) -> None:
        self.client_secret = os.environ.get("ZOOM_CLIENT_SECRET")

        """Process app mention from Zoom Team Chat."""
        try:
            payload = event_data.get("payload", {})
            object_data = payload.get("object", {})

            print("\n" + "="*70)
            print("💬 RECEIVED APP MENTION EVENT")
            print("="*70)
            pprint(event_data, width=100)
            print("="*70 + "\n")

            print("\n" + "-"*50)
            print("🔄 PROCESSING PAYLOAD")
            print("-"*50)
            pprint(payload, width=80)
            print("-"*50 + "\n")
            
            print("\n" + "-"*50)
            print("📊 OBJECT DATA")
            print("-"*50)
            pprint(object_data, width=80)
            print("-"*50 + "\n")
            
            # Extract message information for app mentions
            message_content = object_data.get("message", "")
            sender_jid = payload.get("toJid", "") or object_data.get("robot_jid", "")
            account_id = payload.get("account_id")
            operator_id = payload.get("operator_id", "")
           

            # User JID of the person who mentioned the app is not returned
            message_id = object_data.get("message_id", "")
            channel_id = object_data.get("channel_id", "")
            
            # Handle thread messages: 
            # If reply_main_message_id exists, this is a thread reply - use the reply_main_message_id
            # If no reply_main_message_id, this is the start of a new thread - use message_id
            reply_main_message_id = object_data.get("reply_main_message_id")
            
            # For threading: always reply to the main message ID if we're in a thread
            if reply_main_message_id:
                # This is a follow-up message in an existing thread
                thread_reply_id = reply_main_message_id
                print(f"\n🧵 THREAD REPLY: reply_main_message_id found ({reply_main_message_id})")
                print(f"   Using reply_main_message_id to maintain thread continuity")
                
            else:
                # This is the first message, future replies should thread to this message
                thread_reply_id = message_id
                print(f"\n🆕 NEW THREAD: No reply_main_message_id found")
                print(f"   Starting new conversation thread with message_id {message_id}")
            
            print(f"📌 Threading keeps related messages grouped for better UX\n")
            
            # Skip if no message content
            if not message_content.strip():
                return
            
            print(f"\n🎤 Processing app mention in channel {channel_id}")
            print(f"Message: {message_content}")
            print(f"Message ID: {message_id}")
            print(f"Reply Main Message ID: {reply_main_message_id}")
            print(f"Replying to: {thread_reply_id}\n")
            
            # Process with AI agent
            state = {"messages": [HumanMessage(content=message_content)]}
            response = self.agent.invoke(state)
            response_text = response["messages"][-1].content
            
            # Send response back to the same channel/thread
            self.zoom_client.send_message(
                to_jid=sender_jid,
                user_jid=operator_id,
                channel_id=channel_id,
                message=response_text,
                account_id=account_id,
                reply_to=thread_reply_id,
            )
            
        except Exception as e:
            print(f"\n❌ ERROR processing Zoom app mention: {e}\n")
    
    def handle_webhook(self, flask_request) -> tuple:
        """Handle incoming webhook request from Zoom."""
        try:

            
            # Get request data
            payload = flask_request.get_data(as_text=True)
            signature = flask_request.headers.get("x-zm-signature", "")
            
            # Verify webhook signature
            # if not self.verify_webhook(payload, signature):
            #     return jsonify({"error": "Invalid signature"}), 401
            
            # Parse event data
            event_data = json.loads(payload)
            event_type = event_data.get("event")
            
            # Handle different event types
            if event_type == "bot_notification":
                self.process_message(event_data)
                return jsonify({"status": "success"}), 200
            elif event_type == "team_chat.app_mention":
                
                self.process_app_mention(event_data)


                return jsonify({"status": "success"}), 200
            elif event_type == "endpoint.url_validation":
                # Handle URL validation challenge
                plain_token = event_data.get("payload", {}).get("plainToken", "")
                encrypted_token = self._encrypt_token(plain_token)
                return jsonify({
                    "plainToken": plain_token,
                    "encryptedToken": encrypted_token
                }), 200
            else:
                print(f"\nℹ️  Ignoring unhandled event type: {event_type}\n")
                return jsonify({"status": "ignored"}), 200
                
        except Exception as e:
            print(f"\n❌ WEBHOOK ERROR: {e}\n")
            return jsonify({"error": "Internal server error"}), 500
    
    def _encrypt_token(self, plain_token: str) -> str:
        """Encrypt token for URL validation."""
        return hmac.new(
            self.webhook_secret.encode(),
            plain_token.encode(),
            hashlib.sha256
        ).hexdigest()


def create_zoom_flask_app(agent):
    """Create Flask app for Zoom webhooks."""
    app = Flask(__name__)
    webhook_handler = ZoomWebhookHandler(agent)
    
    @app.route("/zoom/webhook", methods=["POST"])
    def webhook():
        print("\n" + "="*60)
        print("🔗 RECEIVED ZOOM WEBHOOK")
        print("="*60)
        webhook_data = request.get_data(as_text=True)
        try:
            # Try to pretty print JSON data
            parsed_data = json.loads(webhook_data)
            pprint(parsed_data, width=80)
        except json.JSONDecodeError:
            # If not JSON, print raw data
            print(webhook_data)
        print("="*60 + "\n")
        return webhook_handler.handle_webhook(request)
    
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "healthy"}), 200
    
    return app