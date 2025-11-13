import os
import hmac
import hashlib
import json
from flask import Flask, request, jsonify
from langchain_core.messages import HumanMessage
from .client import ZoomClient


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
            print(f"Error processing Zoom message: {e}")
    
    def process_app_mention(self, event_data: dict) -> None:
        self.client_secret = os.environ.get("ZOOM_CLIENT_SECRET")

        """Process app mention from Zoom Team Chat (similar to Slack app_mention)."""
        try:
            payload = event_data.get("payload", {})
            object_data = payload.get("object", {})

            print('\n',"Received app mention event data:", event_data, '\n')

            print( '\n',"Processing  payload:", payload, '\n')
            print('\n', "Object data:", object_data, '\n')
            
            # Extract message information for app mentions
            message_content = object_data.get("message", "")
            sender_jid = payload.get("toJid", "") or object_data.get("robot_jid", "")
            account_id = payload.get("account_id")
            channel_id = object_data.get("channel_id", "")

            # User JID of the person who mentioned the app is not returned
            user_jid = object_data.get("user_jid", "")
            
            # Skip if no message content
            if not message_content.strip():
                return
            
            print(f"Processing app mention in channel {channel_id}: {message_content}")
            
            # Process with AI agent (similar to Slack app mention handling)
            state = {"messages": [HumanMessage(content=message_content)]}
            response = self.agent.invoke(state)
            response_text = response["messages"][-1].content
            
            # Send response back to the same channel/thread
            self.zoom_client.send_message(
                to_jid=sender_jid,
                channel_id=channel_id,
                message=response_text,
                account_id=account_id
            )
            
        except Exception as e:
            print(f"Error processing Zoom app mention: {e}")
    
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
                print(f"Ignoring unhandled event type: {event_type}")
                return jsonify({"status": "ignored"}), 200
                
        except Exception as e:
            print(f"Webhook error: {e}")
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
        print("Received Zoom webhook", request.get_data(as_text=True))
        return webhook_handler.handle_webhook(request)
    
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "healthy"}), 200
    
    return app