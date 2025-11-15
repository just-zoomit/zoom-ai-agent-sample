from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import create_retriever_tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from tools.search import get_vectorstore
from zoom.webhook import create_zoom_flask_app

import os

load_dotenv()

# Configuration flags
ZOOM_WEBHOOK_PORT = int(os.environ.get("ZOOM_WEBHOOK_PORT", "4001"))

vectorstore = get_vectorstore()
retriever_tool = create_retriever_tool(
    vectorstore.as_retriever(),
    name="search",
    description="Retrieve information about the company. You will call this tool when you need to answer a question that you do not know the answer to.",
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, tools=[retriever_tool])

# Initialize Zoom webhook app
zoom_app = create_zoom_flask_app(agent)

def run_zoom_webhook():
    """Run Zoom webhook server."""
    print(f"\n=== Starting Zoom webhook server on port {ZOOM_WEBHOOK_PORT} ===")
    print()
    zoom_app.run(host="0.0.0.0", port=ZOOM_WEBHOOK_PORT, debug=False)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🤖 ZOOM TEAM CHAT AI AGENT STARTING")
    print("="*50)
    print(f"📹 Zoom Team Chat integration enabled")
    print("="*50 + "\n")
    
    try:
        run_zoom_webhook()
    except KeyboardInterrupt:
        print("\n" + "="*30)
        print("🛑 SHUTTING DOWN...")
        print("="*30 + "\n")