import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import create_retriever_tool
from langchain_core.messages import HumanMessage

from tools.search import get_vectorstore

load_dotenv()

bot_token = os.environ["SLACK_BOT_TOKEN"]
app_token = os.environ["SLACK_APP_TOKEN"]

# ---------- Build tools & agent ----------
vectorstore = get_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

docs_tool = create_retriever_tool(
    retriever,
    name="project_docs_search",
    description="Searches your project documentation and codebase."
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, tools=[docs_tool])

# ---------- Slack app ----------
app = App(token=bot_token)

def strip_bot_mention(text: str) -> str:
    return " ".join(t for t in text.split() if not t.startswith("<@")).strip()

@app.event("app_mention")
def handle_hello(body, say):
    event = body["event"]
    message = strip_bot_mention(event.get("text", ""))
    thread_ts = event.get("thread_ts", event["ts"])

    state = {"messages": [HumanMessage(content=message)]}
    response = agent.invoke(state)

    text = response["messages"][-1].content
    say(text=text, thread_ts=thread_ts)

if __name__ == "__main__":
    SocketModeHandler(app, app_token).start()
