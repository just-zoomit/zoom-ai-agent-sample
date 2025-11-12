from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain.agents import create_agent
from langchain_core.tools import create_retriever_tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from tools.search import get_vectorstore

import os

load_dotenv()

bot_token = os.environ.get("SLACK_BOT_TOKEN")
app_token = os.environ.get("SLACK_APP_TOKEN")

if not bot_token or not app_token:
    raise ValueError(
        "Missing required environment variables: SLACK_BOT_TOKEN and/or SLACK_APP_TOKEN"
    )

app = App(token=bot_token)

vectorstore = get_vectorstore()
retriever_tool = create_retriever_tool(
    vectorstore.as_retriever(),
    name="search",
    description="Retrieve information about the company. You will call this tool when you need to answer a question that you do not know the answer to.",
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, tools=[retriever_tool])


@app.event("message")
def handle_message_events(body, logger):
    """Handle general message events."""
    logger.info(body)


@app.event("app_mention")
def handle_hello(body, say):
    event = body["event"]
    message = event["text"]
    thread_ts = event.get("thread_ts", event["ts"])

    state = {"messages": [HumanMessage(content=message)]}
    response = agent.invoke(state)
    text = response["messages"][-1].content

    say(text=text, thread_ts=thread_ts)

if __name__ == "__main__":
    handler = SocketModeHandler(app, app_token)
    handler.start()