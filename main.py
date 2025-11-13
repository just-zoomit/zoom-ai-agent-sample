from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain.agents import create_agent
from langchain_core.tools import create_retriever_tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from tools.search import get_vectorstore
from zoom.webhook import create_zoom_flask_app

import os
import threading

load_dotenv()

# Configuration flags
ENABLE_SLACK = os.environ.get("ENABLE_SLACK", "true").lower() == "true"
ENABLE_ZOOM = os.environ.get("ENABLE_ZOOM", "true").lower() == "true"
ZOOM_WEBHOOK_PORT = int(os.environ.get("ZOOM_WEBHOOK_PORT", "4001"))

# Slack configuration
bot_token = os.environ.get("SLACK_BOT_TOKEN")
app_token = os.environ.get("SLACK_APP_TOKEN")

if ENABLE_SLACK and (not bot_token or not app_token):
    raise ValueError(
        "Missing required environment variables: SLACK_BOT_TOKEN and/or SLACK_APP_TOKEN"
    )

# Initialize Slack app if enabled
slack_app = None
if ENABLE_SLACK:
    slack_app = App(token=bot_token)

vectorstore = get_vectorstore()
retriever_tool = create_retriever_tool(
    vectorstore.as_retriever(),
    name="search",
    description="Retrieve information about the company. You will call this tool when you need to answer a question that you do not know the answer to.",
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, tools=[retriever_tool])

# Slack event handlers
if ENABLE_SLACK and slack_app:
    @slack_app.event("message")
    def handle_message_events(body, logger):
        """Handle general message events."""
        logger.info(body)

    @slack_app.event("app_mention")
    def handle_hello(body, say):
        event = body["event"]
        message = event["text"]
        thread_ts = event.get("thread_ts", event["ts"])

        state = {"messages": [HumanMessage(content=message)]}
        response = agent.invoke(state)
        text = response["messages"][-1].content

        say(text=text, thread_ts=thread_ts)

# Initialize Zoom webhook app if enabled
zoom_app = None
if ENABLE_ZOOM:
    zoom_app = create_zoom_flask_app(agent)

def run_slack_bot():
    """Run Slack bot in Socket Mode."""
    if ENABLE_SLACK and slack_app:
        print("Starting Slack bot...")
        handler = SocketModeHandler(slack_app, app_token)
        handler.start()

def run_zoom_webhook():
    """Run Zoom webhook server."""
    if ENABLE_ZOOM and zoom_app:
        print(f"Starting Zoom webhook server on port {ZOOM_WEBHOOK_PORT}...")
        zoom_app.run(host="0.0.0.0", port=ZOOM_WEBHOOK_PORT, debug=False)

if __name__ == "__main__":
    print("Starting AI Agent Bot...")
    print(f"Slack enabled: {ENABLE_SLACK}")
    print(f"Zoom enabled: {ENABLE_ZOOM}")
    
    threads = []
    
    # Start Slack bot in separate thread if enabled
    if ENABLE_SLACK:
        slack_thread = threading.Thread(target=run_slack_bot, daemon=True)
        slack_thread.start()
        threads.append(slack_thread)
    
    # Start Zoom webhook server in main thread if enabled
    if ENABLE_ZOOM:
        if ENABLE_SLACK:
            # If both are enabled, run Zoom in separate thread too
            zoom_thread = threading.Thread(target=run_zoom_webhook, daemon=True)
            zoom_thread.start()
            threads.append(zoom_thread)
            
            # Keep main thread alive
            try:
                for thread in threads:
                    thread.join()
            except KeyboardInterrupt:
                print("\nShutting down...")
        else:
            # If only Zoom is enabled, run in main thread
            run_zoom_webhook()
    elif ENABLE_SLACK:
        # If only Slack is enabled, keep main thread alive
        try:
            threads[0].join()
        except KeyboardInterrupt:
            print("\nShutting down...")
    else:
        print("No bots enabled. Check your environment variables.")